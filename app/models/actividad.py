from sqlalchemy import Column, ForeignKey, String

from app.database import Base


class Actividad(Base):
    __tablename__ = "actividad"

    id = Column(String(36), primary_key=True, nullable=False)
    id_punto = Column(String(36), ForeignKey("punto.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
