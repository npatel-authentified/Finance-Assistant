"""
Portfolio Analysis Tools

Comprehensive tools for analyzing investment portfolios including diversification,
risk metrics, performance tracking, and rebalancing recommendations.
"""

from langchain.tools import tool
import yfinance as yf
import pandas as pd
import numpy as np

# Risk-free rate (10-year Treasury yield approximation)
RISK_FREE_RATE = 0.04  # 4% annual


@tool("get_portfolio_summary", description="Get a comprehensive summary of portfolio holdings with current values, gains/losses, and overall portfolio value.")
def get_portfolio_summary(holdings: dict) -> str:
    """
    Get portfolio summary with current values and basic metrics.

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values
                 Example: {"AAPL": 10, "MSFT": 5, "GOOGL": 3}

    Returns:
        str: Formatted portfolio summary with positions and total value
    """
    try:
        if not holdings:
            return "Error: Portfolio is empty. Please provide holdings."

        positions = []
        total_value = 0.0

        result = "📊 Portfolio Summary\n\n"

        # Fetch data for each position
        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                info = stock.info

                current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                if current_price == 0:
                    # Try getting from recent history
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]

                company_name = info.get('longName', ticker.upper())
                sector = info.get('sector', 'Unknown')

                position_value = current_price * shares
                total_value += position_value

                positions.append({
                    'ticker': ticker.upper(),
                    'name': company_name,
                    'shares': shares,
                    'price': current_price,
                    'value': position_value,
                    'sector': sector
                })

            except Exception as e:
                result += f"⚠️  Error fetching {ticker}: {str(e)}\n"

        if not positions:
            return "Error: Could not fetch data for any holdings"

        # Calculate percentages
        for pos in positions:
            pos['pct'] = (pos['value'] / total_value * 100) if total_value > 0 else 0

        # Sort by value (largest first)
        positions.sort(key=lambda x: x['value'], reverse=True)

        # Display summary
        result += f"Total Portfolio Value: ${total_value:,.2f}\n"
        result += f"Number of Holdings: {len(positions)}\n\n"

        result += "=" * 70 + "\n"
        result += "Holdings:\n"
        result += "=" * 70 + "\n\n"

        for i, pos in enumerate(positions, 1):
            result += f"{i}. {pos['name']} ({pos['ticker']})\n"
            result += f"   Shares: {pos['shares']:,} @ ${pos['price']:.2f}\n"
            result += f"   Value: ${pos['value']:,.2f} ({pos['pct']:.2f}% of portfolio)\n"
            result += f"   Sector: {pos['sector']}\n\n"

        return result

    except Exception as e:
        return f"Error generating portfolio summary: {str(e)}"


