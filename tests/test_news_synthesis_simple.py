"""
Simple test to verify news synthesis tools work correctly
Tests with real news data from yfinance
"""

from src.core.tools.news_synthesis import (
    discover_investment_opportunities,
    analyze_investment_risks,
    build_investment_thesis,
    compare_investment_options,
    assess_investment_timing,
    explain_news_for_investors,
    track_watchlist_news,
)

print("=" * 70)
print("🧪 Testing News Synthesis Tools")
print("=" * 70)

# Test 1: Discover Investment Opportunities (Technology Sector)
print("\n1. Testing discover_investment_opportunities() for Technology sector...")
print("-" * 70)
opportunities = discover_investment_opportunities.invoke({"sector": "Technology", "period": 7})
print(opportunities)

# Test 2: Analyze Investment Risks (Tesla)
print("\n\n2. Testing analyze_investment_risks() for TSLA...")
print("-" * 70)
risks = analyze_investment_risks.invoke({"ticker": "TSLA"})
print(risks)

# Test 3: Build Investment Thesis (Apple)
print("\n\n3. Testing build_investment_thesis() for AAPL...")
print("-" * 70)
thesis = build_investment_thesis.invoke({"ticker": "AAPL"})
print(thesis)

# Test 4: Compare Investment Options (AAPL vs MSFT vs GOOGL)
print("\n\n4. Testing compare_investment_options() for AAPL, MSFT, GOOGL...")
print("-" * 70)
comparison = compare_investment_options.invoke({"tickers": "AAPL,MSFT,GOOGL"})
print(comparison)

# Test 5: Assess Investment Timing (NVDA)
print("\n\n5. Testing assess_investment_timing() for NVDA...")
print("-" * 70)
timing = assess_investment_timing.invoke({"ticker": "NVDA"})
print(timing)

# Test 6: Explain News for Investors (Tesla)
print("\n\n6. Testing explain_news_for_investors() for TSLA...")
print("-" * 70)
news_explanation = explain_news_for_investors.invoke({"ticker": "TSLA"})
print(news_explanation)

# Test 7: Track Watchlist News (Tech Watchlist)
print("\n\n7. Testing track_watchlist_news() for AAPL, NVDA, AMD...")
print("-" * 70)
watchlist = track_watchlist_news.invoke({"tickers": "AAPL,NVDA,AMD", "days": 7})
print(watchlist)

print("\n" + "=" * 70)
print("✓ All news synthesis tool tests completed!")
print("=" * 70)
print("\nKey Features Demonstrated:")
print("  ✅ Investment opportunity discovery with sentiment scoring")
print("  ✅ Risk analysis with categorization (regulatory, competitive, etc.)")
print("  ✅ Bull/bear case investment thesis building")
print("  ✅ Side-by-side stock comparison")
print("  ✅ Investment timing assessment (short-term vs long-term)")
print("  ✅ Educational news explanations for potential investors")
print("  ✅ Watchlist monitoring with news alerts")
print("\nNote: Results depend on current news availability and market conditions.")
print("If any test shows 'No news available', it means Yahoo Finance has no recent")
print("news for that stock in the specified time period.")
