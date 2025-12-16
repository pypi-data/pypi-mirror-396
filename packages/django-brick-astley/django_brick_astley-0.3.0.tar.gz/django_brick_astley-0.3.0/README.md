# django-brick-astley

Reusable bricks for Django templates.

[![PyPI version](https://badge.fury.io/py/django-brick-astley.svg)](https://pypi.org/project/django-brick-astley/)
[![Documentation Status](https://readthedocs.org/projects/django-brick-astley/badge/?version=latest)](https://django-brick-astley.readthedocs.io/)

**[Documentation](https://django-brick-astley.readthedocs.io/)** | **[PyPI](https://pypi.org/project/django-brick-astley/)** | **[GitHub](https://github.com/philippbosch/django-brick-astley)**

## Installation

```bash
pip install django-brick-astley
```

## Usage

Add `brickastley` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'brickastley',
    # ...
]
```

For detailed usage instructions, see the [full documentation](https://django-brick-astley.readthedocs.io/).

## Example Project

This repository includes a Django demo project in the `example/` directory. To run it:

```bash
cd example
python -m venv .venv
source .venv/bin/activate
pip install -e ..
pip install Django
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the example in action.

## Development

Clone the repository:

```bash
git clone https://github.com/philippbosch/django-brick-astley.git
cd django-brick-astley
```

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

Install in development mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```


## License

MIT
