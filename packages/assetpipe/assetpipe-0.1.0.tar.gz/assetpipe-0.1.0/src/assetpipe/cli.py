"""
AssetPipe CLI - Main entry point
"""

import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint

from assetpipe.core.asset import Asset, AssetType
from assetpipe.core.pipeline import Pipeline
from assetpipe.core.config import load_config, save_config, PipelineConfig, get_default_config, DEFAULT_CONFIGS
from assetpipe.converters import get_converter, list_converters
from assetpipe.validators import validate_asset, list_rules
from assetpipe.optimizers import optimize_asset
from assetpipe.utils.reporting import generate_report

app = typer.Typer(
    name="assetpipe",
    help="🔧 Universal Asset Pipeline CLI - Convert, optimize, and validate 3D/2D assets",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


class OutputFormat(str, Enum):
    gltf = "gltf"
    glb = "glb"
    obj = "obj"
    usd = "usd"
    fbx = "fbx"


class ReportFormat(str, Enum):
    html = "html"
    json = "json"
    markdown = "markdown"


def version_callback(value: bool):
    if value:
        from assetpipe import __version__
        rprint(f"[bold blue]AssetPipe[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    🔧 AssetPipe - Universal Asset Pipeline CLI
    
    Convert, optimize, and validate 3D/2D assets across formats.
    """
    pass


@app.command()
def convert(
    input_path: Path = typer.Argument(..., help="Input file path", exists=True),
    to: OutputFormat = typer.Option(..., "--to", "-t", help="Output format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    optimize: bool = typer.Option(False, "--optimize", help="Optimize the output"),
    validate: bool = typer.Option(False, "--validate", help="Validate before conversion"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """
    Convert a single asset to another format.
    
    Examples:
        assetpipe convert model.fbx --to gltf
        assetpipe convert model.obj --to glb --optimize
    """
    console.print(Panel.fit(
        f"[bold]Converting[/bold] {input_path.name} → [green]{to.value}[/green]",
        title="🔄 AssetPipe Convert"
    ))
    
    try:
        # Load asset
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading asset...", total=None)
            asset = Asset.load(input_path)
            progress.update(task, description="[green]✓[/green] Asset loaded")
            
            # Validate if requested
            if validate:
                progress.update(task, description="Validating...")
                results = validate_asset(asset)
                if results.has_errors:
                    progress.update(task, description="[red]✗[/red] Validation failed")
                    for error in results.errors:
                        console.print(f"  [red]•[/red] {error}")
                    raise typer.Exit(1)
                progress.update(task, description="[green]✓[/green] Validation passed")
            
            # Optimize if requested
            if optimize:
                progress.update(task, description="Optimizing...")
                asset = optimize_asset(asset)
                progress.update(task, description="[green]✓[/green] Optimized")
            
            # Convert
            progress.update(task, description="Converting...")
            converter = get_converter(asset.type, to.value)
            
            # Determine output path
            if output is None:
                output = input_path.with_suffix(f".{to.value}")
            
            converter.convert(asset, output)
            progress.update(task, description="[green]✓[/green] Conversion complete")
        
        console.print(f"\n[green]✓[/green] Output saved to: [bold]{output}[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def preset(
    name: Optional[str] = typer.Argument(None, help="Preset name to use or save"),
    save: bool = typer.Option(False, "--save", "-s", help="Save current options as preset"),
    list_presets: bool = typer.Option(False, "--list", "-l", help="List available presets"),
    output_format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format for preset"),
    rules: Optional[str] = typer.Option(None, "--rules", "-r", help="Validation rules for preset"),
):
    """
    Manage pipeline presets for quick reuse.
    
    Examples:
        assetpipe preset --list
        assetpipe preset game_ready
        assetpipe preset my_pipeline --save --format glb --rules strict
    """
    preset_file = Path.home() / ".assetpipe" / "presets.yaml"
    preset_file.parent.mkdir(exist_ok=True)
    
    if list_presets:
        console.print(Panel.fit("[bold]Available Presets[/bold]", title="📋 Presets"))
        
        # Built-in presets
        console.print("\n[cyan]Built-in:[/cyan]")
        for preset_name in DEFAULT_CONFIGS:
            console.print(f"  • {preset_name}")
        
        # User presets
        if preset_file.exists():
            import yaml
            with open(preset_file) as f:
                user_presets = yaml.safe_load(f) or {}
            if user_presets:
                console.print("\n[green]User-defined:[/green]")
                for preset_name in user_presets:
                    console.print(f"  • {preset_name}")
        
        console.print("\n[dim]Tip: Use 'assetpipe batch ./assets --config <preset>' to apply[/dim]")
        return
    
    if save:
        import yaml
        # Load existing or create new
        presets = {}
        if preset_file.exists():
            with open(preset_file) as f:
                presets = yaml.safe_load(f) or {}
        
        presets[name] = {
            "format": output_format or "gltf",
            "rules": rules or "standard",
        }
        
        with open(preset_file, 'w') as f:
            yaml.dump(presets, f)
        
        console.print(f"[green]✓[/green] Saved preset '[bold]{name}[/bold]' to {preset_file}")
        return
    
    # Show preset details
    if name is None:
        console.print("[yellow]Please specify a preset name or use --list[/yellow]")
        return
    
    if name in DEFAULT_CONFIGS:
        config = get_default_config(name)
        console.print(Panel.fit(f"[bold]{name}[/bold] (built-in)", title="📋 Preset"))
        console.print(f"  Format: {config.output.format}")
        console.print(f"  Rules: {config.validation.rules}")
    else:
        console.print(f"[yellow]Unknown preset: {name}[/yellow]")
        console.print("[dim]Use --list to see available presets[/dim]")


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., help="Input directory", exists=True),
    config: Path = typer.Option(..., "--config", "-c", help="Pipeline config file", exists=True),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    parallel: int = typer.Option(4, "--parallel", "-p", help="Number of parallel workers"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be processed"),
    report: bool = typer.Option(True, "--report/--no-report", help="Auto-generate HTML report after processing"),
):
    """
    Batch process multiple assets using a pipeline config.
    
    Examples:
        assetpipe batch ./assets --config pipeline.yaml
        assetpipe batch ./models --config prod.yaml --parallel 8
    """
    console.print(Panel.fit(
        f"[bold]Batch Processing[/bold] {input_dir}",
        title="📦 AssetPipe Batch"
    ))
    
    try:
        # Load config
        pipeline_config = load_config(config)
        
        # Create pipeline
        pipeline = Pipeline(pipeline_config)
        
        # Find assets
        assets = pipeline.discover_assets(input_dir)
        
        if not assets:
            console.print("[yellow]No assets found matching config filters[/yellow]")
            raise typer.Exit(0)
        
        console.print(f"Found [bold]{len(assets)}[/bold] assets to process\n")
        
        if dry_run:
            table = Table(title="Assets to Process")
            table.add_column("File", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Size", style="yellow")
            
            for asset_path in assets:
                size = asset_path.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
                table.add_row(asset_path.name, asset_path.suffix[1:].upper(), size_str)
            
            console.print(table)
            raise typer.Exit(0)
        
        # Process assets
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Processing...", total=len(assets))
            
            results = pipeline.process_batch(
                assets,
                output_dir=output_dir,
                parallel=parallel,
                progress_callback=lambda: progress.advance(task)
            )
        
        # Summary
        console.print(f"\n[green]✓[/green] Processed: [bold]{results.success_count}[/bold]")
        if results.error_count > 0:
            console.print(f"[red]✗[/red] Failed: [bold]{results.error_count}[/bold]")
            for error in results.errors:
                console.print(f"  [red]•[/red] {error}")
        
        # Auto-generate report
        if report and not dry_run:
            report_dir = output_dir or input_dir
            report_path = report_dir / "assetpipe_report.html"
            try:
                generate_report(report_dir, report_path, format="html")
                console.print(f"\n[blue]📊[/blue] Report saved: [bold]{report_path}[/bold]")
            except Exception as report_err:
                console.print(f"[yellow]Warning:[/yellow] Could not generate report: {report_err}")
        
    except FileNotFoundError as e:
        console.print(f"\n[red]Error:[/red] File not found: {e}")
        console.print("[dim]Tip: Check that the config file path is correct[/dim]")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"\n[red]Error:[/red] Invalid configuration: {e}")
        console.print("[dim]Tip: Validate your YAML config with 'assetpipe validate --config <file>'[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("[dim]Tip: Run with --dry-run to preview what will be processed[/dim]")
        raise typer.Exit(1)


@app.command()
def watch(
    input_dir: Path = typer.Argument(..., help="Directory to watch", exists=True),
    config: Path = typer.Option(..., "--config", "-c", help="Pipeline config file", exists=True),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """
    Watch a directory and automatically process new assets.
    
    Examples:
        assetpipe watch ./incoming --config pipeline.yaml
    """
    console.print(Panel.fit(
        f"[bold]Watching[/bold] {input_dir}",
        title="👁️ AssetPipe Watch"
    ))
    
    try:
        from assetpipe.core.watcher import AssetWatcher
        
        pipeline_config = load_config(config)
        watcher = AssetWatcher(pipeline_config, input_dir, output_dir)
        
        console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")
        watcher.start()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped watching[/yellow]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    input_path: Path = typer.Argument(..., help="File or directory to validate", exists=True),
    rules: Optional[str] = typer.Option(None, "--rules", "-r", help="Rule set: strict, standard, minimal"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file with custom rules"),
    fail_on_error: bool = typer.Option(False, "--fail-on-error", help="Exit with code 1 on validation errors"),
):
    """
    Validate assets against rules.
    
    Examples:
        assetpipe validate model.fbx --rules strict
        assetpipe validate ./assets --config pipeline.yaml
    """
    console.print(Panel.fit(
        f"[bold]Validating[/bold] {input_path}",
        title="✅ AssetPipe Validate"
    ))
    
    try:
        # Collect files
        if input_path.is_file():
            files = [input_path]
        else:
            files = list(input_path.rglob("*"))
            files = [f for f in files if f.is_file() and f.suffix.lower() in ['.fbx', '.obj', '.gltf', '.glb']]
        
        if not files:
            console.print("[yellow]No supported assets found[/yellow]")
            raise typer.Exit(0)
        
        total_errors = 0
        total_warnings = 0
        
        for file_path in files:
            asset = Asset.load(file_path)
            # Convert rules string to list for validate_asset
            rules_list = [rules] if rules else None
            results = validate_asset(asset, rules=rules_list)
            
            status = "[green]✓[/green]" if not results.has_errors else "[red]✗[/red]"
            console.print(f"{status} {file_path.name}")
            
            for error in results.errors:
                console.print(f"    [red]ERROR:[/red] {error}")
                total_errors += 1
            
            for warning in results.warnings:
                console.print(f"    [yellow]WARN:[/yellow] {warning}")
                total_warnings += 1
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold] {len(files)} files, {total_errors} errors, {total_warnings} warnings")
        
        if fail_on_error and total_errors > 0:
            raise typer.Exit(1)
            
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def info(
    input_path: Path = typer.Argument(..., help="Asset file path", exists=True),
):
    """
    Show detailed information about an asset.
    
    Examples:
        assetpipe info model.fbx
    """
    try:
        asset = Asset.load(input_path)
        
        console.print(Panel.fit(
            f"[bold]{input_path.name}[/bold]",
            title="📄 Asset Info"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Type", asset.type.value)
        table.add_row("Format", input_path.suffix[1:].upper())
        table.add_row("Size", f"{input_path.stat().st_size / 1024:.1f} KB")
        
        if asset.mesh_data:
            table.add_row("", "")
            table.add_row("[bold]Mesh Data[/bold]", "")
            table.add_row("  Vertices", f"{asset.mesh_data.vertex_count:,}")
            table.add_row("  Triangles", f"{asset.mesh_data.triangle_count:,}")
            table.add_row("  Has UVs", "Yes" if asset.mesh_data.has_uvs else "No")
            table.add_row("  Has Normals", "Yes" if asset.mesh_data.has_normals else "No")
        
        if asset.materials:
            table.add_row("", "")
            table.add_row("[bold]Materials[/bold]", f"{len(asset.materials)}")
            for mat in asset.materials[:5]:
                table.add_row(f"  • {mat.name}", "")
            if len(asset.materials) > 5:
                table.add_row(f"  ... and {len(asset.materials) - 5} more", "")
        
        if asset.textures:
            table.add_row("", "")
            table.add_row("[bold]Textures[/bold]", f"{len(asset.textures)}")
            for tex in asset.textures[:5]:
                table.add_row(f"  • {tex.name}", tex.resolution or "")
            if len(asset.textures) > 5:
                table.add_row(f"  ... and {len(asset.textures) - 5} more", "")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def report(
    input_dir: Path = typer.Argument(..., help="Directory to analyze", exists=True),
    output: Path = typer.Option("report.html", "--output", "-o", help="Output report file"),
    format: ReportFormat = typer.Option(ReportFormat.html, "--format", "-f", help="Report format"),
):
    """
    Generate a detailed report of assets in a directory.
    
    Examples:
        assetpipe report ./assets --output report.html
        assetpipe report ./models --format json
    """
    console.print(Panel.fit(
        f"[bold]Generating Report[/bold] for {input_dir}",
        title="📊 AssetPipe Report"
    ))
    
    try:
        report_path = generate_report(input_dir, output, format.value)
        console.print(f"\n[green]✓[/green] Report saved to: [bold]{report_path}[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def optimize(
    input_path: Path = typer.Argument(..., help="Asset file path", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    decimate: Optional[float] = typer.Option(None, "--decimate", "-d", help="Decimate ratio (0.0-1.0)"),
    texture_size: Optional[int] = typer.Option(None, "--texture-size", help="Max texture size"),
    generate_lods: bool = typer.Option(False, "--lods", help="Generate LOD levels"),
):
    """
    Optimize an asset (mesh decimation, texture compression, etc.)
    
    Examples:
        assetpipe optimize model.fbx --decimate 0.5
        assetpipe optimize scene.gltf --texture-size 1024 --lods
    """
    console.print(Panel.fit(
        f"[bold]Optimizing[/bold] {input_path.name}",
        title="⚡ AssetPipe Optimize"
    ))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading...", total=None)
            
            asset = Asset.load(input_path)
            original_stats = asset.get_stats()
            
            progress.update(task, description="Optimizing...")
            asset = optimize_asset(
                asset,
                decimate_ratio=decimate,
                max_texture_size=texture_size,
                generate_lods=generate_lods,
            )
            
            new_stats = asset.get_stats()
            
            # Save
            output_path = output or input_path.with_stem(f"{input_path.stem}_optimized")
            progress.update(task, description="Saving...")
            asset.save(output_path)
            
            progress.update(task, description="[green]✓[/green] Complete")
        
        # Show comparison
        table = Table(title="Optimization Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Before", style="yellow")
        table.add_column("After", style="green")
        table.add_column("Reduction", style="magenta")
        
        if original_stats.get('triangles') and new_stats.get('triangles'):
            reduction = (1 - new_stats['triangles'] / original_stats['triangles']) * 100
            table.add_row(
                "Triangles",
                f"{original_stats['triangles']:,}",
                f"{new_stats['triangles']:,}",
                f"{reduction:.1f}%"
            )
        
        console.print(table)
        console.print(f"\n[green]✓[/green] Saved to: [bold]{output_path}[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def plugins(
    action: str = typer.Argument("list", help="Action: list, install, remove"),
    name: Optional[str] = typer.Argument(None, help="Plugin name"),
):
    """
    Manage AssetPipe plugins.
    
    Examples:
        assetpipe plugins list
        assetpipe plugins install usd-converter
    """
    if action == "list":
        from assetpipe.plugins import list_plugins
        
        plugins_list = list_plugins()
        
        if not plugins_list:
            console.print("[dim]No plugins installed[/dim]")
            return
        
        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Type", style="yellow")
        
        for plugin in plugins_list:
            table.add_row(plugin.name, plugin.version, plugin.type)
        
        console.print(table)
    else:
        console.print(f"[yellow]Action '{action}' not yet implemented[/yellow]")


@app.command()
def quickstart(
    output_dir: Path = typer.Argument(".", help="Directory to create quickstart files"),
):
    """
    Generate quickstart config files to get started fast.
    
    Examples:
        assetpipe quickstart
        assetpipe quickstart ./my_project
    """
    import shutil
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    console.print(Panel.fit(
        "[bold]AssetPipe Quick Start[/bold]",
        title="🚀 Setup"
    ))
    
    # Create quickstart config
    config_content = '''# AssetPipe Pipeline Configuration
# Generated by: assetpipe quickstart
# Docs: https://github.com/assetpipe/assetpipe

version: 1
name: my_pipeline

input:
  formats: [fbx, obj, gltf, glb, blend]
  recursive: true

output:
  format: glb
  directory: ./processed

optimization:
  mesh:
    merge_vertices: true
    remove_degenerates: true
  textures:
    max_size: 2048
    format: webp
    quality: 85

validation:
  rules:
    - no_missing_textures
    - valid_uvs
    - no_degenerate_triangles
  fail_on_warning: false
'''
    
    config_path = output_dir / "pipeline.yaml"
    config_path.write_text(config_content)
    console.print(f"[green]✓[/green] Created: [bold]{config_path}[/bold]")
    
    # Create sample directories
    (output_dir / "assets").mkdir(exist_ok=True)
    (output_dir / "processed").mkdir(exist_ok=True)
    console.print(f"[green]✓[/green] Created: [bold]assets/[/bold] and [bold]processed/[/bold] folders")
    
    console.print("\n[bold cyan]Next steps:[/bold cyan]")
    console.print("  1. Put your 3D files in the [bold]assets/[/bold] folder")
    console.print("  2. Run: [bold]assetpipe batch ./assets --config pipeline.yaml[/bold]")
    console.print("  3. Find processed files in [bold]processed/[/bold]")
    console.print("\n[dim]Tip: Edit pipeline.yaml to customize validation and optimization[/dim]")


@app.command()
def doctor():
    """
    Check AssetPipe installation and diagnose issues.
    
    Examples:
        assetpipe doctor
    """
    console.print(Panel.fit(
        "[bold]System Check[/bold]",
        title="🩺 AssetPipe Doctor"
    ))
    
    issues = []
    
    # Check Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 9):
        issues.append(f"Python {py_version} is old, recommend 3.10+")
        console.print(f"[yellow]⚠[/yellow] Python: {py_version} (recommend 3.10+)")
    else:
        console.print(f"[green]✓[/green] Python: {py_version}")
    
    # Check dependencies
    deps = [
        ("numpy", "numpy"),
        ("PIL", "pillow"),
        ("trimesh", "trimesh"),
        ("pygltflib", "pygltflib"),
        ("yaml", "pyyaml"),
    ]
    
    for import_name, package_name in deps:
        try:
            __import__(import_name)
            console.print(f"[green]✓[/green] {package_name}")
        except ImportError:
            issues.append(f"Missing: {package_name}")
            console.print(f"[red]✗[/red] {package_name} - run: pip install {package_name}")
    
    # Check optional deps
    console.print("\n[dim]Optional dependencies:[/dim]")
    optional = [("FBX SDK", "fbx"), ("OpenUSD", "pxr")]
    for name, module in optional:
        try:
            __import__(module)
            console.print(f"[green]✓[/green] {name}")
        except ImportError:
            console.print(f"[dim]○[/dim] {name} (not installed)")
    
    # Summary
    if issues:
        console.print(f"\n[yellow]Found {len(issues)} issue(s)[/yellow]")
        for issue in issues:
            console.print(f"  [yellow]•[/yellow] {issue}")
    else:
        console.print("\n[green]✓ All checks passed![/green]")


if __name__ == "__main__":
    app()
