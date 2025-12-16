"""Configuration wizard for Claude Bedrock CLI"""

import os
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def get_aws_config_dir() -> Path:
    """Get the AWS configuration directory"""
    home = Path.home()
    aws_dir = home / ".aws"
    return aws_dir


def ensure_aws_config_dir() -> Path:
    """Ensure AWS config directory exists"""
    aws_dir = get_aws_config_dir()
    aws_dir.mkdir(exist_ok=True)
    return aws_dir


def read_credentials() -> dict:
    """Read existing AWS credentials if they exist"""
    credentials_file = get_aws_config_dir() / "credentials"
    config = {}

    if credentials_file.exists():
        try:
            with open(credentials_file, 'r') as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        config[current_section] = {}
                    elif '=' in line and current_section:
                        key, value = line.split('=', 1)
                        config[current_section][key.strip()] = value.strip()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read existing credentials: {e}[/yellow]")

    return config


def write_credentials(profile: str, access_key: str, secret_key: str):
    """Write credentials to AWS credentials file"""
    aws_dir = ensure_aws_config_dir()
    credentials_file = aws_dir / "credentials"

    # Read existing credentials
    existing = read_credentials()

    # Update or add the profile
    existing[profile] = {
        'aws_access_key_id': access_key,
        'aws_secret_access_key': secret_key
    }

    # Write back
    try:
        with open(credentials_file, 'w') as f:
            for profile_name, creds in existing.items():
                f.write(f"[{profile_name}]\n")
                for key, value in creds.items():
                    f.write(f"{key} = {value}\n")
                f.write("\n")

        # Set appropriate permissions (readable only by owner)
        if sys.platform != "win32":
            os.chmod(credentials_file, 0o600)

        console.print(f"[green]✓ Credentials saved to {credentials_file}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error writing credentials: {e}[/red]")
        sys.exit(1)


