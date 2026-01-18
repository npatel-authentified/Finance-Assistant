"""
Market Analysis Tools

Comprehensive tools for analyzing market trends, indices, sectors, and individual stocks.
Focuses on macro market analysis and technical/fundamental research.
"""

from langchain.tools import tool
import yfinance as yf
from datetime import datetime

# Major market indices
MARKET_INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX (Volatility)": "^VIX"
}

# Sector ETFs for sector analysis
SECTOR_ETFS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Industrials": "XLI",
    "Consumer Staples": "XLP",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
    "Communication Services": "XLC"
}


@tool("get_market_overview", description="Get current overview of major market indices including S&P 500, Nasdaq, Dow Jones, Russell 2000, and VIX volatility index.")
def get_market_overview() -> str:
    """
    Get overview of major market indices with current prices and daily changes.

    Returns:
        str: Formatted market overview with prices, changes, and percentages
    """
    try:
        result = "📈 Market Overview (Major Indices)\n\n"

        for name, symbol in MARKET_INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")

                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = current_price - prev_close
                    pct_change = (change / prev_close) * 100

                    # Format with color indicators
                    indicator = "🟢" if change >= 0 else "🔴"

                    result += (
                        f"{indicator} {name} ({symbol})\n"
                        f"   Price: {current_price:,.2f}\n"
                        f"   Change: {change:+,.2f} ({pct_change:+.2f}%)\n\n"
                    )
                else:
                    result += f"⚠️  {name} ({symbol}): Insufficient data\n\n"

            except Exception as e:
                result += f"⚠️  {name} ({symbol}): Error - {str(e)}\n\n"

        # Add VIX interpretation
        result += "\n💡 VIX Interpretation:\n"
        result += "   < 15: Low volatility (calm market)\n"
        result += "   15-25: Normal volatility\n"
        result += "   > 25: High volatility (market stress)\n"

        return result

    except Exception as e:
        return f"Error getting market overview: {str(e)}"


@tool("analyze_sector_performance", description="Analyze performance across major market sectors using sector ETFs. Shows which sectors are leading or lagging.")
def analyze_sector_performance(period: str = "1mo") -> str:
    """
    Analyze sector performance across major market sectors.

    Args:
        period: Time period for analysis. Options: '1d', '5d', '1mo', '3mo', '6mo', '1y', 'ytd' (default: '1mo')

    Returns:
        str: Ranked sector performance with returns and analysis
    """
    try:
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', 'ytd']
        if period not in valid_periods:
            return f"Error: Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"

        sector_performance = []

        result = f"🏢 Sector Performance Analysis ({period})\n\n"

        for sector_name, etf_symbol in SECTOR_ETFS.items():
            try:
                ticker = yf.Ticker(etf_symbol)
                hist = ticker.history(period=period)

                if len(hist) >= 2:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    returns = ((end_price - start_price) / start_price) * 100

                    sector_performance.append({
                        'sector': sector_name,
                        'etf': etf_symbol,
                        'return': returns,
                        'current': end_price
                    })

            except Exception as e:
                result += f"⚠️  {sector_name}: Error - {str(e)}\n"

        # Sort by performance
        sector_performance.sort(key=lambda x: x['return'], reverse=True)

        # Display ranked sectors
        for i, sector in enumerate(sector_performance, 1):
            indicator = "🟢" if sector['return'] >= 0 else "🔴"
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

            result += (
                f"{rank_emoji} {indicator} {sector['sector']} ({sector['etf']})\n"
                f"      Return: {sector['return']:+.2f}%\n\n"
            )

        # Sector rotation insights
        if sector_performance:
            top_3 = sector_performance[:3]
            bottom_3 = sector_performance[-3:]

            result += "\n📊 Sector Rotation Insights:\n\n"
            result += f"🔥 Leading Sectors:\n"
            for sector in top_3:
                result += f"   • {sector['sector']} ({sector['return']:+.2f}%)\n"

            result += f"\n📉 Lagging Sectors:\n"
            for sector in bottom_3:
                result += f"   • {sector['sector']} ({sector['return']:+.2f}%)\n"

        return result

    except Exception as e:
        return f"Error analyzing sector performance: {str(e)}"


