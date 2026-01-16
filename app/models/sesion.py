from sqlalchemy import Column, String
from app.database import Base

class Sesion(Base):
    __tablename__ = "sesion"

    id = Column(String(36), primary_key=True, nullable=False)
