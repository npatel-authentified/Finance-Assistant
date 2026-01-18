"""
News Synthesis Tools

Tools for synthesizing and contextualizing financial news for potential investors.
Focuses on investment research, due diligence, and opportunity discovery.
"""

from langchain.tools import tool
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict


def get_news_for_stock(ticker: str, days: int = 7) -> List[Dict]:
    """
    Internal helper to fetch news for a stock.

    Args:
        ticker: Stock ticker symbol
        days: Number of days to look back

    Returns:
        List of news articles with metadata
    """
    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news

        if not news:
            return []

        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_news = []

        for article in news[:20]:  # Limit to recent 20
            timestamp = article.get('providerPublishTime', 0)
            if timestamp:
                article_date = datetime.fromtimestamp(timestamp)
                if article_date >= cutoff_date:
                    filtered_news.append(article)

        return filtered_news
    except Exception:
        return []


def analyze_sentiment_score(news_articles: List[Dict]) -> Dict:
    """
    Simple sentiment analysis based on news titles and content.

    Returns:
        Dict with sentiment metrics
    """
    if not news_articles:
        return {
            'overall': 'neutral',
            'score': 50,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0
        }

    # Simple keyword-based sentiment (can be enhanced with LLM)
    positive_keywords = ['beat', 'surge', 'gain', 'profit', 'growth', 'up', 'rise',
                        'strong', 'exceed', 'outperform', 'success', 'innovation',
                        'partnership', 'expansion', 'record', 'breakthrough']

    negative_keywords = ['miss', 'fall', 'drop', 'loss', 'decline', 'down', 'weak',
                        'disappoint', 'concern', 'risk', 'lawsuit', 'recall', 'cut',
                        'layoff', 'investigation', 'penalty', 'warning']

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for article in news_articles:
        title = article.get('title', '').lower()

        pos_score = sum(1 for kw in positive_keywords if kw in title)
        neg_score = sum(1 for kw in negative_keywords if kw in title)

        if pos_score > neg_score:
            positive_count += 1
        elif neg_score > pos_score:
            negative_count += 1
        else:
            neutral_count += 1

    total = len(news_articles)
    score = int(((positive_count - negative_count) / total + 1) * 50)  # Scale 0-100

    if score >= 65:
        overall = 'positive'
    elif score <= 35:
        overall = 'negative'
    else:
        overall = 'mixed'

    return {
        'overall': overall,
        'score': score,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count
    }


