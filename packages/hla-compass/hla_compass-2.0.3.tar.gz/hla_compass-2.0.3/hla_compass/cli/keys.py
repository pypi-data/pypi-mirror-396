"""
Key management commands for module signing.
"""

import sys
import click
from pathlib import Path

from ..signing import ModuleSigner
from .utils import console


@click.group()
def keys():
    """Manage signing keys used for module publishing."""
    pass


@keys.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing keys")
def keys_init(force: bool):
    """Generate a new RSA key pair for signing manifests."""
    signer = ModuleSigner()
    try:
        priv, pub = signer.generate_keys(force=force)
        console.print(f"[green]✓[/green] Generated keys\n[dim]Private:[/dim] {priv}\n[dim]Public:[/dim] {pub}")
    except FileExistsError as e:
        console.print(f"[yellow]Keys already exist: {e}[/yellow]")
        console.print("Re-run with --force to regenerate.")
    except Exception as e:
        console.print(f"[red]Failed to generate keys: {e}[/red]")
        sys.exit(1)


@keys.command("show")
def keys_show():
    """Show the public key (base64 DER) for distribution."""
    signer = ModuleSigner()
    try:
        fingerprint = signer.get_key_fingerprint()
        public_key = signer.get_public_key_string()
        console.print(f"[green]Public key:[/green] {public_key}")
        console.print(f"[dim]Fingerprint:[/dim] {fingerprint}")
    except FileNotFoundError:
        console.print("[red]No keys found.[/red] Run `hla-compass keys init` first.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed to load keys: {e}[/red]")
        sys.exit(1)
