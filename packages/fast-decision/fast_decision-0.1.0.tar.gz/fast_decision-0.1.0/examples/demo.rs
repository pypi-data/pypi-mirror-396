use fast_decision::{RuleEngine, RuleSet};
use log::{debug, info};
use serde_json::json;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();

    let rules_json = r#"
        {
          "categories": {
            "Complex_Pricing": {
              "stop_on_first": false,
              "rules": [
                {
                  "id": "R1_HighValue",
                  "priority": 1,
                  "conditions": {
                    "$or": [
                      {"user.details.tier": {"$eq": "Platinum"}},
                      {"transaction.amount": {"$gt": 500}}
                    ]
                  },
                  "action": "Flag_for_Premium_Discount"
                },
                {
                  "id": "R2_MediumRange",
                  "priority": 10,
                  "conditions": {
                    "transaction.amount": {"$gte": 100, "$lt": 500},
                    "user.details.tier": {"$ne": "Bronze"}
                  },
                  "action": "Standard_Discount"
                },
                {
                  "id": "R3_SmallTransaction",
                  "priority": 20,
                  "conditions": {
                    "transaction.amount": {"$lte": 99.99}
                  },
                  "action": "No_Discount"
                }
              ]
            }
          }
        }
    "#;

    info!("Loading rules from JSON");
    let ruleset: RuleSet = serde_json::from_str(rules_json)?;
    let engine = RuleEngine::new(ruleset);
    debug!("Rules loaded and engine initialized");

    let categories_to_run = vec!["Complex_Pricing"];

    info!("\n=== TEST 1: Platinum + $550 ===");
    let test1 = json!({
        "user": {"id": 123, "details": {"tier": "Platinum"}},
        "transaction": {"amount": 550.75, "currency": "USD"}
    });
    debug!("Input data: {}", test1);
    let result1 = engine.execute(&test1, &categories_to_run);
    info!("Triggered rules: {:?}", result1);

    info!("\n=== TEST 2: Silver + $250 ===");
    let test2 = json!({
        "user": {"id": 456, "details": {"tier": "Silver"}},
        "transaction": {"amount": 250.0, "currency": "USD"}
    });
    debug!("Input data: {}", test2);
    let result2 = engine.execute(&test2, &categories_to_run);
    info!("Triggered rules: {:?}", result2);

    info!("\n=== TEST 3: Small transaction $50 ===");
    let test3 = json!({
        "user": {"id": 789, "details": {"tier": "Gold"}},
        "transaction": {"amount": 50.0, "currency": "USD"}
    });
    debug!("Input data: {}", test3);
    let result3 = engine.execute(&test3, &categories_to_run);
    info!("Triggered rules: {:?}", result3);

    info!("\n=== TEST 4: Bronze + $200 (should not pass R2) ===");
    let test4 = json!({
        "user": {"id": 999, "details": {"tier": "Bronze"}},
        "transaction": {"amount": 200.0, "currency": "USD"}
    });
    debug!("Input data: {}", test4);
    let result4 = engine.execute(&test4, &categories_to_run);
    info!("Triggered rules: {:?}", result4);

    Ok(())
}