@tool("analyze_portfolio_diversification", description="Analyze portfolio diversification by dollar value across holdings and sectors. Identifies concentration risks.")
def analyze_portfolio_diversification(holdings: dict) -> str:
    """
    Analyze portfolio diversification using CORRECT dollar values (not share counts).

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values

    Returns:
        str: Detailed diversification analysis with concentration risk warnings
    """
    try:
        if not holdings:
            return "Error: Portfolio is empty"

        positions = []
        total_value = 0.0
        sector_values = {}

        # Calculate dollar values for each position
        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                info = stock.info

                current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                if current_price == 0:
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]

                sector = info.get('sector', 'Unknown')
                value = current_price * shares

                positions.append({
                    'ticker': ticker.upper(),
                    'shares': shares,
                    'price': current_price,
                    'value': value,
                    'sector': sector
                })

                total_value += value
                sector_values[sector] = sector_values.get(sector, 0) + value

            except Exception as e:
                pass  # Skip problematic tickers

        if not positions or total_value == 0:
            return "Error: Could not calculate portfolio values"

        # Calculate percentages
        for pos in positions:
            pos['pct'] = (pos['value'] / total_value * 100)

        # Sort by value
        positions.sort(key=lambda x: x['value'], reverse=True)

        # Build result
        result = "🎯 Portfolio Diversification Analysis\n\n"
        result += f"Total Portfolio Value: ${total_value:,.2f}\n\n"

        # Position-level diversification
        result += "=" * 70 + "\n"
        result += "Position Diversification (by Dollar Value):\n"
        result += "=" * 70 + "\n\n"

        concentrated_positions = []

        for i, pos in enumerate(positions, 1):
            # Flag concentration risk (>20% in single position)
            if pos['pct'] > 20:
                flag = "⚠️  CONCENTRATED"
                concentrated_positions.append(pos)
            elif pos['pct'] > 15:
                flag = "⚡ High"
            elif pos['pct'] > 10:
                flag = "○ Moderate"
            else:
                flag = "✓ Good"

            result += f"{i}. {pos['ticker']}: ${pos['value']:,.2f} ({pos['pct']:.1f}%) {flag}\n"

        # Sector diversification
        result += f"\n{'=' * 70}\n"
        result += "Sector Diversification:\n"
        result += f"{'=' * 70}\n\n"

        sector_pcts = []
        for sector, value in sector_values.items():
            pct = (value / total_value * 100)
            sector_pcts.append({'sector': sector, 'value': value, 'pct': pct})

        sector_pcts.sort(key=lambda x: x['value'], reverse=True)

        for item in sector_pcts:
            flag = "⚠️" if item['pct'] > 30 else "✓"
            result += f"  {flag} {item['sector']}: ${item['value']:,.2f} ({item['pct']:.1f}%)\n"

        # Diversification assessment
        result += f"\n{'=' * 70}\n"
        result += "📋 Diversification Assessment:\n"
        result += f"{'=' * 70}\n\n"

        if concentrated_positions:
            result += f"⚠️  CONCENTRATION RISK DETECTED\n\n"
            result += f"You have {len(concentrated_positions)} position(s) over 20% of portfolio:\n"
            for pos in concentrated_positions:
                result += f"  • {pos['ticker']}: {pos['pct']:.1f}% (${pos['value']:,.2f})\n"
            result += "\n💡 Recommendation: Consider reducing positions over 20%\n"
            result += "   to limit single-stock risk.\n\n"
        else:
            result += "✅ Position Diversification: Good\n"
            result += "   No single position exceeds 20% of portfolio\n\n"

        # Sector concentration
        max_sector = max(sector_pcts, key=lambda x: x['pct'])
        if max_sector['pct'] > 40:
            result += f"⚠️  Sector Concentration: {max_sector['sector']} is {max_sector['pct']:.1f}%\n"
            result += "   Consider diversifying across more sectors\n\n"
        elif max_sector['pct'] > 30:
            result += f"⚡ Watch: {max_sector['sector']} is {max_sector['pct']:.1f}% of portfolio\n\n"
        else:
            result += f"✅ Sector Diversification: Balanced\n"
            result += f"   Largest sector ({max_sector['sector']}) is {max_sector['pct']:.1f}%\n\n"

        # Number of holdings assessment
        num_holdings = len(positions)
        if num_holdings < 5:
            result += f"⚠️  Holdings Count: {num_holdings} stocks (consider adding more)\n"
            result += "   Recommendation: 10-20 stocks for better diversification\n"
        elif num_holdings > 30:
            result += f"⚡ Holdings Count: {num_holdings} stocks (may be over-diversified)\n"
            result += "   Consider whether you can effectively monitor this many positions\n"
        else:
            result += f"✅ Holdings Count: {num_holdings} stocks (reasonable)\n"

        return result

    except Exception as e:
        return f"Error analyzing diversification: {str(e)}"


