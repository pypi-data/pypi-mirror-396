"""Runner classes for deploying and serving LangGraph apps."""

from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from orcakit_sdk.context import EnvAwareConfig
from orcakit_sdk.runner.agent_executor import AgentExecutor, LangGraphAgentExecutor
from orcakit_sdk.runner.channels.a2a_channel import A2AChannel
from orcakit_sdk.runner.channels.langgraph_channel import LangGraphChannel
from orcakit_sdk.runner.channels.openai_channel import OpenAIChannel
from orcakit_sdk.runner.channels.wework_channel import WeWorkChannel


class BaseRunner(ABC):
    """Abstract base class for app runners.

    A Runner is responsible for deploying and serving an App,
    providing API access to the underlying StateGraph.
    """

    @abstractmethod
    def run(self, agent_executor: AgentExecutor, **kwargs: str) -> None:
        """Run the given app.

        Args:
            agent_executor: The agent instance to run.
            **kwargs: Additional arguments for running the app.
        """
        ...

    @abstractmethod
    async def run_async(self, agent_executor: AgentExecutor, **kwargs: str) -> None:
        """Run the agent asynchronously.

        Args:
            agent_executor: The agent_executor instance to run.
            **kwargs: Additional arguments for running the app.
        """

    @abstractmethod
    async def stop(self) -> None:
        """Stop the runner."""
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, str]:
        """Check the health status of the runner.

        Returns:
            Dictionary containing health status information.
        """
        ...


# Environment variable keys for dev mode configuration
_DEV_URL_PREFIX_ENV = "ORCAKIT_DEV_URL_PREFIX"


def _create_base_fastapi_app() -> FastAPI:
    """Create and configure the base FastAPI application.

    Returns:
        Configured FastAPI application instance with Scalar docs and CORS.
    """
    fastapi_app = FastAPI(
        title="OrcaKit Simple Runner",
        description="Simple runner for OrcaKit execution",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url=None,  # Disable default Swagger UI
    )

    # Add Scalar API documentation at /docs
    @fastapi_app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url=fastapi_app.openapi_url,
            title="OrcaKit API Reference",
        )

    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app


def _setup_channels(
    app: FastAPI,
    agent_executor: AgentExecutor,
    url_prefix: str = "",
) -> None:
    """Set up API channels on the given FastAPI app.

    Args:
        app: FastAPI application instance.
        agent_executor: The AgentExecutor instance.
        url_prefix: URL prefix for all routes.
    """
    LangGraphChannel().create_router(
        fastapi_app=app,
        agent_executor=agent_executor,
        url_prefix=f"{url_prefix}/langgraph",
    )

    OpenAIChannel().create_router(
        fastapi_app=app,
        agent_executor=agent_executor,
        url_prefix=f"{url_prefix}/openai",
    )

    WeWorkChannel().create_router(
        fastapi_app=app,
        agent_executor=agent_executor,
        url_prefix=f"{url_prefix}/wework",
    )

    a2a_base_url = os.environ.get("A2A_BASE_URL", "")
    A2AChannel().create_router(
        fastapi_app=app,
        agent_executor=agent_executor,
        url_prefix=f"{url_prefix}/a2a-protocol",
        base_url=a2a_base_url,
    )


def create_dev_app() -> FastAPI:
    """Create FastAPI app in dev mode.

    This function is called by uvicorn when reload=True.
    It creates a fresh app instance with reloaded modules.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    # Import graph module fresh to pick up changes
    from react_agent.graph import graph as fresh_graph

    # Get url_prefix from environment variable
    url_prefix = os.environ.get(_DEV_URL_PREFIX_ENV, "")

    # Create fresh FastAPI app
    fastapi_app = _create_base_fastapi_app()

    # Create fresh executor and set up channels
    fresh_executor = LangGraphAgentExecutor(graph=fresh_graph)
    _setup_channels(fastapi_app, fresh_executor, url_prefix)

    return fastapi_app


@dataclass(kw_only=True)
class SimpleRunnerConfig(EnvAwareConfig):
    """Configuration for SimpleRunner.

    Environment variables:
        - HOST: Server host address (default: 0.0.0.0)
        - PORT: Server port (default: 8090)
        - RELOAD: Enable auto-reload (default: false)
        - LOG_LEVEL: Logging level (default: info)
        - DEV: Enable dev mode with hot reload (default: false)
    """

    host: str = "0.0.0.0"
    port: int = 8888
    reload: bool = False
    log_level: str = "info"
    dev: bool = False
    # Store additional configuration parameters
    extra: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize default values for extra fields."""
        if self.extra is None:
            self.extra = {}


