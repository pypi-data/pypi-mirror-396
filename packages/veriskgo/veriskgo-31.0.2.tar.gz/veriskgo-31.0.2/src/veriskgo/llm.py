# veriskgo/llm.py
import time
import traceback
import functools
import inspect
from typing import Any, Dict, Optional

from veriskgo.trace_manager import TraceManager
from veriskgo.trace_manager import serialize_value

# ============================================================
# UNIVERSAL MODEL-AGNOSTIC NORMALIZERS
# ============================================================

def extract_text(resp: dict) -> str:
    """
    Extract model output text from ANY LLM:
    - Bedrock Converse API
    - Bedrock InvokeModel API (Titan / Llama text / Mistral text)
    - Anthropic
    - OpenAI
    - Cohere
    - Generic JSON
    """
    if not isinstance(resp, dict):
        return str(resp)

    try:
        return resp["output"]["message"]["content"][0]["text"]   # Bedrock Converse
    except Exception:
        pass

    try:
        return resp["content"][0]["text"]  # Bedrock Claude legacy
    except Exception:
        pass

    try:
        return resp["results"][0]["outputText"]  # Titan
    except Exception:
        pass

    try:
        return resp["generation"]  # Llama / Mistral text
    except Exception:
        pass

    try:
        return resp["outputs"][0]["text"]  # Mistral AI
    except Exception:
        pass

    try:
        return resp["text"]  # Cohere
    except Exception:
        pass

    try:
        return resp["choices"][0]["message"]["content"]  # OpenAI GPT
    except Exception:
        pass

    return str(resp)


def extract_usage(resp: dict) -> Dict[str, int]:
    """Normalize token usage across all model providers."""
    usage = {"input": 0, "output": 0, "total": 0}

    if not isinstance(resp, dict):
        return usage

    if "usage" in resp:
        usage["input"] = resp["usage"].get("inputTokens", 0)
        usage["output"] = resp["usage"].get("outputTokens", 0)

    if "results" in resp:
        usage["output"] = resp["results"][0].get("tokenCount", usage["output"])

    if "usage" in resp and "prompt_tokens" in resp["usage"]:
        usage["input"] = resp["usage"]["prompt_tokens"]
        usage["output"] = resp["usage"]["completion_tokens"]
        usage["total"] = resp["usage"]["total_tokens"]
        return usage

    usage["total"] = usage["input"] + usage["output"]
    return usage


# ============================================================
# Decorator: track_llm_call (Generation Span)
# ============================================================

# ============================================================
# Decorator: _track_generic_llm (Generation Span)
# ============================================================

from veriskgo.trace_manager import capture_function_locals
import sys