@tool("calculate_portfolio_performance", description="Calculate portfolio performance over various time periods (1 month, 3 months, 6 months, 1 year).")
def calculate_portfolio_performance(holdings: dict, period: str = "1y") -> str:
    """
    Calculate portfolio performance over time.

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values
        period: Time period - '1mo', '3mo', '6mo', '1y' (default: '1y')

    Returns:
        str: Performance analysis with returns and individual stock contributions
    """
    try:
        valid_periods = ['1mo', '3mo', '6mo', '1y']
        if period not in valid_periods:
            return f"Error: Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"

        if not holdings:
            return "Error: Portfolio is empty"

        result = f"📈 Portfolio Performance Analysis ({period})\n\n"

        # Calculate current portfolio value
        current_values = {}
        total_current = 0.0

        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period=period)

                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                current_value = current_price * shares
                current_values[ticker.upper()] = current_value
                total_current += current_value

            except Exception:
                continue

        if total_current == 0:
            return "Error: Could not calculate portfolio value"

        # Calculate starting portfolio value
        starting_values = {}
        total_starting = 0.0
        stock_returns = []

        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period=period)

                if len(hist) < 2:
                    continue

                starting_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]

                starting_value = starting_price * shares
                current_value = current_price * shares

                starting_values[ticker.upper()] = starting_value
                total_starting += starting_value

                stock_return = ((current_price - starting_price) / starting_price * 100)
                contribution = current_value - starting_value

                stock_returns.append({
                    'ticker': ticker.upper(),
                    'return': stock_return,
                    'contribution': contribution,
                    'start_value': starting_value,
                    'current_value': current_value
                })

            except Exception:
                continue

        if total_starting == 0:
            return "Error: Could not calculate starting portfolio value"

        # Calculate total portfolio return
        portfolio_return = ((total_current - total_starting) / total_starting * 100)
        absolute_gain = total_current - total_starting

        # Display results
        result += f"Starting Value: ${total_starting:,.2f}\n"
        result += f"Current Value: ${total_current:,.2f}\n"
        result += f"Absolute Change: ${absolute_gain:+,.2f}\n\n"

        indicator = "🟢" if portfolio_return >= 0 else "🔴"
        result += f"{indicator} Total Return: {portfolio_return:+.2f}%\n\n"

        # Performance assessment
        if period == "1y":
            if portfolio_return > 15:
                assessment = "🔥 Excellent performance"
            elif portfolio_return > 10:
                assessment = "✅ Strong performance"
            elif portfolio_return > 0:
                assessment = "✓ Positive returns"
            elif portfolio_return > -10:
                assessment = "⚠️  Slight underperformance"
            else:
                assessment = "🔴 Significant underperformance"
        else:
            if portfolio_return > 0:
                assessment = "✅ Positive returns"
            else:
                assessment = "⚠️  Negative returns"

        result += f"Assessment: {assessment}\n\n"

        # Individual stock performance
        result += "=" * 70 + "\n"
        result += "Individual Stock Performance:\n"
        result += "=" * 70 + "\n\n"

        stock_returns.sort(key=lambda x: x['return'], reverse=True)

        for i, stock in enumerate(stock_returns, 1):
            indicator = "🟢" if stock['return'] >= 0 else "🔴"
            contribution_indicator = "+" if stock['contribution'] >= 0 else ""

            result += f"{i}. {stock['ticker']}: {stock['return']:+.2f}% {indicator}\n"
            result += f"   Value: ${stock['start_value']:,.2f} → ${stock['current_value']:,.2f}\n"
            result += f"   Contribution to Portfolio: {contribution_indicator}${stock['contribution']:,.2f}\n\n"

        # Top/bottom performers
        if len(stock_returns) >= 2:
            result += "=" * 70 + "\n"
            result += "🏆 Best Performer: "
            best = stock_returns[0]
            result += f"{best['ticker']} ({best['return']:+.2f}%)\n"

            result += "📉 Worst Performer: "
            worst = stock_returns[-1]
            result += f"{worst['ticker']} ({worst['return']:+.2f}%)\n"

        return result

    except Exception as e:
        return f"Error calculating performance: {str(e)}"


