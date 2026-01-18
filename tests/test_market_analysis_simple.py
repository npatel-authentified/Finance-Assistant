"""
Simple test to verify market analysis tools work correctly
Tests with real market data from yfinance
"""

from src.core.tools.market_analysis import (
    get_market_overview,
    analyze_sector_performance,
    get_stock_technicals,
    compare_stock_fundamentals,
    get_market_sentiment,
    get_stock_news,
    get_earnings_calendar,
    analyze_stock_momentum,
)

print("=" * 70)
print("🧪 Testing Market Analysis Tools")
print("=" * 70)

# Test 1: Market Overview
print("\n1. Testing get_market_overview()...")
print("-" * 70)
market_overview = get_market_overview.invoke({})
print(market_overview)

# Test 2: Sector Performance (1 month)
print("\n\n2. Testing analyze_sector_performance() for 1 month...")
print("-" * 70)
sector_perf = analyze_sector_performance.invoke({"period": "1mo"})
print(sector_perf)

# Test 3: Stock Technicals for AAPL
print("\n\n3. Testing get_stock_technicals() for AAPL...")
print("-" * 70)
aapl_technicals = get_stock_technicals.invoke({"ticker": "AAPL"})
print(aapl_technicals)

# Test 4: Compare Fundamentals
print("\n\n4. Testing compare_stock_fundamentals() for AAPL, MSFT, GOOGL...")
print("-" * 70)
comparison = compare_stock_fundamentals.invoke({"tickers": "AAPL,MSFT,GOOGL"})
print(comparison)

# Test 5: Market Sentiment
print("\n\n5. Testing get_market_sentiment()...")
print("-" * 70)
sentiment = get_market_sentiment.invoke({})
print(sentiment)

# Test 6: Stock News
print("\n\n6. Testing get_stock_news() for TSLA...")
print("-" * 70)
news = get_stock_news.invoke({"ticker": "TSLA", "limit": 3})
print(news)

# Test 7: Earnings Calendar
print("\n\n7. Testing get_earnings_calendar() for NVDA...")
print("-" * 70)
earnings = get_earnings_calendar.invoke({"ticker": "NVDA"})
print(earnings)

# Test 8: Stock Momentum Analysis
print("\n\n8. Testing analyze_stock_momentum() for AAPL...")
print("-" * 70)
momentum = analyze_stock_momentum.invoke({"ticker": "AAPL"})
print(momentum)

print("\n" + "=" * 70)
print("✓ All market analysis tool tests completed!")
print("=" * 70)
print("\nNote: Results may vary based on current market data and conditions.")
print("If any tools show errors, it may be due to:")
print("  • Market being closed")
print("  • Network connectivity issues")
print("  • Yahoo Finance API rate limits or outages")
