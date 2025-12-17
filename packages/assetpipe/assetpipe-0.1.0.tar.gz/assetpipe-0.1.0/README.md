# 🔧 AssetPipe

**Universal Asset Pipeline CLI** — One tool to rule them all.

Convert, optimize, and validate 3D/2D assets across formats. Built for game studios, VFX houses, and arch-viz firms.

## Features

- **Format Conversion** — FBX ↔ glTF ↔ OBJ ↔ USD ↔ Alembic
- **Texture Optimization** — Resize, compress, generate mipmaps, convert to KTX2/WebP
- **Mesh Optimization** — Decimate, LOD generation, clean topology
- **Validation** — Missing textures, broken UVs, scale issues, naming conventions
- **Batch Processing** — Watch folders, CI/CD hooks, parallel execution
- **Plugin System** — Add custom rules and converters

## Installation

```bash
pip install assetpipe
```

## Quick Start

```bash
# Convert a single file
assetpipe convert model.fbx --to gltf

# Convert with optimization
assetpipe convert model.fbx --to gltf --optimize --validate

# Batch process a directory
assetpipe batch ./assets --config pipeline.yaml

# Watch folder for automatic processing
assetpipe watch ./incoming --config pipeline.yaml

# Validate assets
assetpipe validate ./assets --rules strict

# Generate report
assetpipe report ./assets --output report.html
```

## Configuration

Create a `pipeline.yaml` file:

```yaml
version: 1

input:
  formats: [fbx, obj, blend]
  
output:
  format: gltf
  directory: ./processed

optimization:
  mesh:
    decimate: 0.5  # Reduce to 50% triangles
    generate_lods: [1.0, 0.5, 0.25]
  textures:
    max_size: 2048
    format: webp
    quality: 85

validation:
  rules:
    - no_missing_textures
    - valid_uvs
    - max_triangles: 100000
    - naming_convention: "^[a-z][a-z0-9_]*$"

notifications:
  slack:
    webhook: $SLACK_WEBHOOK
    on: [error, complete]
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `convert` | Convert a single asset |
| `batch` | Process multiple assets |
| `watch` | Watch folder for changes |
| `validate` | Validate assets against rules |
| `optimize` | Optimize meshes and textures |
| `report` | Generate asset report |
| `info` | Show asset information |
| `plugins` | Manage plugins |

## Supported Formats

### 3D Models
- **Import:** FBX, OBJ, glTF/GLB, BLEND*, USD*, Alembic*
- **Export:** glTF/GLB, OBJ, USD*

### Textures
- **Import:** PNG, JPG, TGA, EXR, PSD*
- **Export:** PNG, JPG, WebP, KTX2*

*Requires additional dependencies

## Plugin Development

Create custom converters and validators:

```python
# plugins/my_validator.py
from assetpipe.plugins import ValidatorPlugin, ValidationResult

class MyValidator(ValidatorPlugin):
    name = "my_custom_check"
    
    def validate(self, asset):
        if asset.triangle_count > 50000:
            return ValidationResult.error("Too many triangles!")
        return ValidationResult.ok()
```

Register in `pipeline.yaml`:

```yaml
plugins:
  - path: ./plugins/my_validator.py
    enabled: true
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Validate Assets
  run: |
    pip install assetpipe
    assetpipe validate ./assets --rules strict --fail-on-error
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: assetpipe-validate
        name: Validate 3D Assets
        entry: assetpipe validate
        files: \.(fbx|obj|gltf|glb)$
        language: system
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
