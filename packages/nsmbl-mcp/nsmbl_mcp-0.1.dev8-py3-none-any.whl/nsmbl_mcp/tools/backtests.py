"""
Backtest tools for NSMBL MCP server.

Provides backtest creation, polling, and convenience tools for async operations.
"""

import asyncio
from typing import Optional, Any, List, Dict
from datetime import datetime
from mcp.types import Tool
from ..client import NSMBLClient, NSMBLAPIError
from ..utils.errors import format_api_error, format_timeout_error
from ..config import get_config
import json
import os
import tempfile


# ============================================================================
# Smart Sampling Helpers
# ============================================================================

def _get_sampling_strategy(start_date: str, end_date: str, total_points: int) -> Dict[str, Any]:
    """
    Determine sampling strategy based on backtest duration.
    
    Thresholds:
    - < 1 year: Return all points (optimal for short-term analysis)
    - 1-5 years: Weekly samples (~52-260 points, good for medium-term)
    - 5+ years: Monthly samples (~60+ points, good for long-term trends)
    
    Args:
        start_date: Start date in ISO format
        end_date: End date in ISO format
        total_points: Total number of data points
        
    Returns:
        dict: Sampling strategy information
    """
    try:
        # Parse dates (handle both with and without timezone)
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        duration_days = (end - start).days
        duration_years = duration_days / 365.25
        
        # < 1 year: Return everything
        if duration_days < 365:
            return {
                "strategy": "none",
                "reason": f"Duration: {duration_years:.1f} years",
                "sample_data": False,
                "step": 1
            }
        
        # 1-5 years: Weekly sampling
        elif duration_days < (365 * 5):
            target_step = max(1, int(total_points / (52 * duration_years)))  # ~52 points per year
            return {
                "strategy": "weekly",
                "reason": f"Duration: {duration_years:.1f} years",
                "sample_data": True,
                "step": target_step
            }
        
        # 5+ years: Monthly sampling
        else:
            target_step = max(1, int(total_points / (12 * duration_years)))  # ~12 points per year
            return {
                "strategy": "monthly",
                "reason": f"Duration: {duration_years:.1f} years",
                "sample_data": True,
                "step": target_step
            }
    except Exception:
        # Fallback: if we can't parse dates, don't sample
        return {
            "strategy": "none",
            "reason": "Unable to determine duration",
            "sample_data": False,
            "step": 1
        }


def _sample_with_extremes(data: List[Dict[str, Any]], step: int) -> List[Dict[str, Any]]:
    """
    Sample data at regular intervals while preserving critical points.
    
    Always includes:
    - First point (start)
    - Last point (end)
    - Peak (highest value)
    - Trough (lowest value)
    - Regular interval samples
    
    Args:
        data: List of equity points with 'value' field
        step: Sampling step size
        
    Returns:
        List of sampled data points, sorted by date
    """
    if not data or len(data) <= step * 2:
        return data
    
    # Always include these indices
    must_include = {0, len(data) - 1}
    
    # Find peak and trough
    peak_idx = max(range(len(data)), key=lambda i: data[i].get('value', 0))
    trough_idx = min(range(len(data)), key=lambda i: data[i].get('value', float('inf')))
    must_include.add(peak_idx)
    must_include.add(trough_idx)
    
    # Sample at regular intervals
    sampled_indices = set(range(0, len(data), step))
    
    # Combine and sort
    all_indices = sorted(must_include | sampled_indices)
    
    return [data[i] for i in all_indices]


def _sample_at_changes(allocations: List[Dict[str, Any]], step: int) -> List[Dict[str, Any]]:
    """
    Sample allocations while preserving all allocation changes.
    
    Always includes:
    - First allocation
    - Last allocation
    - Any point where allocations changed
    - Regular interval samples
    
    Args:
        allocations: List of allocation points with 'positions' field
        step: Sampling step size
        
    Returns:
        List of sampled allocation points, sorted by date
    """
    if not allocations or len(allocations) <= step * 2:
        return allocations
    
    must_include = {0, len(allocations) - 1}
    
    # Find allocation changes
    for i in range(1, len(allocations)):
        if allocations[i].get('positions') != allocations[i-1].get('positions'):
            must_include.add(i)
    
    # Regular sampling
    sampled_indices = set(range(0, len(allocations), step))
    
    # Combine and sort
    all_indices = sorted(must_include | sampled_indices)
    
    return [allocations[i] for i in all_indices]


