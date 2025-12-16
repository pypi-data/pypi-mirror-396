use criterion::{BenchmarkId, Criterion, black_box, criterion_group, criterion_main};
use fast_decision::{RuleEngine, RuleSet};
use serde_json::json;

fn create_simple_ruleset() -> RuleSet {
    let rules_json = r#"
    {
      "categories": {
        "Pricing": {
          "stop_on_first": true,
          "rules": [
            {
              "id": "R1_Platinum",
              "priority": 1,
              "conditions": {"user.tier": {"$eq": "Platinum"}},
              "action": "Premium_Discount"
            },
            {
              "id": "R2_Gold",
              "priority": 10,
              "conditions": {"user.tier": {"$eq": "Gold"}},
              "action": "Standard_Discount"
            },
            {
              "id": "R3_Silver",
              "priority": 20,
              "conditions": {"user.tier": {"$eq": "Silver"}},
              "action": "Basic_Discount"
            }
          ]
        }
      }
    }
    "#;
    serde_json::from_str(rules_json).unwrap()
}

fn create_complex_ruleset() -> RuleSet {
    let rules_json = r#"
    {
      "categories": {
        "Complex": {
          "stop_on_first": false,
          "rules": [
            {
              "id": "R1_Complex",
              "priority": 1,
              "conditions": {
                "$or": [
                  {"user.details.tier": {"$eq": "Platinum"}},
                  {"transaction.amount": {"$gt": 500}}
                ]
              },
              "action": "Premium"
            },
            {
              "id": "R2_Range",
              "priority": 10,
              "conditions": {
                "transaction.amount": {"$gte": 100, "$lt": 500},
                "user.details.tier": {"$ne": "Bronze"}
              },
              "action": "Standard"
            },
            {
              "id": "R3_Nested",
              "priority": 20,
              "conditions": {
                "user.profile.settings.notifications": {"$eq": true}
              },
              "action": "Notify"
            }
          ]
        }
      }
    }
    "#;
    serde_json::from_str(rules_json).unwrap()
}

fn bench_simple_rule_execution(c: &mut Criterion) {
    let ruleset = create_simple_ruleset();
    let engine = RuleEngine::new(ruleset);

    let data = json!({
        "user": {"tier": "Gold"},
        "transaction": {"amount": 100}
    });

    c.bench_function("simple_rule_execution", |b| {
        b.iter(|| {
            let results = engine.execute(black_box(&data), black_box(&["Pricing"]));
            black_box(results);
        })
    });
}

fn bench_complex_rule_execution(c: &mut Criterion) {
    let ruleset = create_complex_ruleset();
    let engine = RuleEngine::new(ruleset);

    let data = json!({
        "user": {
            "details": {"tier": "Gold"},
            "profile": {
                "settings": {"notifications": true}
            }
        },
        "transaction": {"amount": 250}
    });

    c.bench_function("complex_rule_execution", |b| {
        b.iter(|| {
            let results = engine.execute(black_box(&data), black_box(&["Complex"]));
            black_box(results);
        })
    });
}

fn bench_nested_field_access(c: &mut Criterion) {
    let ruleset = create_complex_ruleset();
    let engine = RuleEngine::new(ruleset);

    let mut group = c.benchmark_group("nested_field_depth");

    // Shallow nesting (depth 2)
    let shallow = json!({
        "user": {"tier": "Gold"}
    });
    group.bench_with_input(
        BenchmarkId::from_parameter("depth_2"),
        &shallow,
        |b, data| {
            b.iter(|| {
                let results = engine.execute(black_box(data), black_box(&["Complex"]));
                black_box(results);
            })
        },
    );

    // Deep nesting (depth 4)
    let deep = json!({
        "user": {
            "profile": {
                "settings": {"notifications": true}
            }
        }
    });
    group.bench_with_input(BenchmarkId::from_parameter("depth_4"), &deep, |b, data| {
        b.iter(|| {
            let results = engine.execute(black_box(data), black_box(&["Complex"]));
            black_box(results);
        })
    });

    group.finish();
}

fn bench_rule_count_scaling(c: &mut Criterion) {
    let mut group = c.benchmark_group("rule_count_scaling");

    for rule_count in [5, 10, 20, 50].iter() {
        let rules_json = format!(
            r#"
        {{
          "categories": {{
            "Scaling": {{
              "stop_on_first": false,
              "rules": [{}]
            }}
          }}
        }}
        "#,
            (0..*rule_count)
                .map(|i| format!(
                    r#"
            {{
              "id": "R{}",
              "priority": {},
              "conditions": {{"value": {{"$eq": {}}}}},
              "action": "Action{}"
            }}
        "#,
                    i, i, i, i
                ))
                .collect::<Vec<_>>()
                .join(",")
        );

        let ruleset: RuleSet = serde_json::from_str(&rules_json).unwrap();
        let engine = RuleEngine::new(ruleset);

        let data = json!({"value": rule_count / 2});

        group.bench_with_input(
            BenchmarkId::from_parameter(rule_count),
            &engine,
            |b, eng| {
                b.iter(|| {
                    let results = eng.execute(black_box(&data), black_box(&["Scaling"]));
                    black_box(results);
                })
            },
        );
    }

    group.finish();
}

fn bench_comparison_operators(c: &mut Criterion) {
    let mut group = c.benchmark_group("comparison_operators");

    for (op, value) in [
        ("$eq", 100),
        ("$gt", 99),
        ("$lt", 101),
        ("$gte", 100),
        ("$lte", 100),
    ]
    .iter()
    {
        let rules_json = format!(
            r#"
        {{
          "categories": {{
            "Compare": {{
              "stop_on_first": true,
              "rules": [
                {{
                  "id": "R1",
                  "priority": 1,
                  "conditions": {{"amount": {{"{op}": {value}}}}},
                  "action": "Test"
                }}
              ]
            }}
          }}
        }}
        "#,
            op = op,
            value = value
        );

        let ruleset: RuleSet = serde_json::from_str(&rules_json).unwrap();
        let engine = RuleEngine::new(ruleset);
        let data = json!({"amount": 100});

        group.bench_with_input(BenchmarkId::from_parameter(op), &engine, |b, eng| {
            b.iter(|| {
                let results = eng.execute(black_box(&data), black_box(&["Compare"]));
                black_box(results);
            })
        });
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_simple_rule_execution,
    bench_complex_rule_execution,
    bench_nested_field_access,
    bench_rule_count_scaling,
    bench_comparison_operators
);

criterion_main!(benches);
