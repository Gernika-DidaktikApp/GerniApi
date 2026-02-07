"""
Service for calculating gameplay statistics (partidas, actividades)
Provides data for gameplay statistics dashboard
"""

import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.punto import Punto
from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida


class CacheEntry:
    """Cache entry with TTL"""

    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class GameplayStatisticsService:
    """Service for calculating gameplay statistics with caching"""

    # Cache storage
    _cache: Dict[str, CacheEntry] = {}

    # Cache TTL in seconds (5 minutes by default)
    CACHE_TTL = 300

    @classmethod
    def _get_cached_or_fetch(
        cls, cache_key: str, fetch_func: Callable, *args, ttl: Optional[int] = None
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
    def get_gameplay_summary(db: Session) -> Dict[str, Any]:
        """
        Get summary statistics for gameplay (with caching)

        Returns:
            Dictionary with total partidas, completadas, en progreso, promedio duración
        """
        cache_key = "gameplay_summary"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_gameplay_summary, db
        )

    @staticmethod
    def _fetch_gameplay_summary(db: Session) -> Dict[str, Any]:
        """Internal method to fetch gameplay summary from database"""
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)

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
    def get_partidas_by_day(db: Session, days: int = 30) -> Dict[str, List]:
        """
        Get count of partidas created per day (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and partida counts
        """
        cache_key = f"partidas_by_day_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_partidas_by_day, db, days
        )

    @staticmethod
    def _fetch_partidas_by_day(db: Session, days: int = 30) -> Dict[str, List]:
        """Internal method to fetch partidas by day from database"""
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
    def get_partidas_by_status(db: Session) -> Dict[str, Any]:
        """
        Get count of partidas by status (with caching)

        Returns:
            Dictionary with counts for completada, abandonada, en_progreso
        """
        cache_key = "partidas_by_status"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_partidas_by_status, db
        )

    @staticmethod
    def _fetch_partidas_by_status(db: Session) -> Dict[str, Any]:
        """Internal method to fetch partidas by status from database"""
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
    def get_actividades_by_status_timeline(db: Session, days: int = 30) -> Dict[str, List]:
        """
        Get timeline of activities by status (with caching)


        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and counts for completados, en_progreso, abandonados
        """
        cache_key = f"actividades_by_status_timeline_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_actividades_by_status_timeline, db, days
        )

    @staticmethod
    def _fetch_actividades_by_status_timeline(db: Session, days: int = 30) -> Dict[str, List]:
        """Internal method to fetch activities by status timeline from database"""

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
    def get_duracion_promedio_timeline(db: Session, days: int = 30) -> Dict[str, List]:
        """
        Get average duration of completed partidas over time (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and average durations in minutes
        """
        cache_key = f"duracion_promedio_timeline_{days}"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_duracion_promedio_timeline, db, days
        )

    @staticmethod
    def _fetch_duracion_promedio_timeline(db: Session, days: int = 30) -> Dict[str, List]:
        """Internal method to fetch duracion promedio timeline from database"""
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
    def get_completion_rate_by_punto(db: Session) -> Dict[str, List]:
        """
        Get completion rate by punto (with caching)

        Returns:
            Dictionary with punto names and their completion rates
        """
        cache_key = "completion_rate_by_punto"
        return GameplayStatisticsService._get_cached_or_fetch(
            cache_key, GameplayStatisticsService._fetch_completion_rate_by_punto, db
        )

    @staticmethod
    def _fetch_completion_rate_by_punto(db: Session) -> Dict[str, List]:
        """Internal method to fetch completion rate by punto from database"""
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
