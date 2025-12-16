# <div align="center"> video-specs

Just a light CLI helper to organize your video idea into a JSON/XML/HTML formatted prompt.

## Pre requisites

- Python 3.12+
- `uv` is definitely recommended

## Installation

### From PyPI (recommended)

```bash
pip install video-specs
```

Or with `uv`:
```bash
uv pip install video-specs
```

### From Homebrew (macOS/Linux)

```bash
brew tap dim-gggl/brew
brew install video-specs
```

### From source (for development)

#### With `uv`

```bash
make install
uv pip install -e .
```

#### With `pip`

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