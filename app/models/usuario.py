from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime, timezone
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(CHAR(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    id_clase = Column(Integer, ForeignKey("clase.id_clase"), nullable=True)
    creation = Column(DateTime, default=datetime.now, nullable=False)
    top_score = Column(Integer, default=0, nullable=False)