@tool("analyze_portfolio_risk", description="Analyze portfolio risk metrics including volatility, Sharpe ratio, and beta to market.")
def analyze_portfolio_risk(holdings: dict) -> str:
    """
    Calculate portfolio risk metrics.

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values

    Returns:
        str: Risk analysis with volatility, Sharpe ratio, and beta
    """
    try:
        if not holdings:
            return "Error: Portfolio is empty"

        result = "⚠️  Portfolio Risk Analysis\n\n"

        # Get historical data for portfolio
        portfolio_returns = pd.Series(dtype=float)
        weights = {}
        total_value = 0.0

        # Calculate current weights
        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period="1y")

                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                value = current_price * shares
                weights[ticker.upper()] = value
                total_value += value

            except Exception:
                continue

        if total_value == 0:
            return "Error: Could not calculate portfolio weights"

        # Normalize weights
        for ticker in weights:
            weights[ticker] = weights[ticker] / total_value

        # Calculate portfolio returns
        stock_data = {}

        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period="1y")

                if len(hist) < 20:
                    continue

                # Calculate daily returns
                returns = hist['Close'].pct_change().dropna()
                stock_data[ticker.upper()] = returns

            except Exception:
                continue

        if not stock_data:
            return "Error: Could not calculate returns for any stocks"

        # Calculate weighted portfolio returns
        for date in stock_data[list(stock_data.keys())[0]].index:
            daily_return = 0.0
            for ticker, returns in stock_data.items():
                if date in returns.index:
                    daily_return += returns[date] * weights.get(ticker, 0)
            portfolio_returns[date] = daily_return

        # Calculate metrics
        # 1. Volatility (annualized standard deviation)
        volatility = portfolio_returns.std() * np.sqrt(252) * 100  # Annualized

        # 2. Average annual return
        avg_daily_return = portfolio_returns.mean()
        annual_return = (1 + avg_daily_return) ** 252 - 1

        # 3. Sharpe Ratio
        excess_return = annual_return - RISK_FREE_RATE
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0

        # 4. Beta to S&P 500
        try:
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            spy_returns = spy_hist['Close'].pct_change().dropna()

            # Align dates
            aligned_portfolio = portfolio_returns.reindex(spy_returns.index).dropna()
            aligned_spy = spy_returns.reindex(aligned_portfolio.index).dropna()

            if len(aligned_portfolio) > 0 and len(aligned_spy) > 0:
                covariance = np.cov(aligned_portfolio, aligned_spy)[0][1]
                market_variance = np.var(aligned_spy)
                beta = covariance / market_variance if market_variance > 0 else 1.0
            else:
                beta = None
        except Exception:
            beta = None

        # Display results
        result += f"📊 Risk Metrics (12-month analysis):\n\n"

        # Volatility
        result += f"Volatility (Annual): {volatility:.2f}%\n"
        if volatility < 15:
            vol_assessment = "✅ Low risk (conservative)"
        elif volatility < 25:
            vol_assessment = "○ Moderate risk (balanced)"
        else:
            vol_assessment = "⚠️  High risk (aggressive)"
        result += f"  {vol_assessment}\n\n"

        # Sharpe Ratio
        result += f"Sharpe Ratio: {sharpe_ratio:.2f}\n"
        if sharpe_ratio > 2:
            sharpe_assessment = "🔥 Excellent risk-adjusted returns"
        elif sharpe_ratio > 1:
            sharpe_assessment = "✅ Good risk-adjusted returns"
        elif sharpe_ratio > 0:
            sharpe_assessment = "○ Positive risk-adjusted returns"
        else:
            sharpe_assessment = "⚠️  Poor risk-adjusted returns"
        result += f"  {sharpe_assessment}\n"
        result += f"  (Higher is better, >1 is good, >2 is excellent)\n\n"

        # Beta
        if beta is not None:
            result += f"Beta (vs S&P 500): {beta:.2f}\n"
            if beta < 0.8:
                beta_assessment = "📉 Less volatile than market (defensive)"
            elif beta < 1.2:
                beta_assessment = "○ Similar volatility to market"
            else:
                beta_assessment = "📈 More volatile than market (aggressive)"
            result += f"  {beta_assessment}\n"
            result += f"  (Beta = 1 means moves with market, <1 less volatile, >1 more volatile)\n\n"

        # Risk assessment summary
        result += "=" * 70 + "\n"
        result += "💭 Risk Profile Summary:\n"
        result += "=" * 70 + "\n\n"

        if volatility < 15 and sharpe_ratio > 1:
            result += "✅ Low Risk, Good Returns - Conservative, well-managed portfolio\n"
        elif volatility > 25 and sharpe_ratio > 1.5:
            result += "⚡ High Risk, High Returns - Aggressive growth portfolio\n"
        elif volatility > 25 and sharpe_ratio < 0.5:
            result += "⚠️  High Risk, Poor Returns - Consider rebalancing\n"
        else:
            result += "○ Moderate Risk Profile - Balanced approach\n"

        if beta is not None:
            if beta > 1.3:
                result += "📈 Portfolio is more aggressive than the broad market\n"
            elif beta < 0.7:
                result += "📉 Portfolio is more defensive than the broad market\n"

        return result

    except Exception as e:
        return f"Error analyzing portfolio risk: {str(e)}"


