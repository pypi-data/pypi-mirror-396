"""
VirtueGuardResponsesAgent - Guardrail-protected chat agent using MLflow ResponsesAgent
Compatible with OpenAI Response format and Databricks Model Serving
"""

import json
import logging
import os
import uuid
from typing import Any, Generator, Optional, List

import mlflow
from mlflow.entities import SpanType
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
    to_chat_completions_input, # Added back
)

from together import Together
from virtueai.models import VirtueAIModel, VirtueGuardViolation, VirtueGuardVerdict

class VirtueGuardResponsesAgent(ResponsesAgent):
    """
    VirtueGuard implementation as a Databricks ResponsesAgent.
    Acts as a functional Guard that accepts text/messages and returns a 
    structured safety assessment.
    """
    
    def __init__(
        self,
        api_key: str,
        safety_model: VirtueAIModel = VirtueAIModel.VIRTUE_GUARD_TEXT_LITE,
    ):
        self.client = Together(api_key=api_key)
        self.safety_model = safety_model.value

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """
        Evaluate inputs for safety and return a structured assessment.
        
        Input: List of messages (standard chat format)
        Output: JSON string containing safety status and metadata.
        """
        # Convert request input to standard chat completion format using MLflow helper
        # This handles Pydantic model conversion and validation for us
        messages = to_chat_completions_input(request.input)
        
        # Extract user content for safety check
        user_content = " ".join(m["content"] for m in messages if m["role"] == "user")
        
        assessment = self._run_safety_check(user_content)
        
        output_item = self.create_text_output_item(
            text=json.dumps(assessment),
            id=str(uuid.uuid4())
        )

        return ResponsesAgentResponse(
            output=[output_item],
            custom_outputs={
                "safety_status": assessment["status"],
                "verdict": assessment["verdict"]
            }
        )
    
    def predict_stream(self, request: ResponsesAgentRequest) -> Generator[ResponsesAgentStreamEvent, None, None]:
        """
        Streaming interface - delegates to predict() as safety checks are atomic.
        """
        response = self.predict(request)
        yield ResponsesAgentStreamEvent(
            item=response.output[0],
            type="response.output_item.added"
        )

    def _run_safety_check(self, text: str) -> dict:
        """Synchronous safety check using Together AI"""
        try:
            logging.debug(f"Checking safety for: {text[:20]}...")
            
            response = self.client.chat.completions.create(
                model=self.safety_model,
                messages=[{"role": "user", "content": text}],
                stream=False,
            )
            raw_verdict = response.choices[0].message.content.strip()
            
            is_safe = raw_verdict.lower().startswith("safe")
            
            result = {
                "status": "safe" if is_safe else "unsafe",
                "verdict": raw_verdict,
                "model": self.safety_model
            }
            
            return result

        except Exception as e:
            logging.error(f"Error during safety check: {e}")
            return {
                "status": "error",
                "verdict": "undetermined",
                "error": str(e)
            }


if __name__ == "__main__":
    mlflow.openai.autolog()
    
    AGENT = VirtueGuardResponsesAgent(
        api_key=os.getenv("VIRTUEAI_API_KEY"),
        safety_model=VirtueAIModel.VIRTUE_GUARD_TEXT_LITE
    )
    
    mlflow.models.set_model(AGENT)
    