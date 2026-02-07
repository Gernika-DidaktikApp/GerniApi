"""
Service for calculating teacher dashboard statistics (class-level)
Provides data for teacher dashboard page
"""

import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.punto import Punto
from app.models.clase import Clase
from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida
from app.models.usuario import Usuario


class CacheEntry:
    """Cache entry with TTL"""

    def __init__(self, data: Any, ttl_seconds: int):
        self.data = data
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class TeacherDashboardService:
    """Service for calculating teacher dashboard statistics with caching"""

    # Cache storage
    _cache: Dict[str, CacheEntry] = {}

    # Cache TTL in seconds (2 minutes for teacher dashboard)
    CACHE_TTL = 120

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
    def get_class_summary(
        db: Session, profesor_id: str, clase_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a class

        Args:
            db: Database session
            profesor_id: ID of the profesor
            clase_id: Optional specific class ID (if None, aggregates all classes)
            days: Number of days to look back

        Returns:
            Dictionary with summary stats
        """
        cache_key = f"class_summary_{profesor_id}_{clase_id}_{days}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key, TeacherDashboardService._fetch_class_summary, db, profesor_id, clase_id, days
        )

    @staticmethod
    def _fetch_class_summary(
        db: Session, profesor_id: str, clase_id: Optional[str], days: int
    ) -> Dict[str, Any]:
        """Internal method to fetch class summary from database"""
        # Build base query for students
        students_query = (
            db.query(Usuario)
            .join(Clase, Usuario.id_clase == Clase.id)
            .filter(Clase.id_profesor == profesor_id)
        )

        if clase_id:
            students_query = students_query.filter(Usuario.id_clase == clase_id)

        students = students_query.all()
        total_students = len(students)

        if total_students == 0:
            return {
                "total_alumnos": 0,
                "progreso_medio": 0,
                "tiempo_promedio": 0,
                "nota_media": 0,
                "clase_nombre": "Sin clase",
            }

        student_ids = [s.id for s in students]

        # Calculate average progress (based on completed events)
        # Progress = (completed events / total unique events per student) * 100
        total_events = db.query(func.count(func.distinct(Punto.id))).scalar() or 1

        completed_events_per_student = []
        for student_id in student_ids:
            completed = (
                db.query(func.count(func.distinct(ActividadProgreso.id_evento)))
                .filter(
                    and_(
                        ActividadProgreso.id_juego.in_(
                            db.query(Partida.id).filter(Partida.id_usuario == student_id)
                        ),
                        ActividadProgreso.estado == "completado",
                    )
                )
                .scalar()
                or 0
            )
            completed_events_per_student.append(completed)

        avg_completed = (
            sum(completed_events_per_student) / len(completed_events_per_student)
            if completed_events_per_student
            else 0
        )
        progreso_medio = min(100, (avg_completed / total_events) * 100)

        # Calculate average time (duration in minutes)
        fecha_limite = datetime.now() - timedelta(days=days)

        avg_time = (
            db.query(func.avg(Partida.duracion))
            .filter(
                and_(
                    Partida.id_usuario.in_(student_ids),
                    Partida.duracion.isnot(None),
                    Partida.fecha_inicio >= fecha_limite,
                )
            )
            .scalar()
            or 0
        )

        tiempo_promedio = round(avg_time / 60, 0) if avg_time else 0

        # Calculate average grade (from completed eventos with scores)
        avg_grade = (
            db.query(func.avg(ActividadProgreso.puntuacion))
            .filter(
                and_(
                    ActividadProgreso.id_juego.in_(
                        db.query(Partida.id).filter(
                            and_(
                                Partida.id_usuario.in_(student_ids),
                                Partida.fecha_inicio >= fecha_limite,
                            )
                        )
                    ),
                    ActividadProgreso.puntuacion.isnot(None),
                    ActividadProgreso.estado == "completado",
                )
            )
            .scalar()
            or 0
        )

        # Get class name
        if clase_id:
            clase = db.query(Clase).filter(Clase.id == clase_id).first()
            clase_nombre = clase.nombre if clase else "Sin clase"
        else:
            clase_nombre = "Todas las clases"

        return {
            "total_alumnos": total_students,
            "progreso_medio": round(progreso_medio, 1),
            "tiempo_promedio": int(tiempo_promedio),
            "nota_media": round(avg_grade, 1),
            "clase_nombre": clase_nombre,
        }

    @staticmethod
    def get_student_progress(
        db: Session, profesor_id: str, clase_id: Optional[str] = None
    ) -> Dict[str, List]:
        """
        Get progress for each student in the class

        Args:
            db: Database session
            profesor_id: ID of the profesor
            clase_id: Optional specific class ID

        Returns:
            Dictionary with student names and progress percentages
        """
        cache_key = f"student_progress_{profesor_id}_{clase_id}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key, TeacherDashboardService._fetch_student_progress, db, profesor_id, clase_id
        )

    @staticmethod
    def _fetch_student_progress(
        db: Session, profesor_id: str, clase_id: Optional[str]
    ) -> Dict[str, List]:
        """Internal method to fetch student progress from database"""
        # Get students
        students_query = (
            db.query(Usuario)
            .join(Clase, Usuario.id_clase == Clase.id)
            .filter(Clase.id_profesor == profesor_id)
        )

        if clase_id:
            students_query = students_query.filter(Usuario.id_clase == clase_id)

        students = students_query.all()

        if not students:
            return {"students": [], "progress": []}

        total_events = db.query(func.count(func.distinct(Punto.id))).scalar() or 1

        student_names = []
        progress_values = []

        for student in students:
            # Calculate progress for this student
            completed = (
                db.query(func.count(func.distinct(ActividadProgreso.id_evento)))
                .filter(
                    and_(
                        ActividadProgreso.id_juego.in_(
                            db.query(Partida.id).filter(Partida.id_usuario == student.id)
                        ),
                        ActividadProgreso.estado == "completado",
                    )
                )
                .scalar()
                or 0
            )

            progress = min(100, (completed / total_events) * 100)

            student_names.append(f"{student.nombre} {student.apellido}")
            progress_values.append(round(progress, 1))

        return {"students": student_names, "progress": progress_values}

    @staticmethod
    def get_student_time(
        db: Session, profesor_id: str, clase_id: Optional[str] = None, days: int = 7
    ) -> Dict[str, List]:
        """
        Get time spent for each student in the class

        Args:
            db: Database session
            profesor_id: ID of the profesor
            clase_id: Optional specific class ID
            days: Number of days to look back

        Returns:
            Dictionary with student names and time in minutes
        """
        cache_key = f"student_time_{profesor_id}_{clase_id}_{days}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key, TeacherDashboardService._fetch_student_time, db, profesor_id, clase_id, days
        )

    @staticmethod
    def _fetch_student_time(
        db: Session, profesor_id: str, clase_id: Optional[str], days: int
    ) -> Dict[str, List]:
        """Internal method to fetch student time from database"""
        # Get students
        students_query = (
            db.query(Usuario)
            .join(Clase, Usuario.id_clase == Clase.id)
            .filter(Clase.id_profesor == profesor_id)
        )

        if clase_id:
            students_query = students_query.filter(Usuario.id_clase == clase_id)

        students = students_query.all()

        if not students:
            return {"students": [], "time": []}

        fecha_limite = datetime.now() - timedelta(days=days)

        student_names = []
        time_values = []

        for student in students:
            # Calculate total time for this student
            total_time = (
                db.query(func.sum(Partida.duracion))
                .filter(
                    and_(
                        Partida.id_usuario == student.id,
                        Partida.duracion.isnot(None),
                        Partida.fecha_inicio >= fecha_limite,
                    )
                )
                .scalar()
                or 0
            )

            time_minutes = round(total_time / 60, 0) if total_time else 0

            # Only include students with time > 0
            if time_minutes > 0:
                student_names.append(student.nombre)  # First name only for chart
                time_values.append(int(time_minutes))

        return {"students": student_names, "time": time_values}

    @staticmethod
    def get_activities_by_class(
        db: Session, profesor_id: str, clase_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get activity completion status by class

        Args:
            db: Database session
            profesor_id: ID of the profesor
            clase_id: Optional specific class ID

        Returns:
            Dictionary with activities and completion counts
        """
        cache_key = f"activities_by_class_{profesor_id}_{clase_id}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key, TeacherDashboardService._fetch_activities_by_class, db, profesor_id, clase_id
        )

    @staticmethod
    def _fetch_activities_by_class(
        db: Session, profesor_id: str, clase_id: Optional[str]
    ) -> Dict[str, Any]:
        """Internal method to fetch activities by class from database"""
        # Get students
        students_query = (
            db.query(Usuario)
            .join(Clase, Usuario.id_clase == Clase.id)
            .filter(Clase.id_profesor == profesor_id)
        )

        if clase_id:
            students_query = students_query.filter(Usuario.id_clase == clase_id)

        students = students_query.all()
        student_ids = [s.id for s in students]
        total_students = len(student_ids)

        if total_students == 0:
            return {"activities": [], "completed": [], "in_progress": [], "not_started": []}

        # Get all activities
        activities = db.query(Punto).all()

        activity_names = []
        completed_counts = []
        in_progress_counts = []
        not_started_counts = []

        for activity in activities:
            activity_names.append(activity.nombre)

            # Count students who completed this activity
            completed = (
                db.query(func.count(func.distinct(Partida.id_usuario)))
                .filter(
                    and_(
                        Partida.id_usuario.in_(student_ids),
                        Partida.id.in_(
                            db.query(ActividadProgreso.id_juego).filter(
                                and_(
                                    ActividadProgreso.id_actividad == activity.id,
                                    ActividadProgreso.estado == "completado",
                                )
                            )
                        ),
                    )
                )
                .scalar()
                or 0
            )

            # Count students who have this activity in progress
            in_progress = (
                db.query(func.count(func.distinct(Partida.id_usuario)))
                .filter(
                    and_(
                        Partida.id_usuario.in_(student_ids),
                        Partida.id.in_(
                            db.query(ActividadProgreso.id_juego).filter(
                                and_(
                                    ActividadProgreso.id_actividad == activity.id,
                                    ActividadProgreso.estado == "en_progreso",
                                )
                            )
                        ),
                        # Exclude if already completed
                        ~Partida.id.in_(
                            db.query(ActividadProgreso.id_juego).filter(
                                and_(
                                    ActividadProgreso.id_actividad == activity.id,
                                    ActividadProgreso.estado == "completado",
                                )
                            )
                        ),
                    )
                )
                .scalar()
                or 0
            )

            # Not started = total - (completed + in_progress)
            not_started = max(0, total_students - completed - in_progress)

            completed_counts.append(completed)
            in_progress_counts.append(in_progress)
            not_started_counts.append(not_started)

        return {
            "activities": activity_names,
            "completed": completed_counts,
            "in_progress": in_progress_counts,
            "not_started": not_started_counts,
        }

    @staticmethod
    def get_class_evolution(
        db: Session, profesor_id: str, clase_id: Optional[str] = None, days: int = 14
    ) -> Dict[str, Any]:
        """
        Get class evolution over time (progress and grades)

        Args:
            db: Database session
            profesor_id: ID of the profesor
            clase_id: Optional specific class ID
            days: Number of days to retrieve

        Returns:
            Dictionary with dates, progress, and grades
        """
        cache_key = f"class_evolution_{profesor_id}_{clase_id}_{days}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key,
            TeacherDashboardService._fetch_class_evolution,
            db,
            profesor_id,
            clase_id,
            days,
        )

    @staticmethod
    def _fetch_class_evolution(
        db: Session, profesor_id: str, clase_id: Optional[str], days: int
    ) -> Dict[str, Any]:
        """Internal method to fetch class evolution from database"""
        # Get students
        students_query = (
            db.query(Usuario)
            .join(Clase, Usuario.id_clase == Clase.id)
            .filter(Clase.id_profesor == profesor_id)
        )

        if clase_id:
            students_query = students_query.filter(Usuario.id_clase == clase_id)

        students = students_query.all()
        student_ids = [s.id for s in students]

        if not student_ids:
            return {"dates": [], "progress": [], "grades": []}

        total_events = db.query(func.count(func.distinct(Punto.id))).scalar() or 1

        dates = []
        progress_values = []
        grade_values = []

        now = datetime.now()

        for i in range(days - 1, -1, -1):
            date = now - timedelta(days=i)
            date_start = datetime(date.year, date.month, date.day)
            date_end = date_start + timedelta(days=1)

            # Calculate average progress for this date
            completed_by_date = []
            for student_id in student_ids:
                completed = (
                    db.query(func.count(func.distinct(ActividadProgreso.id_evento)))
                    .filter(
                        and_(
                            ActividadProgreso.id_juego.in_(
                                db.query(Partida.id).filter(
                                    and_(
                                        Partida.id_usuario == student_id,
                                        Partida.fecha_inicio < date_end,
                                    )
                                )
                            ),
                            ActividadProgreso.estado == "completado",
                            ActividadProgreso.fecha_inicio < date_end,
                        )
                    )
                    .scalar()
                    or 0
                )
                completed_by_date.append(completed)

            avg_completed = (
                sum(completed_by_date) / len(completed_by_date) if completed_by_date else 0
            )
            progress = min(100, (avg_completed / total_events) * 100)

            # Calculate average grade for this date
            avg_grade = (
                db.query(func.avg(ActividadProgreso.puntuacion))
                .filter(
                    and_(
                        ActividadProgreso.id_juego.in_(
                            db.query(Partida.id).filter(
                                and_(
                                    Partida.id_usuario.in_(student_ids),
                                    Partida.fecha_inicio < date_end,
                                )
                            )
                        ),
                        ActividadProgreso.puntuacion.isnot(None),
                        ActividadProgreso.estado == "completado",
                        ActividadProgreso.fecha_inicio < date_end,
                    )
                )
                .scalar()
                or 0
            )

            dates.append(date_start.strftime("%Y-%m-%d"))
            progress_values.append(round(progress, 1))
            grade_values.append(round(avg_grade, 1) if avg_grade else 0)

        return {"dates": dates, "progress": progress_values, "grades": grade_values}

    @staticmethod
    def get_profesor_classes(db: Session, profesor_id: str) -> List[Dict[str, str]]:
        """
        Get all classes for a profesor

        Args:
            db: Database session
            profesor_id: ID of the profesor

        Returns:
            List of dictionaries with class info
        """
        cache_key = f"profesor_classes_{profesor_id}"
        return TeacherDashboardService._get_cached_or_fetch(
            cache_key,
            TeacherDashboardService._fetch_profesor_classes,
            db,
            profesor_id,
            ttl=600,  # Cache for 10 minutes
        )

    @staticmethod
    def _fetch_profesor_classes(db: Session, profesor_id: str) -> List[Dict[str, str]]:
        """Internal method to fetch profesor classes from database"""
        classes = db.query(Clase).filter(Clase.id_profesor == profesor_id).all()

        return [{"id": clase.id, "nombre": clase.nombre} for clase in classes]
