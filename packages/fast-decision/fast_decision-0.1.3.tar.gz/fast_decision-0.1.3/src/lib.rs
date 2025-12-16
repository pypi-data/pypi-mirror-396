//! # fast-decision
//!
//! A high-performance rule engine.
//!
//! This crate provides a rule execution engine optimized for speed with zero-cost abstractions.
//!
//! ## Features
//!
//! - **Priority-based execution**: Rules are sorted by priority (lower values = higher priority)
//! - **Stop-on-first**: Per-category flag to stop execution after the first matching rule
//! - **Condition operators**: `$eq`, `$ne`, `$gt`, `$lt`, `$gte`, `$lte`, `$and`, `$or`
//! - **Zero-cost abstractions**: Optimized Rust core with minimal allocations in hot paths
//! - **Python bindings**: Native performance accessible from Python via PyO3
//!
//! ## Architecture
//!
//! The engine consists of three main components:
//! - Rule execution engine ([`RuleEngine`])
//! - Type definitions and data structures ([`RuleSet`], [`Category`], [`Rule`], [`Predicate`])
//! - Python bindings via PyO3 (`FastDecision` class)
//!
//! ## Performance Characteristics
//!
//! - O(n) rule evaluation where n is the number of rules in requested categories
//! - O(d) nested field access where d is the depth of field path
//! - Minimal allocations during execution (results only)
//! - Optimized comparison operations with inline hints
//!
//! ## Example (Rust)
//!
//! ```rust,no_run
//! use fast_decision::{RuleEngine, RuleSet};
//! use serde_json::json;
//!
//! let rules_json = r#"
//! {
//!   "categories": {
//!     "Pricing": {
//!       "stop_on_first": true,
//!       "rules": [{
//!         "id": "Premium",
//!         "priority": 1,
//!         "conditions": {"user.tier": {"$eq": "Gold"}},
//!         "action": "apply_discount"
//!       }]
//!     }
//!   }
//! }
//! "#;
//!
//! let ruleset: RuleSet = serde_json::from_str(rules_json).unwrap();
//! let engine = RuleEngine::new(ruleset);
//!
//! let data = json!({"user": {"tier": "Gold"}});
//! let results = engine.execute(&data, &["Pricing"]);
//! println!("Triggered rules: {:?}", results);
//! ```

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use serde_json::Value;
use pythonize::pythonize;

mod engine;
mod types;

pub use crate::engine::RuleEngine;
pub use crate::types::{Category, Comparison, Operator, Predicate, Rule, RuleSet};

/// Converts a Python object to a `serde_json::Value`.
///
/// Supports:
/// - Dictionaries → JSON objects
/// - Lists → JSON arrays
/// - Strings, integers, floats, booleans → corresponding JSON types
/// - None → JSON null
///
/// # Errors
///
/// Returns `PyTypeError` if the object type is not supported.
///
/// # Performance
///
/// Recursively processes nested structures. Pre-allocates collections with known capacity.
fn pyany_to_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if let Ok(dict) = obj.downcast::<PyDict>() {
        let mut map = serde_json::Map::with_capacity(dict.len());
        for (key, value) in dict.iter() {
            let key_str: String = key.extract()?;
            map.insert(key_str, pyany_to_value(&value)?);
        }
        Ok(Value::Object(map))
    } else if let Ok(list) = obj.downcast::<PyList>() {
        let mut vec = Vec::with_capacity(list.len());
        for item in list.iter() {
            vec.push(pyany_to_value(&item)?);
        }
        Ok(Value::Array(vec))
    } else if let Ok(s) = obj.extract::<String>() {
        Ok(Value::String(s))
    } else if let Ok(i) = obj.extract::<i64>() {
        Ok(Value::Number(i.into()))
    } else if let Ok(f) = obj.extract::<f64>() {
        Ok(Value::Number(serde_json::Number::from_f64(f).ok_or_else(
            || PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid float"),
        )?))
    } else if let Ok(b) = obj.extract::<bool>() {
        Ok(Value::Bool(b))
    } else if obj.is_none() {
        Ok(Value::Null)
    } else {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Unsupported type",
        ))
    }
}

