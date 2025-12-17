"""
Dev loop commands (dev, serve, test, run).
"""

import os
import sys
import json
import click
import subprocess
import uuid
from pathlib import Path
from datetime import datetime, UTC

from rich.panel import Panel

from ..testing import ModuleTester
from ..client import APIClient, APIError
from ..config import Config
from ..auth import Auth
from .utils import console, verbose_option, ensure_docker_available, _ensure_verbose
from .module import build, _write_container_serve_script

@click.group()
def dev_group():
    pass

def _build_default_payload(manifest):
    inputs = manifest.get("inputs", {})
    defaults = {}
    # Simplified defaults
    if isinstance(inputs, dict):
        for k, v in inputs.items():
            if isinstance(v, dict) and "default" in v:
                defaults[k] = v["default"]
    return defaults

def _build_runtime_context(manifest, mode="interactive"):
    return {
        "run_id": f"local-{uuid.uuid4().hex[:8]}",
        "job_id": "local",
        "module_id": manifest.get("name", "dev"),
        "environment": Config.get_environment(),
        "mode": mode,
        "requested_at": datetime.now(UTC).isoformat()
    }

def _run_module_container(
    image=None,
    manifest_path=None,
    payload_path=None,
    context_path=None,
    output_dir=None,
    *,
    image_tag=None,
):
    manifest_path = Path(manifest_path) if manifest_path is not None else None
    payload_path = Path(payload_path) if payload_path is not None else None
    context_path = Path(context_path) if context_path is not None else None
    output_dir = Path(output_dir) if output_dir is not None else None

    if not all([manifest_path, payload_path, context_path, output_dir]):
        raise ValueError(
            "manifest_path, payload_path, context_path, and output_dir are required"
        )

    selected_image = image_tag or image
    if not selected_image:
        raise ValueError("image or image_tag is required")

    if output_dir and output_dir.exists():
        for f in output_dir.iterdir():
            f.unlink()

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{payload_path.resolve()}:/var/input.json:ro",
        "-v",
        f"{context_path.resolve()}:/var/context.json:ro",
        "-v",
        f"{output_dir.resolve()}:/var/dev-out",
        "-v",
        f"{manifest_path.resolve()}:/app/manifest.json:ro",
        "-e",
        "HLA_COMPASS_OUTPUT=/var/dev-out/output.json",
    ]

    auth = Auth()
    api_key = auth.get_api_key()
    if api_key:
        cmd.extend(["-e", f"HLA_API_KEY={api_key}"])
        
    access_token = auth.get_access_token()
    if access_token:
        cmd.extend(["-e", f"HLA_ACCESS_TOKEN={access_token}"])

    cmd.append(selected_image)

    return subprocess.run(cmd).returncode

@click.command()
@verbose_option
@click.option("--mode", default="interactive")
@click.option("--image-tag")
@click.option("--payload", type=click.Path(path_type=Path))
@click.pass_context
def dev(ctx, mode, image_tag, payload):
    """Run module in dev loop"""
    _ensure_verbose(ctx)
    ensure_docker_available()
    
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json missing[/red]")
        return
        
    manifest = json.loads(manifest_path.read_text())
    
    # Build image first
    report = ctx.invoke(build, tag=image_tag, push=False)
    image = report.get("image_tag")
    
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    payload_path = payload or dist_dir / "dev-input.json"
    if not payload:
        payload_path.write_text(json.dumps(_build_default_payload(manifest)), encoding="utf-8")
        
    context_path = dist_dir / "dev-context.json"
    context_path.write_text(json.dumps(_build_runtime_context(manifest, mode)), encoding="utf-8")
    
    output_dir = dist_dir / "dev-output"
    output_dir.mkdir(exist_ok=True)
    
    console.print(f"[cyan]Running {image}...[/cyan]")
    try:
        while True:
            rc = _run_module_container(image, manifest_path, payload_path, context_path, output_dir)
            if (output_dir / "output.json").exists():
                console.print((output_dir / "output.json").read_text())
            input("\nPress Enter to re-run...")
    except KeyboardInterrupt:
        pass

