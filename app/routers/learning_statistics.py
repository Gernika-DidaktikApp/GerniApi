"""
Learning Statistics API endpoints
Provides data for learning/performance statistics dashboard (scores, tiempo)
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.learning_statistics_service import LearningStatisticsService

router = APIRouter(
    prefix="/api/statistics/learning",
    tags=["📊 Statistics - Learning"],
    responses={
        422: {"description": "Error de validación"},
    },
)


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    summary="Get learning statistics summary",
    description="Returns summary metrics: average score, pass rate, average time, evaluated activities",
)
def get_learning_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    ## Get Learning Statistics Summary

    Returns key metrics for the learning statistics dashboard:
    - **puntuacion_media**: Average score (0-10) of completed activities
    - **aprobados_porcentaje**: Pass rate percentage (score >= 5)
    - **tiempo_medio**: Average completion time in minutes
    - **actividades_evaluadas**: Total number of evaluated activities

    This endpoint is used by the learning statistics page summary cards.
    """
    return LearningStatisticsService.get_learning_summary(db)


@router.get(
    "/average-score-by-punto",
    response_model=Dict[str, Any],
    summary="Get average score by punto",
    description="Returns average score for each punto",
)
def get_average_score_by_punto(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    ## Get Average Score by Punto

    Returns average score data for the "Puntuación Media por Punto" chart:
    - **activities**: Array of punto names
    - **scores**: Average score (0-10) for each punto

    Puntos are ordered by score (descending).
    """
    return LearningStatisticsService.get_average_score_by_punto(db)


@router.get(
    "/score-distribution",
    response_model=Dict[str, Any],
    summary="Get score distribution",
    description="Returns distribution of scores for histogram",
)
def get_score_distribution(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    ## Get Score Distribution

    Returns score distribution data for the "Distribución de Puntuaciones" histogram:
    - **scores**: Array of all individual scores
    - **mean**: Mean score value

    This endpoint is used by the histogram chart showing score frequency distribution.
    """
    return LearningStatisticsService.get_score_distribution(db)


@router.get(
    "/time-boxplot-by-punto",
    response_model=Dict[str, Any],
    summary="Get time boxplot data by punto",
    description="Returns time distribution data for boxplot visualization",
)
def get_time_boxplot_by_punto(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    ## Get Time Boxplot by Punto

    Returns time distribution data for the "Tiempo por Punto" boxplot:
    - **activities**: Array of punto names
    - **times**: Array of time arrays (minutes) for each punto

    Each time array contains all completion times for that punto.
    Only puntos with at least 5 completed activities are included.
    """
    return LearningStatisticsService.get_time_boxplot_by_punto(db)


@router.post(
    "/cache/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear learning statistics cache",
    description="Clears all cached learning statistics data",
)
def clear_learning_cache():
    """
    ## Clear Learning Statistics Cache

    Clears all cached learning statistics data to force fresh queries on next request.

    Returns HTTP 204 (No Content) on success.
    """
    LearningStatisticsService.clear_cache()
    return None
