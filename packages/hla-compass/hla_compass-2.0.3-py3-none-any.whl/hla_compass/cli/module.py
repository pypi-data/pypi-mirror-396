"""
Module lifecycle commands (init, build, publish, validate).
"""

import os
import sys
import json
import shutil
import subprocess
import copy
import mimetypes
import uuid
import time
import click
import importlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, UTC

from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from ..auth import Auth
from ..config import Config
from ..client import APIClient, APIError
from ..env import get_publish_defaults, PublishConfigError
from ..mcp import build_mcp_descriptor
from ..signing import ModuleSigner
from ..validation import ModuleValidator
from .utils import console, verbose_option, ensure_docker_available, _ensure_verbose

@click.group()
def module_group():
    """Group for module commands - usually exposed at root in main.py"""
    pass

def _deprecated_compute_option(ctx, param, value):
    if value:
        if value.lower() != "docker":
            console.print(f"[yellow]⚠️ The `--compute` option is deprecated; ignoring '{value}'.[/yellow]")
        else:
            console.print("[yellow]⚠️ The `--compute` option is deprecated.[/yellow]")

def load_sdk_config():
    try:
        config_path = Config.get_config_path()
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception:
        pass
    return None

ALITHEA_BANNER = """
        [bold bright_magenta]█████╗[/bold bright_magenta] [bold bright_cyan]██╗[/bold bright_cyan]     [bold bright_green]██╗[/bold bright_green][bold bright_yellow]████████╗[/bold bright_yellow][bold bright_red]██╗  ██╗[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta] [bold bright_cyan]█████╗[/bold bright_cyan]
       [bold bright_magenta]██╔══██╗[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]╚══██╔══╝[/bold bright_yellow][bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]██╔════╝[/bold bright_magenta][bold bright_cyan]██╔══██╗[/bold bright_cyan]
       [bold bright_magenta]███████║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]███████║[/bold bright_red][bold bright_magenta]█████╗[/bold bright_magenta]  [bold bright_cyan]███████║[/bold bright_cyan]
       [bold bright_magenta]██╔══██║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██╔══██║[/bold bright_red][bold bright_magenta]██╔══╝[/bold bright_magenta]  [bold bright_cyan]██╔══██║[/bold bright_cyan]
       [bold bright_magenta]██║  ██║[/bold bright_magenta][bold bright_cyan]███████╗[/bold bright_cyan][bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta][bold bright_cyan]██║  ██║[/bold bright_cyan]
       [bold bright_magenta]╚═╝  ╚═╝[/bold bright_magenta][bold bright_cyan]╚══════╝[/bold bright_cyan][bold bright_green]╚═╝[/bold bright_green][bold bright_yellow]   ╚═╝[/bold bright_yellow]   [bold bright_red]╚═╝  ╚═╝[/bold bright_red][bold bright_magenta]╚══════╝[/bold bright_magenta][bold bright_cyan]╚═╝  ╚═╝[/bold bright_cyan]

                  [bold bright_white]🧬  B I O I N F O R M A T I C S  🧬[/bold bright_white]
"""

