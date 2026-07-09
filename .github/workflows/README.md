# GitHub workflows documentation

This folder contains GitHub Actions workflow files.

GitHub Actions is used for continuous integration.

---

## Current workflow

### `tests.yml`

Runs automated checks on pushes and pull requests.

The workflow:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs Ruff lint checks
5. Runs the pytest test suite

The main commands executed by the workflow are:

```bash
ruff check .
python -m pytest
```

---

## Purpose

The workflow helps ensure that:

- The project can be installed in a clean environment
- Basic code quality checks pass
- Tests pass automatically
- Future changes do not accidentally break existing functionality

---

## Status badge

The main README includes a GitHub Actions badge showing whether the latest workflow run is passing or failing.
