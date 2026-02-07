"""
Service for calculating statistics and metrics
Provides data for statistics dashboards and charts
"""

import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_, distinct, func
from sqlalchemy.orm import Session

from app.models.juego import Partida
from app.models.usuario import Usuario


class CacheEntry:
    """Cache entry with TTL"""

    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class StatisticsService:
    """Service for calculating user and activity statistics with caching"""

    # Cache storage
    _cache: dict[str, CacheEntry] = {}

    # Cache TTL in seconds (5 minutes by default)
    CACHE_TTL = 300

    @classmethod
    def _get_cached_or_fetch(
        cls, cache_key: str, fetch_func: Callable, *args, ttl: int | None = None
    ) -> Any:
        """
        Generic cache getter with TTL

        Args:
            cache_key: Unique key for this cached data
            fetch_func: Function to call if cache miss
            *args: Arguments to pass to fetch_func
            ttl: Custom TTL in seconds (uses CACHE_TTL if None)

        Returns:
            Cached or freshly fetched data
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
        """Clear all cached data"""
        cls._cache.clear()

    @staticmethod
    def get_users_summary(db: Session) -> dict[str, Any]:
        """
        Get summary statistics for users (with caching)

        Returns:
            Dictionary with DAU, new users today, active/total ratio, and logins today
        """
        cache_key = "users_summary"
        return StatisticsService._get_cached_or_fetch(
            cache_key, StatisticsService._fetch_users_summary, db
        )

    @staticmethod
    def _fetch_users_summary(db: Session) -> dict[str, Any]:
        """Internal method to fetch users summary from database"""
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        week_ago = now - timedelta(days=7)

        # Total users
        total_users = db.query(Usuario).count()

        # New users today
        new_users_today = db.query(Usuario).filter(Usuario.creation >= today_start).count()

        # Daily Active Users (users who started a game today)
        dau = (
            db.query(func.count(distinct(Partida.id_usuario)))
            .filter(Partida.fecha_inicio >= today_start)
            .scalar()
            or 0
        )

        # Logins today (number of games started today as proxy for logins)
        logins_today = db.query(Partida).filter(Partida.fecha_inicio >= today_start).count()

        # Active users in last 7 days
        active_7d = (
            db.query(func.count(distinct(Partida.id_usuario)))
            .filter(Partida.fecha_inicio >= week_ago)
            .scalar()
            or 0
        )

        # Calculate ratio
        ratio = (active_7d / total_users * 100) if total_users > 0 else 0

        return {
            "dau": dau,
            "new_users_today": new_users_today,
            "ratio_active_total": round(ratio, 1),
            "logins_today": logins_today,
            "total_users": total_users,
        }

    @staticmethod
    def get_active_users_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """
        Get timeline of DAU, WAU, MAU for the last N days (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and DAU/WAU/MAU arrays
        """
        cache_key = f"active_users_timeline_{days}"
        return StatisticsService._get_cached_or_fetch(
            cache_key, StatisticsService._fetch_active_users_timeline, db, days
        )

    @staticmethod
    def _fetch_active_users_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch active users timeline from database"""
        now = datetime.now()
        dates = []
        dau_data = []
        wau_data = []
        mau_data = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            # DAU: unique users who played on this day
            dau = (
                db.query(func.count(distinct(Partida.id_usuario)))
                .filter(and_(Partida.fecha_inicio >= date_start, Partida.fecha_inicio < date_end))
                .scalar()
                or 0
            )

            # WAU: unique users in the 7 days ending on this date
            week_start = date_start - timedelta(days=6)
            wau = (
                db.query(func.count(distinct(Partida.id_usuario)))
                .filter(and_(Partida.fecha_inicio >= week_start, Partida.fecha_inicio < date_end))
                .scalar()
                or 0
            )

            # MAU: unique users in the 30 days ending on this date
            month_start = date_start - timedelta(days=29)
            mau = (
                db.query(func.count(distinct(Partida.id_usuario)))
                .filter(and_(Partida.fecha_inicio >= month_start, Partida.fecha_inicio < date_end))
                .scalar()
                or 0
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            dau_data.append(dau)
            wau_data.append(wau)
            mau_data.append(mau)

        return {"dates": dates, "dau": dau_data, "wau": wau_data, "mau": mau_data}

    @staticmethod
    def get_new_users_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """
        Get count of new users registered per day (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and new user counts
        """
        cache_key = f"new_users_by_day_{days}"
        return StatisticsService._get_cached_or_fetch(
            cache_key, StatisticsService._fetch_new_users_by_day, db, days
        )

    @staticmethod
    def _fetch_new_users_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch new users by day from database"""
        now = datetime.now()
        dates = []
        counts = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            count = (
                db.query(Usuario)
                .filter(and_(Usuario.creation >= date_start, Usuario.creation < date_end))
                .count()
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            counts.append(count)

        return {"dates": dates, "counts": counts}

    @staticmethod
    def get_active_ratio_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """
        Get ratio of active users to total users over time (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and ratio percentages
        """
        cache_key = f"active_ratio_timeline_{days}"
        return StatisticsService._get_cached_or_fetch(
            cache_key, StatisticsService._fetch_active_ratio_timeline, db, days
        )

    @staticmethod
    def _fetch_active_ratio_timeline(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch active ratio timeline from database"""
        now = datetime.now()
        dates = []
        ratios = []

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)

            # Total users registered up to this date
            total_users = (
                db.query(Usuario).filter(Usuario.creation <= date_start + timedelta(days=1)).count()
            )

            # Active users in the 7 days before this date
            week_start = date_start - timedelta(days=6)
            week_end = date_start + timedelta(days=1)
            active_users = (
                db.query(func.count(distinct(Partida.id_usuario)))
                .filter(and_(Partida.fecha_inicio >= week_start, Partida.fecha_inicio < week_end))
                .scalar()
                or 0
            )

            ratio = (active_users / total_users * 100) if total_users > 0 else 0

            dates.append(date_start.strftime("%Y-%m-%d"))
            ratios.append(round(ratio, 1))

        return {"dates": dates, "ratios": ratios}

    @staticmethod
    def get_logins_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """
        Get number of game sessions (logins) started per day (with caching)

        Args:
            db: Database session
            days: Number of days to retrieve (default 30)

        Returns:
            Dictionary with dates and login counts
        """
        cache_key = f"logins_by_day_{days}"
        return StatisticsService._get_cached_or_fetch(
            cache_key, StatisticsService._fetch_logins_by_day, db, days
        )

    @staticmethod
    def _fetch_logins_by_day(db: Session, days: int = 30) -> dict[str, list]:
        """Internal method to fetch logins by day from database"""
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
