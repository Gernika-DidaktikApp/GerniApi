"""Gameplay Statistics API endpoints.

Este módulo proporciona endpoints para estadísticas de juego,
incluyendo partidas creadas, estado de actividades, y tasas de completado.

Los endpoints permiten:
    - Obtener resumen de partidas (total, completadas, en progreso, duración promedio)
    - Analizar partidas creadas por día
    - Comparar partidas por estado (completadas, abandonadas, en progreso)
    - Seguir línea temporal de actividades por estado
    - Evaluar tasa de completado por punto

Autor: Gernibide
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.gameplay_statistics_service import GameplayStatisticsService

router = APIRouter(
    prefix="/api/statistics/gameplay",
    tags=["📊 Statistics - Gameplay"],
    responses={
        422: {"description": "Error de validación"},
    },
)


@router.get(
    "/summary",
    response_model=dict[str, Any],
    summary="Get gameplay statistics summary",
    description="Returns summary metrics: total partidas, completadas, en progreso, duración promedio",
)
def get_gameplay_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get Gameplay Statistics Summary

    Returns key metrics for the gameplay statistics dashboard:
    - **total_partidas**: Total number of game sessions
    - **partidas_completadas**: Number of completed games
    - **partidas_en_progreso**: Number of games in progress
    - **duracion_promedio**: Average duration of completed games (in minutes)

    This endpoint is used by the gameplay statistics page summary cards.
    """
    return GameplayStatisticsService.get_gameplay_summary(db)


@router.get(
    "/partidas-by-day",
    response_model=dict[str, Any],
    summary="Get partidas created by day",
    description="Returns count of game sessions created per day",
)
def get_partidas_by_day(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Partidas by Day

    Returns daily game session creation data for the "Partidas Creadas por Día" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **counts**: Number of partidas created on each date

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)
    """
    return GameplayStatisticsService.get_partidas_by_day(db, days)


@router.get(
    "/partidas-by-status",
    response_model=dict[str, Any],
    summary="Get partidas by status",
    description="Returns count of partidas by status (completada, abandonada, en_progreso)",
)
def get_partidas_by_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get Partidas by Status

    Returns partida counts by status for the donut chart:
    - **completadas**: Number of completed games
    - **abandonadas**: Number of abandoned games
    - **en_progreso**: Number of games in progress
    - **total**: Total count

    This endpoint is used by the "Partidas Completadas vs Abandonadas" donut chart.
    """
    return GameplayStatisticsService.get_partidas_by_status(db)


@router.get(
    "/actividades-by-status-timeline",
    response_model=dict[str, Any],
    summary="Get activities by status timeline",
    description="Returns timeline of activities by status (completados, en progreso, abandonados)",
)
def get_actividades_by_status_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Actividades by Status Timeline

    Returns stacked bar chart data for the "Actividades Iniciadas vs Completadas" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **completados**: Number of completed activities for each date
    - **en_progreso**: Number of in-progress activities for each date
    - **abandonados**: Number of abandoned activities for each date

    ### Parameters
    - **days**: Number of days to retrieve (default: 30, max: 365)
    """
    return GameplayStatisticsService.get_actividades_by_status_timeline(db, days)


@router.get(
    "/completion-rate-by-punto",
    response_model=dict[str, Any],
    summary="Get completion rate by punto",
    description="Returns completion rate percentage for each punto",
)
def get_completion_rate_by_punto(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get Completion Rate by Punto

    Returns completion rate data for the "Completion Rate por Punto" chart:
    - **activities**: Array of punto names
    - **rates**: Completion rate percentage (0-100) for each punto

    ### Note
    Only puntos with at least one activity are included.
    Completion rate = (completed activities / total activities) * 100
    """
    return GameplayStatisticsService.get_completion_rate_by_punto(db)


@router.post(
    "/cache/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear gameplay statistics cache",
    description="Clears all cached gameplay statistics data",
)
def clear_gameplay_cache():
    """
    ## Clear Gameplay Statistics Cache

    Clears all cached gameplay statistics data to force fresh queries on next request.

    Returns HTTP 204 (No Content) on success.
    """
    GameplayStatisticsService.clear_cache()
    return None
