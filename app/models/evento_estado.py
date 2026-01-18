from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float
from datetime import datetime
from app.database import Base

class EventoEstado(Base):
    __tablename__ = "evento_estado"

    id = Column(String(36), primary_key=True, nullable=False)
    id_juego = Column(String(36), ForeignKey("juego.id"), nullable=False)
    id_actividad = Column(String(36), ForeignKey("actividad.id"), nullable=False)
    id_evento = Column(String(36), ForeignKey("evento.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    duracion = Column(Integer, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
    puntuacion = Column(Float, nullable=True)
