# neatrl

[![CI](https://github.com/YuvrajSingh-mist/NeatRL/actions/workflows/ci.yml/badge.svg)](https://github.com/YuvrajSingh-mist/NeatRL/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/neatrl.svg)](https://pypi.org/project/neatrl/)

A Python library for reinforcement learning algorithms.

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e .[dev]
```

## Usage

Import the components:

```python
from neatrl import QNet, LinearEpsilonDecay, make_env, evaluate
```

To run the DQN training script:

```bash
python -m neatrl.dqn
```

## Development

```bash
# Install dev dependencies
make install-dev

# Run all checks
make all

# Run tests
make test

# Lint and format
make lint
make format

# Type check
make type-check

# Build package
make build
```

Or directly:

```bash
python neatrl/src/neatrl/dqn.py
```