def _format_columnar(equity_data: List[Dict[str, Any]], allocation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert equity and allocation data to efficient columnar format.
    
    Merges equity and allocations on matching dates and returns columnar arrays
    for maximum token efficiency. Dates are compacted to YYYY-MM-DD format.
    
    Args:
        equity_data: List of equity points with 'date' and 'value'
        allocation_data: List of allocation points with 'date' and 'positions'
        
    Returns:
        Dict with 'dates', 'values', and 'positions' arrays
    """
    if not equity_data:
        return {"dates": [], "values": [], "positions": []}
    
    # Create lookup for allocations by date
    allocation_map = {}
    for alloc in allocation_data:
        date_key = alloc.get('date', '')[:10]  # Extract YYYY-MM-DD
        allocation_map[date_key] = alloc.get('positions', {})
    
    # Build columnar arrays
    dates = []
    values = []
    positions = []
    
    last_positions = {}  # Track last known positions for forward-fill
    
    for equity_point in equity_data:
        date_str = equity_point.get('date', '')
        date_compact = date_str[:10] if date_str else ''  # YYYY-MM-DD format
        
        dates.append(date_compact)
        values.append(equity_point.get('value', 0))
        
        # Get positions for this date, or forward-fill from last known
        if date_compact in allocation_map:
            last_positions = allocation_map[date_compact]
        positions.append(last_positions.copy())
    
    return {
        "dates": dates,
        "values": values,
        "positions": positions
    }


def _generate_html_report(backtest_id: str, backtest_data: Dict[str, Any], columnar_data: Dict[str, Any]) -> str:
    """
    Generate a beautiful, self-contained HTML report with interactive charts.
    
    Creates a professional backtest report with Plotly.js for interactivity.
    All dependencies are loaded via CDN, making it a single-file report.
    
    Args:
        backtest_id: Backtest UUID
        backtest_data: Complete backtest response data
        columnar_data: Columnar format history data
        
    Returns:
        str: Complete HTML document as string
    """
    config = backtest_data.get('backtest_config', {})
    metrics = backtest_data.get('backtest_metrics', {})
    info = backtest_data.get('backtest_info', {})
    
    # Extract key metrics
    target_symbol = config.get('target_symbol', 'Unknown')
    target_type = config.get('target_type', 'asset')
    initial_capital = config.get('initial_capital', 100000)
    
    final_value = metrics.get('final_value', 0)
    total_return = metrics.get('total_return', 0) * 100
    annualized_return = (metrics.get('annualized_return', 0) or 0) * 100
    volatility = (metrics.get('volatility', 0) or 0) * 100
    sharpe_ratio = metrics.get('sharpe_ratio', 0)
    max_drawdown = (metrics.get('max_drawdown', 0) or 0) * 100
    
    # Format dates
    start_date = columnar_data['dates'][0] if columnar_data['dates'] else 'N/A'
    end_date = columnar_data['dates'][-1] if columnar_data['dates'] else 'N/A'
    
    # Calculate drawdown series
    equity_values = columnar_data['values']
    peak = equity_values[0] if equity_values else initial_capital
    drawdowns = []
    for value in equity_values:
        if value > peak:
            peak = value
        dd = ((value - peak) / peak) * 100 if peak > 0 else 0
        drawdowns.append(dd)
    
    # Determine return color
    return_color = '#10b981' if total_return >= 0 else '#ef4444'
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtest Report - {target_symbol}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #1f2937;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .header .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}
        
        .header .date-range {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 12px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
        }}
        
        .metric-label {{
            font-size: 14px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: #1f2937;
        }}
        
        .metric-value.positive {{
            color: #10b981;
        }}
        
        .metric-value.negative {{
            color: #ef4444;
        }}
        
        .chart-container {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
        }}
        
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
        }}
        
        .footer {{
            background: #f9fafb;
            padding: 24px 40px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 14px;
            color: #6b7280;
        }}
        
        .backtest-id {{
            font-family: 'Courier New', monospace;
            background: #f3f4f6;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{target_symbol}</h1>
            <div class="subtitle">Backtest Report ({target_type.title()})</div>
            <div class="date-range">{start_date} → {end_date}</div>
        </div>
        
        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Return</div>
                    <div class="metric-value" style="color: {return_color}">{total_return:+.2f}%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Annualized Return</div>
                    <div class="metric-value">{annualized_return:.2f}%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">{sharpe_ratio:.2f}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Volatility</div>
                    <div class="metric-value">{volatility:.2f}%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Max Drawdown</div>
                    <div class="metric-value negative">{max_drawdown:.2f}%</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Final Value</div>
                    <div class="metric-value">${final_value:,.0f}</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Portfolio Equity Curve</div>
                <div id="equity-chart"></div>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Drawdown Analysis</div>
                <div id="drawdown-chart"></div>
            </div>
        </div>
        
        <div class="footer">
            <div>Generated by NSMBL MCP Server</div>
            <div style="margin-top: 8px;">
                Backtest ID: <span class="backtest-id">{backtest_id}</span>
            </div>
        </div>
    </div>
    
    <script>
        // Equity Curve Chart
        var equityTrace = {{
            x: {json.dumps(columnar_data['dates'])},
            y: {json.dumps(columnar_data['values'])},
            type: 'scatter',
            mode: 'lines',
            name: 'Portfolio Value',
            line: {{
                color: '#667eea',
                width: 3
            }},
            fill: 'tozeroy',
            fillcolor: 'rgba(102, 126, 234, 0.1)',
            hovertemplate: '<b>%{{x}}</b><br>$%{{y:,.2f}}<extra></extra>'
        }};
        
        var equityLayout = {{
            height: 400,
            margin: {{t: 20, r: 20, b: 40, l: 60}},
            xaxis: {{
                title: 'Date',
                gridcolor: '#e5e7eb'
            }},
            yaxis: {{
                title: 'Portfolio Value ($)',
                gridcolor: '#e5e7eb',
                tickformat: '$,.0f'
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'transparent',
            hovermode: 'x unified'
        }};
        
        Plotly.newPlot('equity-chart', [equityTrace], equityLayout, {{responsive: true}});
        
        // Drawdown Chart
        var drawdownTrace = {{
            x: {json.dumps(columnar_data['dates'])},
            y: {json.dumps(drawdowns)},
            type: 'scatter',
            mode: 'lines',
            name: 'Drawdown',
            line: {{
                color: '#ef4444',
                width: 2
            }},
            fill: 'tozeroy',
            fillcolor: 'rgba(239, 68, 68, 0.2)',
            hovertemplate: '<b>%{{x}}</b><br>%{{y:.2f}}%<extra></extra>'
        }};
        
        var drawdownLayout = {{
            height: 300,
            margin: {{t: 20, r: 20, b: 40, l: 60}},
            xaxis: {{
                title: 'Date',
                gridcolor: '#e5e7eb'
            }},
            yaxis: {{
                title: 'Drawdown (%)',
                gridcolor: '#e5e7eb',
                tickformat: '.2f',
                range: [Math.min(...{json.dumps(drawdowns)}) * 1.1, 0]
            }},
            plot_bgcolor: 'white',
            paper_bgcolor: 'transparent',
            hovermode: 'x unified'
        }};
        
        Plotly.newPlot('drawdown-chart', [drawdownTrace], drawdownLayout, {{responsive: true}});
    </script>
</body>
</html>"""
    
    return html


async def create_backtest(
    target_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 100000.0
) -> str:
    """
    Create and queue a backtest (returns immediately).
    
    Args:
        target_id: Asset symbol or strategy ID
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        initial_capital: Initial capital (default: 100000)
        
    Returns:
        str: Backtest ID and status
        
    Note:
        Charged 1¢ per call + projected usage based on complexity.
        Rate limit: 10/minute. Max 10 concurrent backtests.
    """
    try:
        client = NSMBLClient()
        
        # Build request payload
        payload: dict[str, Any] = {
            "target_id": target_id,
            "initial_capital": initial_capital
        }
        
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        
        # Make API request
        backtest = await client.post("/backtests", payload)
        
        # Format response
        result = [
            f"✅ Backtest Queued",
            f"",
            f"Backtest ID: {backtest['backtest_id']}",
            f"Status: {backtest['backtest_status']}",
            f"",
            f"Target: {backtest['backtest_config']['target_symbol']} ({backtest['backtest_config']['target_type']})",
            f"",
            f"The backtest is being processed. Use get_backtest to check status and retrieve results.",
        ]
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def get_backtest(backtest_id: str) -> str:
    """
    Get backtest status and results.
    
    Args:
        backtest_id: Backtest UUID
        
    Returns:
        str: Backtest status, config, metrics, and history
        
    Note:
        Free (no charge) - designed for polling.
    """
    try:
        client = NSMBLClient()
        
        # Make API request
        backtest = await client.get(f"/backtests/{backtest_id}")
        
        status = backtest['backtest_status']
        
        # Format response based on status
        result = [
            f"Backtest Status: {status.upper()}",
            f"",
            f"ID: {backtest['backtest_id']}",
            f"Target: {backtest['backtest_config']['target_symbol']} ({backtest['backtest_config']['target_type']})",
        ]
        
        if status == "queued":
            result.append("\nThe backtest is queued and waiting to execute.")
        
        elif status == "executing":
            result.append("\nThe backtest is currently executing. Please wait...")
        
        elif status == "completed":
            metrics = backtest['backtest_metrics']
            info = backtest['backtest_info']
            
            result.extend([
                f"\n✅ Backtest Completed",
                f"",
                f"Performance Metrics:",
                f"  Final Value: ${metrics.get('final_value', 0):,.2f}",
                f"  Total Return: {metrics.get('total_return', 0) * 100:.2f}%",
                f"  Annualized Return: {(metrics.get('annualized_return', 0) or 0) * 100:.2f}%",
                f"  Volatility: {(metrics.get('volatility', 0) or 0) * 100:.2f}%",
                f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}",
                f"  Max Drawdown: {(metrics.get('max_drawdown', 0) or 0) * 100:.2f}%",
                f"",
                f"Execution Time:",
                f"  Queue Time: {info.get('queued_seconds', 0):.1f}s",
                f"  Execution Time: {info.get('execution_seconds', 0):.1f}s",
                f"  Total Time: {info.get('completion_seconds', 0):.1f}s",
            ])
            
            # Include intelligently sampled historical data
            if backtest.get('backtest_history'):
                history = backtest['backtest_history']
                equity = history.get('equity', [])
                allocations = history.get('allocations', [])
                
                if equity:
                    # Get start and end dates from equity data
                    start_date = equity[0].get('date') if equity else None
                    end_date = equity[-1].get('date') if equity else None
                    
                    if start_date and end_date:
                        # Determine sampling strategy based on duration
                        sampling_info = _get_sampling_strategy(start_date, end_date, len(equity))
                        
                        if sampling_info['sample_data']:
                            # Apply smart sampling
                            sampled_equity = _sample_with_extremes(equity, sampling_info['step'])
                            sampled_allocations = _sample_at_changes(allocations, sampling_info['step']) if allocations else []
                            
                            result.extend([
                                f"",
                                f"📊 Historical Data ({sampling_info['strategy']} sampling):",
                                f"  {len(sampled_equity)} points sampled from {len(equity)} total",
                                f"  Reason: {sampling_info['reason']}",
                                f"  Includes: start, end, peak, trough, allocation changes",
                            ])
                        else:
                            # Return all data (< 1 year)
                            sampled_equity = equity
                            sampled_allocations = allocations
                            result.extend([
                                f"",
                                f"📊 Historical Data (full resolution):",
                                f"  {len(equity)} equity points from {start_date[:10]} to {end_date[:10]}",
                                f"  Reason: {sampling_info['reason']}",
                            ])
                        
                        # Convert to efficient columnar format
                        columnar_data = _format_columnar(sampled_equity, sampled_allocations)
                        
                        # Generate and save HTML report
                        try:
                            html_report = _generate_html_report(backtest_id, backtest, columnar_data)
                            
                            # Try to determine workspace directory
                            # Priority: CWD (if writable) -> Home directory -> Temp directory
                            workspace_dir = None
                            
                            # Try current working directory first
                            try:
                                cwd = os.getcwd()
                                if cwd != '/' and os.access(cwd, os.W_OK):
                                    workspace_dir = cwd
                            except:
                                pass
                            
                            # Fall back to user home directory
                            if not workspace_dir:
                                try:
                                    home = os.path.expanduser('~')
                                    if os.access(home, os.W_OK):
                                        workspace_dir = home
                                except:
                                    pass
                            
                            # Last resort: temp directory
                            if not workspace_dir:
                                workspace_dir = tempfile.gettempdir()
                            
                            # Save report to .nsmbl-mcp/reports directory
                            report_dir = os.path.join(workspace_dir, '.nsmbl-mcp', 'reports')
                            os.makedirs(report_dir, exist_ok=True)
                            
                            report_filename = f"backtest-{backtest_id}.html"
                            report_path = os.path.join(report_dir, report_filename)
                            
                            with open(report_path, 'w', encoding='utf-8') as f:
                                f.write(html_report)
                            
                            result.append(f"")
                            result.append(f"📄 Interactive Report Generated!")
                            result.append(f"   File: {report_path}")
                            result.append(f"   Open this HTML file in your browser for interactive charts and analysis.")
                        except Exception as e:
                            # If report generation fails, just log it but continue
                            result.append(f"\n⚠️  Report generation failed: {str(e)}")
                        
                        # Append JSON data in columnar format for maximum token efficiency
                        result.append(f"\n📊 Raw Data (for custom analysis):")
                        result.append(f"```json")
                        result.append(json.dumps(columnar_data, indent=2))
                        result.append(f"```")
                    else:
                        # Fallback if dates are missing
                        result.append(f"\n📊 Historical Data: {len(equity)} equity points available")
        
        elif status == "failed":
            info = backtest['backtest_info']
            errors = info.get('errors', [])
            result.extend([
                f"\n❌ Backtest Failed",
                f"",
                f"Errors:",
            ])
            for error in errors:
                result.append(f"  - {error}")
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def list_backtests(
    target_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> str:
    """
    List all backtests with optional filtering.
    
    Args:
        target_id: Optional filter by target
        status: Optional filter by status
        limit: Maximum results (default: 100)
        
    Returns:
        str: List of backtests
        
    Note:
        Free (no charge).
    """
    try:
        client = NSMBLClient()
        
        # Build query params
        params: dict[str, Any] = {"limit": limit}
        if target_id:
            params["target_id"] = target_id
        if status:
            if status not in ["queued", "executing", "completed", "failed"]:
                return format_api_error(
                    f"Invalid status: {status}. Must be 'queued', 'executing', 'completed', or 'failed'.",
                    status_code=422
                )
            params["status"] = status
        
        # Make API request
        backtests = await client.get("/backtests", params=params)
        
        if not backtests or len(backtests) == 0:
            return "No backtests found."
        
        # Format response
        result = [f"Found {len(backtests)} backtests:\n"]
        for bt in backtests:
            bt_status = bt['backtest_status']
            target = bt['backtest_config']['target_symbol']
            bt_id = bt['backtest_id']
            
            status_icon = {
                "queued": "⏳",
                "executing": "⚙️",
                "completed": "✅",
                "failed": "❌"
            }.get(bt_status, "•")
            
            result.append(f"{status_icon} {target} - {bt_status}")
            result.append(f"   ID: {bt_id}")
            
            if bt_status == "completed":
                metrics = bt['backtest_metrics']
                total_return = metrics.get('total_return', 0) * 100
                result.append(f"   Return: {total_return:.2f}%")
            
            result.append("")
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def create_backtest_and_wait(
    target_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 100000.0,
    timeout_seconds: Optional[int] = None
) -> str:
    """
    Create backtest and automatically poll until complete (convenience tool).
    
    Args:
        target_id: Asset symbol or strategy ID
        start_date: Optional start date (ISO format)
        end_date: Optional end date (ISO format)
        initial_capital: Initial capital (default: 100000)
        timeout_seconds: Timeout in seconds (default from config)
        
    Returns:
        str: Complete backtest results or timeout message
    """
    config = get_config()
    timeout = timeout_seconds or config.backtest_default_timeout
    poll_interval = config.backtest_poll_interval
    
    try:
        # Create backtest
        client = NSMBLClient()
        
        payload: dict[str, Any] = {
            "target_id": target_id,
            "initial_capital": initial_capital
        }
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        
        backtest = await client.post("/backtests", payload)
        backtest_id = backtest['backtest_id']
        
        # Poll until complete or timeout
        elapsed = 0
        while elapsed < timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            # Check status
            bt = await client.get(f"/backtests/{backtest_id}")
            status = bt['backtest_status']
            
            if status == "completed":
                # Return complete results
                return await get_backtest(backtest_id)
            
            elif status == "failed":
                return await get_backtest(backtest_id)
        
        # Timeout reached
        return format_timeout_error(timeout, backtest_id)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def wait_for_backtest(
    backtest_id: str,
    timeout_seconds: Optional[int] = None
) -> str:
    """
    Poll existing backtest until complete (convenience tool).
    
    Args:
        backtest_id: Backtest UUID
        timeout_seconds: Timeout in seconds (default from config)
        
    Returns:
        str: Complete backtest results or timeout message
    """
    config = get_config()
    timeout = timeout_seconds or config.backtest_default_timeout
    poll_interval = config.backtest_poll_interval
    
    try:
        client = NSMBLClient()
        
        # Poll until complete or timeout
        elapsed = 0
        while elapsed < timeout:
            # Check status
            bt = await client.get(f"/backtests/{backtest_id}")
            status = bt['backtest_status']
            
            if status in ["completed", "failed"]:
                return await get_backtest(backtest_id)
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        # Timeout reached
        return format_timeout_error(timeout, backtest_id)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


async def check_backtest_status(backtest_id: str) -> str:
    """
    Quick status check for backtest (convenience tool).
    
    Args:
        backtest_id: Backtest UUID
        
    Returns:
        str: Simplified status summary
    """
    try:
        client = NSMBLClient()
        
        bt = await client.get(f"/backtests/{backtest_id}")
        status = bt['backtest_status']
        target = bt['backtest_config']['target_symbol']
        
        status_icon = {
            "queued": "⏳",
            "executing": "⚙️",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "•")
        
        result = [
            f"{status_icon} Backtest Status: {status.upper()}",
            f"",
            f"Target: {target}",
            f"ID: {backtest_id}",
        ]
        
        if status == "completed":
            metrics = bt['backtest_metrics']
            result.extend([
                f"",
                f"Total Return: {metrics.get('total_return', 0) * 100:.2f}%",
                f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}",
            ])
            result.append("\nUse get_backtest for full results.")
        
        elif status in ["queued", "executing"]:
            info = bt['backtest_info']
            created_at = info.get('created_at')
            if created_at:
                result.append(f"\nCreated: {created_at}")
            result.append("\nUse get_backtest to check progress or wait_for_backtest to wait for completion.")
        
        return "\n".join(result)
        
    except NSMBLAPIError as e:
        return format_api_error(e.message, e.status_code)
    except Exception as e:
        return format_api_error(f"Unexpected error: {str(e)}")


