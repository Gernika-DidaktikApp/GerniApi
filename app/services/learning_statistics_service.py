"""
Service for calculating learning/performance statistics (scores, tiempo)
Provides data for learning statistics dashboard
"""

import time
from collections.abc import Callable
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.actividad_progreso import ActividadProgreso
from app.models.punto import Punto


class CacheEntry:
    """Cache entry with TTL"""

    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class LearningStatisticsService:
    """Service for calculating learning/performance statistics with caching"""

    # Cache storage
    _cache: dict[str, CacheEntry] = {}

    # Cache TTL in seconds (5 minutes by default)
    CACHE_TTL = 300

    @classmethod
    def _get_cached_or_fetch(
        cls, cache_key: str, fetch_func: Callable, *args, ttl: int | None = None
    ) -> Any:
        """Generic cache getter with TTL"""
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
        """Clear all cached data"""
        cls._cache.clear()

    @staticmethod
    def get_learning_summary(db: Session) -> dict[str, Any]:
        """
        Get summary statistics for learning/performance (with caching)

        Returns:
            Dictionary with average score, pass rate, average time, evaluated activities
        """
        cache_key = "learning_summary"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_learning_summary, db
        )

    @staticmethod
    def _fetch_learning_summary(db: Session) -> dict[str, Any]:
        """Internal method to fetch learning summary from database"""
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

        return {
            "puntuacion_media": round(avg_score, 1),
            "aprobados_porcentaje": round(pass_rate, 1),
            "tiempo_medio": round(avg_time / 60, 0) if avg_time else 0,  # Convert to minutes
            "actividades_evaluadas": evaluated_count,
        }

    @staticmethod
    def get_average_score_by_punto(db: Session) -> dict[str, list]:
        """
        Get average score by punto (with caching)

        Returns:
            Dictionary with punto names and their average scores
        """
        cache_key = "average_score_by_punto"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_average_score_by_punto, db
        )

    @staticmethod
    def _fetch_average_score_by_punto(db: Session) -> dict[str, list]:
        """Internal method to fetch average score by punto from database"""
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
        """
        Get score distribution for histogram (with caching)

        Returns:
            Dictionary with all scores and their mean
        """
        cache_key = "score_distribution"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_score_distribution, db
        )

    @staticmethod
    def _fetch_score_distribution(db: Session) -> dict[str, Any]:
        """Internal method to fetch score distribution from database"""
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
        """
        Get time data for boxplot by punto (with caching)

        Returns:
            Dictionary with punto names and their time distributions
        """
        cache_key = "time_boxplot_by_punto"
        return LearningStatisticsService._get_cached_or_fetch(
            cache_key, LearningStatisticsService._fetch_time_boxplot_by_punto, db
        )

    @staticmethod
    def _fetch_time_boxplot_by_punto(db: Session) -> dict[str, Any]:
        """Internal method to fetch time boxplot data from database"""
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

            times = [round(t[0] / 60, 1) for t in times_query if t[0]]  # Convert to minutes

            # Only include puntos with at least 5 data points
            if len(times) >= 5:
                punto_names.append(punto.nombre)
                punto_times.append(times)

        return {"activities": punto_names, "times": punto_times}