@tool("discover_investment_opportunities", description="Discover stocks with positive news momentum in a specific sector or across the market. Useful for finding investment ideas.")
def discover_investment_opportunities(sector: str = "Technology", period: int = 7) -> str:
    """
    Discover investment opportunities based on recent news sentiment.

    Args:
        sector: Sector to analyze (Technology, Healthcare, Finance, Energy, Consumer)
        period: Days to look back (default: 7)

    Returns:
        str: Investment opportunities with sentiment analysis
    """
    try:
        # Sector to stock mapping (major stocks per sector)
        sector_stocks = {
            "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA"],
            "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "LLY"],
            "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C"],
            "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC"],
            "Consumer": ["AMZN", "WMT", "HD", "MCD", "NKE", "SBUX"]
        }

        stocks = sector_stocks.get(sector, sector_stocks["Technology"])

        result = f"🔍 Investment Opportunities: {sector} Sector (Last {period} Days)\n\n"

        opportunities = []

        for ticker in stocks:
            try:
                news = get_news_for_stock(ticker, period)
                if not news:
                    continue

                sentiment = analyze_sentiment_score(news)

                # Get basic stock info
                stock = yf.Ticker(ticker)
                info = stock.info
                company_name = info.get('longName', ticker)

                opportunities.append({
                    'ticker': ticker,
                    'name': company_name,
                    'sentiment': sentiment,
                    'news_count': len(news),
                    'recent_news': news[:3]
                })

            except Exception:
                continue

        # Sort by sentiment score
        opportunities.sort(key=lambda x: x['sentiment']['score'], reverse=True)

        if not opportunities:
            return f"No significant news found for {sector} sector in the last {period} days."

        # Display top opportunities
        result += "📈 STRONG POSITIVE MOMENTUM\n"
        result += "=" * 70 + "\n\n"

        top_opportunities = [opp for opp in opportunities if opp['sentiment']['score'] >= 65]

        if not top_opportunities:
            result += "No stocks with strongly positive sentiment found.\n\n"
        else:
            for i, opp in enumerate(top_opportunities[:3], 1):
                sentiment = opp['sentiment']
                indicator = "🟢" if sentiment['overall'] == 'positive' else "🟡"

                result += f"{i}. {indicator} {opp['name']} ({opp['ticker']})\n"
                result += f"   Sentiment Score: {sentiment['score']}/100\n"
                result += f"   News Volume: {opp['news_count']} articles\n"
                result += f"   Positive: {sentiment['positive_count']} | "
                result += f"Negative: {sentiment['negative_count']} | "
                result += f"Neutral: {sentiment['neutral_count']}\n\n"

                result += "   Recent Headlines:\n"
                for article in opp['recent_news'][:2]:
                    title = article.get('title', 'No title')
                    result += f"   • {title}\n"

                result += "\n   💡 Investment Consideration:\n"
                if sentiment['score'] >= 80:
                    result += "   Very strong positive news momentum. Research fundamentals\n"
                    result += "   and valuation before investing.\n"
                elif sentiment['score'] >= 65:
                    result += "   Positive news trend. Good candidate for further research.\n"

                result += "\n"

        # Show moderate opportunities
        moderate_opportunities = [opp for opp in opportunities if 50 < opp['sentiment']['score'] < 65]

        if moderate_opportunities:
            result += "\n📊 MODERATE SENTIMENT\n"
            result += "=" * 70 + "\n\n"

            for opp in moderate_opportunities[:2]:
                result += f"• {opp['name']} ({opp['ticker']})\n"
                result += f"  Score: {opp['sentiment']['score']}/100 - Mixed news\n\n"

        result += "\n💡 Next Steps:\n"
        result += "• Use 'build_investment_thesis' for detailed analysis\n"
        result += "• Use 'analyze_investment_risks' to assess risks\n"
        result += "• Use 'compare_investment_options' to compare stocks\n"

        return result

    except Exception as e:
        return f"Error discovering opportunities: {str(e)}"