/// Python interface to the rule engine.
///
/// This class provides Python bindings via PyO3, allowing native-performance
/// rule execution from Python code.
///
/// # Example (Python)
///
/// ```python
/// from fast_decision import FastDecision
///
/// engine = FastDecision("rules.json")
/// data = {"user": {"tier": "Gold"}, "amount": 100}
/// results = engine.execute(data, categories=["Pricing"])
/// print(f"Triggered rules: {results}")
/// ```
#[pyclass]
struct FastDecision {
    engine: RuleEngine,
}

#[pymethods]
impl FastDecision {
    /// Creates a new FastDecision engine from a JSON rules file.
    ///
    /// # Arguments
    ///
    /// * `rules_path` - Path to the JSON file containing rule definitions
    ///
    /// # Errors
    ///
    /// - `PyIOError`: If the file cannot be read
    /// - `PyValueError`: If the JSON is invalid or malformed
    ///
    /// # Example
    ///
    /// ```python
    /// engine = FastDecision("path/to/rules.json")
    /// ```
    #[new]
    fn new(rules_path: &str) -> PyResult<Self> {
        let json_str = std::fs::read_to_string(rules_path).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Failed to read rules file: {}",
                e
            ))
        })?;

        let ruleset: RuleSet = serde_json::from_str(&json_str).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to parse rules JSON: {}",
                e
            ))
        })?;

        Ok(FastDecision {
            engine: RuleEngine::new(ruleset),
        })
    }

    /// Executes rules against Python dictionary data.
    ///
    /// # Arguments
    ///
    /// * `data` - Python dictionary containing the data to evaluate
    /// * `categories` - List of category names to execute
    ///
    /// # Returns
    ///
    /// List of rule objects (as Python dictionaries) that matched the data, in priority order.
    /// Each dictionary contains: id, priority, conditions, action.
    ///
    /// # Performance
    ///
    /// Converts Python dict to Rust `Value` once, then executes rules natively.
    /// Uses pythonize for efficient Rust → Python conversion without intermediate JSON.
    ///
    /// # Example
    ///
    /// ```python
    /// data = {"user": {"tier": "Gold"}}
    /// results = engine.execute(data, categories=["Pricing"])
    /// for rule in results:
    ///     print(f"Rule {rule['id']}: {rule['action']}")
    /// ```
    fn execute(&self, py: Python<'_>, data: &Bound<'_, PyDict>, categories: Vec<String>) -> PyResult<Vec<PyObject>> {
        let value = pyany_to_value(data.as_any())?;
        let categories_refs: Vec<&str> = categories.iter().map(String::as_str).collect();
        let results = self.engine.execute(&value, &categories_refs);

        // Direct Rust → Python conversion with pythonize (no intermediate JSON)
        let mut py_results = Vec::with_capacity(results.len());
        for rule in results {
            py_results.push(pythonize(py, rule)?.unbind());
        }
        Ok(py_results)
    }

    /// Executes rules against JSON string data.
    ///
    /// # Arguments
    ///
    /// * `data_json` - JSON string containing the data to evaluate
    /// * `categories` - List of category names to execute
    ///
    /// # Returns
    ///
    /// List of rule objects (as Python dictionaries) that matched the data, in priority order.
    /// Each dictionary contains: id, priority, conditions, action.
    ///
    /// # Errors
    ///
    /// Returns `PyValueError` if the JSON string is invalid.
    ///
    /// # Performance
    ///
    /// Faster than `execute()` if data is already in JSON format
    /// (avoids Python→Rust conversion overhead).
    /// Uses pythonize for efficient Rust → Python conversion.
    ///
    /// # Example
    ///
    /// ```python
    /// data_json = '{"user": {"tier": "Gold"}}'
    /// results = engine.execute_json(data_json, categories=["Pricing"])
    /// for rule in results:
    ///     print(f"Rule {rule['id']}: {rule['action']}")
    /// ```
    fn execute_json(&self, py: Python<'_>, data_json: &str, categories: Vec<String>) -> PyResult<Vec<PyObject>> {
        let value: Value = serde_json::from_str(data_json).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e))
        })?;

        let categories_refs: Vec<&str> = categories.iter().map(String::as_str).collect();
        let results = self.engine.execute(&value, &categories_refs);

        // Direct Rust → Python conversion with pythonize (no intermediate JSON)
        let mut py_results = Vec::with_capacity(results.len());
        for rule in results {
            py_results.push(pythonize(py, rule)?.unbind());
        }
        Ok(py_results)
    }
}

#[pymodule]
fn fast_decision(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastDecision>()?;
    Ok(())
}