@tool("get_stock_technicals", description="Get technical analysis indicators for a stock including moving averages, RSI, and price trends.")
def get_stock_technicals(ticker: str, period: str = "3mo") -> str:
    """
    Calculate technical indicators for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period: Historical period for analysis (default: '3mo')

    Returns:
        str: Technical analysis with moving averages, RSI, and trend indicators
    """
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period)

        if hist.empty:
            return f"Error: No data found for ticker '{ticker}'"

        # Get current price
        current_price = hist['Close'].iloc[-1]

        # Calculate moving averages
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None

        # Calculate RSI (14-period)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # Calculate volume trend
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].iloc[-5:].mean()
        volume_trend = ((recent_volume - avg_volume) / avg_volume) * 100

        # 52-week high/low
        high_52w = hist['Close'].max()
        low_52w = hist['Close'].min()
        pct_from_high = ((current_price - high_52w) / high_52w) * 100
        pct_from_low = ((current_price - low_52w) / low_52w) * 100

        # Build result
        result = f"📊 Technical Analysis: {ticker.upper()}\n\n"
        result += f"Current Price: ${current_price:.2f}\n\n"

        # Moving Averages
        result += "Moving Averages:\n"
        result += f"  20-Day MA: ${ma_20:.2f} {'🟢 Above' if current_price > ma_20 else '🔴 Below'}\n"
        result += f"  50-Day MA: ${ma_50:.2f} {'🟢 Above' if current_price > ma_50 else '🔴 Below'}\n"
        if ma_200:
            result += f"  200-Day MA: ${ma_200:.2f} {'🟢 Above' if current_price > ma_200 else '🔴 Below'}\n"

        # RSI
        result += f"\nRSI (14-period): {current_rsi:.2f}\n"
        if current_rsi > 70:
            result += "  ⚠️  Overbought territory (> 70)\n"
        elif current_rsi < 30:
            result += "  ⚠️  Oversold territory (< 30)\n"
        else:
            result += "  ✓ Neutral range (30-70)\n"

        # Volume
        result += f"\nVolume Trend: {volume_trend:+.2f}%\n"
        result += f"  Avg Volume: {avg_volume:,.0f}\n"
        result += f"  Recent Avg: {recent_volume:,.0f}\n"

        # 52-week range
        result += f"\n52-Week Range:\n"
        result += f"  High: ${high_52w:.2f} ({pct_from_high:+.2f}% from current)\n"
        result += f"  Low: ${low_52w:.2f} ({pct_from_low:+.2f}% from current)\n"

        # Trend summary
        result += "\n📈 Trend Summary:\n"
        if current_price > ma_20 and current_price > ma_50:
            result += "  • Short-term trend: Bullish (above MA 20 & 50)\n"
        elif current_price < ma_20 and current_price < ma_50:
            result += "  • Short-term trend: Bearish (below MA 20 & 50)\n"
        else:
            result += "  • Short-term trend: Mixed\n"

        if ma_200:
            if current_price > ma_200:
                result += "  • Long-term trend: Bullish (above MA 200)\n"
            else:
                result += "  • Long-term trend: Bearish (below MA 200)\n"

        return result

    except Exception as e:
        return f"Error analyzing technicals for {ticker}: {str(e)}"


