JUSU
====

JUSU is a tiny Python library to build HTML pages using a simple, readable
plain-English style API. It is made for beginners, educators, and quick
prototyping.

Quick usage:

```python
from JUSU import Div, H1, P, Button, Img

page = Div(
	H1("Welcome to JUSU"),
	P("A tiny HTML builder."),
	Button("Click me", onclick="alert('Hello')", cls="btn"),
	Img(src="https://via.placeholder.com/150", alt="demo"),
	cls="container"
)
page.render_to_file("jusu_demo.html")
```

Run tests:

```bash
python -m pytest
```

Install:

```bash
pip install -e .
```

License: MIT

Publish to TestPyPI (recommended first):

1. Create an account on https://test.pypi.org/ and generate an API token.
2. Set the API token as environment variables, for example (Powershell):

```powershell
$Env:TWINE_USERNAME = "__token__"
$Env:TWINE_PASSWORD = "pypi-AgENdGVzdC..."
```

3. Build and upload to TestPyPI:

```powershell
python -m build -o dist
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*
```

Publish to PyPI (after verifying TestPyPI):

```powershell
python -m twine upload dist/*
```

If you prefer to specify the username and token directly instead of environment variables, pass `--username` and `--password` to `twine upload`, but environment variables are more secure.

# JUSU
