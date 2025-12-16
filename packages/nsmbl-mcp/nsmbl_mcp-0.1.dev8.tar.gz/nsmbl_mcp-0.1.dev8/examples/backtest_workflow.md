# Backtest Workflow Examples

Complete workflows for backtesting assets and strategies.

## Workflow 1: Asset Backtest (Simple)

### Step 1: Create and Wait

```
User: Backtest VTI from 2020-01-01 to 2023-12-31 with $100,000 initial capital

Claude: Uses create_backtest_and_wait
Result: Complete backtest results after ~10-30 seconds
```

This is the simplest approach - one command, automatic waiting.

### Step 2: Review Results

The response includes:
- Final portfolio value
- Total return %
- Annualized return %
- Volatility
- Sharpe ratio
- Max drawdown

## Workflow 2: Strategy Backtest (Manual Polling)

When you want more control over the process:

### Step 1: Create Strategy

```
User: Create a risk parity basket with VTI, VEA, and AGG, 
      monthly rebalancing, called "Global Balanced"

Claude: Uses create_strategy
Result: Strategy created with ID sb-xxxxx
```

### Step 2: Queue Backtest

```
User: Create a backtest for that strategy from 2020 to 2023

Claude: Uses create_backtest
Result: Backtest queued with ID bt-yyyyy
```

### Step 3: Check Status

```
User: Check the status

Claude: Uses check_backtest_status
Result: Status update (queued/executing/completed)
```

### Step 4: Get Results (when ready)

```
User: Get the full backtest results

Claude: Uses get_backtest
Result: Complete metrics and history
```

## Workflow 3: Batch Backtesting

Testing multiple strategies:

### Step 1: Create Multiple Backtests

```
User: Create backtests for VTI, VEA, and AGG individually, 
      all from 2020 to 2023

Claude: Uses create_backtest three times
Result: Three backtest IDs
```

### Step 2: List All Backtests

```
User: Show me all my backtest results

Claude: Uses list_backtests
Result: Summary of all backtests with status and returns
```

### Step 3: Compare Results

```
User: Get detailed results for the completed ones

Claude: Uses get_backtest for each completed backtest
Result: Detailed comparison of performance metrics
```

## Workflow 4: Long-Running Strategy Backtest

For complex strategies that take longer:

### Step 1: Queue Backtest

```
User: Create a backtest for my ensemble strategy

Claude: Uses create_backtest
Result: Backtest queued
```

### Step 2: Do Other Work

You can continue working on other tasks while the backtest runs.

### Step 3: Wait When Ready

```
User: Now wait for that backtest to complete

Claude: Uses wait_for_backtest with the backtest ID
Result: Polls until complete, returns full results
```

## Timing Expectations

### Asset Backtests
- Queue time: < 5 seconds
- Execution time: 10-30 seconds
- Total: Usually < 1 minute

### Basket Strategy Backtests
- Queue time: < 5 seconds
- Execution time: 30-90 seconds
- Total: Usually 1-2 minutes

### Tactical Strategy Backtests
- Queue time: < 5 seconds
- Execution time: 60-180 seconds
- Total: Usually 2-4 minutes

### Ensemble/Portfolio Strategy Backtests
- Queue time: < 5 seconds
- Execution time: 120-300 seconds
- Total: Usually 3-6 minutes

## Best Practices

### Use Convenience Tools for Interactive Work

```
User: Backtest my strategy and wait for it

Claude: Uses create_backtest_and_wait
```

This provides the best user experience - one command, automatic completion.

### Use Raw Tools for Batch Operations

When running multiple backtests, queue them all first:

```python
# Queue 10 backtests
for strategy in strategies:
    create_backtest(strategy)

# Then poll them all
while any_incomplete:
    for bt_id in backtest_ids:
        check_backtest_status(bt_id)
```

### Handle Timeouts Gracefully

If a backtest times out:

```
User: That timed out, keep waiting for it

Claude: Uses wait_for_backtest with longer timeout
```

### Filter and Search

```
User: Show me only my completed backtests

Claude: Uses list_backtests(status="completed")
```

```
User: Show me all backtests for VTI

Claude: Uses list_backtests(target_id="VTI")
```

## Error Handling

### Rate Limit Error

```
Error: Rate limit exceeded (10/minute)
Solution: Wait 60 seconds before creating more backtests
```

### Concurrent Limit Error

```
Error: Maximum 10 concurrent backtests
Solution: Wait for some to complete or check status with list_backtests
```

### Insufficient Funds

```
Error: Insufficient funds for projected usage
Solution: Add credits at app.nsmbl.ai
```