@tool("analyze_investment_risks", description="Analyze investment risks for a stock based on recent news. Essential for due diligence before investing.")
def analyze_investment_risks(ticker: str) -> str:
    """
    Analyze investment risks based on recent news.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Comprehensive risk analysis
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        company_name = info.get('longName', ticker.upper())

        result = f"⚠️  Investment Risk Analysis: {ticker.upper()}\n\n"
        result += f"Company: {company_name}\n\n"

        # Get news
        news = get_news_for_stock(ticker, days=90)

        if not news:
            return f"No recent news found for {ticker.upper()} to analyze risks."

        # Categorize risks based on keywords
        risk_categories = {
            'regulatory': ['investigation', 'lawsuit', 'regulatory', 'fine', 'penalty',
                          'antitrust', 'compliance', 'sec', 'ftc'],
            'competitive': ['competition', 'competitor', 'market share', 'rival', 'pressure'],
            'operational': ['recall', 'delay', 'production', 'supply chain', 'disruption',
                           'shortage', 'manufacturing'],
            'financial': ['debt', 'loss', 'earnings miss', 'revenue decline', 'margin',
                         'cash flow', 'bankruptcy'],
            'market': ['volatility', 'selloff', 'downturn', 'bearish', 'correction']
        }

        risk_news = defaultdict(list)

        for article in news:
            title = article.get('title', '').lower()

            for category, keywords in risk_categories.items():
                if any(kw in title for kw in keywords):
                    risk_news[category].append(article)

        # Display risk analysis
        if not risk_news:
            result += "🟢 LOW RISK PROFILE\n\n"
            result += "No major risk signals detected in recent news.\n"
            result += "This suggests a relatively stable news environment.\n\n"
            result += "⚠️  Note: Absence of negative news doesn't guarantee safety.\n"
            result += "Always research fundamentals, valuation, and industry trends.\n"
        else:
            result += "🔴 IDENTIFIED RISK AREAS\n"
            result += "=" * 70 + "\n\n"

            risk_levels = {
                'regulatory': 'HIGH',
                'financial': 'HIGH',
                'operational': 'MEDIUM',
                'competitive': 'MEDIUM',
                'market': 'LOW'
            }

            for category, articles in sorted(risk_news.items(),
                                            key=lambda x: len(x[1]),
                                            reverse=True):
                count = len(articles)
                level = risk_levels.get(category, 'MEDIUM')

                if level == 'HIGH':
                    icon = "🔴"
                elif level == 'MEDIUM':
                    icon = "🟡"
                else:
                    icon = "🟢"

                result += f"{icon} {category.upper()} RISK ({level})\n"
                result += f"   News Articles: {count}\n\n"

                result += "   Recent Developments:\n"
                for article in articles[:2]:
                    title = article.get('title', 'No title')
                    result += f"   • {title}\n"

                result += "\n   💭 Investment Implication:\n"

                if category == 'regulatory':
                    result += "   Regulatory issues can lead to fines, restrictions, or\n"
                    result += "   changes in business model. Monitor closely.\n"
                elif category == 'competitive':
                    result += "   Increased competition may pressure margins and market\n"
                    result += "   share. Assess competitive advantages.\n"
                elif category == 'operational':
                    result += "   Operational issues can impact near-term revenue and\n"
                    result += "   profitability. Usually temporary but worth monitoring.\n"
                elif category == 'financial':
                    result += "   Financial risks are serious. Review financial statements\n"
                    result += "   and debt levels carefully.\n"
                else:
                    result += "   Market-related risks affect all stocks. Consider broader\n"
                    result += "   market conditions in timing decisions.\n"

                result += "\n"

        # Overall risk assessment
        result += "=" * 70 + "\n"
        result += "📊 OVERALL RISK ASSESSMENT\n"
        result += "=" * 70 + "\n\n"

        high_risk_count = len([c for c in risk_news.keys() if c in ['regulatory', 'financial']])
        medium_risk_count = len([c for c in risk_news.keys() if c in ['operational', 'competitive']])

        if high_risk_count >= 2:
            result += "⚠️  HIGH RISK PROFILE\n\n"
            result += "Multiple serious risk factors identified. Proceed with caution.\n"
            result += "Recommended: Thorough research and possibly smaller position size.\n"
        elif high_risk_count == 1 or medium_risk_count >= 2:
            result += "🟡 MEDIUM RISK PROFILE\n\n"
            result += "Some risk factors present. Normal for most investments.\n"
            result += "Recommended: Understand each risk before investing.\n"
        else:
            result += "🟢 LOWER RISK PROFILE\n\n"
            result += "Limited risk signals in recent news.\n"
            result += "Recommended: Still research fundamentals and valuation.\n"

        result += "\n💡 Due Diligence Checklist:\n"
        result += "• Review latest earnings report\n"
        result += "• Check debt-to-equity ratio\n"
        result += "• Understand revenue sources\n"
        result += "• Research competitive position\n"
        result += "• Evaluate valuation (P/E, PEG ratios)\n"

        return result

    except Exception as e:
        return f"Error analyzing risks for {ticker}: {str(e)}"


@tool("build_investment_thesis", description="Build a comprehensive investment thesis with bull case, bear case, and key catalysts for a stock.")
def build_investment_thesis(ticker: str) -> str:
    """
    Build investment thesis based on news analysis.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Investment thesis with bull/bear cases
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        company_name = info.get('longName', ticker.upper())
        sector = info.get('sector', 'Unknown')

        result = f"📊 Investment Thesis: {ticker.upper()}\n\n"
        result += f"Company: {company_name}\n"
        result += f"Sector: {sector}\n\n"

        # Get news
        news = get_news_for_stock(ticker, days=90)

        if not news:
            return f"Insufficient news data to build thesis for {ticker.upper()}"

        sentiment = analyze_sentiment_score(news)

        result += "=" * 70 + "\n"
        result += "📈 INVESTMENT THESIS\n"
        result += "=" * 70 + "\n\n"

        # Bull case
        result += "🟢 THE BULL CASE (Reasons to Consider Investing)\n\n"

        positive_news = [n for n in news if any(kw in n.get('title', '').lower()
                        for kw in ['beat', 'growth', 'profit', 'strong', 'success',
                                  'innovation', 'partnership', 'expansion'])]

        if positive_news:
            result += f"Based on {len(positive_news)} positive developments:\n\n"
            for i, article in enumerate(positive_news[:3], 1):
                title = article.get('title', 'No title')
                result += f"{i}. {title}\n"

            result += "\n💡 Positive Signals:\n"
            result += "• Recent news momentum is favorable\n"
            result += "• Market appears optimistic about company prospects\n"

            if sentiment['score'] >= 70:
                result += "• Strong positive sentiment suggests confidence\n"
        else:
            result += "Limited positive news in recent period.\n"
            result += "Consider waiting for positive catalysts.\n"

        result += "\n"

        # Bear case
        result += "🔴 THE BEAR CASE (Risks and Concerns)\n\n"

        negative_news = [n for n in news if any(kw in n.get('title', '').lower()
                        for kw in ['miss', 'fall', 'concern', 'risk', 'lawsuit',
                                  'decline', 'weak', 'loss'])]

        if negative_news:
            result += f"Based on {len(negative_news)} concerning developments:\n\n"
            for i, article in enumerate(negative_news[:3], 1):
                title = article.get('title', 'No title')
                result += f"{i}. {title}\n"

            result += "\n💡 Risk Factors:\n"
            result += "• Negative news presents headwinds\n"
            result += "• Market has concerns about certain aspects\n"

            if sentiment['score'] <= 40:
                result += "• Low sentiment suggests significant challenges\n"
        else:
            result += "No major negative news in recent period.\n"
            result += "However, absence of bad news doesn't guarantee success.\n"

        result += "\n"

        # Key metrics from info
        result += "=" * 70 + "\n"
        result += "📊 KEY METRICS (For Context)\n"
        result += "=" * 70 + "\n\n"

        pe_ratio = info.get('trailingPE')
        market_cap = info.get('marketCap')
        beta = info.get('beta')

        if pe_ratio:
            result += f"P/E Ratio: {pe_ratio:.2f}\n"
            if pe_ratio > 30:
                result += "  (Higher than market average - growth premium or expensive)\n"
            elif pe_ratio < 15:
                result += "  (Below market average - value opportunity or concerns)\n"

        if market_cap:
            result += f"Market Cap: ${market_cap:,.0f}\n"

        if beta:
            result += f"Beta: {beta:.2f}\n"
            if beta > 1.3:
                result += "  (More volatile than market)\n"
            elif beta < 0.7:
                result += "  (Less volatile than market)\n"

        result += "\n"

        # Investment recommendation framework
        result += "=" * 70 + "\n"
        result += "🎯 INVESTMENT DECISION FRAMEWORK\n"
        result += "=" * 70 + "\n\n"

        result += "This stock may be suitable if you:\n"

        if sentiment['score'] >= 65:
            result += "✅ Believe in the positive momentum continuing\n"
            result += "✅ Are comfortable with current valuation\n"
        elif sentiment['score'] <= 35:
            result += "⚠️  Can tolerate significant near-term volatility\n"
            result += "⚠️  See long-term value despite current challenges\n"
        else:
            result += "○ Accept mixed signals and uncertain outlook\n"
            result += "○ Have patience for clarity to emerge\n"

        result += f"✅ Understand the {sector} sector\n"
        result += "✅ Have 3-5+ year investment horizon\n"
        result += "✅ Have researched company fundamentals\n\n"

        result += "Consider avoiding if you:\n"
        result += "❌ Need guaranteed returns or low risk\n"
        result += "❌ Are investing short-term (< 1 year)\n"
        result += "❌ Don't understand the business model\n"

        result += "\n💭 QUESTIONS TO ASK YOURSELF:\n\n"
        result += "Before investing in " + ticker.upper() + ":\n"
        result += "1. Do I understand how this company makes money?\n"
        result += "2. Can I hold through 20-30% price swings?\n"
        result += "3. Have I compared to alternatives in this sector?\n"
        result += "4. Is my position size appropriate (5-10% max)?\n"
        result += "5. What would make me sell this investment?\n"

        return result

    except Exception as e:
        return f"Error building thesis for {ticker}: {str(e)}"