@tool("compare_stock_fundamentals", description="Compare fundamental metrics of multiple stocks side-by-side (P/E ratio, market cap, dividend yield, profit margins, etc.).")
def compare_stock_fundamentals(tickers: str) -> str:
    """
    Compare fundamental metrics across multiple stocks.

    Args:
        tickers: Comma-separated ticker symbols (e.g., 'AAPL,MSFT,GOOGL')

    Returns:
        str: Side-by-side comparison of fundamental metrics
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]

        if len(ticker_list) > 5:
            return "Error: Please limit comparison to 5 stocks or fewer"

        result = f"📊 Fundamental Comparison\n\n"
        result += f"Comparing: {', '.join(ticker_list)}\n\n"

        stocks_data = []

        for ticker_symbol in ticker_list:
            try:
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info

                stocks_data.append({
                    'symbol': ticker_symbol,
                    'name': info.get('longName', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', None),
                    'forward_pe': info.get('forwardPE', None),
                    'peg_ratio': info.get('pegRatio', None),
                    'div_yield': info.get('dividendYield', 0),
                    'profit_margin': info.get('profitMargins', None),
                    'roe': info.get('returnOnEquity', None),
                    'debt_to_equity': info.get('debtToEquity', None),
                    'revenue_growth': info.get('revenueGrowth', None),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A')
                })
            except Exception as e:
                result += f"⚠️  Error fetching {ticker_symbol}: {str(e)}\n"

        if not stocks_data:
            return "Error: Could not fetch data for any of the provided tickers"

        # Display comparison table
        for stock in stocks_data:
            result += f"\n{'='*60}\n"
            result += f"🏢 {stock['name']} ({stock['symbol']})\n"
            result += f"{'='*60}\n"
            result += f"Sector: {stock['sector']} | Industry: {stock['industry']}\n\n"

            # Valuation metrics
            result += "Valuation:\n"
            result += f"  Market Cap: ${stock['market_cap']:,.0f}\n" if stock['market_cap'] else "  Market Cap: N/A\n"
            result += f"  P/E Ratio: {stock['pe_ratio']:.2f}\n" if stock['pe_ratio'] else "  P/E Ratio: N/A\n"
            result += f"  Forward P/E: {stock['forward_pe']:.2f}\n" if stock['forward_pe'] else "  Forward P/E: N/A\n"
            result += f"  PEG Ratio: {stock['peg_ratio']:.2f}\n" if stock['peg_ratio'] else "  PEG Ratio: N/A\n"

            # Profitability
            result += "\nProfitability:\n"
            result += f"  Profit Margin: {stock['profit_margin']*100:.2f}%\n" if stock['profit_margin'] else "  Profit Margin: N/A\n"
            result += f"  Return on Equity: {stock['roe']*100:.2f}%\n" if stock['roe'] else "  Return on Equity: N/A\n"

            # Growth & Income
            result += "\nGrowth & Income:\n"
            result += f"  Revenue Growth: {stock['revenue_growth']*100:.2f}%\n" if stock['revenue_growth'] else "  Revenue Growth: N/A\n"
            result += f"  Dividend Yield: {stock['div_yield']*100:.2f}%\n" if stock['div_yield'] else "  Dividend Yield: N/A\n"

            # Financial Health
            result += "\nFinancial Health:\n"
            result += f"  Debt-to-Equity: {stock['debt_to_equity']:.2f}\n" if stock['debt_to_equity'] else "  Debt-to-Equity: N/A\n"

        # Quick comparison summary
        result += f"\n\n{'='*60}\n"
        result += "📈 Quick Comparison Summary\n"
        result += f"{'='*60}\n"

        # Lowest P/E
        pe_stocks = [s for s in stocks_data if s['pe_ratio']]
        if pe_stocks:
            lowest_pe = min(pe_stocks, key=lambda x: x['pe_ratio'])
            result += f"\n💰 Lowest P/E (Value): {lowest_pe['symbol']} (P/E: {lowest_pe['pe_ratio']:.2f})\n"

        # Highest dividend
        div_stocks = [s for s in stocks_data if s['div_yield']]
        if div_stocks:
            highest_div = max(div_stocks, key=lambda x: x['div_yield'])
            result += f"💵 Highest Dividend: {highest_div['symbol']} (Yield: {highest_div['div_yield']*100:.2f}%)\n"

        # Highest growth
        growth_stocks = [s for s in stocks_data if s['revenue_growth']]
        if growth_stocks:
            highest_growth = max(growth_stocks, key=lambda x: x['revenue_growth'])
            result += f"🚀 Highest Revenue Growth: {highest_growth['symbol']} ({highest_growth['revenue_growth']*100:.2f}%)\n"

        # Best ROE
        roe_stocks = [s for s in stocks_data if s['roe']]
        if roe_stocks:
            best_roe = max(roe_stocks, key=lambda x: x['roe'])
            result += f"📊 Best ROE: {best_roe['symbol']} (ROE: {best_roe['roe']*100:.2f}%)\n"

        return result

    except Exception as e:
        return f"Error comparing fundamentals: {str(e)}"


@tool("get_market_sentiment", description="Get market sentiment indicators including VIX volatility, put/call ratios, and recent market breadth.")
def get_market_sentiment() -> str:
    """
    Analyze market sentiment using volatility and breadth indicators.

    Returns:
        str: Market sentiment analysis with VIX, trends, and interpretation
    """
    try:
        result = "🎭 Market Sentiment Analysis\n\n"

        # VIX - Volatility Index
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="5d")

        if not vix_hist.empty:
            current_vix = vix_hist['Close'].iloc[-1]
            prev_vix = vix_hist['Close'].iloc[-2] if len(vix_hist) > 1 else current_vix
            vix_change = current_vix - prev_vix

            result += f"🎢 VIX (Fear Index): {current_vix:.2f}\n"
            result += f"   Change: {vix_change:+.2f}\n"

            if current_vix < 15:
                sentiment = "😌 Low Fear - Market is calm"
                color = "🟢"
            elif current_vix < 25:
                sentiment = "😐 Normal Volatility"
                color = "🟡"
            else:
                sentiment = "😰 High Fear - Market stress"
                color = "🔴"

            result += f"   {color} {sentiment}\n\n"

        # Major indices trend (short-term momentum)
        result += "📊 Market Breadth (Major Indices - 5 Day Trend):\n\n"

        indices_to_check = {
            "S&P 500": "^GSPC",
            "Nasdaq": "^IXIC",
            "Dow Jones": "^DJI"
        }

        positive_count = 0
        total_count = 0

        for name, symbol in indices_to_check.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")

                if len(hist) >= 2:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    change_pct = ((end_price - start_price) / start_price) * 100

                    indicator = "🟢" if change_pct >= 0 else "🔴"
                    result += f"  {indicator} {name}: {change_pct:+.2f}%\n"

                    if change_pct >= 0:
                        positive_count += 1
                    total_count += 1

            except Exception as e:
                result += f"  ⚠️  {name}: Error\n"

        # Market breadth interpretation
        if total_count > 0:
            breadth_pct = (positive_count / total_count) * 100
            result += f"\n📈 Market Breadth: {positive_count}/{total_count} indices positive ({breadth_pct:.0f}%)\n"

            if breadth_pct >= 67:
                result += "   ✅ Broad-based rally (strong)\n"
            elif breadth_pct >= 33:
                result += "   ⚠️  Mixed market (selective)\n"
            else:
                result += "   ❌ Broad-based decline (weak)\n"

        # Overall sentiment summary
        result += f"\n{'='*60}\n"
        result += "💭 Sentiment Summary:\n"
        result += f"{'='*60}\n"

        if current_vix < 20 and breadth_pct >= 50:
            result += "🟢 Overall: Positive sentiment\n"
            result += "   Market shows calm with broad participation\n"
        elif current_vix > 25 and breadth_pct < 50:
            result += "🔴 Overall: Negative sentiment\n"
            result += "   Elevated fear with weak breadth\n"
        else:
            result += "🟡 Overall: Mixed sentiment\n"
            result += "   Monitor for clearer directional signals\n"

        return result

    except Exception as e:
        return f"Error analyzing market sentiment: {str(e)}"


@tool("get_stock_news", description="Get recent news headlines and sentiment for a stock.")
def get_stock_news(ticker: str, limit: int = 5) -> str:
    """
    Get recent news for a stock.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of news items to return (default: 5)

    Returns:
        str: Recent news headlines with publishers and timestamps
    """
    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news

        if not news:
            return f"No recent news found for {ticker.upper()}"

        result = f"📰 Recent News: {ticker.upper()}\n\n"

        for i, article in enumerate(news[:limit], 1):
            title = article.get('title', 'No title')
            publisher = article.get('publisher', 'Unknown')
            timestamp = article.get('providerPublishTime', 0)

            # Convert timestamp to readable date
            if timestamp:
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            else:
                date_str = 'Unknown date'

            result += f"{i}. {title}\n"
            result += f"   📅 {date_str} | 🗞️  {publisher}\n\n"

        return result

    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


@tool("get_earnings_calendar", description="Get upcoming earnings date and estimates for a stock.")
def get_earnings_calendar(ticker: str) -> str:
    """
    Get earnings information for a stock.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Earnings date, estimates, and recent results
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        result = f"📅 Earnings Information: {ticker.upper()}\n\n"

        # Company name
        company_name = info.get('longName', ticker.upper())
        result += f"Company: {company_name}\n\n"

        # Earnings date
        earnings_date = info.get('earningsDate', None)
        if earnings_date:
            result += f"Next Earnings Date: {earnings_date}\n"
        else:
            result += "Next Earnings Date: Not available\n"

        # EPS estimates
        result += "\nEPS Information:\n"

        current_eps = info.get('trailingEps', None)
        forward_eps = info.get('forwardEps', None)

        if current_eps:
            result += f"  Current EPS (TTM): ${current_eps:.2f}\n"

        if forward_eps:
            result += f"  Forward EPS (Est): ${forward_eps:.2f}\n"
            if current_eps:
                eps_growth = ((forward_eps - current_eps) / abs(current_eps)) * 100
                result += f"  Expected Growth: {eps_growth:+.2f}%\n"

        # Revenue info
        result += "\nRevenue Information:\n"
        revenue = info.get('totalRevenue', None)
        revenue_growth = info.get('revenueGrowth', None)

        if revenue:
            result += f"  Total Revenue (TTM): ${revenue:,.0f}\n"

        if revenue_growth:
            result += f"  Revenue Growth: {revenue_growth*100:+.2f}%\n"

        # Earnings surprise (if available)
        earnings_quarterly_growth = info.get('earningsQuarterlyGrowth', None)
        if earnings_quarterly_growth:
            result += f"\nRecent Earnings Growth: {earnings_quarterly_growth*100:+.2f}%\n"

        return result

    except Exception as e:
        return f"Error fetching earnings info for {ticker}: {str(e)}"


