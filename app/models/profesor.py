"""Modelo SQLAlchemy para profesores del sistema.

Define la tabla de profesores que gestionan clases y usuarios desde la interfaz web.

Autor: Gernibide
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.database import Base


class Profesor(Base):
    """Modelo de Profesor.

    Representa a los profesores que administran el sistema desde la interfaz web.

    Attributes:
        id: ID único del profesor (UUID).
        username: Nombre de usuario único.
        nombre: Nombre del profesor.
        apellido: Apellido del profesor.
        password: Contraseña hasheada con bcrypt.
        created: Fecha de creación del profesor.
    """

    __tablename__ = "profesor"

    id = Column(String(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
