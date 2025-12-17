"""Start command."""

import signal
import subprocess
import sys
from pathlib import Path

import typer
import uvicorn

app = typer.Typer()

# Global reference to frontend process for cleanup
_frontend_process: subprocess.Popen | None = None


def _cleanup_processes():
    """Clean up frontend process on exit."""
    global _frontend_process
    if _frontend_process:
        try:
            _frontend_process.terminate()
            _frontend_process.wait(timeout=5)
        except Exception:
            _frontend_process.kill()
        _frontend_process = None


@app.command()
def start_cmd(
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    frontend_port: int = typer.Option(5173, "--frontend-port", help="Frontend dev server port"),
    dev: bool = typer.Option(False, "--dev/--no-dev", help="Start in development mode (with frontend dev server)"),
):
    """Start the web server and frontend."""
    # Display alpha warning
    typer.echo("", err=True)
    typer.echo("⚠️  ALPHA RELEASE - USE WITH CAUTION", err=True)
    typer.echo("This project is in alpha and under active development.", err=True)
    typer.echo("Breaking changes are expected and will occur. Use at your own risk.", err=True)
    typer.echo("", err=True)
    
    from ..db.connection import init_db

    init_db()

    # Check if production build exists
    # Try installed package location first (vibelab/web/dist)
    package_dir = Path(__file__).parent.parent
    dist_dir = package_dir / "web" / "dist"
    
    # If not found in package, try source location (development)
    if not dist_dir.exists():
        web_dir = Path(__file__).parent.parent.parent.parent / "web"
        dist_dir = web_dir / "dist"
    else:
        web_dir = package_dir / "web"

    if dev:
        # Development mode: start both backend and frontend dev servers
        typer.echo(f"Starting VibeLab in development mode...")
        typer.echo(f"Backend: http://{host}:{port}")
        typer.echo(f"Frontend: http://localhost:{frontend_port}")

        # Set up signal handlers for cleanup
        def signal_handler(sig, frame):
            typer.echo("\nShutting down...", err=True)
            _cleanup_processes()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start frontend dev server
        global _frontend_process
        try:
            # Set port and API URL via environment variables for Vite
            import os
            env = os.environ.copy()
            env["PORT"] = str(frontend_port)
            env["VITE_API_URL"] = f"http://{host}:{port}"
            
            _frontend_process = subprocess.Popen(
                ["bun", "run", "dev"],
                cwd=web_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                env=env,
            )
            typer.echo("Frontend dev server started", err=True)
        except Exception as e:
            typer.echo(f"Failed to start frontend: {e}", err=True)
            typer.echo("Continuing with backend only...", err=True)

        # Start backend server
        try:
            uvicorn.run(
                "vibelab.api.app:app",
                host=host,
                port=port,
                reload=False,  # Don't use uvicorn reload when managing frontend separately
            )
        except (KeyboardInterrupt, SystemExit):
            signal_handler(None, None)
        finally:
            _cleanup_processes()
    else:
        # Production mode: serve static files from backend
        if not dist_dir.exists():
            typer.echo(
                "Warning: Frontend not built. Run 'cd web && bun run build' first.",
                err=True,
            )
            typer.echo("Starting backend only...", err=True)

        typer.echo(f"Starting VibeLab server on http://{host}:{port}")
        uvicorn.run("vibelab.api.app:app", host=host, port=port, reload=False)


app.command()(start_cmd)
