"""Backend health check command."""

import httpx
import typer

from cli.commands.console import console
from cli.utils.typer_utils import HelpOnErrorGroup


app = typer.Typer(
    name="health", help="Check backend server health", cls=HelpOnErrorGroup
)


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Health check callback - defaults to check."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, run check
        check()


@app.command("check")
def check() -> None:
    """Check if the AnyTask backend server is healthy.

    Calls the /health endpoint on the configured API server
    and displays the server status.

    Examples:
        anyt health          # Check current environment
        anyt health check    # Explicit check command
    """
    try:
        # Get API configuration
        from cli.config import get_effective_api_config

        try:
            api_config = get_effective_api_config()
            api_url = api_config["api_url"]
        except RuntimeError:
            console.print("[red]✗ Not authenticated[/red]")
            console.print(
                "\nSet the ANYT_API_KEY environment variable: [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]"
            )
            raise typer.Exit(code=1)

        console.print("\n[cyan]Checking backend health...[/cyan]")
        console.print(f"API URL: [blue]{api_url}[/blue]\n")

        # Make health check request
        health_url = f"{api_url}/health"

        try:
            response = httpx.get(health_url, timeout=5.0)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Validate response format
            if "status" not in data:
                console.print("[red]✗ Backend server returned invalid response[/red]")
                console.print(
                    "[yellow]Error:[/yellow] Expected 'status' field in response"
                )
                console.print(f"[dim]Response: {data}[/dim]")
                raise typer.Exit(code=1)

            status = data.get("status")
            timestamp = data.get("timestamp", "N/A")

            # Display success
            console.print("[green]✓ Backend server is healthy[/green]")
            console.print(f"Status: [green]{status}[/green]")
            console.print(f"Timestamp: [cyan]{timestamp}[/cyan]")
            console.print()

        except httpx.ConnectError:
            console.print("[red]✗ Backend server is unreachable[/red]")
            console.print(
                "[yellow]Error:[/yellow] Connection refused. Is the server running?"
            )
            console.print(f"[dim]Tried to connect to: {health_url}[/dim]")
            raise typer.Exit(code=1)

        except httpx.TimeoutException:
            console.print("[red]✗ Backend server did not respond in time[/red]")
            console.print(
                "[yellow]Error:[/yellow] Request timed out. Server may be overloaded."
            )
            console.print(f"[dim]Tried to connect to: {health_url}[/dim]")
            raise typer.Exit(code=1)

        except httpx.HTTPStatusError as e:
            console.print("[red]✗ Backend server returned an error[/red]")
            console.print(
                f"[yellow]Error:[/yellow] Server returned status code {e.response.status_code}"
            )
            console.print(f"[dim]Response: {e.response.text}[/dim]")
            raise typer.Exit(code=1)

        except ValueError as e:
            # JSON parsing error
            console.print("[red]✗ Backend server returned invalid JSON[/red]")
            console.print(f"[yellow]Error:[/yellow] {str(e)}")
            raise typer.Exit(code=1)

    except ValueError as e:
        # Configuration error
        console.print(f"[red]✗ Configuration error:[/red] {str(e)}")
        raise typer.Exit(code=1)

    except Exception as e:  # noqa: BLE001 - Intentionally broad: catch-all for unexpected errors
        # Catch-all for unexpected errors not covered above
        console.print(f"[red]✗ Unexpected error:[/red] {str(e)}")
        raise typer.Exit(code=1)
