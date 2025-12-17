# Token2Audio Package

This package provides a Token2Audio server for audio synthesis.

## Installation

```bash
# 无 GPU（默认）：
pip install token2audio
# 有 NVIDIA GPU：
pip install token2audio[gpu]

# or from source
pip install .
```

## Usage

download pre-trained models:

```bash
python -m token2audio.download /path/to/models
```

You can run the server directly using the command line:

```bash
python -m token2audio.server --model-path /path/to/models --host 0.0.0.0 --port 8000
```

Or import and run in Python:

```python
from token2audio import run_app

# Run the server (will parse command line arguments)
if __name__ == "__main__":
    run_app()
```

## Development

The package structure is as follows:

- `token2audio/`: Main package directory
    - `app.py`: FastAPI application factory
    - `server.py`: Server entry point
    - `protocol.py`: Protocol definitions
    - `handlers/`: Request handlers
    - `models/`: Model implementations
    - `utils/`: Utility functions
    - `flashcosyvoice/`: CosyVoice2 implementation

