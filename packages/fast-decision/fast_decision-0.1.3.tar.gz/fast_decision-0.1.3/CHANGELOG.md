# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 10.12.25

### Added
- Initial release of fast-decision rule engine
- Conditon operators: `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`, `$and`, `$or`
- Priority-based rule execution (lower priority = higher precedence)
- Stop-on-first matching per category
- Python bindings via PyO3 for native performance
- Rust library with zero-cost abstractions
- Comprehensive documentation and examples
- Benchmark suite with Criterion
- Type-safe API for both Rust and Python
- Nested field access with dot notation (e.g., "user.profile.age")
- Complex logical predicates with AND/OR operators

### Performance
- Link Time Optimization (LTO) enabled
- Inline optimizations for hot path functions
- Pre-allocated result vectors
- Optimized data structures (`Box<[String]>`, `#[repr(u8)]`)
- Minimal allocations during rule execution
