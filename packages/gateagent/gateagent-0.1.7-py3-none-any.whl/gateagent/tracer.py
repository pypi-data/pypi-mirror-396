from typing import Any, Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler
import time
import uuid
import logging

from .client import Client
from .schemas import Interaction

logger = logging.getLogger(__name__)

class InteractionTracer(BaseCallbackHandler):
    """
    LangChain-compatible callback handler that traces tool interactions,
    injects metadata for LangSmith, and sends structured traces to Gateagent.
    """

    def __init__(
        self,
        *,
        client: Optional[Client] = None,
        project_name: Optional[str] = None,
        capture_headers: bool = True,
        capture_payloads: bool = True,
        default_metadata: Optional[Dict[str, Any]] = None,
        gateagent_base_url: str = "https://api.gateagent.dev",
        frontend_url: str = "https://sandbox.gateagent.dev",
    ):
        self.client = client or Client(api_url=gateagent_base_url)
        self.project_name = project_name
        self.default_metadata = default_metadata or {}
        # The base URL used for the deep link in metadata
        self.gateagent_base_url = gateagent_base_url.rstrip("/")
        self.frontend_url = frontend_url.rstrip("/")

        # Memory store for active runs to calculate duration and link start/end
        self._active_tool_runs: Dict[str, Dict[str, Any]] = {}

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        trace_id = str(uuid.uuid4())
        tool_name = serialized.get("name", "unknown_tool")
        
        # Inject metadata for LangSmith or other downstream tracers
        if metadata is not None:
            metadata.update({
                **self.default_metadata,
                "tool_name": tool_name,
                "gateagent_trace_id": trace_id,
                "gateagent_trace_url": f"{self.frontend_url}/trace/{trace_id}",
            })

        # Parse inputs if possible (assuming string, but could be dict depending on call)
        # We start simplistic.
        try:
            # Attempt to ensure input is reasonably formatted. 
            # In LangChain input_str is usually the string representation.
            inputs = {"input": input_str}
        except:
            inputs = {"input_raw": str(input_str)}

        self._active_tool_runs[run_id] = {
            "trace_id": trace_id,
            "tool_name": tool_name,
            "start_time": time.time(),
            "inputs": inputs,
            "parent_run_id": parent_run_id,
        }

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        run_data = self._active_tool_runs.pop(run_id, None)
        if not run_data:
            return

        end_time = time.time()
        start_time = run_data["start_time"]
        duration_ms = (end_time - start_time) * 1000

        interaction = Interaction(
            trace_id=run_data["trace_id"],
            tool_name=run_data["tool_name"],
            inputs=run_data["inputs"],
            outputs=output, # Pydantic will handle basic serialization
            status="success",
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            parent_run_id=parent_run_id,
            metadata=self.default_metadata,
        )

        # Send asynchronously? For now, sync as per plan to keep it simple.
        # But we don't want to block too much.
        self.client.log_interaction(interaction)

    def on_tool_error(
        self,
        error: Exception,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        run_data = self._active_tool_runs.pop(run_id, None)
        if not run_data:
            return

        end_time = time.time()
        start_time = run_data["start_time"]
        duration_ms = (end_time - start_time) * 1000

        interaction = Interaction(
            trace_id=run_data["trace_id"],
            tool_name=run_data["tool_name"],
            inputs=run_data["inputs"],
            error=str(error),
            status="error",
            start_time=start_time,
            end_time=end_time,
            duration_ms=duration_ms,
            parent_run_id=parent_run_id,
            metadata=self.default_metadata,
        )

        self.client.log_interaction(interaction)
