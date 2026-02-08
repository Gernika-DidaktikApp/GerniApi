"""Modelo SQLAlchemy para usuarios del sistema.

Define la tabla de usuarios (estudiantes) que utilizan la aplicación móvil.

Autor: Gernibide
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Usuario(Base):
    """Modelo de Usuario (estudiante).

    Representa a los usuarios/estudiantes que juegan en la aplicación móvil.

    Attributes:
        id: ID único del usuario (UUID).
        username: Nombre de usuario único.
        nombre: Nombre del usuario.
        apellido: Apellido del usuario.
        password: Contraseña hasheada con bcrypt.
        id_clase: ID de la clase asignada (opcional).
        creation: Fecha de creación del usuario.
        top_score: Puntuación máxima alcanzada.
    """

    __tablename__ = "usuario"

    id = Column(String(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)
    id_clase = Column(String(36), ForeignKey("clase.id"), nullable=True)
    creation = Column(DateTime, default=datetime.now, nullable=False)
    top_score = Column(Integer, default=0, nullable=False)
