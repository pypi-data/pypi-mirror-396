#!/usr/bin/env python3
"""
Splunk GenAI Observability SDK
==============================

Instrumentation library for tracing GenAI/LLM applications.

Usage:
    from genai_telemetry import setup_splunk_telemetry, trace_llm, trace_chain
    
    setup_splunk_telemetry(
        workflow_name="my-app",
        splunk_hec_url="http://splunk:8088",
        splunk_hec_token="your-token"
    )
    
    @trace_llm(model_name="gpt-4o", model_provider="openai")
    def chat(message):
        return client.chat.completions.create(...)
"""

__version__ = "2.1.0"

import json
import time
import uuid
import urllib.request
import urllib.error
import ssl
import threading
import logging
import atexit
from functools import wraps
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable
from contextlib import contextmanager

logger = logging.getLogger("genai_telemetry")


# =============================================================================
# EXPORTERS
# =============================================================================

class SplunkHECExporter:
    """Sends spans to Splunk via HTTP Event Collector."""
    
    def __init__(
        self,
        hec_url: str,
        hec_token: str,
        index: str = "genai_traces",
        sourcetype: str = "genai:trace",
        verify_ssl: bool = False,
        batch_size: int = 1,
        flush_interval: float = 5.0
    ):
        # Build the HEC URL
        self.hec_url = hec_url.rstrip("/")
        if not self.hec_url.endswith("/services/collector/event"):
            self.hec_url += "/services/collector/event"
        
        self.hec_token = hec_token
        self.index = index
        self.sourcetype = sourcetype
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        if not verify_ssl:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        self._batch: List[dict] = []
        self._lock = threading.Lock()
        self._flush_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Register cleanup on exit
        atexit.register(self.stop)
    
    def start(self):
        """Start the background flush thread."""
        if self._running:
            return
        self._running = True
        if self.batch_size > 1:
            self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
            self._flush_thread.start()
    
    def stop(self):
        """Stop the background flush thread and flush remaining spans."""
        self._running = False
        self._flush()
    
    def _flush_loop(self):
        """Background thread to periodically flush spans."""
        while self._running:
            time.sleep(self.flush_interval)
            self._flush()
    
    def _flush(self):
        """Flush batched spans to Splunk."""
        with self._lock:
            if not self._batch:
                return
            batch = self._batch.copy()
            self._batch = []
        
        self._send_batch(batch)
    
    def _send_batch(self, batch: List[dict]) -> bool:
        """Send a batch of events to Splunk HEC."""
        if not batch:
            return True
        
        # Build payload - one JSON per line
        lines = []
        for span in batch:
            event = {
                "index": self.index,
                "sourcetype": self.sourcetype,
                "source": "genai-telemetry",
                "event": span
            }
            lines.append(json.dumps(event))
        
        payload = "\n".join(lines)
        return self._send(payload)
    
    def _send(self, payload: str) -> bool:
        """Send payload to Splunk HEC."""
        data = payload.encode("utf-8")
        
        req = urllib.request.Request(
            self.hec_url,
            data=data,
            headers={
                "Authorization": f"Splunk {self.hec_token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=10) as resp:
                return resp.status == 200
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            logger.error(f"HEC HTTP Error {e.code}: {error_body}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"HEC URL Error: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"HEC Error: {e}")
            return False
    
    def export(self, span_data: dict) -> bool:
        """Export a span - sends immediately if batch_size=1, otherwise batches."""
        if self.batch_size <= 1:
            # Send immediately
            return self._send_batch([span_data])
        
        # Add to batch
        with self._lock:
            self._batch.append(span_data)
            should_flush = len(self._batch) >= self.batch_size
        
        if should_flush:
            self._flush()
        
        return True


class ConsoleExporter:
    """Prints spans to console."""
    
    def export(self, span_data: dict) -> bool:
        span_type = span_data.get('span_type', 'UNKNOWN')
        name = span_data.get('name', 'unknown')
        duration = span_data.get('duration_ms', 0)
        status = span_data.get('status', 'OK')
        print(f"[SPAN] {span_type:12} | {name:30} | {duration:>8.0f}ms | {status}")
        return True


class FileExporter:
    """Writes spans to a JSONL file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._lock = threading.Lock()
    
    def export(self, span_data: dict) -> bool:
        try:
            with self._lock:
                with open(self.file_path, "a") as f:
                    f.write(json.dumps(span_data) + "\n")
            return True
        except Exception as e:
            logger.error(f"Failed to write to file: {e}")
            return False


class MultiExporter:
    """Sends spans to multiple exporters."""
    
    def __init__(self, exporters: List[Any]):
        self.exporters = exporters
    
    def export(self, span_data: dict) -> bool:
        results = []
        for e in self.exporters:
            try:
                results.append(e.export(span_data))
            except Exception as ex:
                logger.error(f"Exporter error: {ex}")
                results.append(False)
        return any(results)


# =============================================================================
# TELEMETRY CORE
# =============================================================================

class Span:
    """Represents a single span in a trace."""
    
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        name: str,
        span_type: str,
        workflow_name: str = None,
        parent_span_id: str = None,
        **kwargs
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.name = name
        self.span_type = span_type
        self.workflow_name = workflow_name
        self.parent_span_id = parent_span_id
        self.start_time = time.time()
        self.end_time = None
        self.duration_ms = None
        self.status = "OK"
        self.is_error = 0
        self.error_message = None
        self.error_type = None
        
        # LLM fields
        self.model_name = kwargs.get("model_name")
        self.model_provider = kwargs.get("model_provider")
        self.input_tokens = kwargs.get("input_tokens", 0)
        self.output_tokens = kwargs.get("output_tokens", 0)
        self.temperature = kwargs.get("temperature")
        self.max_tokens = kwargs.get("max_tokens")
        
        # Embedding fields
        self.embedding_model = kwargs.get("embedding_model")
        self.embedding_dimensions = kwargs.get("embedding_dimensions")
        
        # Retrieval fields
        self.vector_store = kwargs.get("vector_store")
        self.documents_retrieved = kwargs.get("documents_retrieved", 0)
        self.relevance_score = kwargs.get("relevance_score")
        
        # Tool fields
        self.tool_name = kwargs.get("tool_name")
        
        # Agent fields
        self.agent_name = kwargs.get("agent_name")
        self.agent_type = kwargs.get("agent_type")
        
        # Custom attributes
        self.attributes = {}
    
    def set_attribute(self, key: str, value: Any):
        """Set a custom attribute."""
        self.attributes[key] = value
    
    def set_error(self, error: Exception):
        """Set error information."""
        self.status = "ERROR"
        self.is_error = 1
        self.error_message = str(error)
        self.error_type = type(error).__name__
    
    def finish(self, error: Exception = None):
        """Complete the span."""
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        if error:
            self.set_error(error)
    
    def to_dict(self) -> dict:
        """Convert span to dictionary."""
        data = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "name": self.name,
            "span_type": self.span_type,
            "timestamp": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat(),
            "duration_ms": self.duration_ms or 0,
            "status": self.status,
            "is_error": self.is_error,
        }
        
        # Add optional fields if set
        optional_fields = [
            "workflow_name", "parent_span_id", "error_message", "error_type",
            "model_name", "model_provider", "input_tokens", "output_tokens",
            "temperature", "max_tokens", "embedding_model", "embedding_dimensions",
            "vector_store", "documents_retrieved", "relevance_score",
            "tool_name", "agent_name", "agent_type"
        ]
        
        for field in optional_fields:
            value = getattr(self, field, None)
            if value is not None and value != "" and value != 0:
                data[field] = value
        
        # Always include token counts for LLM spans
        if self.span_type == "LLM":
            data["input_tokens"] = self.input_tokens or 0
            data["output_tokens"] = self.output_tokens or 0
        
        if self.attributes:
            data.update(self.attributes)
        
        return data


class GenAITelemetry:
    """Main telemetry manager."""
    
    def __init__(
        self,
        workflow_name: str,
        exporter: Any,
        service_name: str = None
    ):
        self.workflow_name = workflow_name
        self.service_name = service_name or workflow_name
        self.exporter = exporter
        self._trace_id = threading.local()
        self._span_stack = threading.local()
    
    @property
    def trace_id(self) -> str:
        if not hasattr(self._trace_id, "value") or self._trace_id.value is None:
            self._trace_id.value = uuid.uuid4().hex
        return self._trace_id.value
    
    @trace_id.setter
    def trace_id(self, value: str):
        self._trace_id.value = value
    
    @property
    def span_stack(self) -> List[Span]:
        if not hasattr(self._span_stack, "stack"):
            self._span_stack.stack = []
        return self._span_stack.stack
    
    def new_trace(self) -> str:
        """Start a new trace and return the trace_id."""
        self._trace_id.value = uuid.uuid4().hex
        return self._trace_id.value
    
    def current_span(self) -> Optional[Span]:
        """Get the current span."""
        return self.span_stack[-1] if self.span_stack else None
    
    @contextmanager
    def start_span(self, name: str, span_type: str, **kwargs):
        """Context manager for creating spans."""
        parent_id = self.span_stack[-1].span_id if self.span_stack else None
        
        span = Span(
            trace_id=self.trace_id,
            span_id=uuid.uuid4().hex[:16],
            name=name,
            span_type=span_type,
            workflow_name=self.workflow_name,
            parent_span_id=parent_id,
            **kwargs
        )
        
        self.span_stack.append(span)
        
        try:
            yield span
            span.finish()
        except Exception as e:
            span.finish(error=e)
            raise
        finally:
            self.span_stack.pop()
            self.exporter.export(span.to_dict())
    
    def send_span(self, span_type: str, name: str, duration_ms: float = None, **kwargs) -> bool:
        """Send a span directly."""
        parent_id = self.span_stack[-1].span_id if self.span_stack else None
        
        span_data = {
            "trace_id": self.trace_id,
            "span_id": uuid.uuid4().hex[:16],
            "parent_span_id": parent_id,
            "span_type": span_type,
            "name": name,
            "workflow_name": self.workflow_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms or 0,
            "status": kwargs.pop("status", "OK"),
            "is_error": kwargs.pop("is_error", 0),
        }
        
        # Add remaining kwargs
        for key, value in kwargs.items():
            if value is not None and value != "":
                span_data[key] = value
        
        return self.exporter.export(span_data)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_telemetry: Optional[GenAITelemetry] = None


def setup_splunk_telemetry(
    workflow_name: str,
    splunk_hec_url: str = None,
    splunk_hec_token: str = None,
    splunk_index: str = "genai_traces",
    splunk_sourcetype: str = "genai:trace",
    service_name: str = None,
    console: bool = False,
    file_path: str = None,
    verify_ssl: bool = False,
    batch_size: int = 1,
    flush_interval: float = 5.0
) -> GenAITelemetry:
    """
    Initialize Splunk GenAI telemetry.
    
    Args:
        workflow_name: Name of your workflow/application
        splunk_hec_url: Splunk HEC URL (e.g., http://splunk:8088)
        splunk_hec_token: Splunk HEC token
        splunk_index: Target Splunk index (default: genai_traces)
        splunk_sourcetype: Sourcetype (default: genai:trace)
        service_name: Optional service name
        console: If True, also print traces to console
        file_path: If set, also write traces to this file
        verify_ssl: Verify SSL certificates (default: False)
        batch_size: Number of spans to batch (default: 1 = immediate)
        flush_interval: Seconds between batch flushes
    
    Returns:
        GenAITelemetry instance
    """
    global _telemetry
    
    exporters = []
    
    if splunk_hec_url and splunk_hec_token:
        splunk_exporter = SplunkHECExporter(
            hec_url=splunk_hec_url,
            hec_token=splunk_hec_token,
            index=splunk_index,
            sourcetype=splunk_sourcetype,
            verify_ssl=verify_ssl,
            batch_size=batch_size,
            flush_interval=flush_interval
        )
        splunk_exporter.start()
        exporters.append(splunk_exporter)
    
    if console:
        exporters.append(ConsoleExporter())
    
    if file_path:
        exporters.append(FileExporter(file_path))
    
    if not exporters:
        raise ValueError("Must provide splunk_hec_url/token, console=True, or file_path")
    
    exporter = MultiExporter(exporters) if len(exporters) > 1 else exporters[0]
    
    _telemetry = GenAITelemetry(
        workflow_name=workflow_name,
        exporter=exporter,
        service_name=service_name
    )
    
    return _telemetry


def get_telemetry() -> GenAITelemetry:
    """Get the telemetry instance."""
    if _telemetry is None:
        raise RuntimeError("Call setup_splunk_telemetry() first")
    return _telemetry


# =============================================================================
# DECORATORS
# =============================================================================

def trace_llm(
    model_name: str,
    model_provider: str = "openai"
) -> Callable:
    """Decorator to trace LLM calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                # Extract token usage from response
                input_tokens = 0
                output_tokens = 0
                
                if hasattr(result, "usage") and result.usage:
                    input_tokens = getattr(result.usage, "prompt_tokens", 0) or 0
                    output_tokens = getattr(result.usage, "completion_tokens", 0) or 0
                
                telemetry.send_span(
                    span_type="LLM",
                    name=func.__name__,
                    model_name=model_name,
                    model_provider=model_provider,
                    duration_ms=duration,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="LLM",
                    name=func.__name__,
                    model_name=model_name,
                    model_provider=model_provider,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e),
                    error_type=type(e).__name__
                )
                raise
        return wrapper
    return decorator


def trace_embedding(model: str) -> Callable:
    """Decorator to trace embedding calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                telemetry.send_span(
                    span_type="EMBEDDING",
                    name=func.__name__,
                    embedding_model=model,
                    duration_ms=duration
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="EMBEDDING",
                    name=func.__name__,
                    embedding_model=model,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def trace_retrieval(vector_store: str, embedding_model: str = None) -> Callable:
    """Decorator to trace retrieval calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                docs_count = len(result) if isinstance(result, (list, tuple)) else 0
                
                telemetry.send_span(
                    span_type="RETRIEVER",
                    name=func.__name__,
                    vector_store=vector_store,
                    embedding_model=embedding_model,
                    documents_retrieved=docs_count,
                    duration_ms=duration
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="RETRIEVER",
                    name=func.__name__,
                    vector_store=vector_store,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def trace_tool(tool_name: str) -> Callable:
    """Decorator to trace tool calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                telemetry.send_span(
                    span_type="TOOL",
                    name=func.__name__,
                    tool_name=tool_name,
                    duration_ms=duration
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="TOOL",
                    name=func.__name__,
                    tool_name=tool_name,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def trace_chain(name: str) -> Callable:
    """Decorator to trace chain/pipeline calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            telemetry.new_trace()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                telemetry.send_span(
                    span_type="CHAIN",
                    name=name,
                    duration_ms=duration
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="CHAIN",
                    name=name,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def trace_agent(agent_name: str, agent_type: str = None) -> Callable:
    """Decorator to trace agent calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry = get_telemetry()
            telemetry.new_trace()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start) * 1000, 2)
                
                telemetry.send_span(
                    span_type="AGENT",
                    name=func.__name__,
                    agent_name=agent_name,
                    agent_type=agent_type,
                    duration_ms=duration
                )
                return result
                
            except Exception as e:
                duration = round((time.time() - start) * 1000, 2)
                telemetry.send_span(
                    span_type="AGENT",
                    name=func.__name__,
                    agent_name=agent_name,
                    agent_type=agent_type,
                    duration_ms=duration,
                    status="ERROR",
                    is_error=1,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


# =============================================================================
# PUBLIC API
# =============================================================================

# =============================================================================
# AUDIT EVENTS
# =============================================================================

class AuditLogger:
    """Logs audit events to Splunk."""
    
    def __init__(self, exporter, workflow_name: str, index: str = "genai_audit"):
        self.exporter = exporter
        self.workflow_name = workflow_name
        self.index = index
    
    def _send_audit(self, event_type: str, **kwargs) -> bool:
        """Send audit event."""
        audit_data = {
            "event_type": event_type,
            "audit_id": uuid.uuid4().hex[:16],
            "workflow_name": self.workflow_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        audit_data.update(kwargs)
        
        # Send to audit index
        if hasattr(self.exporter, 'exporters'):
            # MultiExporter - find Splunk exporter
            for exp in self.exporter.exporters:
                if isinstance(exp, SplunkHECExporter):
                    original_index = exp.index
                    exp.index = self.index
                    result = exp.export(audit_data)
                    exp.index = original_index
                    return result
        elif isinstance(self.exporter, SplunkHECExporter):
            original_index = self.exporter.index
            self.exporter.index = self.index
            result = self.exporter.export(audit_data)
            self.exporter.index = original_index
            return result
        
        return self.exporter.export(audit_data)
    
    def log_query(
        self,
        user_id: str,
        query: str,
        session_id: str = None,
        metadata: dict = None
    ) -> bool:
        """Log user query."""
        return self._send_audit(
            event_type="QUERY",
            user_id=user_id,
            query=query,
            query_length=len(query),
            session_id=session_id,
            metadata=metadata or {}
        )
    
    def log_response(
        self,
        user_id: str,
        query: str,
        response: str,
        model_name: str = None,
        latency_ms: float = None,
        session_id: str = None,
        metadata: dict = None
    ) -> bool:
        """Log LLM response."""
        return self._send_audit(
            event_type="RESPONSE",
            user_id=user_id,
            query=query,
            response=response[:1000] if response else None,  # Truncate
            response_length=len(response) if response else 0,
            model_name=model_name,
            latency_ms=latency_ms,
            session_id=session_id,
            metadata=metadata or {}
        )
    
    def log_feedback(
        self,
        user_id: str,
        trace_id: str,
        rating: int = None,
        feedback_type: str = None,
        comment: str = None,
        session_id: str = None
    ) -> bool:
        """Log user feedback (thumbs up/down, ratings)."""
        return self._send_audit(
            event_type="FEEDBACK",
            user_id=user_id,
            trace_id=trace_id,
            rating=rating,
            feedback_type=feedback_type,  # "positive", "negative", "report"
            comment=comment,
            session_id=session_id
        )
    
    def log_moderation(
        self,
        user_id: str,
        content: str,
        moderation_result: str,
        categories: list = None,
        action_taken: str = None,
        trace_id: str = None
    ) -> bool:
        """Log content moderation events."""
        return self._send_audit(
            event_type="MODERATION",
            user_id=user_id,
            content=content[:500] if content else None,  # Truncate
            moderation_result=moderation_result,  # "pass", "flag", "block"
            categories=categories or [],
            action_taken=action_taken,
            trace_id=trace_id
        )
    
    def log_pii_detection(
        self,
        user_id: str,
        pii_types: list,
        action_taken: str,
        content_type: str = "input",
        trace_id: str = None
    ) -> bool:
        """Log PII detection events."""
        return self._send_audit(
            event_type="PII_DETECTION",
            user_id=user_id,
            pii_types=pii_types,  # ["email", "phone", "ssn"]
            pii_count=len(pii_types),
            action_taken=action_taken,  # "masked", "blocked", "logged"
            content_type=content_type,  # "input", "output"
            trace_id=trace_id
        )
    
    def log_policy_violation(
        self,
        user_id: str,
        policy_name: str,
        violation_type: str,
        action_taken: str,
        details: str = None,
        trace_id: str = None
    ) -> bool:
        """Log policy violation events."""
        return self._send_audit(
            event_type="POLICY_VIOLATION",
            user_id=user_id,
            policy_name=policy_name,
            violation_type=violation_type,
            action_taken=action_taken,
            details=details,
            trace_id=trace_id
        )
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        ip_address: str = None,
        user_agent: str = None
    ) -> bool:
        """Log access/authentication events."""
        return self._send_audit(
            event_type="ACCESS",
            user_id=user_id,
            action=action,  # "login", "logout", "api_call"
            resource=resource,
            result=result,  # "success", "denied", "error"
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_cost(
        self,
        user_id: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        trace_id: str = None
    ) -> bool:
        """Log cost/billing events."""
        return self._send_audit(
            event_type="COST",
            user_id=user_id,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            trace_id=trace_id
        )
    
    def log_custom(self, event_type: str, **kwargs) -> bool:
        """Log custom audit event."""
        return self._send_audit(event_type=event_type, **kwargs)


# Global audit logger
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get the audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        telemetry = get_telemetry()
        _audit_logger = AuditLogger(
            exporter=telemetry.exporter,
            workflow_name=telemetry.workflow_name
        )
    return _audit_logger


def setup_audit_logger(index: str = "genai_audit") -> AuditLogger:
    """Setup audit logger with custom index."""
    global _audit_logger
    telemetry = get_telemetry()
    _audit_logger = AuditLogger(
        exporter=telemetry.exporter,
        workflow_name=telemetry.workflow_name,
        index=index
    )
    return _audit_logger


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "__version__",
    "setup_splunk_telemetry",
    "get_telemetry",
    "GenAITelemetry",
    "Span",
    "SplunkHECExporter",
    "ConsoleExporter",
    "FileExporter",
    "MultiExporter",
    "trace_llm",
    "trace_embedding",
    "trace_retrieval",
    "trace_tool",
    "trace_chain",
    "trace_agent",
    # Audit
    "AuditLogger",
    "get_audit_logger",
    "setup_audit_logger",
]
