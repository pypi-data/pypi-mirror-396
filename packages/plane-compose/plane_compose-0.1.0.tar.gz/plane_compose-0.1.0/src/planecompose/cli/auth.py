"""Authentication commands."""
import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

app = typer.Typer(help="Authentication commands")
console = Console()

CONFIG_DIR = Path.home() / ".config" / "plane-cli"
TOKEN_FILE = CONFIG_DIR / "credentials"


@app.command()
def login():
    """
    Authenticate with Plane using an API key.
    
    Get your API key from: https://app.plane.so/profile/api-tokens
    """
    console.print("\n[cyan]Plane CLI Authentication[/cyan]")
    console.print("[dim]Get your API key from: https://app.plane.so/profile/api-tokens[/dim]\n")
    
    api_key = Prompt.ask("Enter your Plane API key", password=True)
    
    if not api_key or len(api_key) < 20:
        console.print("[red]✗[/red] Invalid API key format")
        raise typer.Exit(1)
    
    # Test the API key
    try:
        from plane import PlaneClient
        client = PlaneClient(base_url="https://api.plane.so", api_key=api_key)
        me = client.users.get_me()
        
        # Save the key
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(api_key)
        TOKEN_FILE.chmod(0o600)
        
        # Show success with user info
        console.print(f"\n[green]✓ Authenticated successfully![/green]")
        console.print(f"\n[bold]Logged in as:[/bold]")
        console.print(f"  Email: {me.email if hasattr(me, 'email') else 'N/A'}")
        console.print(f"  Name: {me.display_name if hasattr(me, 'display_name') else 'N/A'}")
        
    except Exception as e:
        console.print(f"\n[red]✗ Authentication failed:[/red] {e}")
        console.print("[yellow]Please check your API key and try again[/yellow]")
        raise typer.Exit(1)


@app.command()
def logout():
    """Remove stored credentials."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        console.print("[green]✓[/green] Logged out successfully")
        console.print("[dim]Run 'plane auth login' to authenticate again[/dim]")
    else:
        console.print("[yellow]No credentials stored[/yellow]")


@app.command()
def whoami():
    """Show current authentication status and user information."""
    if not TOKEN_FILE.exists():
        console.print("[red]✗ Not authenticated[/red]")
        console.print("\nRun [cyan]plane auth login[/cyan] to authenticate")
        raise typer.Exit(1)
    
    try:
        from plane import PlaneClient
        api_key = TOKEN_FILE.read_text().strip()
        client = PlaneClient(base_url="https://api.plane.so", api_key=api_key)
        me = client.users.get_me()
        
        # Display user info in a panel
        info_text = f"""[bold]Email:[/bold] {me.email if hasattr(me, 'email') else 'N/A'}
[bold]Name:[/bold] {me.display_name if hasattr(me, 'display_name') else 'N/A'}
[bold]User ID:[/bold] {me.id if hasattr(me, 'id') else 'N/A'}

[dim]API Key:[/dim] [dim]{api_key[:10]}...{api_key[-4:]}[/dim]"""
        
        console.print()
        console.print(Panel(info_text, title="[green]✓ Authenticated[/green]", border_style="green"))
        
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        console.print("\n[yellow]Your API key may be invalid or expired[/yellow]")
        console.print("Run [cyan]plane auth login[/cyan] to re-authenticate")
        raise typer.Exit(1)
