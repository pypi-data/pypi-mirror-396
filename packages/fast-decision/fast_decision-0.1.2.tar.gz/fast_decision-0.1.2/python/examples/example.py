#!/usr/bin/env python3

from fast_decision import FastDecision

def main():
    print("Loading rules from rules.json...")
    engine = FastDecision("rules.json")

    test_data = {
        "user": {
            "id": 123,
            "tier": "Platinum",
            "age": 30
        },
        "transaction": {
            "amount": 550.75,
            "currency": "USD"
        }
    }

    print("\nExecuting rules for categories: ['Pricing']")
    triggered_rules = engine.execute(test_data, categories=["Pricing"])

    print(f"\nTriggered rules: {triggered_rules}")

    for rule_id in triggered_rules:
        print(f"\nExecuting action for rule: {rule_id}")

        if rule_id == "R1_Platinum":
            print("  → Applying 20% platinum discount")
        elif rule_id == "R2_Gold":
            print("  → Applying 10% gold discount")
        else:
            print(f"  → Unknown action for rule {rule_id}")

if __name__ == "__main__":
    main()
