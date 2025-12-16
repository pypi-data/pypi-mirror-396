"""API Key management commands for ThreatWinds Pentest CLI.

Allows the instance owner to manage authorized API keys.
"""

import sys

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from twpt_cli.config import load_credentials, get_api_endpoint
from twpt_cli.sdk import HTTPClient

console = Console()


@click.group()
def keys():
    """Manage authorized API keys for this pt-agent instance.

    The first user to authenticate becomes the instance owner.
    The owner can add additional API keys to allow team members access.

    All key management operations require owner privileges.

    Examples:
        twpt keys list                    # List all authorized keys
        twpt keys add --label "Alice"     # Add a new key (prompts for credentials)
        twpt keys remove <key_id>         # Remove an authorized key
        twpt keys owner                   # Show instance owner info
        twpt keys unbind                  # Reset instance (destructive!)
    """
    pass


@keys.command('list')
def list_keys():
    """List all authorized API keys.

    Shows all keys that can access this pt-agent instance,
    including the owner and any keys they have authorized.

    Requires owner privileges.
    """
    creds = load_credentials()
    if not creds:
        console.print("✗ Not configured. Please run: twpt configure", style="red")
        sys.exit(1)

    try:
        client = HTTPClient(get_api_endpoint(), creds)
        result = client.list_authorized_keys()

        # Display header
        console.print("\n╔══════════════════════════════════════════════╗", style="cyan")
        console.print("║           Authorized API Keys                 ║", style="cyan")
        console.print("╚══════════════════════════════════════════════╝\n", style="cyan")

        keys_list = result.get('keys', [])
        if not keys_list:
            console.print("[yellow]No authorized keys found[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Key ID", style="white")
        table.add_column("Label", style="yellow")
        table.add_column("Role", style="magenta")
        table.add_column("User ID", style="dim", max_width=20)
        table.add_column("Created", style="dim")
        table.add_column("Added By", style="dim", max_width=12)

        for key in keys_list:
            # Format role with color
            role = key.get('role', 'user')
            role_color = "green" if role == "owner" else "blue"
            role_display = f"[{role_color}]{role.upper()}[/{role_color}]"

            # Format user ID (truncate if too long)
            user_id = key.get('user_id', 'N/A')
            if user_id and len(user_id) > 18:
                user_id = user_id[:15] + "..."

            # Format added_by
            added_by = key.get('added_by', '-')
            if added_by and len(added_by) > 10:
                added_by = added_by[:8] + ".."

            # Format created date
            created = key.get('created_at', 'N/A')
            if created and len(created) > 19:
                created = created[:19]  # Truncate to datetime without timezone

            table.add_row(
                key.get('key_id', 'N/A'),
                key.get('label', 'N/A'),
                role_display,
                user_id,
                created,
                added_by if added_by != key.get('user_id') else '-'
            )

        console.print(table)
        console.print(f"\n[dim]Total: {result.get('total', len(keys_list))} keys[/dim]")

        if result.get('is_owner'):
            console.print("[green]✓ You are the instance owner[/green]")
        else:
            console.print("[yellow]⚠ You are not the instance owner[/yellow]")

    except Exception as e:
        console.print(f"\n✗ Failed to list keys: {e}", style="red")
        sys.exit(1)


@keys.command('add')
@click.option(
    '--api-key',
    prompt='API Key to authorize',
    help='The API key to add (will prompt if not provided)'
)
@click.option(
    '--api-secret',
    prompt='API Secret',
    hide_input=True,
    help='The API secret (will prompt securely if not provided)'
)
@click.option(
    '--label', '-l',
    prompt='Label for this key',
    help='Human-readable label (e.g., team member name)'
)
def add_key(api_key: str, api_secret: str, label: str):
    """Add a new authorized API key.

    The key being added must be valid ThreatWinds credentials.
    The server will validate the key before authorizing it.

    Requires owner privileges.

    Examples:
        twpt keys add --label "Alice"
        twpt keys add --api-key KEY --api-secret SECRET --label "Bob"
    """
    creds = load_credentials()
    if not creds:
        console.print("✗ Not configured. Please run: twpt configure", style="red")
        sys.exit(1)

    # Validate input
    if not api_key or not api_secret:
        console.print("✗ API key and secret are required", style="red")
        sys.exit(1)

    if not label:
        console.print("✗ Label is required", style="red")
        sys.exit(1)

    console.print(f"\n[cyan]Adding authorized key: {label}[/cyan]")
    console.print("[dim]Validating credentials with ThreatWinds...[/dim]")

    try:
        client = HTTPClient(get_api_endpoint(), creds)
        result = client.add_authorized_key(api_key, api_secret, label)

        if result.get('success'):
            console.print(f"\n✓ {result.get('message')}", style="green")
            console.print(f"  Key ID: [cyan]{result.get('key_id')}[/cyan]")
            console.print(f"  Label:  [yellow]{result.get('label')}[/yellow]")
        else:
            console.print(f"\n✗ Failed: {result.get('message', 'Unknown error')}", style="red")
            sys.exit(1)

    except Exception as e:
        console.print(f"\n✗ Failed to add key: {e}", style="red")
        sys.exit(1)


