# Example MCP Conversations

Real-world conversation examples showing how to use the NSMBL MCP server with Claude.

## Conversation 1: Complete Investment Strategy

**User**: I want to create a diversified global investment strategy. Can you help me explore the available assets and build something?

**Claude**: I'll help you create a diversified strategy. Let me first see what assets are available.

*Uses list_assets(asset_type="etf")*

**Claude**: Great! I found several global ETFs. I recommend:
- VTI: US Total Market
- VEA: Developed Markets ex-US
- VWO: Emerging Markets
- AGG: US Aggregate Bonds

Would you like me to create a risk parity strategy with these? It will balance risk across all four asset classes.

**User**: Yes, that sounds good. Rebalance it monthly.

**Claude**: Perfect! Creating your Global Risk Parity strategy...

*Uses create_strategy with risk parity allocation*

**Claude**: ✅ Strategy created successfully! 
- Name: Global Risk Parity
- ID: sb-xxxxx
- Assets: VTI, VEA, VWO, AGG
- Allocation: Risk Parity (252-day lookback)
- Rebalancing: Monthly

Would you like me to backtest this strategy?

**User**: Yes, test it from 2020 to 2023.

**Claude**: Running backtest and waiting for results...

*Uses create_backtest_and_wait*

**Claude**: ✅ Backtest completed!

Performance (2020-2023):
- Total Return: +42.5%
- Annualized Return: +12.1%
- Volatility: 14.2%
- Sharpe Ratio: 0.85
- Max Drawdown: -11.3%

Your strategy performed well with good risk-adjusted returns!

## Conversation 2: Tactical Strategy Exploration

**User**: I want to try a momentum strategy. Can you explain how it works and create one?

**Claude**: A momentum strategy selects the best-performing assets from a universe based on recent returns. It's a "buy the winners" approach.

Let me create a momentum strategy that picks the top 3 performers from 5 global equity ETFs.

*Uses create_strategy with momentum tactical model*

**Claude**: ✅ Created "Global Momentum Top 3" strategy
- Selects top 3 from: VTI, VEA, VWO, EEM, EFA
- Signal: 60-day momentum
- Allocation: Equal weight among selected
- Rebalancing: Monthly

This will automatically rotate into the strongest performers each month.

**User**: How did it perform historically?

**Claude**: Let me backtest it...

*Uses create_backtest_and_wait*

**Claude**: Backtest results (2020-2023):
- Total Return: +38.2%
- Annualized Return: +10.8%
- Volatility: 16.8%
- Sharpe Ratio: 0.64
- Max Drawdown: -15.7%

The momentum strategy had slightly lower returns but higher volatility compared to a buy-and-hold approach. It's more sensitive to market conditions.

## Conversation 3: Strategy Comparison

**User**: Compare VTI, VEA, and my "Global Risk Parity" strategy

**Claude**: I'll run backtests for all three...

*Uses create_backtest for VTI, VEA, and the strategy*
*Uses list_backtests to track them*
*Uses get_backtest for each when complete*

**Claude**: Here's the comparison (2020-2023):

**VTI (US Market)**
- Return: +48.2%
- Volatility: 18.5%
- Sharpe: 0.91

**VEA (Int'l Developed)**
- Return: +22.1%
- Volatility: 17.2%
- Sharpe: 0.43

**Global Risk Parity**
- Return: +42.5%
- Volatility: 14.2%
- Sharpe: 0.85

Your Risk Parity strategy achieved nearly VTI's returns with significantly lower volatility, resulting in excellent risk-adjusted performance!

## Conversation 4: Iterative Improvement

**User**: I have a strategy called "Tech Growth" but it's too volatile. Can you help me make it more conservative?

**Claude**: I'll get your current strategy configuration first.

*Uses get_strategy("Tech Growth")*

**Claude**: I see your strategy uses equal weight allocation. To reduce volatility, I recommend:

1. Change to risk parity allocation (balances risk)
2. Add bonds (AGG) to the universe
3. Change from weekly to monthly rebalancing

Would you like me to create an updated version?

**User**: Yes, create "Tech Growth Conservative"

**Claude**: Creating the conservative version...

*Uses create_strategy with modifications*

**Claude**: ✅ Created "Tech Growth Conservative"
- Added AGG (bonds) for stability
- Switched to risk parity allocation
- Monthly rebalancing

Let me backtest both versions to compare...

*Uses create_backtest for both strategies*

**Claude**: 
**Original (Tech Growth)**
- Return: +55%
- Volatility: 24.1%
- Max Drawdown: -22.4%

**Conservative Version**
- Return: +41%
- Volatility: 16.3%
- Max Drawdown: -13.1%

The conservative version sacrificed some return for much better stability - volatility reduced by 32% and drawdown by 42%!

## Conversation 5: Quick Status Check

**User**: I started a backtest earlier but had to step away. Can you check on it?

**Claude**: Let me check your recent backtests...

*Uses list_backtests*

**Claude**: I found your backtest:
- Strategy: "Global Momentum Top 3"
- Status: Completed ✅
- Return: +38.2%

Would you like the full details?

**User**: Yes

**Claude**: 

*Uses get_backtest*

**Claude**: [Full backtest results with all metrics...]

## Tips for Effective Conversations

1. **Be Specific**: "Create a risk parity basket with VTI and VEA" is better than "Create a strategy"

2. **Sequential Building**: Create strategy → Backtest → Analyze → Iterate

3. **Use Comparisons**: Ask Claude to compare multiple strategies or assets

4. **Leverage Convenience**: Say "backtest and wait" for automatic polling

5. **Ask for Explanations**: Claude can explain strategy types, allocation models, and results

6. **Iterate and Improve**: Start simple, then refine based on backtest results

