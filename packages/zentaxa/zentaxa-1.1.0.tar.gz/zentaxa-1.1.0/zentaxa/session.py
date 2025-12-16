"""
ZENTAXA Session Management
==========================

Developer-friendly API for agent observability.
Instrument agents in ≤3 lines of code.

Usage:
    from zentaxa import observe_agent, start_session

    session = start_session(project="my-project")

    @observe_agent(session=session, agent="planner")
    def plan(input_data):
        return "plan output"

    # Or use the context manager
    with start_session(project="demo") as session:
        @observe_agent(session=session, agent="researcher")
        def research(query):
            return f"Results for: {query}"
"""

import functools
import time
import uuid
import json
import logging
import threading
import queue
import os
from typing import Optional, Dict, Any, Callable, List, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from contextlib import contextmanager

from .client import ZentaxaClient

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Structured telemetry event"""
    event_type: str
    timestamp: datetime
    session_id: str
    agent_name: Optional[str] = None
    step_name: Optional[str] = None
    step_number: Optional[int] = None
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost: Optional[float] = None
    model: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime to ISO format
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


class EventBatcher:
    """Batches events for efficient transmission"""
    
    def __init__(
        self,
        client: ZentaxaClient,
        batch_size: int = 10,
        flush_interval: float = 5.0,
        max_queue_size: int = 1000
    ):
        self.client = client
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._shutdown = threading.Event()
        self._flush_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def start(self):
        """Start the background flush thread"""
        if self._flush_thread is None or not self._flush_thread.is_alive():
            self._shutdown.clear()
            self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
            self._flush_thread.start()
    
    def stop(self):
        """Stop the flush thread and flush remaining events"""
        self._shutdown.set()
        self.flush()
        if self._flush_thread:
            self._flush_thread.join(timeout=2.0)
    
    def add(self, event: Event):
        """Add event to queue"""
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            logger.warning("Event queue full, dropping oldest event")
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(event)
            except queue.Empty:
                pass
    
    def flush(self):
        """Flush all queued events"""
        events = []
        while True:
            try:
                event = self._queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        
        if events:
            self._send_batch(events)
    
    def _flush_loop(self):
        """Background thread that periodically flushes events"""
        while not self._shutdown.is_set():
            time.sleep(self.flush_interval)
            
            # Collect batch
            events = []
            while len(events) < self.batch_size:
                try:
                    event = self._queue.get_nowait()
                    events.append(event)
                except queue.Empty:
                    break
            
            if events:
                self._send_batch(events)
    
    def _send_batch(self, events: List[Event]):
        """Send batch of events to server"""
        try:
            formatted_events = []
            for event in events:
                event_dict = event.to_dict()
                formatted_events.append({
                    "type": event.event_type,
                    "data": event_dict
                })
            
            self.client.bulk(formatted_events)
            logger.debug(f"Sent batch of {len(events)} events")
        except Exception as e:
            logger.error(f"Failed to send event batch: {e}")


class OfflineStorage:
    """Stores events locally when offline"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or os.path.expanduser("~/.zentaxa/offline"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_event(self, event: Event):
        """Save event to local JSONL file"""
        filename = self.storage_dir / f"events_{event.session_id}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    
    def get_pending_files(self) -> List[Path]:
        """Get all pending event files"""
        return list(self.storage_dir.glob("events_*.jsonl"))
    
    def load_events(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load events from a file"""
        events = []
        with open(filepath, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        return events
    
    def remove_file(self, filepath: Path):
        """Remove processed file"""
        if filepath.exists():
            filepath.unlink()


class Session:
    """
    Observability session for tracking agent executions.
    
    A session represents a single execution of an agent workflow,
    capturing all steps, tool calls, LLM requests, and metrics.
    
    Args:
        project: Project name for grouping sessions
        base_url: ZENTAXA backend URL
        api_key: Optional API key
        offline_mode: Enable offline storage when server unavailable
        batch_events: Enable event batching for efficiency
    
    Example:
        session = start_session(project="research-agent")
        
        # Session automatically tracks:
        # - Session start/end
        # - Agent steps
        # - Tool calls
        # - Costs and latency
    """
    
    def __init__(
        self,
        project: str,
        base_url: str = "https://zentaxaapp.azurewebsites.net",
        api_key: Optional[str] = None,
        offline_mode: bool = False,
        batch_events: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.project = project
        self.session_id = str(uuid.uuid4())
        self.base_url = base_url
        self.api_key = api_key
        self.offline_mode = offline_mode
        self.metadata = metadata or {}
        
        # Initialize client
        self.client = ZentaxaClient(base_url=base_url, api_key=api_key)
        
        # Event handling
        self._batcher: Optional[EventBatcher] = None
        self._offline_storage: Optional[OfflineStorage] = None
        
        if batch_events:
            self._batcher = EventBatcher(self.client)
            self._batcher.start()
        
        if offline_mode:
            self._offline_storage = OfflineStorage()
        
        # Session state
        self._step_counter = 0
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._total_cost = 0.0
        self._total_tokens = 0
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._is_started = False
        self._is_ended = False
        self._run_id: Optional[str] = None
    
    def start(self) -> "Session":
        """Start the session"""
        if self._is_started:
            logger.warning("Session already started")
            return self
        
        self._start_time = datetime.now(timezone.utc)
        self._is_started = True
        
        # Emit session.start event
        event = Event(
            event_type="session.start",
            timestamp=self._start_time,
            session_id=self.session_id,
            metadata={
                "project": self.project,
                **self.metadata
            }
        )
        
        # Send to server
        try:
            response = self.client.trace(
                run_id=None,
                agent_id=self.project,
                framework="zentaxa-sdk",
                event_type="agent_start",
                metadata={
                    "session_id": self.session_id,
                    "project": self.project,
                    **self.metadata
                }
            )
            self._run_id = response.get("run_id")
            logger.info(f"Session started: {self.session_id} (run_id: {self._run_id})")
        except Exception as e:
            logger.error(f"Failed to start session on server: {e}")
            if self._offline_storage:
                self._offline_storage.save_event(event)
        
        return self
    
    def end(self, output: Any = None, error: Optional[str] = None) -> Dict[str, Any]:
        """End the session and return summary"""
        if not self._is_started:
            logger.warning("Session not started")
            return {}
        
        if self._is_ended:
            logger.warning("Session already ended")
            return self.get_summary()
        
        self._end_time = datetime.now(timezone.utc)
        self._is_ended = True
        
        # Flush any remaining events
        if self._batcher:
            self._batcher.stop()
        
        # Emit session.end event
        duration_ms = (self._end_time - self._start_time).total_seconds() * 1000 if self._start_time else 0
        
        event = Event(
            event_type="session.end",
            timestamp=self._end_time,
            session_id=self.session_id,
            output_data=output,
            error=error,
            latency_ms=duration_ms,
            cost=self._total_cost,
            tokens_in=self._total_tokens,
            metadata={
                "total_steps": self._step_counter,
                "agents": list(self._agents.keys())
            }
        )
        
        # Send to server
        try:
            if self._run_id:
                self.client.trace(
                    run_id=self._run_id,
                    agent_id=self.project,
                    framework="zentaxa-sdk",
                    event_type="agent_end",
                    metadata={
                        "output": str(output) if output else None,
                        "error": error,
                        "total_cost": self._total_cost,
                        "total_tokens": self._total_tokens,
                        "total_steps": self._step_counter,
                        "duration_ms": duration_ms
                    }
                )
        except Exception as e:
            logger.error(f"Failed to end session on server: {e}")
            if self._offline_storage:
                self._offline_storage.save_event(event)
        
        logger.info(f"Session ended: {self.session_id}")
        return self.get_summary()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        duration_ms = None
        if self._start_time and self._end_time:
            duration_ms = (self._end_time - self._start_time).total_seconds() * 1000
        elif self._start_time:
            duration_ms = (datetime.now(timezone.utc) - self._start_time).total_seconds() * 1000
        
        return {
            "session_id": self.session_id,
            "project": self.project,
            "run_id": self._run_id,
            "status": "ended" if self._is_ended else "running" if self._is_started else "not_started",
            "total_steps": self._step_counter,
            "total_cost": self._total_cost,
            "total_tokens": self._total_tokens,
            "duration_ms": duration_ms,
            "agents": list(self._agents.keys())
        }
    
    def log_step(
        self,
        agent_name: str,
        step_name: str,
        input_data: Any = None,
        output_data: Any = None,
        latency_ms: Optional[float] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        cost: Optional[float] = None,
        model: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an agent step"""
        self._step_counter += 1
        
        # Track agent
        if agent_name not in self._agents:
            self._agents[agent_name] = {"steps": 0, "cost": 0.0, "tokens": 0}
        self._agents[agent_name]["steps"] += 1
        
        # Update totals
        if cost:
            self._total_cost += cost
            self._agents[agent_name]["cost"] += cost
        if tokens_in:
            self._total_tokens += tokens_in
            self._agents[agent_name]["tokens"] += tokens_in
        if tokens_out:
            self._total_tokens += tokens_out
            self._agents[agent_name]["tokens"] += tokens_out
        
        event = Event(
            event_type="agent.step.end",
            timestamp=datetime.now(timezone.utc),
            session_id=self.session_id,
            agent_name=agent_name,
            step_name=step_name,
            step_number=self._step_counter,
            input_data=_truncate(input_data),
            output_data=_truncate(output_data),
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            model=model,
            error=error,
            metadata=metadata or {}
        )
        
        self._emit_event(event)
    
    def log_tool_call(
        self,
        agent_name: str,
        tool_name: str,
        tool_args: Optional[Dict[str, Any]] = None,
        tool_result: Any = None,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Log a tool call"""
        event = Event(
            event_type="tool.call",
            timestamp=datetime.now(timezone.utc),
            session_id=self.session_id,
            agent_name=agent_name,
            tool_name=tool_name,
            tool_args=tool_args,
            output_data=_truncate(tool_result),
            latency_ms=latency_ms,
            error=error
        )
        
        self._emit_event(event)
    
    def _emit_event(self, event: Event):
        """Emit event to server or offline storage"""
        if self._batcher:
            self._batcher.add(event)
        elif self._offline_storage and self.offline_mode:
            self._offline_storage.save_event(event)
        else:
            # Direct send
            try:
                self._send_event_direct(event)
            except Exception as e:
                logger.error(f"Failed to send event: {e}")
                if self._offline_storage:
                    self._offline_storage.save_event(event)
    
    def _send_event_direct(self, event: Event):
        """Send event directly to server"""
        if event.event_type.startswith("agent.step"):
            self.client.agent_event(
                run_id=self._run_id or self.session_id,
                event_type="step_complete",
                step_number=event.step_number,
                step_name=event.step_name,
                action_type="llm" if event.model else "tool",
                input_data=event.input_data,
                output_data=event.output_data,
                latency_ms=event.latency_ms,
                cost_usd=event.cost,
                tokens_used=(event.tokens_in or 0) + (event.tokens_out or 0),
                metadata={
                    "agent_name": event.agent_name,
                    "model": event.model,
                    "error": event.error,
                    **event.metadata
                }
            )
        elif event.event_type == "tool.call":
            self.client.agent_event(
                run_id=self._run_id or self.session_id,
                event_type="step_complete",
                step_name=f"tool:{event.tool_name}",
                action_type="tool",
                input_data=event.tool_args,
                output_data=event.output_data,
                latency_ms=event.latency_ms,
                metadata={
                    "agent_name": event.agent_name,
                    "tool_name": event.tool_name,
                    "error": event.error
                }
            )
    
    def __enter__(self) -> "Session":
        """Context manager entry"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        error = str(exc_val) if exc_val else None
        self.end(error=error)
        return False  # Don't suppress exceptions


def _truncate(data: Any, max_length: int = 2000) -> Any:
    """Truncate data for storage"""
    if data is None:
        return None
    
    if isinstance(data, str):
        if len(data) > max_length:
            return data[:max_length] + "... [truncated]"
        return data
    
    if isinstance(data, (dict, list)):
        serialized = json.dumps(data, default=str)
        if len(serialized) > max_length:
            return serialized[:max_length] + "... [truncated]"
        return data
    
    return str(data)[:max_length]


def start_session(
    project: str,
    base_url: str = "https://zentaxaapp.azurewebsites.net",
    api_key: Optional[str] = None,
    offline_mode: bool = False,
    batch_events: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> Session:
    """
    Start a new observability session.
    
    This is the main entry point for instrumenting agent code.
    
    Args:
        project: Project name for grouping sessions
        base_url: ZENTAXA backend URL (default: cloud instance)
        api_key: Optional API key for authentication
        offline_mode: Store events locally when offline
        batch_events: Batch events for efficient transmission
        metadata: Additional metadata for the session
    
    Returns:
        Session object for tracking agent execution
    
    Example:
        # Simple usage
        session = start_session(project="research-bot")
        session.start()
        # ... run agent ...
        session.end()
        
        # Context manager
        with start_session(project="demo") as session:
            @observe_agent(session=session, agent="planner")
            def plan(query):
                return "plan"
    """
    session = Session(
        project=project,
        base_url=base_url,
        api_key=api_key,
        offline_mode=offline_mode,
        batch_events=batch_events,
        metadata=metadata
    )
    return session.start()


def observe_agent(
    session: Session,
    agent: str,
    capture_input: bool = True,
    capture_output: bool = True
) -> Callable:
    """
    Decorator for observing agent functions.
    
    Automatically captures:
      - Function inputs
      - Function outputs
      - Execution time (latency)
      - Errors
    
    Args:
        session: Active Session object
        agent: Agent name for grouping steps
        capture_input: Whether to capture function input
        capture_output: Whether to capture function output
    
    Returns:
        Decorated function
    
    Example:
        session = start_session(project="demo")
        
        @observe_agent(session=session, agent="planner")
        def plan(input_data):
            return "plan output"
        
        # Async functions are also supported
        @observe_agent(session=session, agent="researcher")
        async def research(query):
            return f"Results for: {query}"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                # Build input data
                input_data = None
                if capture_input:
                    if args and kwargs:
                        input_data = {"args": args, "kwargs": kwargs}
                    elif args:
                        input_data = args[0] if len(args) == 1 else args
                    elif kwargs:
                        input_data = kwargs
                
                # Log step
                session.log_step(
                    agent_name=agent,
                    step_name=func.__name__,
                    input_data=input_data if capture_input else None,
                    output_data=result if capture_output else None,
                    latency_ms=latency_ms,
                    error=error
                )
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            import asyncio
            start_time = time.time()
            error = None
            result = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                # Build input data
                input_data = None
                if capture_input:
                    if args and kwargs:
                        input_data = {"args": args, "kwargs": kwargs}
                    elif args:
                        input_data = args[0] if len(args) == 1 else args
                    elif kwargs:
                        input_data = kwargs
                
                # Log step
                session.log_step(
                    agent_name=agent,
                    step_name=func.__name__,
                    input_data=input_data if capture_input else None,
                    output_data=result if capture_output else None,
                    latency_ms=latency_ms,
                    error=error
                )
        
        # Check if function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def observe_tool(
    session: Session,
    agent: str,
    tool_name: Optional[str] = None
) -> Callable:
    """
    Decorator for observing tool functions.
    
    Args:
        session: Active Session object
        agent: Agent name that owns this tool
        tool_name: Tool name (defaults to function name)
    
    Example:
        @observe_tool(session=session, agent="researcher", tool_name="web_search")
        def search_web(query: str) -> str:
            # ... search implementation ...
            return results
    """
    def decorator(func: Callable) -> Callable:
        actual_tool_name = tool_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            result = None
            
            # Build tool args
            tool_args = {}
            if args:
                tool_args["args"] = args
            if kwargs:
                tool_args.update(kwargs)
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                session.log_tool_call(
                    agent_name=agent,
                    tool_name=actual_tool_name,
                    tool_args=tool_args if tool_args else None,
                    tool_result=result,
                    latency_ms=latency_ms,
                    error=error
                )
        
        return wrapper
    
    return decorator
