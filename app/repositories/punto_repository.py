"""Repositorio para operaciones de Punto en la base de datos.

Abstrae el acceso a datos de puntos/módulos, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida
from app.models.punto import Punto


class PuntoRepository:
    """Repositorio para gestionar operaciones de Punto.

    Proporciona queries especializadas para estadísticas de usuarios.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_by_id(self, punto_id: str) -> Punto | None:
        """Obtiene un punto por ID.

        Args:
            punto_id: ID del punto.

        Returns:
            Punto si existe, None si no.
        """
        return self.db.query(Punto).filter(Punto.id == punto_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Punto]:
        """Obtiene lista paginada de puntos.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de puntos.
        """
        return self.db.query(Punto).offset(skip).limit(limit).all()

    def get_all_ordered(self) -> list[Punto]:
        """Obtiene todos los puntos ordenados por nombre.

        Returns:
            Lista de todos los puntos ordenados alfabéticamente.
        """
        return self.db.query(Punto).order_by(Punto.nombre).all()

    def get_completed_modules_by_user(self, user_id: str) -> list[str]:
        """Obtiene nombres de módulos/puntos completados por el usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Lista de nombres de módulos con al menos 1 actividad completada.
        """
        modulos_query = (
            self.db.query(Punto.nombre)
            .join(ActividadProgreso, Punto.id == ActividadProgreso.id_punto)
            .join(Partida, ActividadProgreso.id_juego == Partida.id)
            .filter(
                and_(
                    Partida.id_usuario == user_id,
                    ActividadProgreso.estado == "completado",
                )
            )
            .distinct()
            .all()
        )
        return [modulo[0] for modulo in modulos_query]

    def create(self, punto: Punto) -> Punto:
        """Crea un nuevo punto.

        Args:
            punto: Instancia de Punto a crear.

        Returns:
            Punto creado con datos actualizados.
        """
        self.db.add(punto)
        self.db.commit()
        self.db.refresh(punto)
        return punto

    def update(self, punto: Punto) -> Punto:
        """Actualiza un punto existente.

        Args:
            punto: Instancia de Punto a actualizar.

        Returns:
            Punto actualizado.
        """
        self.db.commit()
        self.db.refresh(punto)
        return punto

    def delete(self, punto: Punto) -> None:
        """Elimina un punto.

        Args:
            punto: Instancia de Punto a eliminar.
        """
        self.db.delete(punto)
        self.db.commit()
