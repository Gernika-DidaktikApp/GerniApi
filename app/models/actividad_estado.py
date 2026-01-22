from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database import Base


class ActividadEstado(Base):
    __tablename__ = "actividad_estado"

    id = Column(String(36), primary_key=True, nullable=False)
    id_juego = Column(String(36), ForeignKey("juego.id"), nullable=False)
    id_actividad = Column(String(36), ForeignKey("actividad.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    duracion = Column(Integer, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
    puntuacion_total = Column(Float, nullable=True, default=0.0)
