from sqlalchemy import Column, String
from app.database import Base

class Actividad(Base):
    __tablename__ = "actividad"

    id = Column(String(36), primary_key=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    