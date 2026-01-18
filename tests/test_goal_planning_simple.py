"""
Simple test to verify goal planning tools work correctly
This doesn't require API keys - just tests the tool functions
"""

from src.core.tools.goal_planning import (
    create_goal,
    list_goals,
    calculate_savings_required,
    prioritize_goals,
    analyze_goal_tradeoffs,
    check_goal_feasibility,
    update_goal_progress,
    get_goal_categories,
    GOALS_SESSION
)

print("=" * 70)
print("🧪 Testing Goal Planning Tools")
print("=" * 70)

# Test 1: Get goal categories
print("\n1. Testing get_goal_categories()...")
categories_result = get_goal_categories.invoke({})
print(categories_result)

# Test 2: Create an emergency fund goal
print("\n2. Testing create_goal() - Emergency Fund...")
goal1_result = create_goal.invoke({
    "name": "Emergency Fund",
    "target_amount": 10000,
    "target_date": "2027-01-16",
    "current_savings": 2000,
    "priority": "high",
    "risk_tolerance": "low",
    "is_investment_based": False,
    "category": "Emergency Fund",
    "notes": "6 months of expenses"
})
print(goal1_result)

# Test 3: Create a vacation goal
print("\n3. Testing create_goal() - Vacation...")
goal2_result = create_goal.invoke({
    "name": "Dream Vacation to Japan",
    "target_amount": 5000,
    "target_date": "2026-07-16",
    "current_savings": 500,
    "priority": "medium",
    "risk_tolerance": "medium",
    "is_investment_based": True,
    "category": "Vacation",
    "notes": "Two-week trip"
})
print(goal2_result)

# Test 4: Create a retirement goal
print("\n4. Testing create_goal() - Retirement...")
goal3_result = create_goal.invoke({
    "name": "Retirement Savings",
    "target_amount": 50000,
    "target_date": "2031-01-16",
    "current_savings": 10000,
    "priority": "high",
    "risk_tolerance": "high",
    "is_investment_based": True,
    "category": "Retirement",
    "notes": "Long-term retirement account"
})
print(goal3_result)

# Test 5: List all goals
print("\n5. Testing list_goals()...")
goals_list = list_goals.invoke({})
print(goals_list)

# Test 6: Calculate savings required for goal 1
print("\n6. Testing calculate_savings_required() for Emergency Fund (ID: 1)...")
savings_calc = calculate_savings_required.invoke({"goal_id": 1})
print(savings_calc)

# Test 7: Calculate savings required for goal 2 (investment-based)
print("\n7. Testing calculate_savings_required() for Vacation (ID: 2)...")
savings_calc2 = calculate_savings_required.invoke({"goal_id": 2})
print(savings_calc2)

# Test 8: Prioritize all goals
print("\n8. Testing prioritize_goals()...")
priority_result = prioritize_goals.invoke({})
print(priority_result)

# Test 9: Analyze trade-offs with a budget
print("\n9. Testing analyze_goal_tradeoffs() with $1500/month budget...")
tradeoff_result = analyze_goal_tradeoffs.invoke({"monthly_budget": 1500})
print(tradeoff_result)

# Test 10: Check feasibility of emergency fund goal
print("\n10. Testing check_goal_feasibility() for Emergency Fund...")
feasibility_result = check_goal_feasibility.invoke({
    "goal_id": 1,
    "monthly_budget": 700
})
print(feasibility_result)

# Test 11: Update progress on a goal
print("\n11. Testing update_goal_progress()...")
update_result = update_goal_progress.invoke({
    "goal_id": 1,
    "new_current_savings": 3500
})
print(update_result)

# Test 12: List goals after update
print("\n12. Testing list_goals() after update...")
goals_list_updated = list_goals.invoke({})
print(goals_list_updated)

print("\n" + "=" * 70)
print("✓ All tool tests completed successfully!")
print("=" * 70)
print(f"\nCurrent session has {len(GOALS_SESSION['goals'])} goals")
