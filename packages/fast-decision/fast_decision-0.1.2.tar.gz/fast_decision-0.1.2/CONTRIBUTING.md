# Contributing to fast-decision

Thank you for your interest in contributing to fast-decision! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Development Setup](#development-setup)
- [Building the Project](#building-the-project)
- [Running Tests](#running-tests)
- [Running Benchmarks](#running-benchmarks)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Performance Guidelines](#performance-guidelines)

## Development Setup

### Prerequisites

- **Rust** (latest stable): Install via [rustup](https://rustup.rs/)
- **Python** 3.8+: For Python bindings
- **maturin**: For building Python packages (`pip install maturin`)

### Clone and Build

```bash
git clone https://github.com/almayce/fast-decision.git
cd fast-decision

# Build Rust library
cargo build

# Build Python package (development mode)
maturin develop
```

## Building the Project

### Rust Only

```bash
# Debug build
cargo build

# Release build (optimized)
cargo build --release

# Build examples
cargo build --examples
```

### Python Bindings

```bash
# Development build
maturin develop

# Release build
maturin develop --release

# Build wheel
maturin build --release
```

## Running Tests

### Rust Tests

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_name
```

### Python Tests

```bash
cd python/tests
python test_features.py
```

### Examples

```bash
# Rust example
cargo run --example demo

# Python example
cd python/examples
python example.py
```

## Running Benchmarks

Benchmarks use [Criterion.rs](https://github.com/bheisler/criterion.rs):

```bash
# Run all benchmarks
cargo bench

# Run specific benchmark
cargo bench simple_rule_execution

# Generate HTML report (in target/criterion)
cargo bench --bench engine_benchmark
```

## Code Style

### Rust

We follow standard Rust style conventions:

```bash
# Format code
cargo fmt

# Check formatting
cargo fmt -- --check

# Run clippy lints
cargo clippy --all-targets --all-features

# Strict clippy (CI mode)
cargo clippy --all-targets --all-features -- -D warnings
```

**Style Guidelines:**
- Use descriptive variable names
- Add doc comments (///) for public APIs
- Include performance notes in hot path functions
- Use `#[inline]` or `#[inline(always)]` appropriately
- Prefer iterators over loops where clear
- Avoid unnecessary allocations in hot paths

### Python

Python code should follow PEP 8:

```bash
# Format with black (if available)
black python/

# Check types with mypy (if stubs available)
mypy python/
```

## Submitting Changes

### Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear commit messages
4. **Run tests and linters**:
   ```bash
   cargo fmt --check
   cargo clippy --all-targets -- -D warnings
   cargo test
   cargo bench  # Ensure no performance regressions
   ```
5. **Update documentation** if needed (README, doc comments, etc.)
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request** with a clear description of changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add support for $in operator

- Implement $in operator for array membership checks
- Add tests for $in with various data types
- Update documentation with $in examples
```

### What to Include

- **Tests**: All new features must include tests
- **Benchmarks**: Performance-sensitive changes should include benchmarks
- **Documentation**: Update doc comments and README as needed
- **Changelog**: Add entry to CHANGELOG.md (if exists)

## Performance Guidelines

fast-decision is performance-critical. Please follow these guidelines:

### Hot Path Optimization

Functions in the execution hot path should:
- Minimize allocations (use `Vec::with_capacity`, `Box<[T]>`, etc.)
- Use `#[inline]` or `#[inline(always)]` for small functions
- Avoid unnecessary clones (prefer borrowing)
- Use efficient data structures (`HashMap`, `Box<[T]>`, etc.)

### Benchmarking Changes

Before submitting performance-related PRs:

```bash
# Baseline (before changes)
git checkout main
cargo bench --bench engine_benchmark > baseline.txt

# Your changes
git checkout feature/your-branch
cargo bench --bench engine_benchmark > changes.txt

# Compare
# Use criterion's comparison or manually check results
```

### Memory Optimization

- Use `Box<[T]>` instead of `Vec<T>` for fixed-size data
- Use `#[repr(u8)]` for small enums
- Avoid `String` cloning in hot paths
- Pre-allocate collections with known capacity

## Questions or Issues?

- **Bug reports**: Open an issue with detailed reproduction steps
- **Feature requests**: Open an issue describing the use case
- **Questions**: Use GitHub Discussions or open an issue

## License

By contributing, you agree that your contributions will be licensed under the same MIT OR Apache-2.0 license as the project.

Thank you for contributing! 🚀
