"""
llmtrace-lite: Zero-config decorator for tracing LLM calls.
"""

import functools
import json
import os
import time
import traceback
from datetime import datetime
from typing import Any, Callable


def trace(func: Callable) -> Callable:
    """
    Decorator that logs basic metadata about LLM function calls.
    
    Captures: function name, timing, status, model, prompt/output sizes.
    Logs to stdout by default, or to file if LLMTRACE_FILE is set.
    """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Start timing
        start_time = time.time()
        start_dt = datetime.utcnow().isoformat() + 'Z'
        
        # Extract metadata
        metadata = {
            'function': func.__name__,
            'start_time': start_dt,
        }
        
        # Try to extract model from kwargs
        if 'model' in kwargs:
            metadata['model'] = kwargs['model']
        
        # Try to extract prompt size
        if 'prompt' in kwargs and isinstance(kwargs['prompt'], str):
            metadata['prompt_chars'] = len(kwargs['prompt'])
        elif args and isinstance(args[0], str):
            # First positional arg might be prompt
            metadata['prompt_chars'] = len(args[0])
        
        # Check for retry count on function
        if hasattr(func, 'retries'):
            metadata['retries'] = func.retries
        
        # Execute function
        result = None
        error = None
        status = 'success'
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            status = 'error'
            error = str(e)
            metadata['status'] = status
            metadata['error'] = error
            metadata['exception_type'] = type(e).__name__
            
            # Calculate timing for error case
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            metadata['latency_ms'] = latency_ms
            metadata['end_time'] = datetime.utcnow().isoformat() + 'Z'
            
            # Log the trace
            _log_trace(metadata, start_time, status)
            raise
        
        # Calculate timing
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        metadata['latency_ms'] = latency_ms
        metadata['end_time'] = datetime.utcnow().isoformat() + 'Z'
        metadata['status'] = status
        
        # Try to extract output size
        if isinstance(result, str):
            metadata['output_chars'] = len(result)
        
        # Log the trace
        _log_trace(metadata, start_time, status)
        
        return result
    
    return wrapper


def _log_trace(metadata: dict, start_time: float, status: str) -> None:
    """
    Log trace data to stdout or file.
    """
    trace_file = os.environ.get('LLMTRACE_FILE')
    
    if trace_file:
        # Append JSON line to file
        try:
            with open(trace_file, 'a') as f:
                f.write(json.dumps(metadata) + '\n')
        except Exception:
            # Silently fail - don't break user code
            pass
    else:
        # Print readable format to stdout
        print(f"[llmtrace] {metadata['function']}")
        
        # Print key fields in order
        if 'model' in metadata:
            print(f"  model: {metadata['model']}")
        
        if 'latency_ms' in metadata:
            print(f"  latency_ms: {metadata['latency_ms']}")
        
        if 'prompt_chars' in metadata:
            print(f"  prompt_chars: {metadata['prompt_chars']}")
        
        if 'output_chars' in metadata:
            print(f"  output_chars: {metadata['output_chars']}")
        
        if 'retries' in metadata:
            print(f"  retries: {metadata['retries']}")
        
        print(f"  status: {metadata['status']}")
        
        if 'error' in metadata:
            print(f"  error: {metadata['error']}")
        
        print()  # Blank line for readability