from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base

class Actividad(Base):
    __tablename__ = "actividad"

    id = Column(CHAR(36), primary_key=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    