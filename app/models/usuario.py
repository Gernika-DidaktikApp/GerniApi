from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(String(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)
    id_clase = Column(String(36), ForeignKey("clase.id"), nullable=True)
    creation = Column(DateTime, default=datetime.now, nullable=False)
    top_score = Column(Integer, default=0, nullable=False)
