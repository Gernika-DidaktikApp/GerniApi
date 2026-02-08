"""Learning Statistics API endpoints.

Este módulo proporciona endpoints para estadísticas de aprendizaje y rendimiento,
incluyendo puntuaciones, distribución de notas, y análisis de tiempo por actividad.

Los endpoints permiten:
    - Obtener resumen de métricas de aprendizaje (puntuación media, tasa de aprobados)
    - Analizar puntuación media por punto
    - Visualizar distribución de puntuaciones
    - Comparar tiempos de completado por punto (boxplot)

Autor: Gernibide
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
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
    response_model=dict[str, Any],
    summary="Get learning statistics summary",
    description="Returns summary metrics: average score, pass rate, average time, evaluated activities",
)
def get_learning_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
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
    response_model=dict[str, Any],
    summary="Get average score by punto",
    description="Returns average score for each punto",
)
def get_average_score_by_punto(db: Session = Depends(get_db)) -> dict[str, Any]:
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
    response_model=dict[str, Any],
    summary="Get score distribution",
    description="Returns distribution of scores for histogram",
)
def get_score_distribution(db: Session = Depends(get_db)) -> dict[str, Any]:
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
    response_model=dict[str, Any],
    summary="Get time boxplot data by punto",
    description="Returns time distribution data for boxplot visualization",
)
def get_time_boxplot_by_punto(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get Time Boxplot by Punto

    Returns time distribution data for the "Tiempo por Punto" boxplot:
    - **activities**: Array of punto names
    - **times**: Array of time arrays (minutes) for each punto

    Each time array contains all completion times for that punto.
    Only puntos with at least 5 completed activities are included.
    """
    return LearningStatisticsService.get_time_boxplot_by_punto(db)


@router.get(
    "/most-played-activities",
    response_model=dict[str, Any],
    summary="Get most played activities",
    description="Returns top 10 activities ordered by number of times played",
)
def get_most_played_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Most Played Activities

    Returns the most played activities ordered by play count:
    - **activities**: Array of activity names
    - **counts**: Number of times each activity was played

    ### Note
    Counts all actividad_progreso records regardless of status.
    """
    return LearningStatisticsService.get_most_played_activities(db, limit)


@router.get(
    "/highest-scoring-activities",
    response_model=dict[str, Any],
    summary="Get highest scoring activities",
    description="Returns top 10 activities with highest average scores",
)
def get_highest_scoring_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ## Get Highest Scoring Activities

    Returns activities with the highest average scores:
    - **activities**: Array of activity names
    - **scores**: Average score (0-10) for each activity

    ### Note
    Only includes activities with at least 3 completed attempts.
    """
    return LearningStatisticsService.get_highest_scoring_activities(db, limit)


@router.get(
    "/class-performance",
    response_model=dict[str, Any],
    summary="Get performance by class",
    description="Returns average performance for each class",
)
def get_class_performance(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    ## Get Class Performance

    Returns average performance metrics for each class:
    - **classes**: Array of class names
    - **scores**: Average score (0-10) for each class
    - **student_counts**: Number of students in each class

    ### Note
    Only includes classes with at least one completed activity.
    Ordered by score (descending).
    """
    return LearningStatisticsService.get_class_performance(db)


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
