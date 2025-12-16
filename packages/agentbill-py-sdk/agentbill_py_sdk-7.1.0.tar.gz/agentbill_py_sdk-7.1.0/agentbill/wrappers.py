"""
AgentBill Wrapper Classes

Explicit wrapper classes for AI providers that give users direct control
over tracking. Alternative to auto-instrumentation for users who prefer
explicit integration.

Usage:
    from agentbill import AgentBillOpenAI, AgentBillAnthropic
    
    # Instead of: client = OpenAI()
    client = AgentBillOpenAI(api_key="ab_xxx", customer_id="cust-123")
    
    # Use normally - tracking is automatic
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

import time
import hashlib
import json
from typing import Any, Dict, Optional, List, Union
from functools import wraps

from .validation import validate_api_key, validate_customer_id
from .exceptions import AgentBillError, BudgetExceededError, ValidationError
from .distributed import get_trace_context, set_trace_context


# ============================================================================
# v7.0.0: Cost calculation is now 100% SERVER-SIDE via OTEL
# SDK sends OTEL spans to otel-collector endpoint with token counts
# Server calculates cost from model_pricing table
# The _calculate_cost function below is DEPRECATED - kept only for backward
# compatibility. The wrappers no longer use it - they send raw token counts.
# ============================================================================

# Default fallback for local estimation only (DEPRECATED - not used in v7.0.0)
DEFAULT_COST_PER_1M = {"input": 1.0, "output": 2.0}


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    DEPRECATED in v7.0.0 - kept for backward compatibility only.
    Cost is now calculated server-side using model_pricing database.
    Wrappers send raw token counts via OTEL spans.
    """
    input_cost = (input_tokens / 1_000_000) * DEFAULT_COST_PER_1M["input"]
    output_cost = (output_tokens / 1_000_000) * DEFAULT_COST_PER_1M["output"]
    return input_cost + output_cost


