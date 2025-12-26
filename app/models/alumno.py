from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Alumno(Base):
    __tablename__ = "alumno"

    usuario = Column(String(45), primary_key=True, nullable=False)
    nombre = Column(String(45), primary_key=True, nullable=False)
    año_nacimiento = Column(String(45), primary_key=True, nullable=False)
    idioma = Column(String(45), nullable=True)
    fecha_alta = Column(Date, nullable=True)
    fecha_baja = Column(Date, nullable=True)
    contrasenya = Column(String(45), nullable=True)
    num_imagen = Column(Integer, nullable=True)
    id_aplicacion = Column(Integer, ForeignKey("aplicacion.id_aplicacion"), primary_key=True, nullable=False)