@tool("compare_investment_options", description="Compare multiple stocks side-by-side based on recent news sentiment and metrics. Helps choose between investment options.")
def compare_investment_options(tickers: str) -> str:
    """
    Compare investment options based on news analysis.

    Args:
        tickers: Comma-separated ticker symbols (e.g., 'AAPL,MSFT,GOOGL')

    Returns:
        str: Side-by-side comparison
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]

        if len(ticker_list) > 4:
            return "Error: Please limit comparison to 4 stocks maximum"

        if len(ticker_list) < 2:
            return "Error: Please provide at least 2 stocks to compare"

        result = f"⚖️  Investment Comparison\n\n"
        result += f"Comparing: {', '.join(ticker_list)}\n\n"

        comparisons = []

        for ticker in ticker_list:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                news = get_news_for_stock(ticker, days=30)

                sentiment = analyze_sentiment_score(news)

                comparisons.append({
                    'ticker': ticker,
                    'name': info.get('longName', ticker),
                    'sentiment': sentiment,
                    'pe': info.get('trailingPE'),
                    'beta': info.get('beta'),
                    'market_cap': info.get('marketCap'),
                    'news_count': len(news)
                })

            except Exception:
                continue

        if len(comparisons) < 2:
            return "Error: Could not fetch data for enough stocks to compare"

        # Sentiment comparison
        result += "=" * 70 + "\n"
        result += "📊 NEWS SENTIMENT COMPARISON (30 Days)\n"
        result += "=" * 70 + "\n\n"

        for comp in comparisons:
            score = comp['sentiment']['score']

            if score >= 65:
                indicator = "🟢"
                level = "Positive"
            elif score <= 35:
                indicator = "🔴"
                level = "Negative"
            else:
                indicator = "🟡"
                level = "Mixed"

            result += f"{indicator} {comp['ticker']}: {level} (Score: {score}/100)\n"
            result += f"   News Volume: {comp['news_count']} articles\n"
            result += f"   Positive: {comp['sentiment']['positive_count']} | "
            result += f"Negative: {comp['sentiment']['negative_count']}\n\n"

        # Risk comparison (using beta)
        result += "=" * 70 + "\n"
        result += "⚠️  VOLATILITY COMPARISON (Risk Level)\n"
        result += "=" * 70 + "\n\n"

        beta_stocks = [c for c in comparisons if c['beta']]
        if beta_stocks:
            beta_stocks.sort(key=lambda x: x['beta'])

            result += "Lower Risk → Higher Risk:\n\n"
            for comp in beta_stocks:
                beta = comp['beta']
                if beta < 0.8:
                    risk_level = "Lower Risk (Defensive)"
                elif beta < 1.2:
                    risk_level = "Market Average Risk"
                else:
                    risk_level = "Higher Risk (Aggressive)"

                result += f"  {comp['ticker']}: Beta {beta:.2f} - {risk_level}\n"

        result += "\n"

        # Valuation comparison
        result += "=" * 70 + "\n"
        result += "💰 VALUATION COMPARISON (P/E Ratio)\n"
        result += "=" * 70 + "\n\n"

        pe_stocks = [c for c in comparisons if c['pe']]
        if pe_stocks:
            pe_stocks.sort(key=lambda x: x['pe'])

            result += "Better Value → More Expensive:\n\n"
            for comp in pe_stocks:
                pe = comp['pe']
                if pe < 15:
                    val_level = "Value Territory"
                elif pe < 25:
                    val_level = "Fair Value"
                else:
                    val_level = "Growth Premium / Expensive"

                result += f"  {comp['ticker']}: P/E {pe:.1f} - {val_level}\n"

        result += "\n"

        # Investment decision guide
        result += "=" * 70 + "\n"
        result += "🎯 INVESTMENT DECISION GUIDE\n"
        result += "=" * 70 + "\n\n"

        # Find best in each category
        best_sentiment = max(comparisons, key=lambda x: x['sentiment']['score'])
        lowest_risk = min([c for c in comparisons if c['beta']],
                         key=lambda x: x['beta']) if beta_stocks else None
        best_value = min([c for c in comparisons if c['pe']],
                        key=lambda x: x['pe']) if pe_stocks else None

        result += f"🟢 Best News Sentiment: {best_sentiment['ticker']}\n"
        result += f"   Choose if you want momentum and positive news flow\n\n"

        if lowest_risk:
            result += f"🛡️  Lowest Volatility: {lowest_risk['ticker']}\n"
            result += f"   Choose if you want stability and lower risk\n\n"

        if best_value:
            result += f"💰 Best Valuation: {best_value['ticker']}\n"
            result += f"   Choose if you want value and reasonable price\n\n"

        result += "💡 Remember:\n"
        result += "• No single metric tells the whole story\n"
        result += "• Consider your investment goals and risk tolerance\n"
        result += "• Research each company's business model\n"
        result += "• Diversification is important - consider owning multiple\n"

        return result

    except Exception as e:
        return f"Error comparing stocks: {str(e)}"


@tool("assess_investment_timing", description="Assess whether now is a good time to invest in a stock based on recent news and upcoming catalysts.")
def assess_investment_timing(ticker: str) -> str:
    """
    Assess investment timing based on news and catalysts.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Timing assessment and recommendations
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        company_name = info.get('longName', ticker.upper())

        result = f"⏰ Investment Timing Assessment: {ticker.upper()}\n\n"
        result += f"Company: {company_name}\n\n"

        # Get recent news
        news_recent = get_news_for_stock(ticker, days=7)
        news_30d = get_news_for_stock(ticker, days=30)

        sentiment_7d = analyze_sentiment_score(news_recent)
        sentiment_30d = analyze_sentiment_score(news_30d)

        result += "=" * 70 + "\n"
        result += "📊 CURRENT STATUS\n"
        result += "=" * 70 + "\n\n"

        # Momentum analysis
        result += "News Momentum:\n"
        result += f"• Last 7 days: {sentiment_7d['overall'].title()} (Score: {sentiment_7d['score']}/100)\n"
        result += f"• Last 30 days: {sentiment_30d['overall'].title()} (Score: {sentiment_30d['score']}/100)\n\n"

        if sentiment_7d['score'] > sentiment_30d['score'] + 10:
            result += "📈 Trend: Improving (recent news more positive)\n"
            momentum = "improving"
        elif sentiment_7d['score'] < sentiment_30d['score'] - 10:
            result += "📉 Trend: Declining (recent news more negative)\n"
            momentum = "declining"
        else:
            result += "➡️  Trend: Stable\n"
            momentum = "stable"

        result += "\n"

        # Timing indicators
        result += "=" * 70 + "\n"
        result += "🟢 POSITIVE TIMING INDICATORS\n"
        result += "=" * 70 + "\n\n"

        positive_indicators = []

        if sentiment_7d['score'] >= 65:
            positive_indicators.append("Strong positive news momentum")
            result += "• Strong positive news momentum\n"

        if momentum == "improving":
            positive_indicators.append("Sentiment trend improving")
            result += "• Sentiment trend improving\n"

        if not positive_indicators:
            result += "• Limited positive timing signals\n"

        result += "\n"

        result += "=" * 70 + "\n"
        result += "🔴 CAUTIONARY TIMING INDICATORS\n"
        result += "=" * 70 + "\n\n"

        negative_indicators = []

        if sentiment_7d['score'] <= 35:
            negative_indicators.append("Negative news sentiment")
            result += "• Negative news sentiment\n"

        if momentum == "declining":
            negative_indicators.append("Sentiment trending worse")
            result += "• Sentiment trending worse\n"

        # Check for recent bad news
        recent_negative = [n for n in news_recent if any(
            kw in n.get('title', '').lower()
            for kw in ['miss', 'fall', 'concern', 'lawsuit', 'decline']
        )]

        if len(recent_negative) >= 2:
            negative_indicators.append("Multiple negative news stories")
            result += "• Multiple negative news stories this week\n"

        if not negative_indicators:
            result += "• No major cautionary signals\n"

        result += "\n"

        # Timing recommendation
        result += "=" * 70 + "\n"
        result += "⏰ TIMING RECOMMENDATION\n"
        result += "=" * 70 + "\n\n"

        if len(positive_indicators) >= 2 and len(negative_indicators) == 0:
            result += "✅ FAVORABLE TIMING\n\n"
            result += "Multiple positive signals with limited concerns.\n"
            result += "For long-term investors: Reasonable time to start a position\n\n"
            result += "💡 Strategy:\n"
            result += "• Consider starting with 50-75% of intended position\n"
            result += "• Reserve capital to add on any pullback\n"
            result += "• Set realistic expectations for entry price\n"

        elif len(negative_indicators) >= 2:
            result += "⚠️  CHALLENGING TIMING\n\n"
            result += "Multiple cautionary signals present.\n"
            result += "For most investors: Consider waiting for clarity\n\n"
            result += "💡 Strategy:\n"
            result += "• Wait for news sentiment to improve\n"
            result += "• Add to watchlist and monitor weekly\n"
            result += "• Consider alternative stocks with better timing\n"
            result += "• If you still want exposure, use smaller position size\n"

        else:
            result += "🟡 MIXED SIGNALS\n\n"
            result += "Some positive and some cautionary indicators.\n"
            result += "Standard market conditions - no strong timing edge either way.\n\n"
            result += "💡 Strategy:\n"
            result += "• For long-term investors: Timing matters less, focus on quality\n"
            result += "• Consider dollar-cost averaging (invest in stages)\n"
            result += "• Research fundamentals - they matter more than timing\n"

        result += "\n"

        # Questions to consider
        result += "💭 QUESTIONS BEFORE INVESTING NOW:\n\n"
        result += "1. Am I investing for 5+ years? (Yes → timing matters less)\n"
        result += "2. Can I handle a 10-15% drop next month?\n"
        result += "3. Have I researched the company thoroughly?\n"
        result += "4. Do I have cash to buy more if price drops?\n"
        result += "5. Is this money I can afford to tie up long-term?\n\n"

        result += "📚 Remember:\n"
        result += "• Timing the market perfectly is nearly impossible\n"
        result += "• Time IN the market > Timing the market\n"
        result += "• Quality companies can be good investments at various prices\n"
        result += "• Dollar-cost averaging reduces timing risk\n"

        return result

    except Exception as e:
        return f"Error assessing timing for {ticker}: {str(e)}"