def show_banner():
    console.print(ALITHEA_BANNER)
    env = Config.get_environment()
    api = Config.get_api_endpoint()
    from .. import __version__
    env_color = {"dev": "green", "staging": "yellow", "prod": "red"}.get(env, "cyan")
    info = (
        f"[bold bright_white]HLA-Compass Platform SDK[/bold bright_white]\n"
        f"[dim white]Version[/dim white] [bold bright_cyan]{__version__}[/bold bright_cyan]   "
        f"[dim white]Environment[/dim white] [bold {env_color}]{env.upper()}[/bold {env_color}]\n"
        f"[dim white]API Endpoint[/dim white] [bright_blue]{api}[/bright_blue]\n"
        f"[bright_magenta]✨[/bright_magenta] [italic]Immuno-Peptidomics • Module Development • AI-Powered Analysis[/italic] [bright_magenta]✨[/bright_magenta]"
    )
    console.print(
        Panel.fit(
            info,
            title="[bold bright_cyan]🔬 Alithea Bio[/bold bright_cyan]",
            subtitle="[bright_blue]https://alithea.bio[/bright_blue]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )

@click.command()
@verbose_option
@click.argument("name", required=False)
@click.option("--template", type=click.Choice(["ui", "no-ui"]), default="no-ui", help="Module template")
@click.option("--interactive", "-i", is_flag=True, help="Use interactive wizard")
@click.option("--compute", hidden=True, callback=_deprecated_compute_option, expose_value=False)
@click.option(
    "--compute-type",
    type=click.Choice(["docker", "fargate"]),
    default="docker",
    help="Compute type (docker maps to Fargate in the platform runtime)",
)
@click.option("--no-banner", is_flag=True, help="Skip banner")
@click.option("--yes", is_flag=True, help="Non-interactive mode")
@click.pass_context
def init(ctx, name, template, interactive, compute_type, no_banner, yes):
    """Create a new HLA-Compass module"""
    _ensure_verbose(ctx)
    if not no_banner:
        show_banner()
    
    if interactive:
        try:
            from ..wizard import run_wizard
            from ..generators import CodeGenerator
        except ImportError:
            console.print("[red]Wizard dependencies missing. Install with pip install 'hla-compass[wizard]'[/red]")
            return
        
        console.print("[bold cyan]🎯 Starting Interactive Module Wizard[/bold cyan]\n")
        config = run_wizard()
        if not config:
            console.print("[yellow]Cancelled[/yellow]")
            return
        
        if name: config['name'] = name
        module_name = config['name']
        module_dir = Path(module_name)
        
        if module_dir.exists() and not yes:
            if not Confirm.ask(f"Directory '{module_name}' exists. Continue?"):
                return
        
        generator = CodeGenerator()
        if generator.generate_module(config, module_dir):
            console.print(f"[green]✓ Module '{module_name}' created successfully![/green]")
        else:
            console.print("[red]Generation failed[/red]")
        return

    if not name:
        console.print("[red]Module name required[/red]")
        return

    # Validate name
    import re
    name_pattern = r"^[a-z0-9]([a-z0-9-]{1,48}[a-z0-9])?$"
    if not re.match(name_pattern, name):
        console.print(f"[red]Invalid module name '{name}'[/red]")
        console.print(f"Name must match regex: {name_pattern}")
        console.print("(Lowercase alphanumeric, hyphens, 2-50 chars, start/end with alphanumeric)")
        return

    module_type = "with-ui" if template == "ui" else "no-ui"
    template_dir_name = f"{template}-template"
    
    # Locate template relative to hla_compass package (parent of this cli package)
    # hla_compass/cli/module.py -> hla_compass/templates
    # We need to go up two levels to sdk/python/hla_compass
    # Or better, use importlib.resources (Python 3.9+) or __file__ relative
    base_path = Path(__file__).parent.parent
    pkg_templates_dir = base_path / "templates" / template_dir_name
    
    if not pkg_templates_dir.exists():
        console.print(f"[red]Template not found at {pkg_templates_dir}[/red]")
        return

    module_dir = Path(name)
    if module_dir.exists() and not yes:
        if not Confirm.ask(f"Directory '{name}' exists. Continue?"): return

    shutil.copytree(pkg_templates_dir, module_dir, dirs_exist_ok=True)
    
    # Update manifest
    manifest_path = module_dir / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    manifest["name"] = name
    manifest["type"] = module_type
    manifest["computeType"] = compute_type
    
    sdk_config = load_sdk_config()
    author_info = sdk_config.get("author", {}) if sdk_config else {}
    
    # Try to get author info from git if not in config
    author_name = author_info.get("name")
    author_email = author_info.get("email")
    
    if not author_name:
        try:
            author_name = subprocess.check_output(["git", "config", "user.name"], text=True).strip()
        except Exception:
            author_name = os.getenv("USER", "Unknown")
            
    if not author_email:
        try:
            author_email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
        except Exception:
            author_email = "developer@example.com"

    manifest["author"]["name"] = author_name
    manifest["author"]["email"] = author_email
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    if module_type == "no-ui":
        shutil.rmtree(module_dir / "frontend", ignore_errors=True)

    # Pin the runtime SDK dependency inside the generated module to match the CLI SDK version.
    # This keeps `hla-compass init` outputs compatible with the CLI used to create them.
    requirements_path = module_dir / "backend" / "requirements.txt"
    if requirements_path.exists():
        try:
            from .._version import __version__ as sdk_version

            lines = requirements_path.read_text(encoding="utf-8").splitlines()
            rewritten: list[str] = []
            replaced = False
            for line in lines:
                stripped = line.strip()
                if stripped in {"hla-compass", "hla_compass"} or stripped.startswith("hla-compass==") or stripped.startswith("hla-compass>="):
                    rewritten.append(f"hla-compass=={sdk_version}")
                    replaced = True
                else:
                    rewritten.append(line)

            if not replaced:
                rewritten.insert(0, f"hla-compass=={sdk_version}")

            requirements_path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")
        except Exception as e:
            console.print(f"[yellow]Warning: failed to pin hla-compass dependency in requirements.txt: {e}[/yellow]")

    console.print(f"[green]✓ Module '{name}' created![/green]")


def _author_email(module: Dict[str, Any]) -> Optional[str]:
    author = module.get("author") or {}
    return (
        author.get("email")
        or module.get("authorEmail")
        or module.get("createdByEmail")
        or module.get("ownerEmail")
    )


def _status_value(module: Dict[str, Any], *, key: str) -> Optional[str]:
    # Normalize status fields from different payload shapes
    if key == "state":
        return module.get("state") or module.get("status") or module.get("publishStatus")
    if key == "validation":
        val = module.get("validation") or {}
        return val.get("status") or module.get("validationStatus")
    return None


def _validation_note(module: Dict[str, Any]) -> Optional[str]:
    val = module.get("validation") or {}
    note = val.get("error") or val.get("message")
    return note


SUPPORTED_COMPUTE_TYPES = {"docker", "fargate"}


def _require_supported_compute(manifest: Dict[str, Any]) -> None:
    ctype = manifest.get("computeType") or "docker"
    if ctype not in SUPPORTED_COMPUTE_TYPES:
        console.print(f"[red]Compute type '{ctype}' is not supported by the CLI yet.[/red]")
        console.print(f"Supported: {', '.join(sorted(SUPPORTED_COMPUTE_TYPES))}")
        sys.exit(1)


def _normalize_compute_for_api(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map CLI-friendly compute values to backend-accepted values.

    The platform currently expects fargate for container modules; if the manifest
    uses docker we map it to fargate before submission.
    """
    mapped = dict(manifest)
    if mapped.get("computeType") == "docker":
        mapped["computeType"] = "fargate"
        console.print("[dim]Mapped computeType 'docker' -> 'fargate' for platform compatibility.[/dim]")
    return mapped


@click.command()
@verbose_option
@click.option("--env", type=click.Choice(["dev", "staging", "prod"]), help="Target environment")
@click.option("--all", "show_all", is_flag=True, help="Show all modules (skip author filter)")
def list_modules(env: Optional[str], show_all: bool):
    """List modules for the current author with publish/validation status."""
    if env:
        Config.set_environment(env)

    client = APIClient()
    try:
        user = client.get_current_user() or {}
        current_email = (
            user.get("email")
            or (user.get("user") or {}).get("email")
            or (user.get("data") or {}).get("email")
        )
    except Exception:
        current_email = None

    try:
        modules = client.list_modules()
    except Exception as e:
        console.print(f"[red]Failed to list modules: {e}[/red]")
        sys.exit(1)

    # Filter to current author unless --all
    if not show_all and current_email:
        modules = [m for m in modules if _author_email(m) == current_email]

    if not modules:
        scope = "all authors" if show_all else "current author"
        console.print(f"[yellow]No modules found for {scope}.[/yellow]")
        return

    table = Table(title="Modules", show_lines=False)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", style="magenta")
    table.add_column("State", style="green")
    table.add_column("Validation", style="yellow")
    table.add_column("Author", style="white")
    table.add_column("Updated", style="dim")

    for module in modules:
        name = module.get("name") or module.get("id") or "-"
        version = module.get("version") or module.get("moduleVersion") or "-"
        state = _status_value(module, key="state") or "unknown"
        validation = _status_value(module, key="validation") or "-"
        validation_note = _validation_note(module)
        if validation_note:
            validation = f"{validation} (error)"
        author_email = _author_email(module) or "-"
        updated = (
            module.get("updatedAt")
            or module.get("lastUpdated")
            or module.get("createdAt")
            or "-"
        )

        table.add_row(str(name), str(version), str(state), str(validation), str(author_email), str(updated))

    console.print(table)

@click.command()
@verbose_option
@click.option("--tag", help="Docker image tag")
@click.option("--registry", help="Registry prefix")
@click.option("--push", is_flag=True, help="Push image")
@click.option("--platform", multiple=True, help="Target platforms")
@click.option("--no-cache", is_flag=True, help="Disable cache")
@click.option("--no-sign", is_flag=True, help="Deprecated")
@click.option("--local-sdk", type=click.Path(exists=True), help="Path to local SDK wheel for development")
@click.pass_context
def build(ctx, tag, registry, push, platform, no_cache, no_sign, local_sdk):
    """Build module container"""
    _ensure_verbose(ctx)
    ensure_docker_available()
    
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found[/red]")
        sys.exit(1)
    
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require_supported_compute(manifest)
    module_name = manifest.get("name", "module")
    version = manifest.get("version", "0.0.0")
    
    # Default tag logic
    def _sanitize(v): return "".join(c if c.isalnum() or c in "-_." else "-" for c in v.lower()).strip("-.")
    default_tag = f"{_sanitize(module_name)}:{_sanitize(version)}"
    image_tag = tag or default_tag
    
    local_tag = image_tag
    registry_tag = None
    if registry:
        registry = registry.rstrip("/")
        # Check if the registry string already contains the repository name (common in this platform)
        # If so, we should use tags to distinguish modules instead of sub-repositories
        if "/" not in image_tag.split(":")[0]:
            # Convert "module:version" to "module-version" for the tag
            # This ensures we push to the single 'registry' repo with a unique tag
            # Ensure the tag is sanitized to prevent confusion with registry separators
            safe_tag = image_tag.replace("/", "-") 
            tag_suffix = safe_tag.replace(":", "-")
            registry_tag = f"{registry}:{tag_suffix}"
        else:
            # If image_tag already has a slash, assume user knows what they are doing (custom full path)
            registry_tag = image_tag
            local_tag = image_tag # Use full reference locally too if provided

    # NOTE: The suffix replacement logic above (replacing ':' with '-') is crucial for 
    # maintaining a clean repository structure where all module versions are stored 
    # as tags within a single repository per module, rather than creating separate 
    # repositories for each version. This simplifies ECR management and access control.

    dist_dir = Path("dist")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Helper to write container-serve.py
    _write_container_serve_script(dist_dir)
    
    mcp_dir = dist_dir / "mcp"
    descriptor_path = build_mcp_descriptor(manifest, mcp_dir)
    
    # Handle local SDK wheel
    sdk_wheel_name = None
    if local_sdk:
        wheel_path = Path(local_sdk)
        sdk_wheel_name = wheel_path.name
        shutil.copy(wheel_path, dist_dir / sdk_wheel_name)
        console.print(f"[yellow]Using local SDK wheel: {sdk_wheel_name}[/yellow]")

    dockerfile_path = dist_dir / "Dockerfile.hla"
    dockerfile_path.write_text(_generate_dockerfile_content(manifest, descriptor_path, sdk_wheel_name), encoding="utf-8")
    
    console.print(f"[cyan]Building {local_tag}...[/cyan]")
    cmd = ["docker", "build", "-f", str(dockerfile_path), "-t", local_tag, "."]
    if no_cache: cmd.append("--no-cache")
    subprocess.run(cmd, check=True)
    
    published_tag = local_tag
    if registry_tag:
        subprocess.run(["docker", "tag", local_tag, registry_tag], check=True)
        published_tag = registry_tag
    
    if push:
        # Authenticate to ECR if pushing to an ECR registry
        if registry_tag and ".dkr.ecr." in registry_tag and ".amazonaws.com" in registry_tag:
            _ecr_docker_login(registry_tag)
        console.print(f"[cyan]Pushing {published_tag}...[/cyan]")
        try:
            subprocess.run(["docker", "push", published_tag], check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to push image: {e}[/red]")
            if "denied" in str(e) or "unauthorized" in str(e) or "forbidden" in str(e).lower():
                console.print("[yellow]Tip: Check your permissions. You might need to run:[/yellow]")
                console.print(f"  docker login {published_tag.split('/')[0]}")
            raise e
        
    # Report
    report = {
        "image_tag": local_tag,
        "published_tag": published_tag,
        "pushed": push,
        "descriptor": str(descriptor_path)
    }
    (dist_dir / "build.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    return report

def _ecr_docker_login(registry_tag: str):
    """Authenticate Docker to ECR registry using AWS credentials."""
    import re
    # Extract registry URL (everything before the first /)
    match = re.match(r'^([^/]+)', registry_tag)
    if not match:
        return
    registry_url = match.group(1)
    
    # Extract region from registry URL (format: account.dkr.ecr.region.amazonaws.com)
    region_match = re.search(r'\.dkr\.ecr\.([^.]+)\.amazonaws\.com', registry_url)
    if not region_match:
        console.print("[yellow]Warning: Could not determine ECR region[/yellow]")
        return
    region = region_match.group(1)
    
    console.print(f"[dim]Authenticating to ECR in {region}...[/dim]")
    console.print(f"[dim]Authenticating to ECR in {region}...[/dim]")
    try:
        # Use boto3 to get the login password securely
        # This avoids piping the password through a shell command
        import boto3
        import base64
        
        session = boto3.Session(region_name=region)
        ecr_client = session.client('ecr')
        
        # Get authorization token
        response = ecr_client.get_authorization_token()
        auth_data = response['authorizationData'][0]
        token = auth_data['authorizationToken']
        
        # Decode the token (it's base64 encoded user:password)
        decoded_token = base64.b64decode(token).decode('utf-8')
        username, password = decoded_token.split(':')
        
        # Login to Docker
        # We still use subprocess for docker login, but we pass the password via stdin directly from python variable
        # without it ever being a command line argument or visible in process list as an argument
        login_result = subprocess.run(
            ["docker", "login", "--username", username, "--password-stdin", registry_url],
            input=password,
            capture_output=True,
            text=True
        )
        
        if login_result.returncode != 0:
            console.print(f"[yellow]Warning: Docker ECR login failed: {login_result.stderr}[/yellow]")
        else:
            console.print("[dim]ECR authentication successful[/dim]")
            
    except ImportError:
        console.print("[yellow]Warning: boto3 not found. Please install hla-compass[dev] or boto3.[/yellow]")
    except Exception as e:
        # SAFEGUARD: Do not log the exception message if it might contain the password, 
        # but boto3 exceptions usually don't contain the token.
        console.print(f"[yellow]Warning: ECR authentication failed: {str(e)}[/yellow]")


# Helper functions for build
def _write_container_serve_script(dist_dir: Path):
    # (Same content as original cli.py)
    script = r'''#!/usr/bin/env python3
import os
import json
import importlib
from pathlib import Path
from aiohttp import web

MODULE_ENTRY = os.getenv("HLA_COMPASS_MODULE", None)
MANIFEST_PATH = Path("/app/manifest.json")

def _resolve_module(entry: str):
    if ":" not in entry: return None
    mod, cls = entry.split(":", 1)
    m = importlib.import_module(mod)
    return getattr(m, cls)()

def _load_manifest():
    try: return json.loads(MANIFEST_PATH.read_text())
    except: return {}

def _locate_ui_dist():
    candidates = [Path("/app/ui/dist"), Path("/app/frontend/dist")]
    for p in candidates:
        if p.exists(): return p
    return None

async def handle_execute(request):
    try: payload = await request.json()
    except: payload = {}
    input_data = payload.get("input", {})
    context = {"mode": "interactive", "run_id": "serve-dev"}
    try:
        mod = request.app["module"]
        res = mod.run(input_data, context)
        return web.json_response(res)
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_index(request):
    return web.Response(text="<html><body><div id='root'></div><script src='/bundle.js'></script></body></html>", content_type="text/html")

async def handle_static(request):
    root = request.app.get("ui_root")
    if not root: return web.Response(text="No UI", content_type="text/html")
    path = request.match_info.get("path", "")
    f = root / path
    if f.is_file(): return web.FileResponse(f)
    return await handle_index(request)

def main():
    app = web.Application()
    manifest = _load_manifest()
    entry = MODULE_ENTRY or manifest.get("execution", {}).get("entrypoint") or "backend.main:Module"
    app["module"] = _resolve_module(entry)
    app["ui_root"] = _locate_ui_dist()
    app.router.add_post("/api/execute", handle_execute)
    app.router.add_get("/", handle_index)
    app.router.add_get("/{path:.*}", handle_static)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
'''
    (dist_dir / "container-serve.py").write_text(script, encoding="utf-8")

def _generate_dockerfile_content(manifest, descriptor_path, sdk_wheel_name=None):
    entry = manifest.get("execution", {}).get("entrypoint") or "backend.main:Module"
    
    lines = ["# syntax=docker/dockerfile:1"]
    
    has_frontend = Path("frontend/package.json").exists()
    if has_frontend:
        lines.extend([
            "FROM node:20.11.0-alpine AS ui",
            "WORKDIR /ui",
            "COPY frontend/package*.json ./",
            "RUN npm install --legacy-peer-deps",
            "COPY frontend/ ./",
            "RUN npm run build"
        ])
        
    lines.extend([
        "FROM python:3.11.7-slim",
        "WORKDIR /app",
    ])

    if sdk_wheel_name:
        lines.extend([
            f"COPY dist/{sdk_wheel_name} /tmp/{sdk_wheel_name}",
            f"RUN pip install --no-cache-dir /tmp/{sdk_wheel_name}"
        ])
    else:
        from .._version import __version__ as sdk_version
        lines.append(f"RUN pip install --no-cache-dir hla-compass=={sdk_version}")

    # Use the full relative path from build context (module root)
    # descriptor_path is like dist/mcp/tool.json
    descriptor_rel = str(descriptor_path)
    lines.extend([
        "COPY manifest.json /app/manifest.json",
        f"COPY {descriptor_rel} /app/mcp/tool.json"
    ])
    
    if Path("backend/requirements.txt").exists():
        lock_path = Path("backend/requirements.lock.txt")
        if lock_path.exists():
            lines.append("COPY backend/requirements.lock.txt /tmp/reqs.lock.txt")
            lines.append("RUN pip install --require-hashes -r /tmp/reqs.lock.txt")
        else:
            lines.append("COPY backend/requirements.txt /tmp/reqs.txt")
            lines.append("RUN pip install -r /tmp/reqs.txt")
        
    lines.append("COPY backend/ /app/backend/")
    
    if has_frontend:
        lines.extend([
            "RUN mkdir -p /app/ui",
            "COPY --from=ui /ui/dist /app/ui/dist"
        ])
        
    lines.extend([
        "ENV PYTHONPATH=/app",
        f"ENV HLA_COMPASS_MODULE={entry}",
        "COPY dist/container-serve.py /app/container-serve.py",
        "EXPOSE 8080",
        'ENTRYPOINT ["module-runner"]'
    ])
    
    return "\n".join(lines)

@click.command()
@verbose_option
@click.option("--env", required=True, type=click.Choice(["dev", "staging", "prod"]))
@click.option("--image-ref", help="Image reference")
@click.option("--registry", help="Registry override")
@click.option(
    "--scope",
    type=click.Choice(["org", "public"]),
    default="org",
    help="Module scope: 'org' (auto-approved, org-only) or 'public' (needs approval)"
)
@click.option("--visibility", hidden=True, help="Deprecated alias for --scope")
@click.option("--no-sign", is_flag=True)
@click.option("--generate-keys", is_flag=True, help="Auto-generate signing keys if missing")
@click.pass_context
def publish(ctx, env, image_ref, registry, scope, visibility, no_sign, generate_keys):
    """Publish module to the HLA-Compass platform.
    
    Scope determines approval workflow:
    - org: Auto-approved, only your organization can use it
    - public: Requires superuser approval before others can use it
    """
    _ensure_verbose(ctx)
    Config.set_environment(env)
    
    # Handle deprecated visibility flag
    if visibility:
        console.print("[yellow]⚠️ The '--visibility' option is deprecated; please use '--scope' instead.[/yellow]")
        # If scope is default ("org") but visibility is set, map visibility to scope
        # We check if scope was explicitly provided to avoid overwriting it
        if ctx.get_parameter_source("scope").name == "DEFAULT":
            if visibility.lower() in ("private", "org"):
                scope = "org"
            elif visibility.lower() == "public":
                scope = "public"
    
    auth = Auth()
    if not auth.is_authenticated():
        console.print("[red]Not authenticated[/red]")
        sys.exit(1)
    
    # Fetch registry from API if not provided
    if not registry:
        try:
            publish_config = get_publish_defaults(env)
            registry = publish_config.get("registry")
            if registry:
                console.print(f"[dim]Using registry: {registry}[/dim]")
        except PublishConfigError as e:
            console.print(f"[yellow]Warning: Could not fetch publish config: {e}[/yellow]")
        
    if not image_ref:
        # Build first
        report = ctx.invoke(build, push=True, registry=registry)
        image_ref = report.get("published_tag")
        
    client = APIClient()
    
    manifest = json.loads(Path("manifest.json").read_text())
    _require_supported_compute(manifest)
    
    # Map computeType for backend compatibility (docker -> fargate)
    # Sign the exact payload we submit to avoid signature mismatch.
    manifest_for_api = _normalize_compute_for_api(manifest)

    if not no_sign:
        signer = ModuleSigner()
        try:
            manifest_for_api["signature"] = signer.sign_manifest(manifest_for_api)
            manifest_for_api["publicKey"] = signer.get_public_key_string()
            manifest_for_api["keyFingerprint"] = signer.get_key_fingerprint()
            manifest_for_api["signatureAlgorithm"] = signer.ALGORITHM
            manifest_for_api["hashAlgorithm"] = signer.HASH_ALGORITHM
        except FileNotFoundError:
            if generate_keys:
                console.print("[yellow]Signing keys not found. Generating new keys...[/yellow]")
                signer.generate_keys()
                manifest_for_api["signature"] = signer.sign_manifest(manifest_for_api)
                manifest_for_api["publicKey"] = signer.get_public_key_string()
                manifest_for_api["keyFingerprint"] = signer.get_key_fingerprint()
                manifest_for_api["signatureAlgorithm"] = signer.ALGORITHM
                manifest_for_api["hashAlgorithm"] = signer.HASH_ALGORITHM
            else:
                console.print("[red]Signing keys not found.[/red]")
                console.print("Run `hla-compass keys init` or re-run publish with --generate-keys.")
                sys.exit(1)
        
    payload = {
        "imageRef": image_ref,
        "manifest": manifest_for_api,
        "scope": scope
    }
    
    try:
        result = client.register_container_module(payload)
    except APIError as e:
        status = f"{e.status_code}" if getattr(e, "status_code", None) else "unknown"
        console.print(f"[red]Publish failed ({status}): {e}[/red]")
        if getattr(e, "status_code", None) == 401:
            console.print("[dim]Hint: Run `hla-compass auth login --env {env}` and retry.[/dim]".format(env=env))
        elif getattr(e, "status_code", None) == 403:
            console.print("[dim]Hint: Ensure your account/org has permission to publish modules in this environment.[/dim]")
        sys.exit(1)

    publish_id = result.get("publishId") if isinstance(result, dict) else None
    if publish_id:
        console.print(f"[dim]Publish job: {publish_id}[/dim]")
    
    # Display result based on module state
    state = result.get("state") if isinstance(result, dict) else None
    if state == "SUBMITTED":
        console.print(f"[yellow]✓ Module submitted for approval (scope: public)[/yellow]")
        console.print("[dim]A superuser must approve before it's publicly available[/dim]")
    elif state == "APPROVED":
        console.print(f"[green]✓ Module published and approved (scope: {scope})[/green]")
    else:
        console.print(f"[green]✓ Module published to {env}[/green]")

@click.command(name="publish-status")
@verbose_option
@click.option("--env", type=click.Choice(["dev", "staging", "prod"]), help="Target environment")
@click.option("--watch", is_flag=True, help="Poll until the publish job completes")
@click.option("--timeout", type=int, default=900, show_default=True, help="Max seconds to wait when --watch is set")
@click.option("--interval", type=int, default=10, show_default=True, help="Poll interval seconds when --watch is set")
@click.argument("publish_id")
def publish_status(env: Optional[str], watch: bool, timeout: int, interval: int, publish_id: str):
    """Show (and optionally watch) module publish intake status."""
    if env:
        Config.set_environment(env)

    client = APIClient()
    deadline = time.time() + max(timeout, 30)

    def _render(status_payload: Dict[str, Any]) -> Table:
        table = Table(title="Publish Status", show_lines=False)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        for key in (
            "publishId",
            "status",
            "buildStatus",
            "currentPhase",
            "failureReason",
            "startTime",
            "endTime",
            "message",
            "logsUrl",
        ):
            if key in status_payload and status_payload.get(key) is not None:
                table.add_row(key, str(status_payload.get(key)))
        return table

    last_payload: Optional[Dict[str, Any]] = None

    def _fetch() -> Dict[str, Any]:
        return client.get_module_publish_status(publish_id)

    try:
        if not watch:
            payload = _fetch()
            console.print(_render(payload))
            return

        with Live(console=console, refresh_per_second=4) as live:
            while True:
                payload = _fetch()
                last_payload = payload
                live.update(_render(payload))

                normalized = (payload.get("status") or "").lower()
                if normalized in {"completed", "failed", "cancelled"}:
                    break
                if time.time() >= deadline:
                    raise click.ClickException(f"Timed out waiting for publish job {publish_id}")
                time.sleep(max(interval, 1))

        normalized = ((last_payload or {}).get("status") or "").lower()
        if normalized == "failed":
            reason = (last_payload or {}).get("failureReason") or (last_payload or {}).get("message")
            if reason:
                raise click.ClickException(f"Publish job failed: {publish_id} ({reason})")
            raise click.ClickException(f"Publish job failed: {publish_id}")
    except APIError as e:
        raise click.ClickException(str(e))

@click.command()
@verbose_option
@click.option("--manifest", default="manifest.json")
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.option("--strict", is_flag=True, help="Fail on warnings")
def validate(manifest, format, strict):
    """Validate manifest"""
    validator = ModuleValidator(manifest_path=manifest)
    res = validator.run(strict=strict)
    
    if format == "json":
        output = {
            "valid": res.valid,
            "issues": [{"code": i.code, "message": i.message} for i in res.issues]
        }
        click.echo(json.dumps(output))
    else:
        if res.valid:
            console.print("[green]✓ Valid[/green]")
        else:
            console.print("[red]✗ Invalid[/red]")
            for issue in res.issues:
                console.print(f"{issue.code}: {issue.message}")
    
    if not res.valid:
        sys.exit(1)
        
    if strict and res.issues:
        sys.exit(1)

@click.command()
@verbose_option
@click.option("--json", "json_format", is_flag=True, help="Output JSON")
def preflight(json_format):
    """Run preflight checks"""
    validator = ModuleValidator(manifest_path="manifest.json")
    res = validator.run()
    
    if json_format:
        output = {
            "valid": res.valid,
            "issues": [{"code": i.code, "message": i.message} for i in res.issues]
        }
        click.echo(json.dumps(output))
    else:
        if res.valid:
            console.print("[green]✓ Preflight passed[/green]")
        else:
            console.print("[red]✗ Preflight failed[/red]")
            for issue in res.issues:
                console.print(f"{issue.code}: {issue.message}")

    if not res.valid:
        sys.exit(1)
