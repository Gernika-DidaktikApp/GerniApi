"""Modelo SQLAlchemy para partidas de juego.

Define la tabla de partidas que representan las sesiones de juego de los usuarios.

Autor: Gernibide
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Partida(Base):
    """Modelo de Partida (sesión de juego).

    Representa una sesión de juego de un usuario.
    Un usuario solo puede tener una partida activa a la vez.

    Attributes:
        id: ID único de la partida (UUID).
        id_usuario: ID del usuario que juega la partida.
        fecha_inicio: Fecha y hora de inicio de la partida.
        fecha_fin: Fecha y hora de finalización (opcional).
        duracion: Duración en segundos (opcional).
        estado: Estado de la partida ("en_progreso" o "completado").
    """

    __tablename__ = "juego"

    id = Column(String(36), primary_key=True, nullable=False)
    id_usuario = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    duracion = Column(Integer, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
