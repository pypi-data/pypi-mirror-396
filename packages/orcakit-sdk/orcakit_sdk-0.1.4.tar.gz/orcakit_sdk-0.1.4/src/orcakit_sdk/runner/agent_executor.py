"""App class for wrapping LangGraph StateGraph."""

from __future__ import annotations

import logging
import os
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AnyMessage
from langchain_core.runnables.config import RunnableConfig
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import override

logger = logging.getLogger(__name__)

# Blocked instrumentation scopes to filter out A2A SDK traces
_BLOCKED_SCOPES = ["a2a-python-sdk"]

# Global Langfuse client instance (initialized once with blocked scopes)
_langfuse_client: Langfuse | None = None


def _get_langfuse_client() -> Langfuse:
    """Get or initialize the global Langfuse client with blocked scopes.

    Returns:
        Langfuse client instance with A2A SDK traces filtered out.
    """
    global _langfuse_client
    if _langfuse_client is None:
        _langfuse_client = Langfuse(blocked_instrumentation_scopes=_BLOCKED_SCOPES)
    return _langfuse_client


class AgentExecutor(ABC):
    """Abstract interface for agent implementations.

    This interface defines the contract that all agent implementations
    should follow, providing a consistent API for different agent types.
    """

    @abstractmethod
    async def call(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        user: str | None = None,
        tags: list[str] | None = None,
        config: RunnableConfig | None = None,
    ) -> dict[str, dict[str, str | Any]]:
        """Invoke the agent with a list of messages.

        Args:
            messages: List of messages to send to the agent.
            thread_id: Optional thread ID for conversation continuity.
            user: Optional user ID for tracking user interactions.
            tags: Optional tags for tracking user interactions.
            config: Optional configuration for the agent execution.

        Returns:
            Dictionary containing the agent's response.
        """
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        user: str | None = None,
        tags: list[str] | None = None,
        config: RunnableConfig | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream responses from the agent with a list of messages.

        Args:
            messages: List of messages to send to the agent.
            thread_id: Optional thread ID for conversation continuity.
            user: Optional user ID for tracking user interactions.
            tags: Optional tags for tracking user interactions.
            config: Optional configuration for the agent execution.

        Yields:
            Dictionaries containing partial response content and metadata.
        """
        ...


class LangGraphAgentExecutor(AgentExecutor):
    """Wrapper for LangGraph StateGraph providing deployment capabilities.

    This class encapsulates a LangGraph StateGraph and provides convenient
    methods for running and deploying the graph with different runners.

    This class implements the AgentInterface to provide a consistent API
    for interacting with different agent types.

    Example:
        >>> from langgraph.graph import StateGraph
        >>> from react_agent import App, SimpleRunner
        >>>
        >>> # Create your StateGraph
        >>> graph = StateGraph(...)
        >>> # ... configure graph ...
        >>>
        >>> # Wrap it with App
        >>> app = App(graph)
        >>>
        >>> # Run with built-in simple runner
        >>> app.run(host="0.0.0.0", port=8090)
        >>>
        >>> # Or deploy with custom runner
        >>> await app.deploy(SimpleRunner(host="0.0.0.0", port=8091))
    """

    def __init__(
        self, graph: StateGraph | CompiledStateGraph, name: str = "agent"
    ) -> None:
        """Initialize the App with a StateGraph or CompiledStateGraph.

        Args:
            graph: LangGraph StateGraph instance or compiled graph to wrap.
            name: Name for the compiled graph.
        """
        # Check if graph is already compiled
        if hasattr(graph, "invoke") and hasattr(graph, "ainvoke"):
            # Already compiled
            self._graph: StateGraph | None = None
            self._compiled_graph: CompiledStateGraph = graph
        else:
            # Not compiled yet
            self._graph = graph
            self._compiled_graph: CompiledStateGraph = graph.compile(name=name)

        self._compiled_graph.name = name
        self._name = name

        # Checkpointer state - will be initialized lazily for async postgres
        self._checkpointer_initialized = False
        self._postgres_uri = os.getenv("POSTGRES_URI")
        self._async_checkpointer_context: Any = None

        # Set sync checkpointer initially (MemorySaver as fallback)
        if not self._postgres_uri:
            self._compiled_graph.checkpointer = self._get_sync_checkpointer()

        # Initialize Langfuse client with blocked scopes to filter A2A traces
        self._langfuse = _get_langfuse_client()

        # Initialize Langfuse CallbackHandler for Langchain (tracing)
        self._langfuse_handler = CallbackHandler()

    @property
    def graph(self) -> StateGraph | None:
        """Get the underlying StateGraph.

        Returns:
            The wrapped StateGraph instance, or None if initialized with compiled graph.
        """
        return self._graph

    @property
    def compiled_graph(self) -> CompiledStateGraph:
        """Get the compiled graph.

        Returns:
            The compiled graph instance ready for execution.
        """
        return self._compiled_graph

    def _get_sync_checkpointer(self):
        """Get synchronous checkpointer (MemorySaver).

        Returns:
            MemorySaver instance or None.
        """
        try:
            from langgraph.checkpoint.memory import MemorySaver

            logger.info("Using in-memory checkpointer")
            return MemorySaver()
        except ImportError:
            logger.error("No checkpointer available, running without persistence")
            return None

    async def _ensure_async_checkpointer(self) -> None:
        """Ensure async PostgreSQL checkpointer is initialized.

        This method lazily initializes the AsyncPostgresSaver when POSTGRES_URI
        is configured. It uses the async context manager pattern properly.
        """
        if self._checkpointer_initialized:
            return

        if not self._postgres_uri:
            # No postgres URI, use sync checkpointer (already set in __init__)
            self._checkpointer_initialized = True
            return

        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            logger.info(f"Initializing AsyncPostgresSaver at {self._postgres_uri}")

            # Create the async context manager
            self._async_checkpointer_context = AsyncPostgresSaver.from_conn_string(
                self._postgres_uri
            )

            # Enter the context manager
            checkpointer = await self._async_checkpointer_context.__aenter__()

            # Setup tables
            await checkpointer.setup()

            # Set the checkpointer on the compiled graph
            self._compiled_graph.checkpointer = checkpointer

            logger.info("AsyncPostgresSaver initialized successfully")
            self._checkpointer_initialized = True

        except ImportError as e:
            logger.warning(
                f"POSTGRES_URI is configured but required packages are not installed: {e}. "
                "Please install with: pip install langgraph-checkpoint-postgres psycopg[pool]"
            )
            # Fall back to memory saver
            self._compiled_graph.checkpointer = self._get_sync_checkpointer()
            self._checkpointer_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize AsyncPostgresSaver: {str(e)}")
            # Fall back to memory saver
            self._compiled_graph.checkpointer = self._get_sync_checkpointer()
            self._checkpointer_initialized = True

    async def close(self) -> None:
        """Close the async checkpointer connection if initialized.

        Call this method when shutting down to properly close database connections.
        """
        if self._async_checkpointer_context is not None:
            try:
                await self._async_checkpointer_context.__aexit__(None, None, None)
                logger.info("AsyncPostgresSaver closed")
            except Exception as e:
                logger.error(f"Error closing AsyncPostgresSaver: {str(e)}")
            finally:
                self._async_checkpointer_context = None

    def _ensure_config_with_langfuse(
        self,
        config: RunnableConfig | None = None,
        thread_id: str | None = None,
        user: str | None = None,
        tags: list[str] | None = None,
    ) -> RunnableConfig:
        """Ensure config has langfuse callbacks and metadata for tracing.

        Args:
            config: Optional RunnableConfig configuration.
            thread_id: Optional thread/session ID for conversation continuity.
            user: Optional user ID for tracking user interactions.
            tags: Optional list of tags for tracing.

        Returns:
            RunnableConfig with langfuse callbacks and metadata configured.
        """
        if config is None:
            config = {}

        # Ensure callbacks list exists and includes a langfuse handler
        if "callbacks" not in config:
            config["callbacks"] = [self._langfuse_handler]
        elif self._langfuse_handler not in config["callbacks"]:
            config["callbacks"].append(self._langfuse_handler)

        # Ensure configurable section exists
        if "configurable" not in config:
            config["configurable"] = {}

        # Set thread_id (generate one if not provided)
        if thread_id:
            config["configurable"]["thread_id"] = thread_id
        elif "thread_id" not in config["configurable"]:
            config["configurable"]["thread_id"] = str(uuid.uuid4())

        # Set user_name if provided
        if user:
            config["configurable"]["user_name"] = user

        # Ensure metadata section exists for langfuse
        if "metadata" not in config:
            config["metadata"] = {}

        # Set langfuse metadata
        if user:
            config["metadata"]["langfuse_user_id"] = user
        if tags:
            existing_tags: list[str] = config["metadata"].get("langfuse_tags", [])
            config["metadata"]["langfuse_tags"] = existing_tags + tags
        if thread_id:
            config["metadata"]["langfuse_session_id"] = thread_id
        elif config["configurable"].get("thread_id"):
            config["metadata"]["langfuse_session_id"] = config["configurable"][
                "thread_id"
            ]

        return config

    @override
    async def call(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        user: str | None = None,
        tags: list[str] | None = None,
        config: RunnableConfig | None = None,
    ) -> dict[str, dict[str, str | Any]]:
        """Invoke the compiled graph with a chat request.

        Args:
            messages: List of messages to send to the graph.
            thread_id: Optional thread ID for conversation continuity.
            user: Optional user ID for tracking user interactions.
            tags: Optional tags for tracing.
            config: Optional configuration for the graph execution.

        Returns:
            Dictionary containing the assistant's response.
        """
        # Ensure async checkpointer is initialized
        await self._ensure_async_checkpointer()

        config = self._ensure_config_with_langfuse(
            config, thread_id=thread_id, user=user, tags=tags
        )
        logger.debug(f"call() - config: {config}")
        logger.debug(f"call() - messages: {messages}")
        return await self._compiled_graph.ainvoke({"messages": messages}, config=config)

    @override
    async def stream(
        self,
        messages: list[AnyMessage],
        thread_id: str | None = None,
        user: str | None = None,
        tags: list[str] | None = None,
        config: RunnableConfig | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream messages from the compiled graph with a chat request.

        Args:
            messages: List of messages to send to the graph.
            thread_id: Optional thread ID for conversation continuity.
            user: Optional user ID for tracking user interactions.
            tags: Optional tags for tracing.
            config: Optional configuration for the graph execution.

        Yields:
            Dictionaries containing message content and metadata.
        """
        # Ensure async checkpointer is initialized
        await self._ensure_async_checkpointer()

        config = self._ensure_config_with_langfuse(
            config, thread_id=thread_id, user=user, tags=tags
        )
        logger.debug(f"stream() - config: {config}")
        logger.debug(f"stream() - messages: {messages}")
        async for event in self._stream_events(messages, config=config):
            yield event

    async def _stream_events(
        self,
        messages: list[AnyMessage],
        config: RunnableConfig | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events from the compiled graph with a chat request.

        Args:
            messages: List of messages to send to the graph.
            config: Optional configuration for the graph execution.

        Yields:
            Dictionaries containing event content and metadata.
        """
        try:
            async for event in self._compiled_graph.astream_events(
                {"messages": messages}, config=config
            ):
                kind = event["event"]

                # Stream tokens from LLM
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        # Convert content to string if it's a list
                        if isinstance(content, str):
                            content_str = content
                        elif isinstance(content, list):
                            content_str = "".join(str(item) for item in content)
                        else:
                            content_str = str(content)

                        yield {
                            "content": content_str,
                            "role": "assistant",
                            "finished": False,
                        }

                # Tool call events
                elif kind == "on_tool_start":
                    logger.info(
                        f"\n--- Calling Tool: {event['name']} with args {event['data'].get('input')} ---"
                    )

                elif kind == "on_tool_end":
                    logger.info(
                        f"\n--- Tool {event['name']} Finished, Output: {event['data'].get('output')} ---"
                    )

                # Chain events (node start/end)
                elif kind == "on_chain_end":
                    logger.debug(f"\n--- Node '{event['name']}' Ended ---")
                    logger.debug(f"Output: {event['data'].get('output')}")

            yield {
                "content": "",
                "role": "assistant",
                "finished": True,
            }
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}", exc_info=True)
            yield {
                "content": f"Error: {str(e)}",
                "role": "error",
                "finished": True,
            }
            raise
        finally:
            logger.info("Stream completed")
