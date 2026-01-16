from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base

class Profesor(Base):
    __tablename__ = "profesor"

    id = Column(String(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
