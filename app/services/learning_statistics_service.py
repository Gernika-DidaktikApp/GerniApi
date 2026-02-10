"""Service for calculating learning/performance statistics.

This module provides data for learning statistics dashboards, including
academic performance metrics such as scores, pass rates, and time spent.

Autor: Gernibide
"""

import time
from collections.abc import Callable
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.actividad import Actividad
from app.models.actividad_progreso import ActividadProgreso
from app.models.clase import Clase
from app.models.juego import Partida
from app.models.punto import Punto
from app.models.usuario import Usuario


class CacheEntry:
    """Cache entry with TTL (Time To Live) for temporary data storage.

    Attributes:
        data: The cached data of any type.
        expires_at: Unix timestamp when this cache entry expires.
    """

    def __init__(self, data: Any, ttl_seconds: int):
        """Initialize cache entry.

        Args:
            data: The data to cache.
            ttl_seconds: Time to live in seconds.
        """
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        """Check if cache entry has expired.

        Returns:
            True if current time exceeds expiration time, False otherwise.
        """
        return time.time() > self.expires_at


class LearningStatisticsService:
    """Service for calculating learning/performance statistics with caching.

    This service provides comprehensive learning metrics including:
    - Average scores and grade distributions
    - Pass/fail rates
    - Time spent on activities
    - Performance analysis by activity punto

    All methods utilize an in-memory cache with configurable TTL to reduce
    database load.

    Attributes:
        _cache: Class-level cache storage for computed statistics.
        CACHE_TTL: Default cache time-to-live in seconds (300 = 5 minutes).
    """

    # Cache storage
    _cache: dict[str, CacheEntry] = {}

    # Cache TTL in seconds (5 minutes by default)
    CACHE_TTL = 300

    @classmethod
    def _get_cached_or_fetch(
        cls, cache_key: str, fetch_func: Callable, *args, ttl: int | None = None
    ) -> Any:
        """Generic cache getter with TTL.

        Args:
            cache_key: Unique key for this cached data.
            fetch_func: Function to call if cache miss.
            *args: Arguments to pass to fetch_func.
            ttl: Custom TTL in seconds. Uses CACHE_TTL if None.

        Returns:
            Cached or freshly fetched data.
        """
        # Check cache
        if cache_key in cls._cache:
            entry = cls._cache[cache_key]
            if not entry.is_expired():
                return entry.data

        # Cache miss or expired - fetch new data
        data = fetch_func(*args)

        # Store in cache
        ttl_seconds = ttl if ttl is not None else cls.CACHE_TTL
        cls._cache[cache_key] = CacheEntry(data, ttl_seconds)

        return data

    @classmethod
    def clear_cache(cls):
        """Clear all cached data.

        Use this method when you need to force refresh of all statistics,
        for example after bulk data imports or updates.
        """
        cls._cache.clear()

    @staticmethod
    def get_learning_summary(db: Session) -> dict[str, Any]:
        """Get summary statistics for learning/performance (with caching).

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - puntuacion_media: Average score across all completed activities
                - aprobados_porcentaje: Pass rate (score >= 5) as percentage
                - tiempo_medio: Average time spent in minutes
                - actividades_evaluadas: Number of evaluated activities
        """
        cache_key = "learning_summary"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_learning_summary, db
        )

    @staticmethod
    def _fetch_learning_summary(db: Session) -> dict[str, Any]:
        """Internal method to fetch learning summary from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with learning summary metrics.
        """
        # Average score (puntuacion) of completed activities
        avg_score = (
            db.query(func.avg(ActividadProgreso.puntuacion))
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .scalar()
            or 0
        )

        # Count of evaluated activities (completed activities with score)
        evaluated_count = (
            db.query(ActividadProgreso)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .count()
        )

        # Pass rate (puntuacion >= 5)
        total_with_score = (
            db.query(ActividadProgreso)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .count()
        )

        passed_count = (
            db.query(ActividadProgreso)
            .filter(
                and_(ActividadProgreso.puntuacion >= 5, ActividadProgreso.estado == "completado")
            )
            .count()
        )

        pass_rate = (passed_count / total_with_score * 100) if total_with_score > 0 else 0

        # Average time (duracion) in minutes
        avg_time = (
            db.query(func.avg(ActividadProgreso.duracion))
            .filter(
                and_(
                    ActividadProgreso.duracion.isnot(None), ActividadProgreso.estado == "completado"
                )
            )
            .scalar()
            or 0
        )

        # Detectar si las duraciones están en milisegundos o segundos
        # Si el promedio es > 3600 (1 hora en segundos), probablemente está en milisegundos
        if avg_time and avg_time > 3600:
            tiempo_medio_min = round(avg_time / 60000, 0)  # milisegundos a minutos
        else:
            tiempo_medio_min = round(avg_time / 60, 0) if avg_time else 0  # segundos a minutos

        return {
            "puntuacion_media": round(avg_score, 1),
            "aprobados_porcentaje": round(pass_rate, 1),
            "tiempo_medio": tiempo_medio_min,
            "actividades_evaluadas": evaluated_count,
        }

    @staticmethod
    def get_average_score_by_punto(db: Session) -> dict[str, list]:
        """Get average score by punto (with caching).

        Calculates average scores for each activity punto, ordered by
        score descending.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - activities: List of punto names (sorted by score)
                - scores: Average score for each punto (0-10 scale)
        """
        cache_key = "average_score_by_punto"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_average_score_by_punto, db
        )

    @staticmethod
    def _fetch_average_score_by_punto(db: Session) -> dict[str, list]:
        """Internal method to fetch average score by punto from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with average scores per punto.
        """
        # Query puntos with their average scores
        results = (
            db.query(Punto.nombre, func.avg(ActividadProgreso.puntuacion).label("avg_score"))
            .join(ActividadProgreso, ActividadProgreso.id_punto == Punto.id)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .group_by(Punto.id, Punto.nombre)
            .order_by(func.avg(ActividadProgreso.puntuacion).desc())
            .all()
        )

        activities = []
        scores = []

        for nombre, avg_score in results:
            activities.append(nombre)
            scores.append(round(avg_score, 1) if avg_score else 0)

        return {"activities": activities, "scores": scores}

    @staticmethod
    def get_score_distribution(db: Session) -> dict[str, list]:
        """Get score distribution for histogram (with caching).

        Retrieves all individual scores from completed activities to enable
        histogram visualization and statistical analysis.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - scores: List of all individual scores
                - mean: Mean score value
        """
        cache_key = "score_distribution"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_score_distribution, db
        )

    @staticmethod
    def _fetch_score_distribution(db: Session) -> dict[str, Any]:
        """Internal method to fetch score distribution from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with score distribution data.
        """
        # Get all scores from completed activities
        scores_query = (
            db.query(ActividadProgreso.puntuacion)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .all()
        )

        scores = [score[0] for score in scores_query if score[0] is not None]

        # Calculate mean
        mean_score = sum(scores) / len(scores) if scores else 0

        return {"scores": scores, "mean": round(mean_score, 1)}

    @staticmethod
    def get_time_boxplot_by_punto(db: Session) -> dict[str, Any]:
        """Get time data for boxplot by punto (with caching).

        Retrieves time distribution data for each punto to enable boxplot
        visualization. Only includes puntos with at least 5 data points.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - activities: List of punto names (filtered to those with >= 5 data points)
                - times: List of time arrays (in minutes) for each punto
        """
        cache_key = "time_boxplot_by_punto"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_time_boxplot_by_punto, db
        )

    @staticmethod
    def _fetch_time_boxplot_by_punto(db: Session) -> dict[str, Any]:
        """Internal method to fetch time boxplot data from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with time distribution data per punto.
        """
        # Get puntos
        puntos = db.query(Punto).all()

        punto_names = []
        punto_times = []

        for punto in puntos:
            # Get all durations for this punto (in minutes)
            times_query = (
                db.query(ActividadProgreso.duracion)
                .filter(
                    and_(
                        ActividadProgreso.id_punto == punto.id,
                        ActividadProgreso.duracion.isnot(None),
                        ActividadProgreso.estado == "completado",
                    )
                )
                .all()
            )

            # Detectar si está en milisegundos o segundos basándose en el primer valor
            if times_query and times_query[0][0] and times_query[0][0] > 3600:
                # Milisegundos a minutos
                times = [round(t[0] / 60000, 1) for t in times_query if t[0]]
            else:
                # Segundos a minutos
                times = [round(t[0] / 60, 1) for t in times_query if t[0]]

            # Only include puntos with at least 5 data points
            if len(times) >= 5:
                punto_names.append(punto.nombre)
                punto_times.append(times)

        return {"activities": punto_names, "times": punto_times}

    @staticmethod
    def get_most_played_activities(db: Session, limit: int = 10) -> dict[str, list]:
        """Get most played activities ordered by play count.

        Args:
            db: Database session for querying.
            limit: Number of top activities to return.

        Returns:
            Dictionary containing:
                - activities: List of activity names
                - counts: Number of times each activity was played
        """
        cache_key = f"most_played_activities_{limit}"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key,
            lambda db: LearningStatisticsService._fetch_most_played_activities(db, limit),
            db,
        )

    @staticmethod
    def _fetch_most_played_activities(db: Session, limit: int) -> dict[str, list]:
        """Internal method to fetch most played activities from database.

        Args:
            db: Database session for querying.
            limit: Number of top activities to return.

        Returns:
            Dictionary with activity names and play counts.
        """
        results = (
            db.query(Actividad.nombre, func.count(ActividadProgreso.id).label("count"))
            .join(ActividadProgreso, Actividad.id == ActividadProgreso.id_actividad)
            .group_by(Actividad.id, Actividad.nombre)
            .order_by(func.count(ActividadProgreso.id).desc())
            .limit(limit)
            .all()
        )

        activity_names = [row[0] for row in results]
        play_counts = [row[1] for row in results]

        return {"activities": activity_names, "counts": play_counts}

    @staticmethod
    def get_highest_scoring_activities(db: Session, limit: int = 10) -> dict[str, list]:
        """Get activities with highest average scores.

        Args:
            db: Database session for querying.
            limit: Number of top activities to return.

        Returns:
            Dictionary containing:
                - activities: List of activity names
                - scores: Average score (0-10) for each activity
        """
        cache_key = f"highest_scoring_activities_{limit}"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key,
            lambda db: LearningStatisticsService._fetch_highest_scoring_activities(db, limit),
            db,
        )

    @staticmethod
    def _fetch_highest_scoring_activities(db: Session, limit: int) -> dict[str, list]:
        """Internal method to fetch highest scoring activities from database.

        Args:
            db: Database session for querying.
            limit: Number of top activities to return.

        Returns:
            Dictionary with activity names and average scores.
        """
        results = (
            db.query(
                Actividad.nombre,
                func.avg(ActividadProgreso.puntuacion).label("avg_score"),
                func.count(ActividadProgreso.id).label("attempts"),
            )
            .join(ActividadProgreso, Actividad.id == ActividadProgreso.id_actividad)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .group_by(Actividad.id, Actividad.nombre)
            .having(func.count(ActividadProgreso.id) >= 3)  # Minimum 3 attempts
            .order_by(func.avg(ActividadProgreso.puntuacion).desc())
            .limit(limit)
            .all()
        )

        activity_names = [row[0] for row in results]
        avg_scores = [round(row[1], 1) for row in results]

        return {"activities": activity_names, "scores": avg_scores}

    @staticmethod
    def get_class_performance(db: Session) -> dict[str, list]:
        """Get average performance by class.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - classes: List of class names
                - scores: Average score (0-10) for each class
                - student_counts: Number of students in each class
        """
        cache_key = "class_performance"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_class_performance, db
        )

    @staticmethod
    def _fetch_class_performance(db: Session) -> dict[str, list]:
        """Internal method to fetch class performance from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with class names, average scores, and student counts.
        """
        results = (
            db.query(
                Clase.nombre,
                func.avg(ActividadProgreso.puntuacion).label("avg_score"),
                func.count(func.distinct(Usuario.id)).label("num_students"),
            )
            .join(Usuario, Clase.id == Usuario.id_clase)
            .join(Partida, Usuario.id == Partida.id_usuario)
            .join(ActividadProgreso, Partida.id == ActividadProgreso.id_juego)
            .filter(
                and_(
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .group_by(Clase.id, Clase.nombre)
            .order_by(func.avg(ActividadProgreso.puntuacion).desc())
            .all()
        )

        class_names = [row[0] for row in results]
        avg_scores = [round(row[1], 1) for row in results]
        student_counts = [row[2] for row in results]

        return {
            "classes": class_names,
            "scores": avg_scores,
            "student_counts": student_counts,
        }