@tool("analyze_stock_momentum", description="Analyze stock momentum and recent performance over multiple timeframes (1 day, 1 week, 1 month, 3 months, 1 year).")
def analyze_stock_momentum(ticker: str) -> str:
    """
    Analyze stock momentum across multiple timeframes.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Performance analysis across different time periods
    """
    try:
        stock = yf.Ticker(ticker.upper())

        # Get historical data for different periods
        periods = {
            "1 Day": "2d",
            "1 Week": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "Year-to-Date": "ytd"
        }

        result = f"🚀 Momentum Analysis: {ticker.upper()}\n\n"

        # Get current price first
        current_data = stock.history(period="1d")
        if current_data.empty:
            return f"Error: No data found for {ticker.upper()}"

        current_price = current_data['Close'].iloc[-1]
        result += f"Current Price: ${current_price:.2f}\n\n"
        result += "Performance by Period:\n"

        performance_data = []

        for period_name, period_code in periods.items():
            try:
                hist = stock.history(period=period_code)

                if len(hist) >= 2:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    returns = ((end_price - start_price) / start_price) * 100

                    indicator = "🟢" if returns >= 0 else "🔴"

                    performance_data.append({
                        'period': period_name,
                        'return': returns
                    })

                    result += f"  {indicator} {period_name:12s}: {returns:+7.2f}%\n"

            except Exception as e:
                result += f"  ⚠️  {period_name:12s}: Error\n"

        # Momentum assessment
        result += f"\n{'='*50}\n"
        result += "📊 Momentum Assessment:\n"
        result += f"{'='*50}\n"

        if performance_data:
            # Short-term momentum (1 day, 1 week, 1 month)
            short_term = [p['return'] for p in performance_data[:3]]
            short_term_avg = sum(short_term) / len(short_term) if short_term else 0

            # Long-term momentum (3mo, 6mo, 1y)
            long_term = [p['return'] for p in performance_data[3:6]]
            long_term_avg = sum(long_term) / len(long_term) if long_term else 0

            result += f"\nShort-term (1D-1M avg): {short_term_avg:+.2f}%\n"
            if short_term_avg > 5:
                result += "  🔥 Strong positive momentum\n"
            elif short_term_avg > 0:
                result += "  ✅ Positive momentum\n"
            elif short_term_avg > -5:
                result += "  ⚠️  Slight negative momentum\n"
            else:
                result += "  ❌ Strong negative momentum\n"

            result += f"\nLong-term (3M-1Y avg): {long_term_avg:+.2f}%\n"
            if long_term_avg > 15:
                result += "  🚀 Strong uptrend\n"
            elif long_term_avg > 0:
                result += "  ✅ Uptrend\n"
            elif long_term_avg > -15:
                result += "  ⚠️  Downtrend\n"
            else:
                result += "  ❌ Strong downtrend\n"

            # Trend consistency
            positive_periods = sum(1 for p in performance_data if p['return'] > 0)
            consistency = (positive_periods / len(performance_data)) * 100

            result += f"\nTrend Consistency: {positive_periods}/{len(performance_data)} periods positive ({consistency:.0f}%)\n"

        return result

    except Exception as e:
        return f"Error analyzing momentum for {ticker}: {str(e)}"
