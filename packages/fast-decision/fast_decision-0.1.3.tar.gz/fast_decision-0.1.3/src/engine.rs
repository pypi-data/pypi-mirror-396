//! Rule execution engine.
//!
//! This module contains the core rule execution logic, including:
//! - Nested field value extraction
//! - Comparison operations (eq, ne, gt, lt, gte, lte)
//! - Predicate evaluation (AND/OR logic)
//! - Rule matching and execution
//!
//! All comparison and lookup functions are marked `#[inline]` for optimal performance.

use crate::types::{Comparison, Operator, Predicate, Rule, RuleSet};
use log::{debug, trace};
use serde_json::Value;

/// Retrieves a nested value from JSON data using dot-separated path tokens.
///
/// # Performance
///
/// This function is marked `#[inline]` and performs O(d) lookups where d is the path depth.
/// Returns `None` immediately if any path component doesn't exist.
///
/// # Examples
///
/// ```ignore
/// let data = json!({"user": {"profile": {"age": 25}}});
/// let tokens = vec!["user".to_string(), "profile".to_string(), "age".to_string()];
/// let value = get_nested_value(&data, &tokens);
/// assert_eq!(value, Some(&json!(25)));
/// ```
#[inline]
fn get_nested_value<'a>(data: &'a Value, tokens: &[String]) -> Option<&'a Value> {
    let mut current = data;
    for token in tokens {
        current = current.as_object()?.get(token)?;
    }
    Some(current)
}

/// Compares two JSON values for equality.
///
/// For numeric values, uses epsilon comparison for floating-point safety.
/// For other types, uses direct equality comparison.
///
/// # Performance
///
/// Marked `#[inline(always)]` for zero-cost abstraction in hot path.
#[inline(always)]
fn compare_eq(v1: &Value, v2: &Value) -> bool {
    if let (Some(n1), Some(n2)) = (v1.as_f64(), v2.as_f64()) {
        return (n1 - n2).abs() < f64::EPSILON;
    }
    v1 == v2
}

/// Greater-than comparison for numeric values.
///
/// Returns `false` if either value is not numeric.
/// Marked `#[inline(always)]` for hot path optimization.
#[inline(always)]
fn compare_gt(v1: &Value, v2: &Value) -> bool {
    matches!((v1.as_f64(), v2.as_f64()), (Some(n1), Some(n2)) if n1 > n2)
}

/// Less-than comparison for numeric values.
///
/// Returns `false` if either value is not numeric.
/// Marked `#[inline(always)]` for hot path optimization.
#[inline(always)]
fn compare_lt(v1: &Value, v2: &Value) -> bool {
    matches!((v1.as_f64(), v2.as_f64()), (Some(n1), Some(n2)) if n1 < n2)
}

/// Greater-than-or-equal comparison for numeric values.
///
/// Returns `false` if either value is not numeric.
/// Marked `#[inline(always)]` for hot path optimization.
#[inline(always)]
fn compare_gte(v1: &Value, v2: &Value) -> bool {
    matches!((v1.as_f64(), v2.as_f64()), (Some(n1), Some(n2)) if n1 >= n2)
}

/// Less-than-or-equal comparison for numeric values.
///
/// Returns `false` if either value is not numeric.
/// Marked `#[inline(always)]` for hot path optimization.
#[inline(always)]
fn compare_lte(v1: &Value, v2: &Value) -> bool {
    matches!((v1.as_f64(), v2.as_f64()), (Some(n1), Some(n2)) if n1 <= n2)
}

/// Evaluates a single comparison against data.
///
/// Extracts the value at the specified path and applies the comparison operator.
/// Returns `false` if the path doesn't exist in the data.
fn check_comparison(data: &Value, comp: &Comparison) -> bool {
    let data_value = match get_nested_value(data, &comp.path_tokens) {
        Some(v) => v,
        None => return false,
    };

    match comp.op {
        Operator::Equal => compare_eq(data_value, &comp.value),
        Operator::NotEqual => !compare_eq(data_value, &comp.value),
        Operator::GreaterThan => compare_gt(data_value, &comp.value),
        Operator::LessThan => compare_lt(data_value, &comp.value),
        Operator::GreaterThanOrEqual => compare_gte(data_value, &comp.value),
        Operator::LessThanOrEqual => compare_lte(data_value, &comp.value),
    }
}