@tool("compare_portfolio_to_benchmark", description="Compare portfolio performance against a benchmark index like S&P 500 over the past year.")
def compare_portfolio_to_benchmark(holdings: dict, benchmark: str = "^GSPC") -> str:
    """
    Compare portfolio performance to benchmark.

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values
        benchmark: Benchmark ticker (default: '^GSPC' for S&P 500)
                  Other options: '^IXIC' (Nasdaq), '^DJI' (Dow Jones)

    Returns:
        str: Comparison of portfolio vs benchmark performance
    """
    try:
        if not holdings:
            return "Error: Portfolio is empty"

        benchmark_names = {
            "^GSPC": "S&P 500",
            "^IXIC": "Nasdaq",
            "^DJI": "Dow Jones",
            "SPY": "S&P 500 ETF",
            "QQQ": "Nasdaq 100 ETF"
        }

        benchmark_name = benchmark_names.get(benchmark, benchmark)

        result = f"📊 Portfolio vs {benchmark_name} Comparison\n\n"

        # Calculate portfolio performance
        total_starting = 0.0
        total_current = 0.0

        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period="1y")

                if len(hist) < 2:
                    continue

                starting_price = hist['Close'].iloc[0]
                current_price = hist['Close'].iloc[-1]

                total_starting += starting_price * shares
                total_current += current_price * shares

            except Exception:
                continue

        if total_starting == 0:
            return "Error: Could not calculate portfolio performance"

        portfolio_return = ((total_current - total_starting) / total_starting * 100)

        # Get benchmark performance
        try:
            bench = yf.Ticker(benchmark)
            bench_hist = bench.history(period="1y")

            if len(bench_hist) < 2:
                return f"Error: Could not fetch benchmark data for {benchmark}"

            bench_start = bench_hist['Close'].iloc[0]
            bench_current = bench_hist['Close'].iloc[-1]
            benchmark_return = ((bench_current - bench_start) / bench_start * 100)

        except Exception as e:
            return f"Error fetching benchmark {benchmark}: {str(e)}"

        # Calculate alpha (excess return)
        alpha = portfolio_return - benchmark_return

        # Display results
        result += "1-Year Performance:\n\n"

        port_indicator = "🟢" if portfolio_return >= 0 else "🔴"
        bench_indicator = "🟢" if benchmark_return >= 0 else "🔴"

        result += f"{port_indicator} Your Portfolio: {portfolio_return:+.2f}%\n"
        result += f"{bench_indicator} {benchmark_name}: {benchmark_return:+.2f}%\n\n"

        result += "=" * 70 + "\n"
        result += "Performance Comparison:\n"
        result += "=" * 70 + "\n\n"

        if alpha > 0:
            result += f"✅ OUTPERFORMANCE: +{alpha:.2f}%\n\n"
            result += f"Your portfolio beat the {benchmark_name} by {alpha:.2f} percentage points!\n\n"

            if alpha > 10:
                result += "🔥 Exceptional outperformance\n"
            elif alpha > 5:
                result += "✅ Strong outperformance\n"
            else:
                result += "✓ Modest outperformance\n"
        else:
            result += f"📉 UNDERPERFORMANCE: {alpha:.2f}%\n\n"
            result += f"Your portfolio trailed the {benchmark_name} by {abs(alpha):.2f} percentage points.\n\n"

            if alpha < -10:
                result += "⚠️  Significant underperformance - consider reviewing strategy\n"
            elif alpha < -5:
                result += "○ Moderate underperformance\n"
            else:
                result += "○ Slight underperformance\n"

        # Context
        result += "\n💡 Context:\n"
        result += f"• Beating the {benchmark_name} consistently is difficult\n"
        result += "• Many professional fund managers fail to beat the market\n"

        if alpha > 0:
            result += f"• Your {alpha:.2f}% outperformance is noteworthy\n"
        else:
            result += f"• Consider low-cost index funds if underperformance persists\n"

        return result

    except Exception as e:
        return f"Error comparing to benchmark: {str(e)}"


