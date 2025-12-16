#!/usr/bin/env python3

from fast_decision import FastDecision

def main():
    engine = FastDecision("rules.json")

    print("=== TEST 1: Priority sorting (Platinum tier) ===")
    data1 = {"user": {"tier": "Platinum"}, "transaction": {"amount": 100}}
    result1 = engine.execute(data1, categories=["Pricing"])
    print(f"Result: {result1}")
    print(f"Expected: ['R1_Platinum'] (priority 1, stop_on_first=true)")
    print(f"Success: {result1 == ['R1_Platinum']}\n")

    print("=== TEST 2: Second priority rule (Gold tier) ===")
    data2 = {"user": {"tier": "Gold"}, "transaction": {"amount": 100}}
    result2 = engine.execute(data2, categories=["Pricing"])
    print(f"Result: {result2}")
    print(f"Expected: ['R2_Gold'] (priority 1, stop_on_first=true)")
    print(f"Success: {result2 == ['R2_Gold']}\n")

    print("=== TEST 3: Third priority rule (Silver tier) ===")
    data3 = {"user": {"tier": "Silver"}, "transaction": {"amount": 100}}
    result3 = engine.execute(data3, categories=["Pricing"])
    print(f"Result: {result3}")
    print(f"Expected: ['R3_Silver'] (priority 20, stop_on_first=true)")
    print(f"Success: {result3 == ['R3_Silver']}\n")

    print("=== TEST 4: Multiple matches without stop_on_first (Fraud) ===")
    data4 = {"user": {"tier": "Gold"}, "transaction": {"amount": 15000}}
    result4 = engine.execute(data4, categories=["Fraud"])
    print(f"Result: {result4}")
    print(f"Expected: ['F1_HighAmount'] (stop_on_first=false)")
    print(f"Success: {result4 == ['F1_HighAmount']}\n")

    print("=== TEST 5: Multiple categories ===")
    data5 = {"user": {"tier": "Platinum"}, "transaction": {"amount": 15000}}
    result5 = engine.execute(data5, categories=["Pricing", "Fraud"])
    print(f"Result: {result5}")
    print(f"Expected: ['R1_Platinum', 'F1_HighAmount']")
    print(f"Success: {result5 == ['R1_Platinum', 'F1_HighAmount']}\n")

if __name__ == "__main__":
    main()