/// Recursively evaluates a predicate (comparison, AND, or OR).
///
/// # Logic
///
/// - `Comparison`: Direct comparison evaluation
/// - `And`: All child predicates must be true (short-circuits on first false)
/// - `Or`: At least one child predicate must be true (short-circuits on first true)
fn check_predicate(data: &Value, predicate: &Predicate) -> bool {
    match predicate {
        Predicate::Comparison(comp) => check_comparison(data, comp),
        // AND logic: all child predicates must be true
        Predicate::And(predicates) => predicates.iter().all(|p| check_predicate(data, p)),
        // OR logic: at least one child predicate must be true
        Predicate::Or(predicates) => predicates.iter().any(|p| check_predicate(data, p)),
    }
}

/// The main rule execution engine.
///
/// Holds a compiled ruleset and provides methods to execute rules against data.
///
/// # Performance
///
/// The engine pre-sorts rules by priority during construction and performs
/// minimal allocations during execution.
pub struct RuleEngine {
    ruleset: RuleSet,
}

impl RuleEngine {
    /// Creates a new rule engine from a ruleset.
    ///
    /// # Warning Detection
    ///
    /// This constructor checks for duplicate priorities within categories
    /// and logs warnings if found (order of execution may be non-deterministic).
    ///
    /// # Examples
    ///
    /// ```rust,no_run
    /// use fast_decision::{RuleEngine, RuleSet};
    /// # let rules_json = "{}";
    /// let ruleset: RuleSet = serde_json::from_str(rules_json).unwrap();
    /// let engine = RuleEngine::new(ruleset);
    /// ```
    pub fn new(ruleset: RuleSet) -> Self {
        for (name, category) in &ruleset.categories {
            category.warn_duplicate_priorities(name);
        }
        RuleEngine { ruleset }
    }

    /// Checks if a single rule matches the given data.
    ///
    /// Returns `Some(&rule)` if the rule matches, `None` otherwise.
    /// Logs trace and debug messages via the `log` crate.
    fn check_rule<'a>(data: &Value, rule: &'a Rule) -> Option<&'a Rule> {
        trace!("Checking rule: {}", rule.id);
        if check_predicate(data, &rule.predicate) {
            debug!("Rule {} triggered", rule.id);
            Some(rule)
        } else {
            trace!("Rule {} not triggered", rule.id);
            None
        }
    }

    /// Executes rules from specified categories against the provided data.
    ///
    /// # Arguments
    ///
    /// * `data` - JSON data to evaluate rules against
    /// * `categories_to_run` - List of category names to execute
    ///
    /// # Returns
    ///
    /// A vector of references to Rule objects that matched the data, in priority order.
    ///
    /// # Behavior
    ///
    /// - Rules are evaluated in priority order (lower priority value = higher precedence)
    /// - If a category has `stop_on_first: true`, execution stops after the first match
    /// - Non-existent categories are silently skipped
    /// - Results accumulate across all requested categories
    ///
    /// # Performance
    ///
    /// - O(n) where n is total number of rules in requested categories
    /// - Pre-allocates result vector with exact capacity
    /// - Minimal allocations during execution
    ///
    /// # Examples
    ///
    /// ```rust,no_run
    /// # use fast_decision::{RuleEngine, RuleSet};
    /// # use serde_json::json;
    /// # let ruleset: RuleSet = serde_json::from_str("{}").unwrap();
    /// # let engine = RuleEngine::new(ruleset);
    /// let data = json!({"user": {"tier": "Gold"}});
    /// let results = engine.execute(&data, &["Pricing", "Fraud"]);
    /// for rule in results {
    ///     println!("Matched rule: {} - {}", rule.id, rule.action);
    /// }
    /// ```
    pub fn execute<'a>(&'a self, data: &Value, categories_to_run: &[&str]) -> Vec<&'a Rule> {
        let categories: Vec<_> = categories_to_run
            .iter()
            .filter_map(|&name| self.ruleset.categories.get(name).map(|cat| (name, cat)))
            .collect();

        let total_rules: usize = categories.iter().map(|(_, cat)| cat.rules.len()).sum();
        let mut results = Vec::with_capacity(total_rules);

        for (_name, category) in categories {
            debug!(
                "Processing category: {} ({} rules)",
                _name,
                category.rules.len()
            );

            for rule in &category.rules {
                if let Some(matched_rule) = Self::check_rule(data, rule) {
                    results.push(matched_rule);

                    if category.stop_on_first {
                        debug!("stop_on_first enabled, stopping after first match");
                        break;
                    }
                }
            }
        }
        results
    }
}
