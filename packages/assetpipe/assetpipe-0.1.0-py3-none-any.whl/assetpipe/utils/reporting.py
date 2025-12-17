"""
Report Generation - HTML, JSON, Markdown reports
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

from assetpipe.core.asset import Asset


def generate_report(
    input_dir: Path,
    output_path: Path,
    format: str = "html",
) -> Path:
    """
    Generate a report of assets in a directory.
    
    Args:
        input_dir: Directory to analyze
        output_path: Output report file path
        format: Report format (html, json, markdown)
        
    Returns:
        Path to generated report
    """
    input_dir = Path(input_dir)
    output_path = Path(output_path)
    
    # Collect asset data
    assets_data = []
    total_triangles = 0
    total_textures = 0
    total_size = 0
    
    extensions = ['.fbx', '.obj', '.gltf', '.glb']
    
    for file_path in input_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in extensions:
            continue
        
        try:
            asset = Asset.load(file_path)
            stats = asset.get_stats()
            
            file_size = file_path.stat().st_size
            total_size += file_size
            
            asset_info = {
                "name": asset.name,
                "path": str(file_path.relative_to(input_dir)),
                "type": asset.type.value,
                "format": file_path.suffix[1:].upper(),
                "size_bytes": file_size,
                "size_human": _format_size(file_size),
                "triangles": stats.get("triangles", 0),
                "vertices": stats.get("vertices", 0),
                "materials": stats.get("material_count", 0),
                "textures": stats.get("texture_count", 0),
                "has_uvs": stats.get("has_uvs", False),
                "has_normals": stats.get("has_normals", False),
            }
            
            assets_data.append(asset_info)
            total_triangles += asset_info["triangles"]
            total_textures += asset_info["textures"]
            
        except Exception as e:
            assets_data.append({
                "name": file_path.stem,
                "path": str(file_path.relative_to(input_dir)),
                "error": str(e),
            })
    
    # Summary
    summary = {
        "directory": str(input_dir),
        "generated_at": datetime.now().isoformat(),
        "total_assets": len(assets_data),
        "total_triangles": total_triangles,
        "total_textures": total_textures,
        "total_size_bytes": total_size,
        "total_size_human": _format_size(total_size),
    }
    
    # Generate report in requested format
    if format == "json":
        _generate_json_report(output_path, summary, assets_data)
    elif format == "markdown":
        _generate_markdown_report(output_path, summary, assets_data)
    else:
        _generate_html_report(output_path, summary, assets_data)
    
    return output_path


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _generate_json_report(
    output_path: Path,
    summary: Dict[str, Any],
    assets: List[Dict[str, Any]],
) -> None:
    """Generate JSON report"""
    report = {
        "summary": summary,
        "assets": assets,
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)


def _generate_markdown_report(
    output_path: Path,
    summary: Dict[str, Any],
    assets: List[Dict[str, Any]],
) -> None:
    """Generate Markdown report"""
    lines = [
        "# AssetPipe Report",
        "",
        f"**Directory:** `{summary['directory']}`",
        f"**Generated:** {summary['generated_at']}",
        "",
        "## Summary",
        "",
        f"- **Total Assets:** {summary['total_assets']}",
        f"- **Total Triangles:** {summary['total_triangles']:,}",
        f"- **Total Textures:** {summary['total_textures']}",
        f"- **Total Size:** {summary['total_size_human']}",
        "",
        "## Assets",
        "",
        "| Name | Format | Triangles | Size | UVs | Normals |",
        "|------|--------|-----------|------|-----|---------|",
    ]
    
    for asset in assets:
        if "error" in asset:
            lines.append(f"| {asset['name']} | ERROR | - | - | - | - |")
        else:
            uvs = "✓" if asset.get("has_uvs") else "✗"
            normals = "✓" if asset.get("has_normals") else "✗"
            lines.append(
                f"| {asset['name']} | {asset['format']} | "
                f"{asset['triangles']:,} | {asset['size_human']} | {uvs} | {normals} |"
            )
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def _generate_html_report(
    output_path: Path,
    summary: Dict[str, Any],
    assets: List[Dict[str, Any]],
) -> None:
    """Generate HTML report"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AssetPipe Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #fff;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }}
        .subtitle {{
            color: #888;
            margin-bottom: 2rem;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #4ade80;
        }}
        .stat-label {{
            color: #888;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1a1a1a;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            background: #252525;
            color: #fff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        tr:hover {{
            background: #252525;
        }}
        .format-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            background: #333;
        }}
        .format-gltf {{ background: #4ade80; color: #000; }}
        .format-glb {{ background: #4ade80; color: #000; }}
        .format-fbx {{ background: #f59e0b; color: #000; }}
        .format-obj {{ background: #3b82f6; color: #fff; }}
        .check {{ color: #4ade80; }}
        .cross {{ color: #ef4444; }}
        .error-row {{ background: #2d1f1f; }}
        .error-text {{ color: #ef4444; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 AssetPipe Report</h1>
        <p class="subtitle">Generated {summary['generated_at']}</p>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{summary['total_assets']}</div>
                <div class="stat-label">Total Assets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['total_triangles']:,}</div>
                <div class="stat-label">Total Triangles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['total_textures']}</div>
                <div class="stat-label">Total Textures</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['total_size_human']}</div>
                <div class="stat-label">Total Size</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Format</th>
                    <th>Triangles</th>
                    <th>Vertices</th>
                    <th>Materials</th>
                    <th>Size</th>
                    <th>UVs</th>
                    <th>Normals</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for asset in assets:
        if "error" in asset:
            html += f"""
                <tr class="error-row">
                    <td>{asset['name']}</td>
                    <td colspan="7" class="error-text">Error: {asset['error']}</td>
                </tr>
"""
        else:
            fmt_class = f"format-{asset['format'].lower()}"
            uvs = '<span class="check">✓</span>' if asset.get("has_uvs") else '<span class="cross">✗</span>'
            normals = '<span class="check">✓</span>' if asset.get("has_normals") else '<span class="cross">✗</span>'
            
            html += f"""
                <tr>
                    <td>{asset['name']}</td>
                    <td><span class="format-badge {fmt_class}">{asset['format']}</span></td>
                    <td>{asset['triangles']:,}</td>
                    <td>{asset['vertices']:,}</td>
                    <td>{asset['materials']}</td>
                    <td>{asset['size_human']}</td>
                    <td>{uvs}</td>
                    <td>{normals}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