def _hash_prompt(messages: Any) -> str:
    """Generate a hash of the prompt for tracking."""
    try:
        content = json.dumps(messages, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    except Exception:
        return "unknown"


class BaseAgentBillWrapper:
    """Base class for AgentBill wrapper classes."""
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize AgentBill wrapper.
        
        Args:
            api_key: AgentBill API key (ab_xxx)
            customer_id: Customer identifier for tracking
            daily_budget: Optional daily budget limit (enables Cost Guard)
            monthly_budget: Optional monthly budget limit (enables Cost Guard)
            base_url: AgentBill API base URL
            debug: Enable debug logging
            **kwargs: Additional arguments passed to the underlying client
        """
        validate_api_key(api_key)
        if customer_id:
            validate_customer_id(customer_id)
            
        self._agentbill_api_key = api_key
        self._customer_id = customer_id
        self._daily_budget = daily_budget
        self._monthly_budget = monthly_budget
        self._base_url = base_url or "https://bgwyprqxtdreuutzpbgw.supabase.co/functions/v1"
        self._debug = debug
        self._provider_kwargs = kwargs
        
    def _log(self, message: str):
        """Debug logging."""
        if self._debug:
            print(f"[AgentBill] {message}")
            
    async def _validate_budget(self, model: str) -> Dict[str, Any]:
        """Pre-validate request against Cost Guard."""
        if not self._daily_budget and not self._monthly_budget:
            return {"allowed": True, "reason": "no_budget_configured"}
            
        import aiohttp
        
        payload = {
            "api_key": self._agentbill_api_key,
            "customer_id": self._customer_id,
            "model": model,
            "daily_budget": self._daily_budget,
            "monthly_budget": self._monthly_budget,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/ai-cost-guard-router",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    result = await resp.json()
                    self._log(f"Cost Guard validation: {result}")
                    return result
        except Exception as e:
            self._log(f"Cost Guard validation failed (allowing): {e}")
            return {"allowed": True, "reason": "validation_failed_open"}
            
    def _validate_budget_sync(self, model: str) -> Dict[str, Any]:
        """Synchronous budget validation."""
        if not self._daily_budget and not self._monthly_budget:
            return {"allowed": True, "reason": "no_budget_configured"}
            
        import requests
        
        payload = {
            "api_key": self._agentbill_api_key,
            "customer_id": self._customer_id,
            "model": model,
            "daily_budget": self._daily_budget,
            "monthly_budget": self._monthly_budget,
        }
        
        try:
            resp = requests.post(
                f"{self._base_url}/ai-cost-guard-router",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            result = resp.json()
            self._log(f"Cost Guard validation: {result}")
            return result
        except Exception as e:
            self._log(f"Cost Guard validation failed (allowing): {e}")
            return {"allowed": True, "reason": "validation_failed_open"}
            
    def _track_usage_sync(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        prompt_hash: str,
        event_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Track AI usage synchronously via OTEL.
        
        v7.0.0: Now sends OTEL spans to otel-collector instead of track-ai-usage.
        Cost is calculated server-side from model_pricing database.
        """
        import requests
        import uuid
        import time
        
        # Get or create trace context for correlation
        ctx = get_trace_context()
        if ctx:
            trace_id = ctx.get("trace_id")
            parent_span_id = ctx.get("span_id")
            span_id = uuid.uuid4().hex[:16]
            set_trace_context(trace_id, span_id, parent_span_id)
            self._log(f"Using trace context: trace_id={trace_id[:8]}..., span_id={span_id[:8]}...")
        else:
            trace_id = uuid.uuid4().hex
            span_id = uuid.uuid4().hex[:16]
            parent_span_id = None
            set_trace_context(trace_id, span_id)
            self._log(f"Generated new trace context: trace_id={trace_id[:8]}...")
        
        # Build OTEL span payload - cost calculated server-side
        start_time_ns = str(int((time.time() - latency_ms / 1000) * 1_000_000_000))
        end_time_ns = str(int(time.time() * 1_000_000_000))
        
        # v7.0.2: Use OTEL GenAI-compliant attributes for otel-collector validation
        span_attributes = [
            # Required GenAI attributes (per OTEL GenAI spec)
            {"key": "gen_ai.request.model", "value": {"stringValue": model}},
            {"key": "gen_ai.system", "value": {"stringValue": self._provider_name}},
            {"key": "gen_ai.usage.prompt_tokens", "value": {"intValue": input_tokens}},
            {"key": "gen_ai.usage.completion_tokens", "value": {"intValue": output_tokens}},
            # Additional useful attributes
            {"key": "gen_ai.usage.total_tokens", "value": {"intValue": input_tokens + output_tokens}},
            {"key": "agentbill.latency_ms", "value": {"doubleValue": latency_ms}},
            {"key": "agentbill.prompt_hash", "value": {"stringValue": prompt_hash}},
            {"key": "agentbill.event_name", "value": {"stringValue": event_name or "ai_call"}},
        ]
        
        if metadata:
            span_attributes.append({"key": "agentbill.metadata", "value": {"stringValue": json.dumps(metadata)}})
        
        resource_attributes = [
            {"key": "service.name", "value": {"stringValue": "agentbill-python-sdk"}},
            {"key": "service.version", "value": {"stringValue": "7.0.4"}},
        ]
        if self._customer_id:
            resource_attributes.append({"key": "customer.id", "value": {"stringValue": self._customer_id}})
        
        otel_span = {
            "traceId": trace_id,
            "spanId": span_id,
            "name": "agentbill.trace.signal",
            "kind": 1,
            "startTimeUnixNano": start_time_ns,
            "endTimeUnixNano": end_time_ns,
            "attributes": span_attributes,
            "status": {"code": 0},
        }
        if parent_span_id:
            otel_span["parentSpanId"] = parent_span_id
        
        payload = {
            "resourceSpans": [{
                "resource": {"attributes": resource_attributes},
                "scopeSpans": [{
                    "scope": {"name": "agentbill", "version": "7.0.4"},
                    "spans": [otel_span]
                }]
            }]
        }
        
        try:
            resp = requests.post(
                f"{self._base_url}/otel-collector",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self._agentbill_api_key,
                },
                timeout=5
            )
            self._log(f"OTEL span sent: {resp.status_code}, trace_id={trace_id[:8]}...")
        except Exception as e:
            self._log(f"Failed to send OTEL span: {e}")
            
    async def _track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        prompt_hash: str,
        event_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Track AI usage asynchronously via OTEL.
        
        v7.0.0: Now sends OTEL spans to otel-collector instead of track-ai-usage.
        Cost is calculated server-side from model_pricing database.
        """
        import aiohttp
        import uuid
        import time
        
        # Get or create trace context for correlation
        ctx = get_trace_context()
        if ctx:
            trace_id = ctx.get("trace_id")
            parent_span_id = ctx.get("span_id")
            span_id = uuid.uuid4().hex[:16]
            set_trace_context(trace_id, span_id, parent_span_id)
            self._log(f"Using trace context: trace_id={trace_id[:8]}..., span_id={span_id[:8]}...")
        else:
            trace_id = uuid.uuid4().hex
            span_id = uuid.uuid4().hex[:16]
            parent_span_id = None
            set_trace_context(trace_id, span_id)
            self._log(f"Generated new trace context: trace_id={trace_id[:8]}...")
        
        # Build OTEL span payload - cost calculated server-side
        start_time_ns = str(int((time.time() - latency_ms / 1000) * 1_000_000_000))
        end_time_ns = str(int(time.time() * 1_000_000_000))
        
        # v7.0.2: Use OTEL GenAI-compliant attributes for otel-collector validation
        span_attributes = [
            # Required GenAI attributes (per OTEL GenAI spec)
            {"key": "gen_ai.request.model", "value": {"stringValue": model}},
            {"key": "gen_ai.system", "value": {"stringValue": self._provider_name}},
            {"key": "gen_ai.usage.prompt_tokens", "value": {"intValue": input_tokens}},
            {"key": "gen_ai.usage.completion_tokens", "value": {"intValue": output_tokens}},
            # Additional useful attributes
            {"key": "gen_ai.usage.total_tokens", "value": {"intValue": input_tokens + output_tokens}},
            {"key": "agentbill.latency_ms", "value": {"doubleValue": latency_ms}},
            {"key": "agentbill.prompt_hash", "value": {"stringValue": prompt_hash}},
            {"key": "agentbill.event_name", "value": {"stringValue": event_name or "ai_call"}},
        ]
        
        if metadata:
            span_attributes.append({"key": "agentbill.metadata", "value": {"stringValue": json.dumps(metadata)}})
        
        resource_attributes = [
            {"key": "service.name", "value": {"stringValue": "agentbill-python-sdk"}},
            {"key": "service.version", "value": {"stringValue": "7.0.4"}},
        ]
        if self._customer_id:
            resource_attributes.append({"key": "customer.id", "value": {"stringValue": self._customer_id}})
        
        otel_span = {
            "traceId": trace_id,
            "spanId": span_id,
            "name": "agentbill.trace.signal",
            "kind": 1,
            "startTimeUnixNano": start_time_ns,
            "endTimeUnixNano": end_time_ns,
            "attributes": span_attributes,
            "status": {"code": 0},
        }
        if parent_span_id:
            otel_span["parentSpanId"] = parent_span_id
        
        payload = {
            "resourceSpans": [{
                "resource": {"attributes": resource_attributes},
                "scopeSpans": [{
                    "scope": {"name": "agentbill", "version": "7.0.4"},
                    "spans": [otel_span]
                }]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/otel-collector",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self._agentbill_api_key,
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    self._log(f"OTEL span sent: {resp.status}, trace_id={trace_id[:8]}...")
        except Exception as e:
            self._log(f"Failed to send OTEL span: {e}")
            
    @property
    def _provider_name(self) -> str:
        """Override in subclasses."""
        return "unknown"


class AgentBillOpenAI(BaseAgentBillWrapper):
    """
    OpenAI client wrapper with automatic AgentBill tracking.
    
    Usage:
        from agentbill import AgentBillOpenAI
        
        client = AgentBillOpenAI(
            api_key="ab_xxx",
            customer_id="cust-123",
            daily_budget=10.00,  # Optional Cost Guard
            openai_api_key="sk-xxx"  # Or use OPENAI_API_KEY env var
        )
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            customer_id=customer_id,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            base_url=base_url,
            debug=debug,
            **kwargs
        )
        
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
            
        # Create underlying OpenAI client
        client_kwargs = {k: v for k, v in kwargs.items() if k != "openai_api_key"}
        if openai_api_key:
            client_kwargs["api_key"] = openai_api_key
        self._client = OpenAI(**client_kwargs)
        
        # Wrap the chat completions
        self.chat = _WrappedChatCompletions(self._client.chat, self)
        
        # Pass through other attributes
        self.models = self._client.models
        self.embeddings = self._client.embeddings
        self.files = self._client.files
        self.images = self._client.images
        self.audio = self._client.audio
        self.moderations = self._client.moderations
        
    @property
    def _provider_name(self) -> str:
        return "openai"


