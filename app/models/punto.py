"""Modelo SQLAlchemy para puntos educativos.

Define la tabla de puntos que representan módulos o temas del juego educativo.

Autor: Gernibide
"""

from sqlalchemy import Column, String

from app.database import Base


class Punto(Base):
    """Modelo de Punto (módulo educativo).

    Representa un módulo o tema dentro del juego educativo.
    Cada punto contiene múltiples actividades.

    Attributes:
        id: ID único del punto (UUID).
        nombre: Nombre descriptivo del punto.
    """

    __tablename__ = "punto"

    id = Column(String(36), primary_key=True, nullable=False)
    nombre = Column(String(100), nullable=False)