@tool("explain_news_for_investors", description="Explain financial news in simple terms with focus on investment implications. Includes educational context.")
def explain_news_for_investors(ticker: str) -> str:
    """
    Explain recent news in investor-friendly language.

    Args:
        ticker: Stock ticker symbol

    Returns:
        str: Educational explanation of recent news
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        company_name = info.get('longName', ticker.upper())

        result = f"📰 News Explanation for Investors: {ticker.upper()}\n\n"
        result += f"Company: {company_name}\n\n"

        news = get_news_for_stock(ticker, days=7)

        if not news:
            return f"No recent news found for {ticker.upper()}"

        # Show top 3 most recent
        result += "=" * 70 + "\n"
        result += "RECENT NEWS EXPLAINED\n"
        result += "=" * 70 + "\n\n"

        for i, article in enumerate(news[:3], 1):
            title = article.get('title', 'No title')
            publisher = article.get('publisher', 'Unknown')
            timestamp = article.get('providerPublishTime', 0)

            if timestamp:
                date_str = datetime.fromtimestamp(timestamp).strftime('%B %d, %Y')
            else:
                date_str = 'Recent'

            result += f"{i}. {title}\n"
            result += f"   Source: {publisher} | Date: {date_str}\n\n"

            # Simple sentiment
            title_lower = title.lower()
            is_positive = any(kw in title_lower for kw in
                            ['beat', 'surge', 'growth', 'profit', 'success', 'strong'])
            is_negative = any(kw in title_lower for kw in
                            ['miss', 'fall', 'concern', 'lawsuit', 'decline', 'weak'])

            if is_positive:
                result += "   💡 Investment Signal: 🟢 Positive news\n"
            elif is_negative:
                result += "   💡 Investment Signal: 🔴 Concerning news\n"
            else:
                result += "   💡 Investment Signal: 🟡 Neutral/Informational\n"

            result += "\n"

        # Overall context
        sentiment = analyze_sentiment_score(news)

        result += "=" * 70 + "\n"
        result += "📊 OVERALL NEWS CONTEXT (Last 7 Days)\n"
        result += "=" * 70 + "\n\n"

        result += f"News Sentiment: {sentiment['overall'].title()}\n"
        result += f"Sentiment Score: {sentiment['score']}/100\n\n"

        result += f"Breakdown:\n"
        result += f"• {sentiment['positive_count']} positive stories\n"
        result += f"• {sentiment['negative_count']} negative stories\n"
        result += f"• {sentiment['neutral_count']} neutral stories\n\n"

        # Investment implications
        result += "=" * 70 + "\n"
        result += "💭 WHAT THIS MEANS FOR POTENTIAL INVESTORS\n"
        result += "=" * 70 + "\n\n"

        if sentiment['score'] >= 70:
            result += "🟢 Strong Positive News Flow:\n\n"
            result += "The company is experiencing favorable news momentum.\n"
            result += "This often (but not always) supports stock price appreciation.\n\n"
            result += "Consider:\n"
            result += "• Is good news already reflected in stock price?\n"
            result += "• Can this positive momentum continue?\n"
            result += "• What are the risks if momentum reverses?\n"

        elif sentiment['score'] <= 30:
            result += "🔴 Challenging News Environment:\n\n"
            result += "The company is facing negative news pressure.\n"
            result += "This may create volatility or downward price pressure.\n\n"
            result += "Consider:\n"
            result += "• Are concerns temporary or structural?\n"
            result += "• Does this create a buying opportunity?\n"
            result += "• What could reverse the negative trend?\n"

        else:
            result += "🟡 Mixed News Environment:\n\n"
            result += "News sentiment is balanced with both positive and negative elements.\n"
            result += "This is common and represents normal business operations.\n\n"
            result += "Consider:\n"
            result += "• Focus on company fundamentals over news\n"
            result += "• Watch for trend emergence (improving or declining)\n"
            result += "• Quality matters more than short-term news\n"

        result += "\n📚 Educational Note:\n\n"
        result += "News sentiment is just one factor in investment decisions.\n"
        result += "Also research:\n"
        result += "• Financial health (earnings, revenue, debt)\n"
        result += "• Valuation (P/E ratio, compared to peers)\n"
        result += "• Competitive position and industry trends\n"
        result += "• Your investment timeline and risk tolerance\n"

        return result

    except Exception as e:
        return f"Error explaining news for {ticker}: {str(e)}"


@tool("track_watchlist_news", description="Track news for multiple stocks in a watchlist. Useful for monitoring potential investments.")
def track_watchlist_news(tickers: str, days: int = 7) -> str:
    """
    Track news for a watchlist of stocks.

    Args:
        tickers: Comma-separated ticker symbols
        days: Days to look back (default: 7)

    Returns:
        str: News summary for watchlist
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]

        result = f"📋 Watchlist News Tracker ({days} Days)\n\n"
        result += f"Tracking: {', '.join(ticker_list)}\n\n"

        watchlist_items = []

        for ticker in ticker_list:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                news = get_news_for_stock(ticker, days)

                if not news:
                    continue

                sentiment = analyze_sentiment_score(news)

                watchlist_items.append({
                    'ticker': ticker,
                    'name': info.get('longName', ticker),
                    'sentiment': sentiment,
                    'news_count': len(news),
                    'latest_news': news[0] if news else None
                })

            except Exception:
                continue

        if not watchlist_items:
            return "No news found for watchlist stocks"

        # Sort by sentiment score
        watchlist_items.sort(key=lambda x: x['sentiment']['score'], reverse=True)

        # Display results
        result += "=" * 70 + "\n"
        result += "WATCHLIST STATUS\n"
        result += "=" * 70 + "\n\n"

        for item in watchlist_items:
            score = item['sentiment']['score']

            if score >= 65:
                status = "🟢 POSITIVE"
            elif score <= 35:
                status = "🔴 NEGATIVE"
            else:
                status = "🟡 NEUTRAL"

            result += f"{status} - {item['ticker']}\n"
            result += f"   {item['name']}\n"
            result += f"   Sentiment: {score}/100 | News: {item['news_count']} articles\n"

            if item['latest_news']:
                title = item['latest_news'].get('title', 'No title')
                result += f"   Latest: {title}\n"

            result += "\n"

        # Alerts
        high_positive = [i for i in watchlist_items if i['sentiment']['score'] >= 75]
        high_negative = [i for i in watchlist_items if i['sentiment']['score'] <= 30]

        if high_positive or high_negative:
            result += "=" * 70 + "\n"
            result += "⚠️  ALERTS\n"
            result += "=" * 70 + "\n\n"

        if high_positive:
            result += "🔥 Strong Positive Momentum:\n"
            for item in high_positive:
                result += f"• {item['ticker']} - Consider researching for investment\n"
            result += "\n"

        if high_negative:
            result += "⚠️  Significant Concerns:\n"
            for item in high_negative:
                result += f"• {item['ticker']} - Review risks before investing\n"
            result += "\n"

        result += "💡 Next Steps:\n"
        result += "• Use 'build_investment_thesis' for detailed analysis\n"
        result += "• Use 'analyze_investment_risks' for risk assessment\n"
        result += "• Use 'compare_investment_options' to choose best option\n"

        return result

    except Exception as e:
        return f"Error tracking watchlist: {str(e)}"
