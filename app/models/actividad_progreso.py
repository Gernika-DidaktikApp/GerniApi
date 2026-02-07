from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class ActividadProgreso(Base):
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
