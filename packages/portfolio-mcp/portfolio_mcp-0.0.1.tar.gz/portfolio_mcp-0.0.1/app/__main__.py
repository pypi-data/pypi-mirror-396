"""CLI entry point for portfolio-mcp Server.

Usage:
    uvx portfolio-mcp stdio           # Local CLI mode (Claude Desktop)
    uvx portfolio-mcp sse             # SSE server mode (deprecated)
    uvx portfolio-mcp streamable-http # Streamable HTTP (recommended for remote)

Environment Variables:
    PORTFOLIO_MCP_PORT: Server port for HTTP modes (default: 8000)
    PORTFOLIO_MCP_HOST: Server host for HTTP modes (default: 0.0.0.0)
    CACHE_BACKEND: Cache backend - memory, sqlite, redis (default: auto)
    REDIS_URL: Redis connection URL (default: redis://localhost:6379)
"""

import sys

import typer

from app.config import settings

app = typer.Typer(
    name="portfolio-mcp",
    help="Portfolio Analysis MCP Server powered by mcp-refcache",
    add_completion=False,
)


def _print_startup_info(transport: str) -> None:
    """Print startup information."""
    typer.echo("📊 portfolio-mcp")
    typer.echo(f"   Transport: {transport}")
    typer.echo(f"   Cache backend: {settings.cache_backend}")


def _handle_shutdown() -> None:
    """Handle graceful shutdown."""
    typer.echo("\nShutting down server...")
    typer.echo("Service stopped.")


@app.command()
def stdio() -> None:
    """Start server in stdio mode (for Claude Desktop and local CLI).

    This is the recommended mode for local usage with Claude Desktop
    or other MCP clients that communicate via stdin/stdout.

    Cache backend defaults to SQLite for persistence across sessions.
    """
    from .server import mcp

    _print_startup_info("stdio")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.command()
def sse(
    host: str = typer.Option(None, "--host", "-h", help="Server host"),
    port: int = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Start server in SSE mode (Server-Sent Events).

    Note: SSE transport is deprecated. Use streamable-http for new deployments.

    Cache backend defaults to Redis for distributed deployments.
    """
    from .server import mcp

    server_host = host or settings.portfolio_mcp_host
    server_port = port or settings.portfolio_mcp_port

    _print_startup_info("sse")
    typer.echo(f"   Server: http://{server_host}:{server_port}/sse")
    typer.secho(
        "   Warning: SSE transport is deprecated. Use streamable-http instead.",
        fg=typer.colors.YELLOW,
    )

    try:
        mcp.run(transport="sse", host=server_host, port=server_port)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.command("streamable-http")
def streamable_http(
    host: str = typer.Option(None, "--host", "-h", help="Server host"),
    port: int = typer.Option(None, "--port", "-p", help="Server port"),
) -> None:
    """Start server in streamable HTTP mode (recommended for remote).

    This is the recommended mode for remote deployments, Docker containers,
    and any scenario where the client connects over HTTP.

    Cache backend defaults to Redis for distributed deployments.
    """
    from .server import mcp

    server_host = host or settings.portfolio_mcp_host
    server_port = port or settings.portfolio_mcp_port

    _print_startup_info("streamable-http")
    typer.echo(f"   Server: http://{server_host}:{server_port}/mcp")

    try:
        mcp.run(transport="streamable-http", host=server_host, port=server_port)
    except KeyboardInterrupt:
        pass
    except Exception as error:
        typer.echo(f"\nError: {error}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        _handle_shutdown()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
) -> None:
    """Portfolio Analysis MCP Server powered by mcp-refcache.

    Provides comprehensive portfolio management, analysis, and optimization
    tools for AI assistants via the Model Context Protocol.

    Features:
    - Portfolio creation from Yahoo Finance, CoinGecko, or synthetic data
    - Analysis: returns, volatility, Sharpe ratio, Sortino, VaR, drawdowns
    - Optimization: Efficient Frontier, Monte Carlo simulation
    - Reference-based caching for large datasets
    """
    if version:
        from . import __version__

        typer.echo(f"portfolio-mcp {__version__}")
        raise typer.Exit()

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


if __name__ == "__main__":
    app()
