"""Router de estadísticas generales.

Este módulo proporciona endpoints para obtener estadísticas de usuarios,
actividad y métricas para los dashboards de visualización.

Autor: Gernibide
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging.logger import log_info, log_with_context
from app.services.statistics_service import StatisticsService

router = APIRouter(
    prefix="/api/statistics",
    tags=["📊 Statistics"],
    responses={
        422: {"description": "Error de validación"},
    },
)


@router.get(
    "/users/summary",
    response_model=dict[str, Any],
    summary="Get user statistics summary",
    description="Returns summary metrics: DAU, new users today, active/total ratio, and logins today",
)
def get_users_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get User Statistics Summary

    Returns key metrics for the users statistics dashboard:
    - **dau**: Daily Active Users (users who started a game today)
    - **new_users_today**: Number of users registered today
    - **ratio_active_total**: Percentage of active users (last 7 days) vs total users
    - **logins_today**: Number of game sessions started today
    - **total_users**: Total number of registered users

    This endpoint is used by the statistics page summary cards.
    """
    summary = StatisticsService.get_users_summary(db)

    log_with_context(
        "info",
        "Resumen de estadísticas de usuarios consultado",
        dau=summary.get("dau", 0),
        total_users=summary.get("total_users", 0),
        new_users_today=summary.get("new_users_today", 0),
    )

    return summary


@router.get(
    "/users/active-timeline",
    response_model=dict[str, Any],
    summary="Get active users timeline",
    description="Returns DAU, WAU, and MAU data for the specified number of days",
)
def get_active_users_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Active Users Timeline (DAU/WAU/MAU)

    Returns timeline data for the "Usuarios Activos" chart showing:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **dau**: Daily Active Users for each date
    - **wau**: Weekly Active Users (7-day rolling window)
    - **mau**: Monthly Active Users (30-day rolling window)

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)

    ### Notes
    - DAU: Unique users who started a game on that specific day
    - WAU: Unique users who started a game in the 7 days ending on that date
    - MAU: Unique users who started a game in the 30 days ending on that date
    """
    result = StatisticsService.get_active_users_timeline(db, days)

    log_info(
        "Timeline de usuarios activos consultado",
        days=days,
        data_points=len(result.get("dates", [])),
    )

    return result


@router.get(
    "/users/new-by-day",
    response_model=dict[str, Any],
    summary="Get new users by day",
    description="Returns count of new user registrations per day",
)
def get_new_users_by_day(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get New Users by Day

    Returns daily new user registration data for the "Nuevos Usuarios por Día" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **counts**: Number of users registered on each date

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)
    """
    result = StatisticsService.get_new_users_by_day(db, days)

    log_info(
        "Nuevos usuarios por día consultado",
        days=days,
        data_points=len(result.get("dates", [])),
    )

    return result


@router.get(
    "/users/active-ratio-timeline",
    response_model=dict[str, Any],
    summary="Get active ratio timeline",
    description="Returns the ratio of active users to total users over time",
)
def get_active_ratio_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Active Ratio Timeline

    Returns the percentage of active users vs total users for the "Ratio Usuarios Activos / Totales" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **ratios**: Percentage of active users (last 7 days) vs total registered users on each date

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)

    ### Calculation
    - Active users = unique users who started a game in the 7 days before the date
    - Total users = all users registered up to that date
    - Ratio = (active users / total users) * 100
    """
    result = StatisticsService.get_active_ratio_timeline(db, days)

    log_info(
        "Ratio de usuarios activos consultado",
        days=days,
        data_points=len(result.get("dates", [])),
    )

    return result


@router.get(
    "/users/logins-by-day",
    response_model=dict[str, Any],
    summary="Get logins by day",
    description="Returns number of game sessions (logins) started per day",
)
def get_logins_by_day(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Logins by Day

    Returns daily login counts for the "Logins por Día" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **counts**: Number of game sessions (partidas) started on each date

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)

    ### Note
    A "login" is counted as each time a user starts a new game session (partida).
    Multiple logins per user per day are counted separately.
    """
    result = StatisticsService.get_logins_by_day(db, days)

    log_info(
        "Logins por día consultado",
        days=days,
        data_points=len(result.get("dates", [])),
    )

    return result


@router.post(
    "/cache/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear statistics cache",
    description="Clears all cached statistics data. Use this after importing new data or when you need fresh results.",
)
def clear_statistics_cache():
    """
    ## Clear Statistics Cache

    Clears all cached statistics data to force fresh queries on next request.

    **Use cases:**
    - After importing/generating new test data
    - After database migrations
    - When you suspect stale data

    **Note:** The cache automatically expires after 5 minutes (300 seconds),
    so you typically don't need to clear it manually.

    Returns HTTP 204 (No Content) on success.
    """
    StatisticsService.clear_cache()
    return None
