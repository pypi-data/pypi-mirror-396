# Rust Examples

This directory contains Rust examples demonstrating the fast-decision rule engine.

## Available Examples

### demo.rs

Comprehensive demo showing:
- Complex rule conditions with nested fields
- `$or` logical operators
- Multiple comparison operators (`$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`)
- Priority-based rule execution
- Logging and debugging

**Run:**
```bash
cargo run --example demo
```

**With debug logging:**
```bash
RUST_LOG=debug cargo run --example demo
```

**With trace logging:**
```bash
RUST_LOG=trace cargo run --example demo
```

## Rule Format

Rules are defined in JSON format:

```json
{
  "categories": {
    "CategoryName": {
      "stop_on_first": true,
      "rules": [
        {
          "id": "Rule_ID",
          "priority": 1,
          "conditions": {
            "field.path": {"$eq": "value"}
          },
          "action": "Action_Name"
        }
      ]
    }
  }
}
```

## Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$eq` | Equal | `{"amount": {"$eq": 100}}` |
| `$ne` | Not equal | `{"tier": {"$ne": "Bronze"}}` |
| `$gt` | Greater than | `{"amount": {"$gt": 50}}` |
| `$lt` | Less than | `{"amount": {"$lt": 1000}}` |
| `$gte` | Greater than or equal | `{"amount": {"$gte": 100}}` |
| `$lte` | Less than or equal | `{"amount": {"$lte": 500}}` |

## Logical Operators

### Implicit AND

Multiple conditions in the same object are implicitly ANDed:

```json
{
  "conditions": {
    "amount": {"$gte": 100, "$lt": 500},
    "tier": {"$ne": "Bronze"}
  }
}
```

### Explicit OR

Use `$or` for OR logic:

```json
{
  "conditions": {
    "$or": [
      {"tier": {"$eq": "Platinum"}},
      {"amount": {"$gt": 500}}
    ]
  }
}
```

### Nested Logic

Combine AND and OR:

```json
{
  "conditions": {
    "$or": [
      {"tier": {"$eq": "Platinum"}},
      {
        "tier": {"$eq": "Gold"},
        "amount": {"$gt": 1000}
      }
    ]
  }
}
```

## Data Format

Data is provided as JSON with nested fields:

```rust
use serde_json::json;

let data = json!({
    "user": {
        "id": 123,
        "details": {
            "tier": "Gold"
        }
    },
    "transaction": {
        "amount": 250.0,
        "currency": "USD"
    }
});
```

## Field Paths

Access nested fields with dot notation:
- `"user.tier"` → matches `{"user": {"tier": "..."}}`
- `"user.details.tier"` → matches `{"user": {"details": {"tier": "..."}}}`
- `"transaction.amount"` → matches `{"transaction": {"amount": 100}}`

## Priority and Execution

- **Lower priority value = Higher precedence**
- Priority 1 executes before priority 10
- Rules within a category are sorted by priority
- `stop_on_first: true` stops after first match in category
- `stop_on_first: false` evaluates all rules in category

## Creating Your Own Example

1. Create a new file in `examples/`:
```bash
touch examples/my_example.rs
```

2. Add your code:
```rust
use fast_decision::{RuleEngine, RuleSet};
use serde_json::json;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rules_json = r#"{ /* your rules */ }"#;
    let ruleset: RuleSet = serde_json::from_str(rules_json)?;
    let engine = RuleEngine::new(ruleset);

    let data = json!({ /* your data */ });
    let results = engine.execute(&data, &["YourCategory"]);

    println!("Results: {:?}", results);
    Ok(())
}
```

3. Run it:
```bash
cargo run --example my_example
```

## Performance Tips

- Use `--release` for production performance:
  ```bash
  cargo run --release --example demo
  ```
- Rules are pre-sorted by priority, so no runtime sorting overhead
- Nested field access is O(depth), optimized with inline functions
- Consider `stop_on_first: true` if only the first match matters

## See Also

- [Main README](../README.md)
- [Python Examples](../python/examples/)
- [CONTRIBUTING](../CONTRIBUTING.md)
