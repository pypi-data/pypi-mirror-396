"""Configuration commands for DUTVulnScanner CLI."""

import typer
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv, set_key, unset_key

app = typer.Typer()
console = Console()

# Path to user's .env file
USER_ENV_FILE = Path.home() / ".dutVulnScanner" / ".env"


def ensure_env_file():
    """Ensure .env file exists in user config directory."""
    USER_ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USER_ENV_FILE.exists():
        USER_ENV_FILE.touch()


@app.command()
def show():
    """
    Show current configuration settings.

    Example:
        dutVulnScanner settings show
    """
    ensure_env_file()
    load_dotenv(USER_ENV_FILE)

    table = Table(title="DUTVulnScanner Configuration", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    # Discord webhook
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if discord_webhook:
        # Mask webhook URL for security
        masked = discord_webhook[:30] + "..." if len(discord_webhook) > 30 else discord_webhook
        table.add_row("DISCORD_WEBHOOK_URL", masked, "✓ Configured")
    else:
        table.add_row("DISCORD_WEBHOOK_URL", "Not set", "✗ Not configured")

    # Gemini API Key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        # Mask API key for security
        masked = gemini_api_key[:10] + "..." if len(gemini_api_key) > 10 else gemini_api_key
        table.add_row("GEMINI_API_KEY", masked, "✓ Configured")
    else:
        table.add_row("GEMINI_API_KEY", "Not set", "✗ Not configured")

    # Firebase credentials
    firebase_creds = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if firebase_creds:
        # Show just the filename for security
        creds_file = Path(firebase_creds).name if firebase_creds else "N/A"
        table.add_row("FIREBASE_CREDENTIALS_PATH", creds_file, "✓ Configured")
    else:
        table.add_row("FIREBASE_CREDENTIALS_PATH", "Not set", "✗ Not configured")

    # Firebase storage bucket
    firebase_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
    if firebase_bucket:
        table.add_row("FIREBASE_STORAGE_BUCKET", firebase_bucket, "✓ Configured")
    else:
        table.add_row("FIREBASE_STORAGE_BUCKET", "Default (auto-detect)", "ℹ Optional")

    console.print(table)
    console.print(f"\n[dim]Config file location: {USER_ENV_FILE}[/dim]")


@app.command()
def set_discord(webhook_url: str = typer.Argument(..., help="Discord webhook URL")):
    """
    Set Discord webhook URL for notifications.

    Example:
        dutVulnScanner settings set-discord https://discord.com/api/webhooks/...
    """
    ensure_env_file()

    # Validate webhook URL format
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        console.print("[bold red]Error:[/bold red] Invalid Discord webhook URL format")
        console.print("[dim]URL should start with: https://discord.com/api/webhooks/[/dim]")
        raise typer.Exit(1)

    # Set the environment variable in .env file
    set_key(USER_ENV_FILE, "DISCORD_WEBHOOK_URL", webhook_url)

    console.print("[bold green]✓[/bold green] Discord webhook URL configured successfully!")
    console.print(f"[dim]Saved to: {USER_ENV_FILE}[/dim]")
    console.print("\n[cyan]Discord notifications will now be sent when scans complete.[/cyan]")


@app.command()
def remove_discord():
    """
    Remove Discord webhook URL configuration.

    Example:
        dutVulnScanner settings remove-discord
    """
    ensure_env_file()

    # Remove the environment variable from .env file
    unset_key(USER_ENV_FILE, "DISCORD_WEBHOOK_URL")

    console.print("[bold green]✓[/bold green] Discord webhook URL removed")
    console.print("[dim]Discord notifications are now disabled[/dim]")


@app.command()
def set_gemini(api_key: str = typer.Argument(..., help="Gemini API Key")):
    """
    Set Google Gemini API Key for AI-powered report generation.

    Example:
        dutVulnScanner settings set-gemini YOUR_GEMINI_API_KEY
    """
    ensure_env_file()

    if not api_key or len(api_key.strip()) < 10:
        console.print("[bold red]Error:[/bold red] Invalid Gemini API Key")
        console.print("[dim]API Key should be at least 10 characters long[/dim]")
        raise typer.Exit(1)

    # Set the environment variable in .env file
    set_key(USER_ENV_FILE, "GEMINI_API_KEY", api_key)

    console.print("[bold green]✓[/bold green] Gemini API Key configured successfully!")
    console.print(f"[dim]Saved to: {USER_ENV_FILE}[/dim]")
    console.print("\n[cyan]AI-powered report generation is now enabled.[/cyan]")
    console.print("[dim]Use --generate-report flag with scan commands to generate AI reports.[/dim]")


@app.command()
def remove_gemini():
    """
    Remove Gemini API Key configuration.

    Example:
        dutVulnScanner settings remove-gemini
    """
    ensure_env_file()

    # Remove the environment variable from .env file
    unset_key(USER_ENV_FILE, "GEMINI_API_KEY")

    console.print("[bold green]✓[/bold green] Gemini API Key removed")
    console.print("[dim]AI-powered report generation is now disabled[/dim]")


@app.command()
def set_firebase(credentials_path: str = typer.Argument(..., help="Path to Firebase service account JSON file")):
    """
    Set Firebase credentials for PDF upload functionality.

    Example:
        dutVulnScanner settings set-firebase /path/to/serviceAccountKey.json
    """
    ensure_env_file()

    # Validate that file exists
    creds_file = Path(credentials_path).expanduser()
    if not creds_file.exists():
        console.print("[bold red]Error:[/bold red] Firebase credentials file not found")
        console.print(f"[dim]Checked path: {creds_file}[/dim]")
        raise typer.Exit(1)

    # Validate it's a JSON file
    if not creds_file.suffix.lower() == ".json":
        console.print("[bold yellow]Warning:[/bold yellow] File is not a JSON file")
        console.print("[dim]Firebase credentials should be a JSON file[/dim]")
        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(1)

    # Store absolute path
    abs_path = str(creds_file.absolute())
    set_key(USER_ENV_FILE, "FIREBASE_CREDENTIALS_PATH", abs_path)

    console.print("[bold green]✓[/bold green] Firebase credentials configured successfully!")
    console.print(f"[dim]Path: {abs_path}[/dim]")
    console.print(f"[dim]Saved to: {USER_ENV_FILE}[/dim]")
    console.print("\n[cyan]PDF upload to Firebase Storage is now enabled.[/cyan]")
    console.print("[dim]Use --upload-pdf flag with scan commands to upload generated reports.[/dim]")


@app.command()
def set_firebase_bucket(bucket_name: str = typer.Argument(..., help="Firebase Storage bucket name")):
    """
    Set Firebase Storage bucket name (optional).

    Example:
        dutVulnScanner settings set-firebase-bucket my-project.appspot.com
    """
    ensure_env_file()

    if not bucket_name or not bucket_name.strip():
        console.print("[bold red]Error:[/bold red] Bucket name cannot be empty")
        raise typer.Exit(1)

    set_key(USER_ENV_FILE, "FIREBASE_STORAGE_BUCKET", bucket_name)

    console.print("[bold green]✓[/bold green] Firebase Storage bucket configured!")
    console.print(f"[dim]Bucket: {bucket_name}[/dim]")
    console.print("[dim]Note: If not set, the default bucket from your Firebase project will be used[/dim]")


@app.command()
def remove_firebase():
    """
    Remove Firebase credentials configuration.

    Example:
        dutVulnScanner settings remove-firebase
    """
    ensure_env_file()

    # Remove both Firebase settings
    unset_key(USER_ENV_FILE, "FIREBASE_CREDENTIALS_PATH")
    unset_key(USER_ENV_FILE, "FIREBASE_STORAGE_BUCKET")

    console.print("[bold green]✓[/bold green] Firebase configuration removed")
    console.print("[dim]PDF upload to Firebase Storage is now disabled[/dim]")


@app.command()
def init():
    """
    Initialize configuration with interactive prompts.

    Example:
        dutVulnScanner settings init
    """
    ensure_env_file()

    console.print("[bold cyan]DUTVulnScanner Configuration Setup[/bold cyan]\n")

    # Discord webhook setup
    console.print("[bold]Discord Notifications (Optional)[/bold]")
    console.print("To receive scan completion notifications via Discord:")
    console.print("1. Go to your Discord server settings")
    console.print("2. Navigate to Integrations → Webhooks")
    console.print("3. Create a new webhook and copy the URL\n")

    setup_discord = typer.confirm("Do you want to configure Discord notifications?", default=False)

    if setup_discord:
        webhook_url = typer.prompt("Enter your Discord webhook URL")

        if webhook_url.startswith("https://discord.com/api/webhooks/"):
            set_key(USER_ENV_FILE, "DISCORD_WEBHOOK_URL", webhook_url)
            console.print("[bold green]✓[/bold green] Discord webhook configured!")
        else:
            console.print("[bold yellow]⚠[/bold yellow] Invalid webhook URL, skipping Discord setup")

    # Gemini API Key setup
    console.print("\n[bold]Gemini API Key (Optional)[/bold]")
    console.print("To enable AI-powered report generation:")
    console.print("1. Go to https://aistudio.google.com/api-keys")
    console.print("2. Get your Gemini API Key")
    console.print("3. Enter it below\n")

    setup_gemini = typer.confirm("Do you want to configure Gemini API Key?", default=False)

    if setup_gemini:
        api_key = typer.prompt("Enter your Gemini API Key", hide_input=True)

        if api_key and len(api_key.strip()) >= 10:
            set_key(USER_ENV_FILE, "GEMINI_API_KEY", api_key)
            console.print("[bold green]✓[/bold green] Gemini API Key configured!")
        else:
            console.print("[bold yellow]⚠[/bold yellow] Invalid API Key, skipping Gemini setup")

    # Firebase credentials setup
    console.print("\n[bold]Firebase Storage (Optional)[/bold]")
    console.print("To enable PDF upload to Firebase Storage:")
    console.print("1. Go to Firebase Console: https://console.firebase.google.com")
    console.print("2. Create a new project or select existing one")
    console.print("3. Go to Project Settings → Service Accounts")
    console.print("4. Click 'Generate New Private Key' and save the JSON file")
    console.print("5. Provide the path to the JSON file below\n")

    setup_firebase = typer.confirm("Do you want to configure Firebase Storage?", default=False)

    if setup_firebase:
        creds_path = typer.prompt("Enter path to Firebase service account JSON file")
        creds_file = Path(creds_path).expanduser()

        if creds_file.exists():
            abs_path = str(creds_file.absolute())
            set_key(USER_ENV_FILE, "FIREBASE_CREDENTIALS_PATH", abs_path)
            console.print("[bold green]✓[/bold green] Firebase credentials configured!")

            # Optional: Ask for bucket name
            set_bucket = typer.confirm("Do you want to specify a custom bucket name?", default=False)
            if set_bucket:
                bucket_name = typer.prompt("Enter Firebase Storage bucket name (e.g., my-project.appspot.com)")
                if bucket_name:
                    set_key(USER_ENV_FILE, "FIREBASE_STORAGE_BUCKET", bucket_name)
                    console.print("[bold green]✓[/bold green] Firebase bucket configured!")
        else:
            console.print(f"[bold yellow]⚠[/bold yellow] File not found: {creds_file}")
            console.print("[dim]Skipping Firebase setup[/dim]")

    console.print("\n[bold green]Configuration complete![/bold green]")
    console.print(f"[dim]Config saved to: {USER_ENV_FILE}[/dim]")
    console.print("\n[cyan]You can update settings anytime using:[/cyan]")
    console.print("  dutVulnScanner settings show")
    console.print("  dutVulnScanner settings set-discord <url>")
    console.print("  dutVulnScanner settings set-gemini <api-key>")
    console.print("  dutVulnScanner settings set-firebase <path>")
    console.print("  dutVulnScanner settings set-firebase-bucket <bucket-name>")