@keys.command('remove')
@click.argument('key_id')
@click.option(
    '--yes', '-y',
    is_flag=True,
    help='Skip confirmation prompt'
)
def remove_key(key_id: str, yes: bool):
    """Remove an authorized API key.

    Cannot remove the owner's key. Use 'keys unbind' to reset the instance.

    Requires owner privileges.

    Examples:
        twpt keys remove abc123def456
        twpt keys remove abc123def456 --yes
    """
    creds = load_credentials()
    if not creds:
        console.print("✗ Not configured. Please run: twpt configure", style="red")
        sys.exit(1)

    # Confirm removal
    if not yes:
        console.print(f"\n[yellow]⚠ This will revoke access for key: {key_id}[/yellow]")
        if not click.confirm("Are you sure you want to remove this key?"):
            console.print("Cancelled", style="dim")
            return

    try:
        client = HTTPClient(get_api_endpoint(), creds)
        result = client.remove_authorized_key(key_id)

        if result.get('success'):
            console.print(f"\n✓ {result.get('message')}", style="green")
        else:
            console.print(f"\n✗ Failed: {result.get('message', 'Unknown error')}", style="red")
            sys.exit(1)

    except Exception as e:
        console.print(f"\n✗ Failed to remove key: {e}", style="red")
        sys.exit(1)


@keys.command('owner')
def show_owner():
    """Show instance owner information.

    Displays who owns this pt-agent instance and when it was bound.

    Requires owner privileges.
    """
    creds = load_credentials()
    if not creds:
        console.print("✗ Not configured. Please run: twpt configure", style="red")
        sys.exit(1)

    try:
        client = HTTPClient(get_api_endpoint(), creds)
        result = client.get_instance_owner()

        console.print("\n╔══════════════════════════════════════════════╗", style="cyan")
        console.print("║             Instance Owner                    ║", style="cyan")
        console.print("╚══════════════════════════════════════════════╝\n", style="cyan")

        if not result.get('has_owner'):
            console.print("[yellow]⚠ No owner bound to this instance[/yellow]")
            console.print("[dim]The next user to authenticate will become the owner.[/dim]")
            return

        # Display owner info
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Has Owner", "[green]Yes[/green]")
        table.add_row("Key ID", result.get('key_id', 'N/A'))
        table.add_row("User ID", result.get('user_id', 'N/A'))
        table.add_row("Bound At", result.get('created_at', 'N/A'))

        console.print(table)

    except Exception as e:
        console.print(f"\n✗ Failed to get owner info: {e}", style="red")
        sys.exit(1)


@keys.command('unbind')
@click.option(
    '--yes', '-y',
    is_flag=True,
    help='Skip confirmation prompt'
)
def unbind_instance(yes: bool):
    """Unbind the instance - remove ALL authorization.

    WARNING: This is a destructive operation!

    - Removes the owner
    - Removes ALL authorized keys
    - The next user to authenticate becomes the new owner

    Use this to transfer ownership or reset a locked instance.

    Requires owner privileges.
    """
    creds = load_credentials()
    if not creds:
        console.print("✗ Not configured. Please run: twpt configure", style="red")
        sys.exit(1)

    # Strong confirmation
    if not yes:
        console.print("\n" + "=" * 50, style="red")
        console.print("⚠  WARNING: DESTRUCTIVE OPERATION  ⚠", style="bold red")
        console.print("=" * 50, style="red")
        console.print("\nThis will:")
        console.print("  • Remove the instance owner")
        console.print("  • Remove ALL authorized keys")
        console.print("  • Anyone can become the new owner")
        console.print("")

        if not click.confirm("Are you SURE you want to unbind this instance?", default=False):
            console.print("Cancelled", style="dim")
            return

        # Double confirmation
        console.print("\n[yellow]Type 'UNBIND' to confirm:[/yellow]")
        confirmation = click.prompt("Confirm", default="")
        if confirmation != "UNBIND":
            console.print("Cancelled - confirmation text did not match", style="dim")
            return

    try:
        client = HTTPClient(get_api_endpoint(), creds)
        result = client.unbind_instance()

        if result.get('success'):
            console.print(f"\n✓ {result.get('message')}", style="green")
            console.print("\n[yellow]⚠ You are no longer the owner.[/yellow]")
            console.print("[dim]The next authentication will bind a new owner.[/dim]")
        else:
            console.print(f"\n✗ Failed: {result.get('message', 'Unknown error')}", style="red")
            sys.exit(1)

    except Exception as e:
        console.print(f"\n✗ Failed to unbind instance: {e}", style="red")
        sys.exit(1)