class _WrappedChatCompletions:
    """Wrapped chat completions with tracking."""
    
    def __init__(self, chat, wrapper: BaseAgentBillWrapper):
        self._chat = chat
        self._wrapper = wrapper
        self.completions = _WrappedCompletions(chat.completions, wrapper)


class _WrappedCompletions:
    """Wrapped completions.create with tracking."""
    
    def __init__(self, completions, wrapper: BaseAgentBillWrapper):
        self._completions = completions
        self._wrapper = wrapper
        
    def create(
        self,
        *args,
        agentbill_event_name: Optional[str] = None,
        agentbill_metadata: Optional[Dict] = None,
        **kwargs
    ):
        """Create chat completion with automatic tracking."""
        model = kwargs.get("model", "gpt-4")
        messages = kwargs.get("messages", [])
        prompt_hash = _hash_prompt(messages)
        
        # Pre-validate budget
        validation = self._wrapper._validate_budget_sync(model)
        if not validation.get("allowed", True):
            raise BudgetExceededError(
                reason=validation.get("reason", "budget_exceeded"),
                budget_type=validation.get("budget_type", "unknown"),
                limit=validation.get("limit"),
                current_usage=validation.get("current_usage")
            )
        
        # Make the actual call
        start_time = time.time()
        response = self._completions.create(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract usage
        input_tokens = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "completion_tokens", 0) if response.usage else 0
        
        # Track usage
        self._wrapper._track_usage_sync(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            prompt_hash=prompt_hash,
            event_name=agentbill_event_name,
            metadata=agentbill_metadata,
        )
        
        return response


