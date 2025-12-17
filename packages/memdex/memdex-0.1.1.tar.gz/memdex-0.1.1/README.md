<p align="center">
  <img src="./assets/logo.png" width="512" alt="memdex" />
</p>

<p align="center">
  A small Python package. Placeholder for now.
</p>

## Install

```bash
uv add memdex
```

## Develop

```bash
uv pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

## Releases

Releases are automated via **release-please** on GitHub Actions.

- Merge the release PR to create a `v*` tag and GitHub Release
- Tag push triggers the **PyPI Trusted Publisher (OIDC)** publish workflow

## License

MIT. See `LICENSE`.