@click.command()
@verbose_option
@click.option("--port", default=8080)
@click.pass_context
def serve(ctx, port):
    """Serve module UI locally"""
    _ensure_verbose(ctx)
    ensure_docker_available()
    
    report = ctx.invoke(build, push=False)
    image = report.get("image_tag")
    
    cmd = ["docker", "run", "--rm", "-p", f"{port}:8080", "--entrypoint", "python", image, "/app/container-serve.py"]
    subprocess.run(cmd)

@click.command()
@verbose_option
@click.option("--docker", is_flag=True)
@click.option("--input", type=click.Path(path_type=Path))
@click.option("--output", type=click.Path(path_type=Path))
@click.option("--json", "json_format", is_flag=True)
@click.pass_context
def test(ctx, docker, input, output, json_format):
    """Run tests"""
    _ensure_verbose(ctx)
    if docker:
        ensure_docker_available()
        manifest_path = Path("manifest.json")
        if not manifest_path.exists():
            console.print("[red]manifest.json missing[/red]")
            sys.exit(1)

        manifest = json.loads(manifest_path.read_text())
        report = ctx.invoke(build, push=False)
        image = report.get("image_tag")

        dist_dir = Path("dist")
        dist_dir.mkdir(exist_ok=True)

        payload_path = input or dist_dir / "test-input.json"
        if not input:
            payload_path.write_text(json.dumps(_build_default_payload(manifest)), encoding="utf-8")

        context_path = dist_dir / "test-context.json"
        context_path.write_text(json.dumps(_build_runtime_context(manifest, mode="test")), encoding="utf-8")

        output_dir = dist_dir / "test-output"
        output_dir.mkdir(exist_ok=True)

        rc = _run_module_container(image, manifest_path, payload_path, context_path, output_dir)
        output_file = output_dir / "output.json"
        if output and output_file.exists():
            output.write_text(output_file.read_text())

        if json_format and output_file.exists():
            console.print(output_file.read_text())
        elif output_file.exists():
            console.print(output_file.read_text())

        if rc != 0:
            sys.exit(rc)
        return

    tester = ModuleTester()
    input_data = {}
    if input and input.exists():
        input_data = json.loads(input.read_text())
        
    try:
        result = tester.test_local("backend/main.py", input_data)
        
        if output:
            output.write_text(json.dumps(result, indent=2))
            
        if json_format:
            console.print(json.dumps(result, indent=2))
        console.print("[green]✓ Test passed[/green]")
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
        sys.exit(1)

@click.command()
@verbose_option
@click.option("--env", type=click.Choice(["dev", "staging", "prod"]), help="Target environment")
@click.option(
    "--parameters",
    type=click.Path(path_type=Path),
    help="Path to JSON file with module parameters",
)
@click.option("--mode", default="interactive", show_default=True, help="Run mode")
@click.option("--compute-profile", help="Compute profile override")
@click.option("--version", help="Module version override")
@click.argument("module_id")
def run(env, parameters, mode, compute_profile, version, module_id):
    """Run remote module"""
    if env:
        Config.set_environment(env)

    payload = {}
    if parameters:
        try:
            payload = json.loads(parameters.read_text(encoding="utf-8"))
        except Exception as e:
            console.print(f"[red]Failed to read parameters file: {e}[/red]")
            sys.exit(1)

    client = APIClient()
    try:
        res = client.start_module_run(
            module_id,
            parameters=payload,
            mode=mode,
            compute_profile=compute_profile,
            version=version,
        )
    except APIError as e:
        status = f"{e.status_code}" if getattr(e, "status_code", None) else "unknown"
        console.print(f"[red]Failed to start module run ({status}): {e}[/red]")
        if getattr(e, "status_code", None) == 401:
            console.print("[dim]Hint: Run `hla-compass auth login` and retry.[/dim]")
        elif getattr(e, "status_code", None) == 403:
            console.print("[dim]Hint: Your user/org may not have permission to start module runs.[/dim]")
        sys.exit(1)

    run_id = None
    if isinstance(res, dict):
        run_id = res.get("runId") or res.get("id") or res.get("run_id")
    console.print(f"[green]✓[/green] Run started: {run_id or res}")