def write_user_config(username: str):
    """Write user configuration to Claude CLI config"""
    from .config import get_config_dir
    config_dir = Path(get_config_dir())
    user_config_file = config_dir / "user_config.json"

    import json
    try:
        config_data = {"username": username}
        with open(user_config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        console.print(f"[green]✓ User configuration saved[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save user config: {e}[/yellow]")


def write_config(profile: str, region: str):
    """Write configuration to AWS config file"""
    aws_dir = ensure_aws_config_dir()
    config_file = aws_dir / "config"

    # Read existing config
    existing = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        existing[current_section] = {}
                    elif '=' in line and current_section:
                        key, value = line.split('=', 1)
                        existing[current_section][key.strip()] = value.strip()
        except Exception:
            pass

    # Update or add the profile
    section_name = f"profile {profile}" if profile != "default" else "default"
    existing[section_name] = existing.get(section_name, {})
    existing[section_name]['region'] = region

    # Write back
    try:
        with open(config_file, 'w') as f:
            for section_name, config_data in existing.items():
                f.write(f"[{section_name}]\n")
                for key, value in config_data.items():
                    f.write(f"{key} = {value}\n")
                f.write("\n")

        console.print(f"[green]✓ Configuration saved to {config_file}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error writing config: {e}[/red]")
        sys.exit(1)


@click.command()
@click.option('--profile', default='default', help='AWS profile name (default: default)')
def configure(profile):
    """Configure AWS credentials for Claude Bedrock CLI

    This command helps you set up AWS credentials without needing the AWS CLI.
    Credentials are stored in the standard AWS location (~/.aws/credentials).

    EXAMPLES:

      # Configure default profile
      claude-bedrock-configure

      # Configure a named profile
      claude-bedrock-configure --profile myproject
    """
    console.print(Panel.fit(
        "[bold cyan]Claude Bedrock CLI - AWS Configuration[/bold cyan]\n\n"
        "This wizard will help you configure AWS credentials for accessing Bedrock.\n"
        "Your credentials will be stored securely in ~/.aws/credentials\n\n"
        "[dim]You'll need:\n"
        "  • AWS Access Key ID\n"
        "  • AWS Secret Access Key\n"
        "  • AWS Region (e.g., us-east-1)[/dim]",
        title="Setup Wizard",
        border_style="cyan"
    ))

    console.print()

    # Check if AWS CLI is available
    import shutil
    has_aws_cli = shutil.which('aws') is not None

    if has_aws_cli:
        console.print("[green]✓ AWS CLI detected[/green]")
        use_aws_cli = Confirm.ask(
            "Would you like to use 'aws configure' instead?",
            default=True
        )

        if use_aws_cli:
            console.print("\n[cyan]Running: aws configure[/cyan]")
            if profile != 'default':
                os.system(f'aws configure --profile {profile}')
            else:
                os.system('aws configure')
            console.print("\n[green]✓ Configuration complete![/green]")
            return
    else:
        console.print("[yellow]ℹ AWS CLI not detected - using built-in configuration[/yellow]")

    console.print()

    # Prompt for user information
    console.print("[bold]User Information[/bold]\n")

    username = Prompt.ask(
        "[cyan]Your email or username[/cyan]",
        default=""
    )

    console.print()

    # Prompt for credentials
    console.print(f"[bold]AWS Configuration (profile: {profile})[/bold]\n")

    access_key = Prompt.ask(
        "[cyan]AWS Access Key ID[/cyan]",
        password=False
    )

    secret_key = Prompt.ask(
        "[cyan]AWS Secret Access Key[/cyan]",
        password=True
    )

    region = Prompt.ask(
        "[cyan]Default region name[/cyan]",
        default="us-east-1"
    )

    console.print()

    # Write credentials
    console.print("[dim]Saving credentials...[/dim]")
    if username:
        write_user_config(username)
    write_credentials(profile, access_key, secret_key)
    write_config(profile, region)

    console.print()
    console.print(Panel.fit(
        "[bold green]✓ Configuration Complete![/bold green]\n\n"
        f"Profile: [cyan]{profile}[/cyan]\n"
        f"Region: [cyan]{region}[/cyan]\n"
        f"Credentials saved to: [dim]~/.aws/credentials[/dim]\n\n"
        "[yellow]Next steps:[/yellow]\n"
        "  1. Enable Bedrock model access in AWS Console\n"
        "  2. Run: [cyan]claude-bedrock[/cyan] to start the CLI",
        title="Success",
        border_style="green"
    ))

    # Offer to test the connection
    console.print()
    test_connection = Confirm.ask(
        "Would you like to test the Bedrock connection?",
        default=True
    )

    if test_connection:
        test_bedrock_connection(profile, region)


def test_bedrock_connection(profile: str, region: str):
    """Test the Bedrock connection"""
    console.print("\n[dim]Testing Bedrock connection...[/dim]")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        # Create session with the profile
        session = boto3.Session(profile_name=profile if profile != 'default' else None)
        bedrock = session.client('bedrock', region_name=region)

        # Try to list foundation models
        response = bedrock.list_foundation_models()

        # Check if any Claude models are available
        claude_models = [
            model for model in response.get('modelSummaries', [])
            if 'claude' in model.get('modelId', '').lower()
        ]

        if claude_models:
            console.print(f"\n[green]✓ Connection successful![/green]")
            console.print(f"\n[cyan]Available Claude models:[/cyan]")
            for model in claude_models[:5]:  # Show first 5
                console.print(f"  • {model['modelId']}")
            if len(claude_models) > 5:
                console.print(f"  [dim]... and {len(claude_models) - 5} more[/dim]")
        else:
            console.print("\n[yellow]⚠ Connection works, but no Claude models found[/yellow]")
            console.print("[dim]You may need to enable model access in the AWS Console[/dim]")

    except NoCredentialsError:
        console.print("\n[red]✗ Credentials not found or invalid[/red]")
        console.print("[dim]Please check your AWS credentials[/dim]")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'UnrecognizedClientException':
            console.print("\n[red]✗ Invalid credentials[/red]")
        elif error_code == 'AccessDeniedException':
            console.print("\n[yellow]⚠ Access denied to Bedrock[/yellow]")
            console.print("[dim]Your credentials work, but you need IAM permissions for Bedrock[/dim]")
        else:
            console.print(f"\n[red]✗ Error: {e}[/red]")
    except Exception as e:
        console.print(f"\n[red]✗ Unexpected error: {e}[/red]")


if __name__ == "__main__":
    configure()
