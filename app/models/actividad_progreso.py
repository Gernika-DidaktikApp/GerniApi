"""Modelo SQLAlchemy para progreso de actividades.

Define la tabla que registra el progreso de los usuarios en las actividades.

Autor: Gernibide
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class ActividadProgreso(Base):
    """Modelo de ActividadProgreso.

    Registra el progreso de un usuario en una actividad específica durante una partida.
    Incluye tiempos, estado y puntuación obtenida.

    Attributes:
        id: ID único del progreso (UUID).
        id_juego: ID de la partida a la que pertenece.
        id_punto: ID del punto de la actividad.
        id_actividad: ID de la actividad.
        fecha_inicio: Fecha y hora de inicio de la actividad.
        duracion: Duración en segundos (calculado automáticamente).
        fecha_fin: Fecha y hora de finalización (opcional).
        estado: Estado de la actividad ("en_progreso" o "completado").
        puntuacion: Puntuación obtenida (opcional).
        respuesta_contenido: Contenido de la respuesta del usuario (opcional).
    """

    __tablename__ = "actividad_progreso"

    id = Column(String(36), primary_key=True, nullable=False)
    id_juego = Column(String(36), ForeignKey("juego.id"), nullable=False)
    id_punto = Column(String(36), ForeignKey("punto.id"), nullable=False)
    id_actividad = Column(String(36), ForeignKey("actividad.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    duracion = Column(Integer, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
    puntuacion = Column(Float, nullable=True)
    respuesta_contenido = Column(Text, nullable=True)
