# <div align="center"> video-specs

Just a light CLI helper to organize your video idea into a JSON/XML/HTML formatted prompt.

## Pre requisites

- Python 3.12+
- `uv` is definitely recommended

## Quick Start

### With `uv`

```bash
make install
uv pip install -e .
```

### with `pip`

```bash
python3 -m venv venv
source venv/bin/activate
pip install click rich rich-click
pip install -e .
```

## Start

```bash
video-specs
```

This should lauch the interactive mode, otherwise you can start with a simple :

```bash
video-specs --help
```