def _track_generic_llm(name=None, tags=None, capture_locals=True, capture_self=True):
    """
    Wraps an LLM call inside a Langfuse-compatible 'generation' span.
    Supports BOTH sync and async LLM functions.
    NEVER modifies the user function's return value.
    """

    def decorator(func):
        span_name = name or func.__name__
        is_async = inspect.iscoroutinefunction(func)

        # =====================================================================
        # SHARED PARSE FUNCTION
        # =====================================================================
        def parse_for_tracing(resp):
            text = extract_text(resp)
            usage = extract_usage(resp)

            input_tokens = usage["input"]
            output_tokens = usage["output"]
            total_tokens = usage["total"]

            input_cost = input_tokens * 0.0000015
            output_cost = output_tokens * 0.000005

            return {
                "text": text,
                "usage_details": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens,
                },
                "cost_details": {
                    "input": round(input_cost, 6),
                    "output": round(output_cost, 6),
                    "total": round(input_cost + output_cost, 6),
                },
            }

        # =====================================================================
        # SYNC WRAPPER
        # =====================================================================
        def sync_wrapper(*args, **kwargs):
            if not TraceManager.has_active_trace():
                return func(*args, **kwargs)
            
            # Get parent span ID from stack
            with TraceManager._lock:
                parent_span_id = TraceManager._active["stack"][-1]["span_id"] if TraceManager._active["stack"] else None
                trace_id = TraceManager._active["trace_id"]
            
            span_id = TraceManager._id()
            start_time = time.time()
            start_timestamp = TraceManager._now()
            
            # Extract prompt
            prompt_value = None
            for a in args:
                if isinstance(a, str):
                    prompt_value = a
                    break
            
            tracer, locals_before, locals_after = capture_function_locals(func, capture_locals=capture_locals, capture_self=capture_self)
            if tracer:
                sys.settrace(tracer)

            try:
                resp = func(*args, **kwargs)  # ORIGINAL RETURN VALUE
                if tracer:
                    sys.settrace(None)

                latency = int((time.time() - start_time) * 1000)

                parsed = parse_for_tracing(resp)

                # Send generation span event to SQS immediately
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "type": "generation",
                    "timestamp": start_timestamp,
                    "duration_ms": latency,
                    "input": {
                        "prompt": prompt_value,
                        "model": resp.get("model") if isinstance(resp, dict) else None,
                        "messages": resp.get("messages") if isinstance(resp, dict) else None,
                        "args": serialize_value(args),
                        "kwargs": serialize_value(kwargs),
                    },
                    "output": {
                        "text": serialize_value(parsed["text"]),
                        "finish_reason": "stop",
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                        "raw": serialize_value(resp) if isinstance(resp, (dict, list)) else str(resp)[:1000]
                    },
                    "model": resp.get("model") if isinstance(resp, dict) else None,
                    "usage_details": parsed["usage_details"],
                    "cost_details": parsed["cost_details"],
                    "usage": {
                        "input_tokens": parsed["usage_details"]["input"],
                        "output_tokens": parsed["usage_details"]["output"],
                        "total_tokens": parsed["usage_details"]["total"],
                    },
                    "cost": {
                        "input_cost": parsed["cost_details"]["input"],
                        "output_cost": parsed["cost_details"]["output"],
                        "total_cost": parsed["cost_details"]["total"],
                    },
                    "metadata": tags or {}
                }
                
                from .sqs import send_to_sqs
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (generation): {span_name}")

                return resp  # <-- RETURN ORIGINAL VALUE

            except Exception as e:
                if tracer:
                    sys.settrace(None)

                latency = int((time.time() - start_time) * 1000)

                # Send error span event
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "type": "generation",
                    "timestamp": start_timestamp,
                    "duration_ms": latency,
                    "input": {
                        "prompt": prompt_value,
                        "args": serialize_value(args),
                        "kwargs": serialize_value(kwargs)
                    },
                    "output": {
                        "status": "error",
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                    },
                    "metadata": tags or {}
                }
                
                from .sqs import send_to_sqs
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (error): {span_name}")
                raise

        # =====================================================================
        # ASYNC WRAPPER
        # =====================================================================
        async def async_wrapper(*args, **kwargs):
            if not TraceManager.has_active_trace():
                return await func(*args, **kwargs)
            
            # Get parent span ID from stack
            with TraceManager._lock:
                parent_span_id = TraceManager._active["stack"][-1]["span_id"] if TraceManager._active["stack"] else None
                trace_id = TraceManager._active["trace_id"]
            
            span_id = TraceManager._id()
            start_time = time.time()
            start_timestamp = TraceManager._now()
            
            # Extract prompt
            prompt_value = None
            for a in args:
                if isinstance(a, str):
                    prompt_value = a
                    break
            
            tracer, locals_before, locals_after = capture_function_locals(func, capture_locals=capture_locals, capture_self=capture_self)
            if tracer:
                sys.settrace(tracer)

            try:
                resp = await func(*args, **kwargs)  # ORIGINAL OUTPUT
                if tracer:
                    sys.settrace(None)

                latency = int((time.time() - start_time) * 1000)

                parsed = parse_for_tracing(resp)

                # Send generation span event to SQS immediately
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "type": "generation",
                    "timestamp": start_timestamp,
                    "duration_ms": latency,
                    "input": {
                        "prompt": prompt_value,
                        "model": resp.get("model") if isinstance(resp, dict) else None,
                        "messages": resp.get("messages") if isinstance(resp, dict) else None,
                        "args": serialize_value(args),
                        "kwargs": serialize_value(kwargs),
                    },

                    "output": {
                        "text": serialize_value(parsed["text"]),
                        "finish_reason": "stop",
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                        "raw": serialize_value(resp) if isinstance(resp, (dict, list)) else str(resp)[:1000]
                    },
                    "model": resp.get("model") if isinstance(resp, dict) else None,
                    "usage_details": parsed["usage_details"],
                    "cost_details": parsed["cost_details"],
                    "usage": {
                        "input_tokens": parsed["usage_details"]["input"],
                        "output_tokens": parsed["usage_details"]["output"],
                        "total_tokens": parsed["usage_details"]["total"],
                    },
                    "cost": {
                        "input_cost": parsed["cost_details"]["input"],
                        "output_cost": parsed["cost_details"]["output"],
                        "total_cost": parsed["cost_details"]["total"],
                    },
                    "metadata": tags or {}
                }
                
                from .sqs import send_to_sqs
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (generation): {span_name}")

                return resp  # <-- RETURN ORIGINAL VALUE

            except Exception as e:
                if tracer:
                    sys.settrace(None)

                latency = int((time.time() - start_time) * 1000)

                # Send error span event
                span_event = {
                    "event_type": "span",
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": span_name,
                    "type": "generation",
                    "timestamp": start_timestamp,
                    "duration_ms": latency,
                    "input": {
                        "prompt": prompt_value,
                        "args": serialize_value(args),
                        "kwargs": serialize_value(kwargs)
                    },
                    "output": {
                        "status": "error",
                        "error": str(e),
                        "stacktrace": traceback.format_exc(),
                        "locals_before": locals_before,
                        "locals_after": locals_after,
                    },
                    "metadata": tags or {}
                }
                
                from .sqs import send_to_sqs
                send_to_sqs(span_event)
                print(f"[VeriskGO] Span sent (error): {span_name}")
                raise

        return functools.wraps(func)(async_wrapper if is_async else sync_wrapper)

    return decorator