# Tool definitions for MCP
CREATE_BACKTEST_TOOL = Tool(
    name="create_backtest",
    description=(
        "Create and queue a backtest (returns immediately). "
        "The backtest runs asynchronously. Use get_backtest to check status. "
        "Charged 1¢ per call + projected usage based on complexity. "
        "Rate limit: 10/minute. Max 10 concurrent backtests."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "target_id": {
                "type": "string",
                "description": "Asset symbol (e.g., 'VTI') or strategy ID (e.g., 'sb-...')"
            },
            "start_date": {
                "type": "string",
                "description": "Optional: Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            },
            "end_date": {
                "type": "string",
                "description": "Optional: End date in ISO format"
            },
            "initial_capital": {
                "type": "number",
                "description": "Initial capital for backtest (default: 100000)"
            }
        },
        "required": ["target_id"]
    }
)

GET_BACKTEST_TOOL = Tool(
    name="get_backtest",
    description=(
        "Get backtest status and results. "
        "Returns status, config, and metrics for all statuses. "
        "When completed, automatically generates an interactive HTML report with "
        "beautiful Plotly charts (equity curve, drawdown analysis) saved to "
        ".nsmbl-mcp/reports/ directory. Also includes intelligently sampled historical data "
        "in efficient columnar format (dates[], values[], positions[]) for custom analysis. "
        "Sampling: <1yr=full data, 1-5yr=weekly samples, 5+yr=monthly samples. "
        "Always preserves critical points: start, end, peak, trough, allocation changes. "
        "Free (no charge) - designed for polling."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "backtest_id": {
                "type": "string",
                "description": "Backtest UUID"
            }
        },
        "required": ["backtest_id"]
    }
)

