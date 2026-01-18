"""
Simple test to verify portfolio analysis tools work correctly
Tests with real portfolio data from yfinance
"""

from src.core.tools.portfolio_analysis import (
    get_portfolio_summary,
    analyze_portfolio_diversification,
    calculate_portfolio_performance,
    analyze_portfolio_risk,
    compare_portfolio_to_benchmark,
    get_rebalancing_recommendations,
    analyze_individual_position,
)

# Sample portfolio holdings
sample_portfolio = {
    "AAPL": 10,  # Apple
    "MSFT": 5,   # Microsoft
    "GOOGL": 3,  # Alphabet
}

# More diversified portfolio
diversified_portfolio = {
    "AAPL": 5,
    "MSFT": 5,
    "GOOGL": 3,
    "TSLA": 2,
    "NVDA": 4,
    "JPM": 8,
}

# Concentrated portfolio
concentrated_portfolio = {
    "AAPL": 50,  # Too much AAPL
    "MSFT": 2,
}

print("=" * 70)
print("🧪 Testing Portfolio Analysis Tools")
print("=" * 70)

# Test 1: Portfolio Summary
print("\n1. Testing get_portfolio_summary()...")
print("-" * 70)
summary = get_portfolio_summary.invoke({"holdings": sample_portfolio})
print(summary)

# Test 2: Diversification Analysis (Well-balanced)
print("\n\n2. Testing analyze_portfolio_diversification() - Diversified Portfolio...")
print("-" * 70)
diversification = analyze_portfolio_diversification.invoke({"holdings": diversified_portfolio})
print(diversification)

# Test 3: Diversification Analysis (Concentrated)
print("\n\n3. Testing analyze_portfolio_diversification() - Concentrated Portfolio...")
print("-" * 70)
diversification_concentrated = analyze_portfolio_diversification.invoke({"holdings": concentrated_portfolio})
print(diversification_concentrated)

# Test 4: Portfolio Performance
print("\n\n4. Testing calculate_portfolio_performance() for 1 year...")
print("-" * 70)
performance = calculate_portfolio_performance.invoke({"holdings": sample_portfolio, "period": "1y"})
print(performance)

# Test 5: Portfolio Risk
print("\n\n5. Testing analyze_portfolio_risk()...")
print("-" * 70)
risk = analyze_portfolio_risk.invoke({"holdings": sample_portfolio})
print(risk)

# Test 6: Benchmark Comparison
print("\n\n6. Testing compare_portfolio_to_benchmark() vs S&P 500...")
print("-" * 70)
benchmark = compare_portfolio_to_benchmark.invoke({"holdings": sample_portfolio, "benchmark": "^GSPC"})
print(benchmark)

# Test 7: Rebalancing Recommendations (Without Target)
print("\n\n7. Testing get_rebalancing_recommendations() - No target (check concentration)...")
print("-" * 70)
rebalancing = get_rebalancing_recommendations.invoke({"holdings": concentrated_portfolio})
print(rebalancing)

# Test 8: Rebalancing Recommendations (With Target)
print("\n\n8. Testing get_rebalancing_recommendations() - With target allocation...")
print("-" * 70)
target_alloc = {
    "AAPL": 20,
    "MSFT": 20,
    "GOOGL": 20,
    "TSLA": 20,
    "NVDA": 20
}
rebalancing_target = get_rebalancing_recommendations.invoke({
    "holdings": diversified_portfolio,
    "target_allocation": target_alloc
})
print(rebalancing_target)

# Test 9: Individual Position Analysis
print("\n\n9. Testing analyze_individual_position() for AAPL with 10 shares...")
print("-" * 70)
position = analyze_individual_position.invoke({"ticker": "AAPL", "shares": 10})
print(position)

print("\n" + "=" * 70)
print("✓ All portfolio analysis tool tests completed!")
print("=" * 70)
print("\nKey Improvements Over Old Version:")
print("  ✅ FIXED: diversification now uses dollar values (not share counts)")
print("  ✅ All tools return formatted strings (consistent)")
print("  ✅ Proper error handling that doesn't break type contracts")
print("  ✅ Added comprehensive risk metrics (volatility, Sharpe, beta)")
print("  ✅ Added performance tracking with individual stock contributions")
print("  ✅ Added rebalancing recommendations")
print("  ✅ User-friendly formatted output")
print("\nNote: Results may vary based on current market data.")
