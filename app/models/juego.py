from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Partida(Base):
    __tablename__ = "juego"

    id = Column(String(36), primary_key=True, nullable=False)
    id_usuario = Column(String(36), ForeignKey("usuario.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    duracion = Column(Integer, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