def track_llm_call(
    provider_or_name: Optional[str] = None, 
    name: Optional[str] = None, 
    *, 
    tags: Optional[Dict] = None,
    capture_locals: bool = True,
    capture_self: bool = True
):
    """
    Unified LLM Tracking Decorator.
    
    Usage:
    @track_llm_call("bedrock")
    @track_llm_call("langchain")
    @track_llm_call(name="my_custom_trace")
    
    Args:
        provider_or_name: "bedrock", "langchain", "ollama", "openai", or the trace name.
                         If it matches a known provider, it routes logic.
                         Otherwise it is treated as the trace name (legacy support).
        name: Explicit trace name (overrides provider_or_name if that was just a provider).
        tags: Dictionary of metadata tags.
        capture_locals: Capture local variables (default True).
        capture_self: Capture 'self' in methods (default True).
    """
    
    # KNOWN PROVIDERS
    PROVIDERS = {"bedrock", "langchain", "ollama", "openai"}
    
    # Determine provider and real name
    provider = "bedrock" # Default
    real_name = name
    
    if provider_or_name:
        candidate = provider_or_name.lower()
        if candidate in PROVIDERS:
            provider = candidate
            # if name is None, use function name later
        else:
            # It's likely a name, not a provider
            real_name = provider_or_name
            # keep default provider as bedrock (or generic)

    # ROUTING
    if provider == "langchain":
        from .langchain_tracker import track_langchain
        return track_langchain(name=real_name, tags=tags, capture_locals=capture_locals, capture_self=capture_self)
    
    # Default / Bedrock / OpenAI / Ollama -> generic handler
    return _track_generic_llm(name=real_name, tags=tags, capture_locals=capture_locals, capture_self=capture_self)


# ============================================================
# Helper for LLM Response Processing (legacy)
# ============================================================

def _process_llm_response(prompt: str, response: Dict[str, Any], latency_ms: int):
    """
    Backward-compatible helper. 
    Uses universal extractors but does not modify app behavior.
    """
    text = extract_text(response)
    usage = extract_usage(response)

    input_tokens = usage["input"]
    output_tokens = usage["output"]
    total_tokens = usage["total"]

    input_cost = input_tokens * 0.0000015
    output_cost = output_tokens * 0.000005
    total_cost = input_cost + output_cost

    model = response.get("model", "unknown") if isinstance(response, dict) else "unknown"

    return {
        "status": "success",
        "type": "generation",
        "latency_ms": latency_ms,
        "input": {
            "prompt": prompt,
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        "output": {
            "text": text,
            "finish_reason": "stop",
        },
        "usage_details": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_tokens,
        },
        "cost_details": {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(total_cost, 6),
        },
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "cost": {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
        },
        "raw_response": serialize_value(response),
    }
