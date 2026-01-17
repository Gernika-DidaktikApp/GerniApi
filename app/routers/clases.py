from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.clase import Clase
from app.models.profesor import Profesor
from app.schemas.clase import ClaseCreate, ClaseUpdate, ClaseResponse
from app.logging import log_with_context

router = APIRouter(prefix="/clases", tags=["🏫 Clases"])

@router.post("", response_model=ClaseResponse, status_code=status.HTTP_201_CREATED)
def crear_clase(clase_data: ClaseCreate, db: Session = Depends(get_db)):
    """Crear una nueva clase."""
    # Validar que el profesor existe
    profesor = db.query(Profesor).filter(Profesor.id == clase_data.id_profesor).first()
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El profesor especificado no existe"
        )

    # Crear clase con UUID generado
    nueva_clase = Clase(
        id=str(uuid.uuid4()),
        id_profesor=clase_data.id_profesor,
        nombre=clase_data.nombre
    )

    db.add(nueva_clase)
    db.commit()
    db.refresh(nueva_clase)

    log_with_context("info", "Clase creada", clase_id=nueva_clase.id, nombre=nueva_clase.nombre)

    return nueva_clase

@router.get("", response_model=List[ClaseResponse])
def listar_clases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de clases."""
    clases = db.query(Clase).offset(skip).limit(limit).all()
    return clases

@router.get("/{clase_id}", response_model=ClaseResponse)
def obtener_clase(clase_id: str, db: Session = Depends(get_db)):
    """Obtener una clase por ID."""
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )
    return clase

@router.put("/{clase_id}", response_model=ClaseResponse)
def actualizar_clase(clase_id: str, clase_data: ClaseUpdate, db: Session = Depends(get_db)):
    """Actualizar una clase existente."""
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )

    # Validar profesor si se proporciona
    if clase_data.id_profesor:
        profesor = db.query(Profesor).filter(Profesor.id == clase_data.id_profesor).first()
        if not profesor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El profesor especificado no existe"
            )

    # Actualizar campos proporcionados
    update_data = clase_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(clase, field, value)

    db.commit()
    db.refresh(clase)

    log_with_context("info", "Clase actualizada", clase_id=clase.id)

    return clase

@router.delete("/{clase_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_clase(clase_id: str, db: Session = Depends(get_db)):
    """Eliminar una clase."""
    clase = db.query(Clase).filter(Clase.id == clase_id).first()
    if not clase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clase no encontrada"
        )

    db.delete(clase)
    db.commit()

    log_with_context("info", "Clase eliminada", clase_id=clase_id)
