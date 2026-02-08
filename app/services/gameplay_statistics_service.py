"""Service for calculating gameplay statistics (partidas, actividades).

This module provides data for gameplay statistics dashboards, including
game session metrics, activity completion rates, and duration analytics.

Autor: Gernibide
"""

import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida
from app.models.punto import Punto


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


class GameplayStatisticsService:
    """Service for calculating gameplay statistics with caching.

    This service provides comprehensive gameplay metrics including:
    - Game session (partida) counts and status distribution
    - Activity completion tracking
    - Average game duration analysis
    - Completion rates by activity points (puntos)

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
    def get_gameplay_summary(db: Session) -> dict[str, Any]:
        """Get summary statistics for gameplay (with caching).

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - total_partidas: Total number of game sessions
                - partidas_completadas: Number of completed sessions
                - partidas_en_progreso: Number of in-progress sessions
                - duracion_promedio: Average duration in minutes
                - actividades_completadas: Total completed activities
        """
        cache_key = "gameplay_summary"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_gameplay_summary, db
        )

    @staticmethod
    def _fetch_gameplay_summary(db: Session) -> dict[str, Any]:
        """Internal method to fetch gameplay summary from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with gameplay summary metrics.
        """
        # Total partidas
        total_partidas = db.query(Partida).count()

        # Partidas completadas
        completadas = db.query(Partida).filter(Partida.estado == "completada").count()

        # Partidas en progreso
        en_progreso = db.query(Partida).filter(Partida.estado == "en_progreso").count()

        # Duración promedio de partidas completadas (en minutos)
        avg_duration = (
            db.query(func.avg(Partida.duracion)).filter(Partida.duracion.isnot(None)).scalar() or 0
        )

        # Actividades completadas
        actividades_completadas = (
            db.query(ActividadProgreso).filter(ActividadProgreso.estado == "completado").count()
        )

        return {
            "total_partidas": total_partidas,
            "partidas_completadas": completadas,
            "partidas_en_progreso": en_progreso,
            "duracion_promedio": (
                round(avg_duration / 60, 1) if avg_duration else 0
            ),  # Convertir a minutos
            "actividades_completadas": actividades_completadas,
        }

    @staticmethod
    def get_partidas_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """Get count of partidas created per day (with caching).

        Args:
            db: Database session for querying.
            days: Number of days to retrieve. Defaults to 30.

        Returns:
            Dictionary containing:
                - dates: List of date strings (YYYY-MM-DD format)
                - counts: Number of partidas created on each date
        """
        cache_key = f"partidas_by_day_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_partidas_by_day, db, days
        )

    @staticmethod
    def _fetch_partidas_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch partidas by day from database.

        Args:
            db: Database session for querying.
            days: Number of days to retrieve.

        Returns:
            Dictionary with partida counts per day.
        """
        now = datetime.now()
        dates = []
        counts = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            count = (
                db.query(Partida)
                .filter(and_(Partida.fecha_inicio >= date_start, Partida.fecha_inicio < date_end))
                .count()
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            counts.append(count)

        return {"dates": dates, "counts": counts}

    @staticmethod
    def get_partidas_by_status(db: Session) -> dict[str, Any]:
        """Get count of partidas by status (with caching).

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - completadas: Number of completed partidas
                - abandonadas: Number of abandoned partidas
                - en_progreso: Number of in-progress partidas
                - total: Total count of all partidas
        """
        cache_key = "partidas_by_status"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_partidas_by_status, db
        )

    @staticmethod
    def _fetch_partidas_by_status(db: Session) -> dict[str, Any]:
        """Internal method to fetch partidas by status from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with partida counts by status.
        """
        completadas = db.query(Partida).filter(Partida.estado == "completada").count()

        abandonadas = db.query(Partida).filter(Partida.estado == "abandonada").count()

        en_progreso = db.query(Partida).filter(Partida.estado == "en_progreso").count()

        total = completadas + abandonadas + en_progreso

        return {
            "completadas": completadas,
            "abandonadas": abandonadas,
            "en_progreso": en_progreso,
            "total": total,
        }

    @staticmethod
    def get_actividades_by_status_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Get timeline of activities by status (with caching).

        Args:
            db: Database session for querying.
            days: Number of days to retrieve. Defaults to 30.

        Returns:
            Dictionary containing:
                - dates: List of date strings (YYYY-MM-DD format)
                - completados: Number of completed activities per date
                - en_progreso: Number of in-progress activities per date
                - abandonados: Number of abandoned activities per date
        """
        cache_key = f"actividades_by_status_timeline_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_actividades_by_status_timeline, db, days
        )

    @staticmethod
    def _fetch_actividades_by_status_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch activities by status timeline from database.

        Args:
            db: Database session for querying.
            days: Number of days to retrieve.

        Returns:
            Dictionary with activity status counts per day.
        """

        now = datetime.now()
        dates = []
        completados = []
        en_progreso = []
        abandonados = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            # Count actividades by status for this day
            comp = (
                db.query(ActividadProgreso)
                .filter(
                    and_(
                        ActividadProgreso.fecha_inicio >= date_start,
                        ActividadProgreso.fecha_inicio < date_end,
                        ActividadProgreso.estado == "completado",
                    )
                )
                .count()
            )

            prog = (
                db.query(ActividadProgreso)
                .filter(
                    and_(
                        ActividadProgreso.fecha_inicio >= date_start,
                        ActividadProgreso.fecha_inicio < date_end,
                        ActividadProgreso.estado == "en_progreso",
                    )
                )
                .count()
            )

            aban = (
                db.query(ActividadProgreso)
                .filter(
                    and_(
                        ActividadProgreso.fecha_inicio >= date_start,
                        ActividadProgreso.fecha_inicio < date_end,
                        ActividadProgreso.estado == "abandonado",
                    )
                )
                .count()
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            completados.append(comp)
            en_progreso.append(prog)
            abandonados.append(aban)

        return {
            "dates": dates,
            "completados": completados,
            "en_progreso": en_progreso,
            "abandonados": abandonados,
        }

    @staticmethod
    def get_duracion_promedio_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Get average duration of completed partidas over time (with caching).

        Args:
            db: Database session for querying.
            days: Number of days to retrieve. Defaults to 30.

        Returns:
            Dictionary containing:
                - dates: List of date strings (YYYY-MM-DD format)
                - durations: Average duration in minutes for each date
        """
        cache_key = f"duracion_promedio_timeline_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_duracion_promedio_timeline, db, days
        )

    @staticmethod
    def _fetch_duracion_promedio_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch average duration timeline from database.

        Args:
            db: Database session for querying.
            days: Number of days to retrieve.

        Returns:
            Dictionary with average durations per day.
        """
        now = datetime.now()
        dates = []
        durations = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            # Average duration for this day (in seconds)
            avg_dur = (
                db.query(func.avg(Partida.duracion))
                .filter(
                    and_(
                        Partida.fecha_inicio >= date_start,
                        Partida.fecha_inicio < date_end,
                        Partida.duracion.isnot(None),
                    )
                )
                .scalar()
                or 0
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            durations.append(round(avg_dur / 60, 1) if avg_dur else 0)  # Convert to minutes

        return {"dates": dates, "durations": durations}

    @staticmethod
    def get_completion_rate_by_punto(db: Session) -> dict[str, list]:
        """Get completion rate by punto (with caching).

        Calculates the percentage of completed activities for each punto
        (activity point/location in the game).

        Args:
            db: Database session for querying.

        Returns:
            Dictionary containing:
                - activities: List of punto names
                - rates: Completion rate percentage (0-100) for each punto
        """
        cache_key = "completion_rate_by_punto"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_completion_rate_by_punto, db
        )

    @staticmethod
    def _fetch_completion_rate_by_punto(db: Session) -> dict[str, list]:
        """Internal method to fetch completion rate by punto from database.

        Args:
            db: Database session for querying.

        Returns:
            Dictionary with completion rates per punto.
        """
        # Get all puntos
        puntos = db.query(Punto).all()

        punto_names = []
        completion_rates = []

        for punto in puntos:
            # Count total activities for this punto
            total_actividades = (
                db.query(ActividadProgreso).filter(ActividadProgreso.id_punto == punto.id).count()
            )

            # Count completed activities for this punto
            completed_actividades = (
                db.query(ActividadProgreso)
                .filter(
                    and_(
                        ActividadProgreso.id_punto == punto.id,
                        ActividadProgreso.estado == "completado",
                    )
                )
                .count()
            )

            # Calculate completion rate
            if total_actividades > 0:
                rate = (completed_actividades / total_actividades) * 100
                punto_names.append(punto.nombre)
                completion_rates.append(round(rate, 1))

        return {"activities": punto_names, "rates": completion_rates}