class SimpleRunner(BaseRunner):
    """Simple FastAPI-based runner for LangGraph apps.

    This runner creates a FastAPI web server that exposes the StateGraph
    through REST API endpoints, supporting ainvoke, astream, and astream_events.

    Example:
        >>> from react_agent import App, SimpleRunner
        >>>
        >>> app = App(graph)
        >>> runner = SimpleRunner(host="0.0.0.0", port=8091)
        >>> await runner.run(app)
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8888,
        reload: bool = False,
        log_level: str = "info",
        dev: bool = False,
        fastapi_app: FastAPI | None = None,
        **kwargs: str,
    ) -> None:
        """Initialize the SimpleRunner.

        Args:
            host: Host address to bind the server.
            port: Port number to bind the server.
            reload: Whether to enable auto-reload during development.
            log_level: Logging level (debug, info, warning, error, critical).
            dev: Enable dev mode with hot reload support.
            fastapi_app: Optional pre-configured FastAPI app.
            **kwargs: Additional configuration parameters.
        """
        self.config: SimpleRunnerConfig = SimpleRunnerConfig(
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            dev=dev,
            extra=kwargs if kwargs else None,
        )
        self.server: uvicorn.Server | None = None
        self.fastapi_app: FastAPI | None = fastapi_app
        if self.fastapi_app is None:
            self.fastapi_app = _create_base_fastapi_app()

    def run(self, agent_executor: AgentExecutor, **kwargs: str) -> None:
        """Run the app.

        Args:
            agent_executor: The AgentExecutor instance to run.
            **kwargs: Additional arguments for running the app.
        """
        url_prefix: str = str(kwargs.get("url_prefix", ""))

        if self.config.dev:
            # Dev mode: use string import path for hot reload
            self._run_dev_mode(url_prefix)
        else:
            # Normal mode: use app object directly
            self._create_channels(agent_executor, url_prefix=url_prefix)
            self._start_server_sync()

    def _run_dev_mode(self, url_prefix: str = "") -> None:
        """Run in dev mode with hot reload support.

        Args:
            url_prefix: URL prefix for all routes.
        """
        # Store url_prefix in environment variable for subprocess to access
        os.environ[_DEV_URL_PREFIX_ENV] = url_prefix

        # Run with string import path for hot reload
        uvicorn.run(
            app="sdk.runner:create_dev_app",
            factory=True,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            reload=True,
            reload_dirs=["src"],
        )

    async def run_async(self, agent_executor: AgentExecutor, **kwargs: str) -> None:
        """Run the app asynchronously.

        Args:
            agent_executor: The AgentExecutor instance to run.
            **kwargs: Additional arguments for running the app.
        """
        url_prefix: str = str(kwargs.get("url_prefix", ""))
        self._create_channels(agent_executor, url_prefix=url_prefix)
        await self.stop()
        await self._start_server_async()

    async def stop(self) -> None:
        """Stop the running server."""
        if self.server:
            self.server.should_exit = True
            await asyncio.sleep(0.1)

    async def health_check(self) -> dict[str, str]:
        """Check the health status.

        Returns:
            Dictionary with health status.
        """
        return {"status": "healthy", "runner": "SimpleRunner"}

    def _create_channels(
        self, agent_executor: AgentExecutor, url_prefix: str = ""
    ) -> None:
        """Create and register API channels on the FastAPI app.

        Args:
            agent_executor: The AgentExecutor instance.
            url_prefix: URL prefix for all routes.
        """
        if self.fastapi_app is not None:
            _setup_channels(self.fastapi_app, agent_executor, url_prefix)

    def _start_server_sync(self) -> None:
        """Start the server synchronously."""
        if self.fastapi_app is None:
            raise RuntimeError("FastAPI app not initialized")
        uvicorn.run(
            app=self.fastapi_app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            reload=self.config.reload,
        )

    async def _start_server_async(self) -> None:
        """Start the server asynchronously."""
        if self.fastapi_app is None:
            raise RuntimeError("FastAPI app not initialized")
        config = uvicorn.Config(
            app=self.fastapi_app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level,
            reload=self.config.reload,
        )

        server = uvicorn.Server(config)
        self.server = server
        # Run in the current event loop
        await server.serve()
