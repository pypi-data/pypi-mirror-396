# fast-decision

[![Crates.io](https://img.shields.io/crates/v/fast-decision.svg)](https://crates.io/crates/fast-decision)
[![PyPI](https://img.shields.io/pypi/v/fast-decision.svg)](https://pypi.org/project/fast-decision/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](https://github.com/almayce/fast-decision#license)

A high-performance rule engine written in Rust with Python bindings, designed for applications that need to evaluate complex business rules with minimal latency and maximum throughput.

## Features

- **High Performance**: Rust-powered engine with zero-cost abstractions
- **Priority-based Execution**: Rules sorted by priority (lower number = higher priority)
- **Stop-on-First**: Per-category flag to stop after first match
- **Condition Operators**: Familiar syntax with `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`, `$and`, `$or`
- **Complex Logic**: Support for nested AND/OR predicates
- **Python Bindings**: Native performance with idiomatic Python API via PyO3
- **Memory Efficient**: Minimal allocations in hot path, optimized data structures
- **Benchmarked**: Built-in performance benchmarks with Criterion

## Use Cases

- Business rule engines
- Dynamic pricing systems
- Feature flags and A/B testing
- Access control and authorization
- Data validation and filtering
- Workflow automation

## Installation

### Rust

Add to your `Cargo.toml`:

```toml
[dependencies]
fast-decision = "0.1"
```

### Python

```bash
pip install fast-decision
```

Or install from source:

```bash
git clone https://github.com/almayce/fast-decision.git
cd fast-decision
maturin develop --release
```

## Quick Start

### Rust Example

```rust
use fast_decision::{RuleEngine, RuleSet};
use serde_json::json;

fn main() {
    let rules_json = r#"
    {
      "categories": {
        "Pricing": {
          "stop_on_first": true,
          "rules": [
            {
              "id": "Platinum_Discount",
              "priority": 1,
              "conditions": {"user.tier": {"$eq": "Platinum"}},
              "action": "apply_20_percent_discount"
            },
            {
              "id": "Gold_Discount",
              "priority": 10,
              "conditions": {"user.tier": {"$eq": "Gold"}},
              "action": "apply_10_percent_discount"
            }
          ]
        }
      }
    }
    "#;

    let ruleset: RuleSet = serde_json::from_str(rules_json).unwrap();
    let engine = RuleEngine::new(ruleset);

    let data = json!({
        "user": {"tier": "Gold", "id": 123},
        "transaction": {"amount": 100}
    });

    let results = engine.execute(&data, &["Pricing"]);
    println!("Triggered rules: {:?}", results);
    // Output: ["Gold_Discount"]
}
```

### Python Example

See [python/README.md](python/README.md) for detailed Python documentation.

```python
from fast_decision import FastDecision

# Load rules from JSON file
engine = FastDecision("rules.json")

# Execute rules
data = {
    "user": {"tier": "Gold", "id": 123},
    "transaction": {"amount": 100}
}

results = engine.execute(data, categories=["Pricing"])
print(f"Triggered rules: {results}")
# Output: ['Gold_Discount']
```

## Rule Format

Rules are defined in JSON:

```json
{
  "categories": {
    "CategoryName": {
      "stop_on_first": true,
      "rules": [
        {
          "id": "rule_identifier",
          "priority": 1,
          "conditions": {
            "field.path": {"$eq": "value"}
          },
          "action": "action_name"
        }
      ]
    }
  }
}
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equal | `{"age": {"$eq": 18}}` |
| `$ne` | Not equal | `{"status": {"$ne": "inactive"}}` |
| `$gt` | Greater than | `{"score": {"$gt": 100}}` |
| `$lt` | Less than | `{"price": {"$lt": 50}}` |
| `$gte` | Greater than or equal | `{"age": {"$gte": 21}}` |
| `$lte` | Less than or equal | `{"count": {"$lte": 10}}` |

### Logical Operators

**Implicit AND** - Multiple conditions in one object:
```json
{
  "conditions": {
    "age": {"$gte": 18, "$lt": 65},
    "status": {"$eq": "active"}
  }
}
```

**Explicit OR** - Use `$or`:
```json
{
  "conditions": {
    "$or": [
      {"tier": {"$eq": "Platinum"}},
      {"score": {"$gt": 1000}}
    ]
  }
}
```

**Nested Logic**:
```json
{
  "conditions": {
    "$or": [
      {"tier": {"$eq": "Platinum"}},
      {
        "tier": {"$eq": "Gold"},
        "amount": {"$gt": 500}
      }
    ]
  }
}
```

## Performance

### Benchmarks

Run benchmarks:
```bash
cargo bench
```

### Optimization Features

- **Rust backend**: Native machine code performance
- **Zero allocations** in hot execution path
- **Inline functions**: Critical comparison functions marked `#[inline(always)]`
- **Optimized data structures**: `Box<[String]>` for path tokens, `#[repr(u8)]` for operators
- **Pre-sorted rules**: Rules sorted by priority at load time
- **Direct conversion**: Python dict → Rust without intermediate JSON serialization
- **Link Time Optimization (LTO)**: Enabled in release profile

### Performance Characteristics

- **Rule evaluation**: O(n) where n = number of rules in requested categories
- **Field lookup**: O(d) where d = depth of nested field path
- **Memory**: Minimal allocations during execution (only for results)

## Development

```bash
# Run tests
cargo test

# Run Rust examples
cargo run --example demo

# Run benchmarks
cargo bench

# Build documentation
cargo doc --no-deps --open

# Run Python tests
cd python/tests
python test_features.py

# Run Python examples
cd python/examples
python example.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Architecture

```
fast-decision/
├── src/              # Rust core engine
│   ├── lib.rs        # Python bindings (PyO3)
│   ├── engine.rs     # Rule execution engine
│   └── types.rs      # Data structures
├── benches/          # Performance benchmarks
├── examples/         # Rust examples
├── python/           # Python bindings and examples
│   ├── examples/     # Usage examples
│   └── tests/        # Tests
├── Cargo.toml        # Rust configuration
└── pyproject.toml    # Python packaging
```

## License

Licensed under either of:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
