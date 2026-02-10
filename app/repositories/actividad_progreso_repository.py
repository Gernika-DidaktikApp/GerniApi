"""Repositorio para operaciones de ActividadProgreso en la base de datos.

Abstrae el acceso a datos de progreso de actividades, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida


class ActividadProgresoRepository:
    """Repositorio para gestionar operaciones de ActividadProgreso.

    Proporciona queries especializadas para estadísticas de usuarios.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def count_completed_by_user(self, user_id: str) -> int:
        """Cuenta actividades completadas por el usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Número de actividades completadas.
        """
        count = (
            self.db.query(func.count(ActividadProgreso.id))
            .join(Partida, ActividadProgreso.id_juego == Partida.id)
            .filter(
                and_(
                    Partida.id_usuario == user_id,
                    ActividadProgreso.estado == "completado",
                )
            )
            .scalar()
        )
        return count or 0

    def sum_points_by_user(self, user_id: str) -> float:
        """Suma total de puntos obtenidos por el usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Suma de puntos (0.0 si no hay puntos).
        """
        total = (
            self.db.query(func.sum(ActividadProgreso.puntuacion))
            .join(Partida, ActividadProgreso.id_juego == Partida.id)
            .filter(
                and_(
                    Partida.id_usuario == user_id,
                    ActividadProgreso.puntuacion.isnot(None),
                )
            )
            .scalar()
        )
        return total or 0.0

    def get_progreso_by_punto_and_user(
        self, punto_id: str, user_id: str
    ) -> dict[str, ActividadProgreso]:
        """Obtiene el progreso más reciente de cada actividad de un punto para un usuario.

        Args:
            punto_id: ID del punto.
            user_id: ID del usuario.

        Returns:
            Diccionario {id_actividad: ActividadProgreso} con el progreso más reciente.
        """
        # Obtener IDs de partidas del usuario
        partidas_usuario = self.db.query(Partida.id).filter(Partida.id_usuario == user_id).all()
        ids_partidas = [p.id for p in partidas_usuario]

        if not ids_partidas:
            return {}

        # Obtener todos los progresos del punto para el usuario
        progresos_query = (
            self.db.query(ActividadProgreso)
            .filter(
                and_(
                    ActividadProgreso.id_punto == punto_id,
                    ActividadProgreso.id_juego.in_(ids_partidas),
                )
            )
            .all()
        )

        # Crear dict con el progreso más relevante por actividad
        # Prioridad: completado > en_progreso (por fecha más reciente)
        progresos_dict = {}
        for prog in progresos_query:
            if prog.id_actividad not in progresos_dict:
                progresos_dict[prog.id_actividad] = prog
            else:
                actual = progresos_dict[prog.id_actividad]

                # Determinar si debemos reemplazar el progreso actual
                debe_reemplazar = False

                # Priorizar completado sobre en_progreso
                if (
                    prog.estado == "completado"
                    and actual.estado != "completado"
                    or prog.estado == actual.estado
                    and prog.fecha_inicio > actual.fecha_inicio
                ):
                    debe_reemplazar = True
                # Si actual es completado y nuevo es en_progreso, mantener completado

                if debe_reemplazar:
                    progresos_dict[prog.id_actividad] = prog

        return progresos_dict
