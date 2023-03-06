isort .
black --line-length=79 --include='\.pyi?$' --exclude="""\.git \.__pycache__ \.hg \.mypy_cache \.tox \.venv _build buck-out build dist""" .
  flake8 .
  mypy .
  find . -type f -name "*.py" | xargs pylint