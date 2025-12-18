# Example Package

This is used to upload dummy packages to Pypi.

This is a simple example package. You can use
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

To upload a new package to public pypi repository update the pyproject.toml file and give it a name.

Run these commands to upload

```bash
pip install build twine
twine upload dist/*
```

Twine will ask for token then provide the token from the Pypi account.