LIST_BACKTESTS_TOOL = Tool(
    name="list_backtests",
    description=(
        "List all backtests with optional filtering by target or status. "
        "Results ordered by newest first. "
        "Free (no charge)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "target_id": {
                "type": "string",
                "description": "Optional: Filter by specific target (asset symbol or strategy ID)"
            },
            "status": {
                "type": "string",
                "enum": ["queued", "executing", "completed", "failed"],
                "description": "Optional: Filter by execution status"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default: 100)"
            }
        }
    }
)

CREATE_BACKTEST_AND_WAIT_TOOL = Tool(
    name="create_backtest_and_wait",
    description=(
        "Convenience tool: Create backtest and automatically poll until complete. "
        "Waits up to timeout_seconds (default: 300) before returning. "
        "Better UX than manual polling. Complex backtests may take several minutes."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "target_id": {
                "type": "string",
                "description": "Asset symbol (e.g., 'VTI') or strategy ID"
            },
            "start_date": {
                "type": "string",
                "description": "Optional: Start date in ISO format"
            },
            "end_date": {
                "type": "string",
                "description": "Optional: End date in ISO format"
            },
            "initial_capital": {
                "type": "number",
                "description": "Initial capital (default: 100000)"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Timeout in seconds (default: 300)"
            }
        },
        "required": ["target_id"]
    }
)

WAIT_FOR_BACKTEST_TOOL = Tool(
    name="wait_for_backtest",
    description=(
        "Convenience tool: Poll existing backtest until complete. "
        "Useful when you want to wait for a previously created backtest."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "backtest_id": {
                "type": "string",
                "description": "Backtest UUID"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Timeout in seconds (default: 300)"
            }
        },
        "required": ["backtest_id"]
    }
)

CHECK_BACKTEST_STATUS_TOOL = Tool(
    name="check_backtest_status",
    description=(
        "Convenience tool: Quick status check without full results. "
        "Returns simplified status summary."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "backtest_id": {
                "type": "string",
                "description": "Backtest UUID"
            }
        },
        "required": ["backtest_id"]
    }
)

