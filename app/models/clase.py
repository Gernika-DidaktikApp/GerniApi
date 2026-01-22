from sqlalchemy import Column, ForeignKey, String

from app.database import Base


class Clase(Base):
    __tablename__ = "clase"

    id = Column(String(36), primary_key=True, nullable=False)
    id_profesor = Column(String(36), ForeignKey("profesor.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
