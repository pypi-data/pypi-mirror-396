# Contributing to Foliar

## Prerequisites

Foliar is written in Rust. You'll need to install the [Rust toolchain](https://www.rust-lang.org/tools/install) to build and contribute to Foliar.

Also install Python development tools:

```bash
pip install -r requirements-dev.txt
```

These tools include:

- [maturin](https://www.maturin.rs/) to build and manage the Python package.
- [ruff](https://ruff.rs/) for linting and formatting Python code.
- [mypy](http://mypy-lang.org/) for type checking Python code.

## Development

To run the package in your development environment, use:

```bash
maturin develop
```

### Code Quality

To lint Rust code, run:

```bash
cargo clippy --fix --allow-dirty -- -W clippy::pedantic
```

To format Rust code, run:

```bash
cargo fmt
```

To lint Python code, run:

```bash
ruff check
```

To format Python code, run:
```bash
ruff format
```

To type check Python code, run:

```bash
mypy .
```