@tool("get_rebalancing_recommendations", description="Get recommendations for rebalancing portfolio to target allocations or to reduce concentration risk.")
def get_rebalancing_recommendations(holdings: dict, target_allocation: dict = None) -> str:
    """
    Provide rebalancing recommendations.

    Args:
        holdings: Dictionary with ticker symbols as keys and number of shares as values
        target_allocation: Optional dict with ticker symbols and target percentages
                          Example: {"AAPL": 15, "MSFT": 15, "GOOGL": 10, ...}

    Returns:
        str: Rebalancing recommendations with specific actions
    """
    try:
        if not holdings:
            return "Error: Portfolio is empty"

        result = "⚖️  Portfolio Rebalancing Analysis\n\n"

        # Calculate current allocations
        positions = []
        total_value = 0.0

        for ticker, shares in holdings.items():
            try:
                stock = yf.Ticker(ticker.upper())
                hist = stock.history(period="1d")

                if hist.empty:
                    continue

                current_price = hist['Close'].iloc[-1]
                value = current_price * shares

                positions.append({
                    'ticker': ticker.upper(),
                    'shares': shares,
                    'price': current_price,
                    'value': value
                })

                total_value += value

            except Exception:
                continue

        if total_value == 0:
            return "Error: Could not calculate portfolio value"

        # Calculate current percentages
        for pos in positions:
            pos['current_pct'] = (pos['value'] / total_value * 100)

        result += f"Total Portfolio Value: ${total_value:,.2f}\n\n"

        # If target allocation provided
        if target_allocation:
            result += "=" * 70 + "\n"
            result += "Rebalancing to Target Allocation:\n"
            result += "=" * 70 + "\n\n"

            actions = []

            for pos in positions:
                ticker = pos['ticker']
                current_pct = pos['current_pct']
                target_pct = target_allocation.get(ticker, 0)

                difference = target_pct - current_pct
                target_value = (target_pct / 100) * total_value
                current_value = pos['value']
                dollar_diff = target_value - current_value
                shares_diff = dollar_diff / pos['price'] if pos['price'] > 0 else 0

                if abs(difference) > 2:  # Only show if difference > 2%
                    action = "BUY" if difference > 0 else "SELL"
                    actions.append({
                        'ticker': ticker,
                        'action': action,
                        'current_pct': current_pct,
                        'target_pct': target_pct,
                        'difference': difference,
                        'shares_diff': abs(shares_diff),
                        'dollar_diff': abs(dollar_diff)
                    })

            if not actions:
                result += "✅ Portfolio is well-balanced relative to targets\n"
                result += "   No rebalancing needed (all positions within 2% of target)\n"
            else:
                actions.sort(key=lambda x: abs(x['difference']), reverse=True)

                for i, action in enumerate(actions, 1):
                    arrow = "📈" if action['action'] == "BUY" else "📉"
                    result += f"{i}. {arrow} {action['action']} {action['ticker']}\n"
                    result += f"   Current: {action['current_pct']:.1f}% → Target: {action['target_pct']:.1f}%\n"
                    result += f"   {action['action']}: {action['shares_diff']:.0f} shares (${action['dollar_diff']:,.2f})\n\n"

        # Concentration risk rebalancing
        else:
            result += "=" * 70 + "\n"
            result += "Rebalancing for Diversification:\n"
            result += "=" * 70 + "\n\n"

            concentrated = [p for p in positions if p['current_pct'] > 20]

            if concentrated:
                result += "⚠️  Concentration Risk Detected\n\n"
                result += "Recommendations to reduce single-stock risk:\n\n"

                for pos in concentrated:
                    excess_pct = pos['current_pct'] - 20
                    excess_value = (excess_pct / 100) * total_value
                    shares_to_sell = excess_value / pos['price']

                    result += f"📉 REDUCE {pos['ticker']}\n"
                    result += f"   Current: {pos['current_pct']:.1f}% (${pos['value']:,.2f})\n"
                    result += f"   Suggested: Reduce to 20% or below\n"
                    result += f"   Consider selling: {shares_to_sell:.0f} shares (${excess_value:,.2f})\n\n"

                result += "\n💡 Use proceeds to:\n"
                result += "   • Add new positions in different sectors\n"
                result += "   • Add to existing smaller positions\n"
                result += "   • Invest in broad market index funds\n"
            else:
                result += "✅ No concentration risk detected\n"
                result += "   All positions are below 20% of portfolio\n\n"

                # Check for underweight positions
                small_positions = [p for p in positions if p['current_pct'] < 3]
                if small_positions and len(positions) > 5:
                    result += "💡 Consider consolidating small positions:\n\n"
                    for pos in small_positions:
                        result += f"   • {pos['ticker']}: {pos['current_pct']:.1f}% (${pos['value']:,.2f})\n"
                    result += "\n   These small positions may have limited impact on portfolio.\n"

        return result

    except Exception as e:
        return f"Error generating rebalancing recommendations: {str(e)}"


