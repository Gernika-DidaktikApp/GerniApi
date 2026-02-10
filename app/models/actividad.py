"""Modelo SQLAlchemy para actividades educativas.

Define la tabla de actividades que forman parte de los puntos del juego.

Autor: Gernibide
"""

from sqlalchemy import Column, ForeignKey, String

from app.database import Base


class Actividad(Base):
    """Modelo de Actividad.

    Representa una actividad educativa dentro de un punto.
    Los usuarios completan actividades para progresar en el juego.

    Attributes:
        id: ID único de la actividad (UUID).
        id_punto: ID del punto al que pertenece la actividad.
        nombre: Nombre descriptivo de la actividad.
    """

    __tablename__ = "actividad"

    id = Column(String(36), primary_key=True, nullable=False)
    id_punto = Column(String(36), ForeignKey("punto.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
