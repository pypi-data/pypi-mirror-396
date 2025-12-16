"""
Strategies endpoint for LLM-generated strategies.

Creates strategies from natural language prompts using LangGraph + Anthropic + Modal.
Persists strategies to database with clean schema and minimal responses.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
import math

from app.core.middleware import get_current_user, get_optional_user
from app.core.logging import get_domain_logger
from app.core.config import settings
from app.db.connection import get_db
from app.db.strategies.tables_strategies import Strategy
from app.errors.exceptions import handle_validation_error, handle_not_found_error
from app.api.v1.schemas.strategies.schema_strategy import (
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyResponse,
    StrategyDetailResponse,
    StrategyHistoryResponse,
    StrategyMetricsResponse,
    StrategyUsage,
    StrategyAvailability
)
from app.db.strategies import crud_strategies
from app.db.strategies.crud_strategies import calculate_script_hash
from app.db.strategies.tables_strategies import generate_strategy_symbol
from app.services.internal.auth.user_service import charge_strategy_generation

logger = get_domain_logger('api', __name__)

router = APIRouter()


# ================================
# Helper Functions
# ================================

def calculate_billing_units(token_usage: Dict[str, int], duration_seconds: float) -> Dict[str, Any]:
    """
    Calculate billing units for Stripe metering.
    
    Pricing Model (1 Unit = 1 cent):
    - Base Fee: 1 unit (API call)
    - Token Fee: 1 unit per 1000 tokens (input + output)
    - Compute Fee: 1 unit per second of Modal execution time
    """
    
    # 1. Base Fee
    base_units = 1
    
    # 2. Token Fee
    input_tokens = token_usage.get("input_tokens", 0)
    output_tokens = token_usage.get("output_tokens", 0)
    total_tokens = input_tokens + output_tokens
    token_units = math.ceil(total_tokens / 1000.0)
    
    # 3. Compute Fee
    compute_units = math.ceil(duration_seconds)
    
    # Total
    total_units = base_units + token_units + compute_units
    
    # Return ONLY billing data
    return {
        "units": total_units,
        "base": base_units,
        "tokens": token_units,
        "seconds": compute_units
    }


async def report_usage_background(user_id: str, units: int):
    """Background task to report usage to Stripe via user service"""
    try:
        import uuid
        await charge_strategy_generation(uuid.UUID(user_id), units)
    except Exception as e:
        logger.error(f"Failed to report usage to Stripe: {e}")


def calculate_performance_metrics(history: Dict[str, Any]) -> Dict[str, float]:
    """Calculate performance metrics from history data"""
    if not history or "returns" not in history or not history["returns"]:
        return {
            "cagr": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "trades": 0,
            "trading_days": 0
        }
        
    returns = pd.Series(history["returns"])
    
    # Remove NaN values for calculations
    clean_returns = returns.dropna()
    
    if len(clean_returns) == 0:
        return {
            "cagr": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "trades": 0,
            "trading_days": 0
        }
    
    # CAGR
    cumulative_return = float((1 + clean_returns).prod() - 1)
    days = len(clean_returns)
    years = days / 252.0
    cagr = float((1 + cumulative_return) ** (1/years) - 1) if years > 0 else 0.0
    
    # Volatility (using clean returns without NaN)
    volatility = float(clean_returns.std(ddof=1) * np.sqrt(252))
    
    # Sharpe
    sharpe = float(cagr / volatility) if volatility > 0 and not np.isnan(volatility) else 0.0
    
    # Drawdown (using clean returns)
    cum_series = (1 + clean_returns).cumprod()
    running_max = cum_series.cummax()
    drawdown = (cum_series / running_max - 1)
    max_drawdown = float(drawdown.min()) if len(drawdown) > 0 else 0.0
    
    # Trades (estimate from position changes)
    trades = 0
    if "positions" in history:
        positions = history["positions"]
        if len(positions) > 1:
            prev_pos = positions[0]
            for i in range(1, len(positions)):
                curr_pos = positions[i]
                if curr_pos != prev_pos:
                    trades += 1 # Rebalance
                prev_pos = curr_pos
    
    return {
        "cagr": cagr,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "trades": trades,
        "trading_days": days
    }


def build_strategy_response(strategy: Strategy) -> StrategyResponse:
    """Build strategy response with computed fields"""
    return StrategyResponse(
        id=strategy.id,
        name=strategy.name,
        symbol=strategy.symbol,
        prompt=strategy.prompt,
        url=f"{settings.FRONTEND_URL}/strategy/{strategy.slug}",
        embed=f'<iframe src="{settings.FRONTEND_URL}/embed/{strategy.slug}" width="100%" height="400" frameborder="0" loading="lazy"></iframe>',
        is_public=strategy.is_public,
        created_at=strategy.created_at,
        updated_at=strategy.updated_at
    )


def build_detail_response(strategy: Strategy) -> StrategyDetailResponse:
    """Build strategy detail response with computed fields"""
    availability_data = None
    if strategy.history and "availability" in strategy.history:
        availability_data = strategy.history["availability"]
    
    return StrategyDetailResponse(
        id=strategy.id,
        name=strategy.name,
        symbol=strategy.symbol,
        prompt=strategy.prompt,
        url=f"{settings.FRONTEND_URL}/strategy/{strategy.slug}",
        embed=f'<iframe src="{settings.FRONTEND_URL}/embed/{strategy.slug}" width="100%" height="400" frameborder="0" loading="lazy"></iframe>',
        is_public=strategy.is_public,
        created_at=strategy.created_at,
        updated_at=strategy.updated_at,
        script=strategy.script,
        usage=StrategyUsage(**strategy.usage) if strategy.usage else None,
        timing=strategy.timing,
        availability=StrategyAvailability(**availability_data) if availability_data else None
    )


# ================================
# Endpoints
# ================================

@router.post(
    "",
    operation_id="createStrategy",
    summary="Create Strategy",
    response_model=StrategyResponse,
    status_code=201
)
async def create_strategy(
    strategy_data: StrategyCreateRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new strategy from natural language prompt.
    
    Generates code via LLM, executes to create history, persists to database.
    Synchronous execution (user waits 10-50s).
    """
    
    user_id, _ = current_user
    
    # Generate correlation ID for tracing
    import uuid
    correlation_id = str(uuid.uuid4())
    logger.info(f"[{correlation_id}] Creating strategy for user {user_id}")
    
    try:
        # Validate input
        prompt = strategy_data.prompt.strip()
        if not prompt:
            raise handle_validation_error("empty_prompt", "Prompt cannot be empty")
        
        # Step 1: Generate strategy name (LLM or use provided)
        if strategy_data.name:
            strategy_name = strategy_data.name
            logger.info(f"Using user-provided name: {strategy_name}")
        else:
            from app.pipelines.strategies.nodes.n2b_name_generation import generate_strategy_name
            strategy_name = generate_strategy_name(prompt)
            logger.info(f"Generated name: {strategy_name}")
        
        # Step 2: Generate symbol
        strategy_symbol = generate_strategy_symbol(strategy_name)
        logger.info(f"Generated symbol: {strategy_symbol}")
        
        # Step 3: Run workflow (code generation + execution)
        from app.pipelines.strategies.workflow import run_agent_workflow
        
        initial_state = {
            "user_description": prompt,
            "user_id": str(user_id),
            "trace_id": correlation_id,
            "timing": {}
        }
        
        logger.info(f"[{correlation_id}] Running workflow...")
        final_state = await run_agent_workflow(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            logger.error(f"Workflow failed: {final_state['error']}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "generation_failed",
                    "message": final_state["error"]
                }
            )
        
        execution_result = final_state.get("execution_result", {})
        if execution_result.get("status") == "error":
            logger.error(f"Execution failed: {execution_result.get('message')}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "execution_failed",
                    "message": execution_result.get("message", "Execution failed")
                }
            )
        
        # Step 4: Extract results
        generated_code = final_state.get("generated_code", "")
        dates = execution_result.get("dates", [])
        returns = execution_result.get("returns", [])
        positions = execution_result.get("position_history", [])
        start_dates_data = execution_result.get("start_dates", {})
        
        # Calculate hash
        script_hash = calculate_script_hash(generated_code)
        
        # Build availability
        availability = {
            "partial": start_dates_data.get("partial_universe_start_date"),
            "complete": start_dates_data.get("complete_universe_start_date")
        }
        
        # Build history JSONB (includes availability now)
        history = {
            "dates": [str(d) for d in dates],
            "returns": returns,
            "positions": positions,
            "availability": availability
        }
        
        # Build usage JSONB (Billing only) and timing JSONB (Pipeline metrics)
        timing_data = final_state.get("timing", {})
        execution_timing = timing_data.get("n4_modal_execution", {})
        duration_seconds = execution_timing.get("duration_seconds", 0)
        token_usage = final_state.get("token_usage", {})
        
        # Calculate billing units (pure billing data only)
        usage_data = calculate_billing_units(token_usage, duration_seconds)
        
        # Timing data stored separately  
        pipeline_timing = timing_data
        
        # Report usage to Stripe (Background)
        background_tasks.add_task(report_usage_background, str(user_id), usage_data["units"])
        
        # Step 5: Save to database
        db_strategy = crud_strategies.create_strategy(
            db=db,
            user_id=user_id,
            name=strategy_name,
            symbol=strategy_symbol,
            prompt=prompt,
            script=generated_code,
            script_hash=script_hash,
            usage=usage_data,
            timing=pipeline_timing,
            history=history
        )
        
        logger.info(f"[{correlation_id}] Strategy created: {db_strategy.id}")
        
        # Step 6: Build response
        return build_strategy_response(db_strategy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating strategy: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Internal error: {str(e)}"
            }
        )


