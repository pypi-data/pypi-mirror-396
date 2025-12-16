"""Command-line interface for GluRPC client."""
from typing import Optional
import typer
from pathlib import Path

from glucosedao_client.app import launch_app
from glucosedao_client.server import start_server, stop_server, is_server_running


app = typer.Typer(
    name="glucosedao-client",
    help="GluRPC Client - Glucose prediction client application"
)


@app.command()
def launch(
    share: bool = typer.Option(
        False,
        "--share",
        help="Create a public Gradio share link"
    ),
    server_name: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Hostname to bind to"
    ),
    server_port: int = typer.Option(
        7860,
        "--port",
        help="Port to bind to"
    ),
    with_server: bool = typer.Option(
        False,
        "--with-server",
        help="Start GluRPC server locally for testing"
    ),
    server_host: str = typer.Option(
        "127.0.0.1",
        "--server-host",
        help="GluRPC server host (when starting with --with-server)"
    ),
    server_port_backend: int = typer.Option(
        8000,
        "--server-port",
        help="GluRPC server port (when starting with --with-server)"
    )
):
    """Launch the Gradio web interface.
    
    Examples:
    
    # Launch client only (assumes server is running elsewhere)
    glucosedao-client launch
    
    # Launch client with local server for testing
    glucosedao-client launch --with-server
    
    # Launch with custom ports
    glucosedao-client launch --port 8080 --with-server --server-port 8001
    
    # Create public share link
    glucosedao-client launch --share
    """
    server_process = None
    
    try:
        if with_server:
            typer.echo("🚀 Starting GluRPC server for local testing...")
            server_process = start_server(
                host=server_host,
                port=server_port_backend,
                background=True,
                wait=True
            )
            
            if server_process is None and not is_server_running(f"http://{server_host}:{server_port_backend}"):
                typer.echo("❌ Failed to start server", err=True)
                raise typer.Exit(1)
        
        typer.echo(f"🚀 Launching Gradio client on {server_name}:{server_port}...")
        
        if with_server:
            typer.echo(f"   Server running at http://{server_host}:{server_port_backend}")
        
        launch_app(
            share=share,
            server_name=server_name,
            server_port=server_port
        )
        
    except KeyboardInterrupt:
        typer.echo("\n🛑 Shutting down...")
    finally:
        if server_process is not None:
            stop_server(server_process)


@app.command()
def server(
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        help="Host to bind to"
    ),
    port: int = typer.Option(
        8000,
        "--port",
        help="Port to bind to"
    )
):
    """Start only the GluRPC server (no client interface).
    
    This is useful for running the server separately.
    
    Example:
    
    glucosedao-client server --host 0.0.0.0 --port 8000
    """
    typer.echo(f"🚀 Starting GluRPC server on {host}:{port}...")
    
    try:
        start_server(
            host=host,
            port=port,
            background=False,
            wait=False
        )
    except KeyboardInterrupt:
        typer.echo("\n🛑 Server stopped")


@app.command()
def check(
    url: str = typer.Option(
        "http://localhost:8000",
        "--url",
        help="Server URL to check"
    )
):
    """Check if GluRPC server is running and healthy.
    
    Example:
    
    glucosedao-client check --url http://localhost:8000
    """
    typer.echo(f"🔍 Checking server at {url}...")
    
    if is_server_running(url):
        typer.echo(f"✅ Server is running and healthy at {url}")
    else:
        typer.echo(f"❌ Server is not responding at {url}")
        raise typer.Exit(1)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

