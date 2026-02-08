"""Modelo SQLAlchemy para clases del sistema.

Define la tabla de clases que agrupan usuarios bajo un profesor.

Autor: Gernibide
"""

from sqlalchemy import Column, ForeignKey, String

from app.database import Base


class Clase(Base):
    """Modelo de Clase.

    Representa una clase o grupo de usuarios gestionado por un profesor.

    Attributes:
        id: ID único de la clase (UUID).
        id_profesor: ID del profesor que gestiona la clase.
        nombre: Nombre de la clase.
    """

    __tablename__ = "clase"

    id = Column(String(36), primary_key=True, nullable=False)
    id_profesor = Column(String(36), ForeignKey("profesor.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
