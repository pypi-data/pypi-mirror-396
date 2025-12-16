"""LangGraph channel for exposing LangGraph apps through FastAPI routers."""

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from typing_extensions import override

from orcakit_sdk.runner.agent_executor import AgentExecutor

from .base import BaseChannel

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Standard request model for chat endpoints."""

    content: str = Field(..., description="The user message content")
    thread_id: str | None = Field(
        default=None,
        description="Thread ID for conversation continuity. If not provided, a new thread will be created.",
    )
    model: str | None = Field(
        default=None,
        description="Model to use for the request (optional)",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0)",
    )
    max_tokens: int | None = Field(
        default=None,
        gt=0,
        description="Maximum number of tokens to generate",
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description="Additional metadata for the request",
    )

    def to_config(self) -> RunnableConfig:
        """Convert request parameters to RunnableConfig format."""
        thread_id = self.thread_id if self.thread_id else str(uuid.uuid4())
        configurable: dict[str, str | float | int] = {"thread_id": thread_id}

        if self.model:
            configurable["model"] = self.model

        if self.temperature is not None:
            configurable["temperature"] = self.temperature

        if self.max_tokens is not None:
            configurable["max_tokens"] = self.max_tokens

        config: RunnableConfig = {"configurable": configurable}

        if self.metadata:
            config["metadata"] = self.metadata

        return config

    def to_messages(self) -> list[AnyMessage]:
        """Convert content to message list."""
        return [HumanMessage(content=self.content)]


class ChatResponse(BaseModel):
    """Standard response model for chat endpoints."""

    content: str = Field(..., description="The assistant's response content")
    thread_id: str = Field(..., description="Thread ID for the conversation")
    role: str = Field(default="assistant", description="Role of the responder")
    metadata: dict[str, str] | None = Field(
        default=None,
        description="Additional response metadata",
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(default="healthy", description="Service health status")


class ErrorResponse(BaseModel):
    """Response model for error cases."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Detailed error information")


class LangGraphChannel(BaseChannel):
    """Channel for exposing LangGraph apps through FastAPI routers.

    This channel creates a FastAPI router with standard endpoints for
    interacting with LangGraph apps, including /health, /call, and /stream.

    Example:
        >>> from fastapi import FastAPI
        >>> from react_agent import Agent, LangGraphChannel
        >>>
        >>> fastapi_app = FastAPI()
        >>> agent = Agent(graph)
        >>> channel = LangGraphChannel()
        >>> channel.create_router(fastapi_app, agent.agent_executor, prefix="/api")
    """

    def __init__(self) -> None:
        """Initialize the LangGraph channel."""
        self.agent_executor: AgentExecutor | None = None

    @override
    def create_router(
        self,
        fastapi_app: FastAPI,
        agent_executor: AgentExecutor,
        url_prefix: str = "/langgraph",
        **_kwargs: object,
    ) -> None:
        """Create and register FastAPI router with standard LangGraph endpoints.

        Args:
            fastapi_app: The FastAPI application to register routes on.
            agent_executor: The AgentExecutor instance to create a router for.
            prefix: Path prefix for the router endpoints.
            **_kwargs: Additional arguments for future extension.
        """
        self.agent_executor = agent_executor
        router = self._create_router(url_prefix)
        fastapi_app.include_router(router)

    def _create_router(self, prefix: str = "") -> APIRouter:
        """Create a FastAPI router with standard LangGraph endpoints.

        Args:
            prefix: Path prefix for the router endpoints.

        Returns:
            A FastAPI router with /health, /call, and /stream endpoints.

        Raises:
            RuntimeError: If no agent instance has been set.
        """
        if self.agent_executor is None:
            raise RuntimeError(
                "No agent instance available. Use LangGraphChannel(agent) or call create_router() first."
            )

        # Normalize prefix
        prefix = self.normalize_prefix(prefix)
        router = APIRouter(prefix=prefix, tags=["LangGraph"])
        executor = self.agent_executor

        @router.get("/health", response_model=HealthResponse)
        async def health_check() -> HealthResponse:
            """Health check endpoint."""
            return HealthResponse(status="healthy")

        @router.post("/call", response_model=None)
        async def call(request: ChatRequest) -> ChatResponse | ErrorResponse:
            """Chat endpoint for single-turn conversation."""
            try:
                config = request.to_config()
                messages = request.to_messages()
                result = await executor.call(
                    messages, tags=["langgraph"], config=config
                )

                # Extract response content from result
                content = self.extract_content(result)
                thread_id = str(config.get("configurable", {}).get("thread_id", ""))

                return ChatResponse(
                    content=content,
                    thread_id=thread_id,
                    role="assistant",
                )
            except Exception as e:
                logger.exception("Error in call endpoint")
                return ErrorResponse(error=str(e))

        @router.post("/stream", response_model=None)
        async def stream(request: ChatRequest) -> StreamingResponse:
            """Stream endpoint for streaming chat responses."""
            config = request.to_config()
            messages = request.to_messages()
            thread_id = str(config.get("configurable", {}).get("thread_id", ""))

            async def event_generator():
                try:
                    async for chunk in executor.stream(
                        messages, tags=["langgraph"], config=config
                    ):
                        data = {
                            "content": chunk.get("content", ""),
                            "thread_id": thread_id,
                            "role": chunk.get("role", "assistant"),
                            "finished": chunk.get("finished", False),
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                except Exception as e:
                    logger.exception("Error in stream endpoint")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return router
