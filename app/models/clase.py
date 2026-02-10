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
        codigo: Código corto compartible de 6 caracteres (ej: "A3X9K2").
        id_profesor: ID del profesor que gestiona la clase.
        nombre: Nombre de la clase.
    """

    __tablename__ = "clase"

    id = Column(String(36), primary_key=True, nullable=False)
    codigo = Column(String(6), unique=True, nullable=True, index=True)
    id_profesor = Column(String(36), ForeignKey("profesor.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