class AgentBillAnthropic(BaseAgentBillWrapper):
    """
    Anthropic client wrapper with automatic AgentBill tracking.
    
    Usage:
        from agentbill import AgentBillAnthropic
        
        client = AgentBillAnthropic(
            api_key="ab_xxx",
            customer_id="cust-123",
            anthropic_api_key="sk-ant-xxx"
        )
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        anthropic_api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            customer_id=customer_id,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            base_url=base_url,
            debug=debug,
            **kwargs
        )
        
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
            
        client_kwargs = {k: v for k, v in kwargs.items() if k != "anthropic_api_key"}
        if anthropic_api_key:
            client_kwargs["api_key"] = anthropic_api_key
        self._client = Anthropic(**client_kwargs)
        
        # Wrap messages
        self.messages = _WrappedAnthropicMessages(self._client.messages, self)
        
    @property
    def _provider_name(self) -> str:
        return "anthropic"


class _WrappedAnthropicMessages:
    """Wrapped Anthropic messages with tracking."""
    
    def __init__(self, messages, wrapper: BaseAgentBillWrapper):
        self._messages = messages
        self._wrapper = wrapper
        
    def create(
        self,
        *args,
        agentbill_event_name: Optional[str] = None,
        agentbill_metadata: Optional[Dict] = None,
        **kwargs
    ):
        """Create message with automatic tracking."""
        model = kwargs.get("model", "claude-3-sonnet-20240229")
        messages = kwargs.get("messages", [])
        prompt_hash = _hash_prompt(messages)
        
        # Pre-validate budget
        validation = self._wrapper._validate_budget_sync(model)
        if not validation.get("allowed", True):
            raise BudgetExceededError(
                reason=validation.get("reason", "budget_exceeded"),
                budget_type=validation.get("budget_type", "unknown"),
                limit=validation.get("limit"),
                current_usage=validation.get("current_usage")
            )
        
        # Make the actual call
        start_time = time.time()
        response = self._messages.create(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract usage
        input_tokens = getattr(response.usage, "input_tokens", 0) if response.usage else 0
        output_tokens = getattr(response.usage, "output_tokens", 0) if response.usage else 0
        
        # Track usage
        self._wrapper._track_usage_sync(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            prompt_hash=prompt_hash,
            event_name=agentbill_event_name,
            metadata=agentbill_metadata,
        )
        
        return response


class AgentBillCohere(BaseAgentBillWrapper):
    """
    Cohere client wrapper with automatic AgentBill tracking.
    
    Usage:
        from agentbill import AgentBillCohere
        
        client = AgentBillCohere(
            api_key="ab_xxx",
            customer_id="cust-123",
            cohere_api_key="xxx"
        )
        
        response = client.chat(
            model="command-r-plus",
            message="Hello!"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        cohere_api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            customer_id=customer_id,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            base_url=base_url,
            debug=debug,
            **kwargs
        )
        
        try:
            import cohere
        except ImportError:
            raise ImportError("cohere package required. Install with: pip install cohere")
            
        client_kwargs = {k: v for k, v in kwargs.items() if k != "cohere_api_key"}
        if cohere_api_key:
            client_kwargs["api_key"] = cohere_api_key
        self._client = cohere.Client(**client_kwargs)
        self._original_chat = self._client.chat
        
    def chat(
        self,
        *args,
        agentbill_event_name: Optional[str] = None,
        agentbill_metadata: Optional[Dict] = None,
        **kwargs
    ):
        """Chat with automatic tracking."""
        model = kwargs.get("model", "command-r")
        message = kwargs.get("message", "")
        prompt_hash = _hash_prompt(message)
        
        # Pre-validate budget
        validation = self._validate_budget_sync(model)
        if not validation.get("allowed", True):
            raise BudgetExceededError(
                reason=validation.get("reason", "budget_exceeded"),
                budget_type=validation.get("budget_type", "unknown"),
                limit=validation.get("limit"),
                current_usage=validation.get("current_usage")
            )
        
        # Make the actual call
        start_time = time.time()
        response = self._original_chat(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract usage from meta
        meta = getattr(response, "meta", None)
        tokens = getattr(meta, "tokens", None) if meta else None
        input_tokens = getattr(tokens, "input_tokens", 0) if tokens else 0
        output_tokens = getattr(tokens, "output_tokens", 0) if tokens else 0
        
        # Track usage
        self._track_usage_sync(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            prompt_hash=prompt_hash,
            event_name=agentbill_event_name,
            metadata=agentbill_metadata,
        )
        
        return response
        
    @property
    def _provider_name(self) -> str:
        return "cohere"


class AgentBillGoogleAI(BaseAgentBillWrapper):
    """
    Google AI (Gemini) client wrapper with automatic AgentBill tracking.
    
    Usage:
        from agentbill import AgentBillGoogleAI
        
        client = AgentBillGoogleAI(
            api_key="ab_xxx",
            customer_id="cust-123",
            google_api_key="xxx"
        )
        
        response = client.generate_content(
            model="gemini-1.5-pro",
            contents="Hello!"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        google_api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            customer_id=customer_id,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            base_url=base_url,
            debug=debug,
            **kwargs
        )
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package required. Install with: pip install google-generativeai")
            
        if google_api_key:
            genai.configure(api_key=google_api_key)
        self._genai = genai
        
    def generate_content(
        self,
        model: str = "gemini-1.5-pro",
        contents: Any = None,
        agentbill_event_name: Optional[str] = None,
        agentbill_metadata: Optional[Dict] = None,
        **kwargs
    ):
        """Generate content with automatic tracking."""
        prompt_hash = _hash_prompt(contents)
        
        # Pre-validate budget
        validation = self._validate_budget_sync(model)
        if not validation.get("allowed", True):
            raise BudgetExceededError(
                reason=validation.get("reason", "budget_exceeded"),
                budget_type=validation.get("budget_type", "unknown"),
                limit=validation.get("limit"),
                current_usage=validation.get("current_usage")
            )
        
        # Make the actual call
        start_time = time.time()
        model_instance = self._genai.GenerativeModel(model)
        response = model_instance.generate_content(contents, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract usage
        usage = getattr(response, "usage_metadata", None)
        input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
        output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
        
        # Track usage
        self._track_usage_sync(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            prompt_hash=prompt_hash,
            event_name=agentbill_event_name,
            metadata=agentbill_metadata,
        )
        
        return response
        
    @property
    def _provider_name(self) -> str:
        return "google"


class AgentBillBedrock(BaseAgentBillWrapper):
    """
    AWS Bedrock client wrapper with automatic AgentBill tracking.
    
    Usage:
        from agentbill import AgentBillBedrock
        
        client = AgentBillBedrock(
            api_key="ab_xxx",
            customer_id="cust-123",
            region_name="us-east-1"
        )
        
        response = client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body={"prompt": "Hello!"}
        )
    """
    
    def __init__(
        self,
        api_key: str,
        customer_id: Optional[str] = None,
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
        base_url: Optional[str] = None,
        debug: bool = False,
        region_name: str = "us-east-1",
        **kwargs
    ):
        super().__init__(
            api_key=api_key,
            customer_id=customer_id,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            base_url=base_url,
            debug=debug,
            **kwargs
        )
        
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 package required. Install with: pip install boto3")
            
        client_kwargs = {k: v for k, v in kwargs.items() if k != "region_name"}
        self._client = boto3.client("bedrock-runtime", region_name=region_name, **client_kwargs)
        
    def invoke_model(
        self,
        modelId: str,
        body: Union[str, Dict],
        agentbill_event_name: Optional[str] = None,
        agentbill_metadata: Optional[Dict] = None,
        **kwargs
    ):
        """Invoke model with automatic tracking."""
        prompt_hash = _hash_prompt(body)
        
        # Pre-validate budget
        validation = self._validate_budget_sync(modelId)
        if not validation.get("allowed", True):
            raise BudgetExceededError(
                reason=validation.get("reason", "budget_exceeded"),
                budget_type=validation.get("budget_type", "unknown"),
                limit=validation.get("limit"),
                current_usage=validation.get("current_usage")
            )
        
        # Prepare body
        if isinstance(body, dict):
            import json
            body = json.dumps(body)
        
        # Make the actual call
        start_time = time.time()
        response = self._client.invoke_model(modelId=modelId, body=body, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Parse response for usage (varies by model)
        response_body = json.loads(response["body"].read())
        
        # Try to extract usage (Anthropic models on Bedrock)
        usage = response_body.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        # Track usage
        self._track_usage_sync(
            model=modelId,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            prompt_hash=prompt_hash,
            event_name=agentbill_event_name,
            metadata=agentbill_metadata,
        )
        
        return response_body
        
    @property
    def _provider_name(self) -> str:
        return "bedrock"