@tool("analyze_individual_position", description="Get detailed analysis of a single stock position within the portfolio including metrics and recommendations.")
def analyze_individual_position(ticker: str, shares: int) -> str:
    """
    Analyze a single stock position in detail.

    Args:
        ticker: Stock ticker symbol
        shares: Number of shares held

    Returns:
        str: Detailed position analysis
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        hist = stock.history(period="1y")

        if hist.empty:
            return f"Error: No data found for {ticker.upper()}"

        result = f"🔍 Position Analysis: {ticker.upper()}\n\n"

        # Basic info
        company_name = info.get('longName', ticker.upper())
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')

        result += f"Company: {company_name}\n"
        result += f"Sector: {sector} | Industry: {industry}\n\n"

        # Position value
        current_price = hist['Close'].iloc[-1]
        position_value = current_price * shares

        result += "=" * 70 + "\n"
        result += "Position Details:\n"
        result += "=" * 70 + "\n\n"
        result += f"Shares Held: {shares:,}\n"
        result += f"Current Price: ${current_price:.2f}\n"
        result += f"Position Value: ${position_value:,.2f}\n\n"

        # Performance
        if len(hist) >= 2:
            year_start_price = hist['Close'].iloc[0]
            year_return = ((current_price - year_start_price) / year_start_price * 100)

            indicator = "🟢" if year_return >= 0 else "🔴"
            result += f"{indicator} 1-Year Return: {year_return:+.2f}%\n\n"

        # Fundamentals
        result += "=" * 70 + "\n"
        result += "Key Metrics:\n"
        result += "=" * 70 + "\n\n"

        pe_ratio = info.get('trailingPE', None)
        if pe_ratio:
            result += f"P/E Ratio: {pe_ratio:.2f}\n"

        market_cap = info.get('marketCap', None)
        if market_cap:
            result += f"Market Cap: ${market_cap:,.0f}\n"

        div_yield = info.get('dividendYield', None)
        if div_yield:
            result += f"Dividend Yield: {div_yield*100:.2f}%\n"

        beta = info.get('beta', None)
        if beta:
            result += f"Beta: {beta:.2f}\n"

        return result

    except Exception as e:
        return f"Error analyzing position {ticker}: {str(e)}"
