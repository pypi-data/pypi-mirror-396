# CLI Usage

Thulium provides a command-line interface for common tasks.

## Installation

The CLI is installed automatically with the package:

```bash
pip install thulium
```

## Commands

### `thulium recognize`

Recognize text from images.

```bash
thulium recognize IMAGE [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `IMAGE` | Path to image or directory |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-l, --language` | `en` | ISO language code |
| `-p, --pipeline` | `default` | Pipeline name |
| `-d, --device` | `auto` | Device (cpu/cuda) |
| `-o, --output` | None | Output JSON path |

**Examples:**

```bash
# Single image
thulium recognize letter.png -l de

# Batch processing
thulium recognize documents/ -l en -o results.json

# GPU inference
thulium recognize page.png -d cuda
```

---

### `thulium train`

Train a model.

```bash
thulium train CONFIG [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `CONFIG` | Path to training YAML config |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--resume` | None | Resume from checkpoint |
| `--output-dir` | `checkpoints/` | Output directory |

**Example:**

```bash
thulium train config/train_iam.yaml --output-dir runs/exp1
```

---

### `thulium benchmark`

Run benchmarks.

```bash
thulium benchmark DATASET [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `thulium-base` | Model to benchmark |
| `--languages` | all | Languages to test |
| `--output` | None | Save results to file |

**Example:**

```bash
thulium benchmark iam --model thulium-large --output bench.json
```

---

### `thulium profiles`

Manage language profiles.

```bash
# List all supported languages
thulium profiles list

# Show profile details
thulium profiles show de

# Filter by region
thulium profiles list --region "Western Europe"

# Filter by script
thulium profiles list --script Cyrillic
```

---

### `thulium analyze`

Analyze recognition errors.

```bash
thulium analyze PREDICTIONS GROUND_TRUTH [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--top-k` | 10 | Top K errors to show |
| `--format` | `table` | Output format |

---

## Global Options

All commands support:

| Option | Description |
|--------|-------------|
| `--version` | Show version |
| `--debug` | Enable debug logging |
| `--help` | Show help message |

## Configuration Files

Commands can read defaults from `~/.thulium/config.yaml`:

```yaml
defaults:
  language: en
  device: cuda
  pipeline: thulium-base
```

## See Also

- [API Reference](reference.md) — Python API
- [Getting Started](../getting_started.md) — Installation