@router.get(
    "",
    operation_id="listStrategies",
    summary="List Strategies",
    response_model=List[StrategyResponse]
)
async def list_strategies(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all strategies for the user"""
    
    user_id, _ = current_user
    strategies = crud_strategies.list_strategies(db, user_id)
    
    return [build_strategy_response(s) for s in strategies]


@router.get(
    "/{identifier}",
    operation_id="getStrategy",
    summary="Get Strategy",
    response_model=StrategyDetailResponse
)
async def get_strategy(
    identifier: str,
    current_user = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get strategy by slug (public) or ID (owner)"""
    
    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            return build_detail_response(strategy)
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                return build_detail_response(strategy)
        raise HTTPException(404, {"error": "not_found", "message": "Strategy not found"})
    
    # Try private access by ID (requires auth)
    if current_user:
        user_id, _ = current_user
        strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
        if strategy:
            return build_detail_response(strategy)
    
    raise handle_not_found_error("Strategy", identifier)


@router.get(
    "/{identifier}/history",
    operation_id="getStrategyHistory",
    summary="Get Strategy History",
    response_model=StrategyHistoryResponse
)
async def get_strategy_history(
    identifier: str,
    current_user = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get daily price history for strategy (public or owner)"""
    
    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            pass
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                pass
            else:
                raise HTTPException(404, {"error": "not_found", "message": "Strategy not found"})
        else:
            raise HTTPException(404, {"error": "not_found", "message": "Strategy not found"})
    else:
        # Try private access by ID (requires auth)
        if current_user:
            user_id, _ = current_user
            strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
            if not strategy:
                raise handle_not_found_error("Strategy", identifier)
        else:
            raise handle_not_found_error("Strategy", identifier)
    
    if not strategy.history:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "no_history",
                "message": "Strategy has no history data"
            }
        )
    
    history_data = strategy.history or {}
    availability_data = history_data.get("availability")
    
    return StrategyHistoryResponse(
        dates=history_data.get("dates", []),
        returns=history_data.get("returns", []),
        positions=history_data.get("positions", []),
        availability=StrategyAvailability(**availability_data) if availability_data else None
    )


@router.get(
    "/{identifier}/metrics",
    operation_id="getStrategyMetrics",
    summary="Get Strategy Metrics",
    response_model=StrategyMetricsResponse
)
async def get_strategy_metrics(
    identifier: str,
    current_user = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """Get calculated performance metrics for strategy (public or owner)"""
    
    # Try public access by slug
    strategy = crud_strategies.get_strategy_by_slug(db, identifier)
    if strategy:
        if strategy.is_public:
            # Public access allowed
            pass
        elif current_user:
            user_id, _ = current_user
            if strategy.user_id == user_id:
                # Owner access allowed
                pass
            else:
                raise HTTPException(404, {"error": "not_found", "message": "Strategy not found"})
        else:
            raise HTTPException(404, {"error": "not_found", "message": "Strategy not found"})
    else:
        # Try private access by ID (requires auth)
        if current_user:
            user_id, _ = current_user
            strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
            if not strategy:
                raise handle_not_found_error("Strategy", identifier)
        else:
            raise handle_not_found_error("Strategy", identifier)
    
    # Calculate metrics on the fly from history
    metrics = calculate_performance_metrics(strategy.history)
    
    return StrategyMetricsResponse(**metrics)


@router.patch(
    "/{identifier}",
    operation_id="updateStrategy",
    summary="Update Strategy",
    response_model=StrategyResponse
)
async def update_strategy(
    identifier: str,
    updates: StrategyUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update strategy (owner only)"""
    user_id, _ = current_user
    
    # Must be owner
    strategy = crud_strategies.get_strategy_by_id(db, user_id, identifier)
    if not strategy:
        raise handle_not_found_error("Strategy", identifier)
    
    # Apply updates
    updated_strategy = crud_strategies.update_strategy(
        db, strategy, updates.name, updates.symbol, updates.is_public
    )
    
    return build_strategy_response(updated_strategy)


@router.delete(
    "/{identifier}",
    operation_id="deleteStrategy",
    summary="Delete Strategy",
    status_code=204
)
async def delete_strategy(
    identifier: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete strategy"""
    
    user_id, _ = current_user
    success = crud_strategies.delete_strategy(db, user_id, identifier)
    
    if not success:
        raise handle_not_found_error("Strategy", identifier)
    
    return Response(status_code=204)
