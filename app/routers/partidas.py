import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import log_with_context
from app.models.juego import Partida
from app.models.usuario import Usuario
from app.schemas.partida import PartidaCreate, PartidaResponse, PartidaUpdate
from app.utils.dependencies import (
    AuthResult,
    require_api_key_only,
    require_auth,
    validate_user_ownership,
)

router = APIRouter(prefix="/partidas", tags=["🎮 Partidas"])


@router.post("", response_model=PartidaResponse, status_code=status.HTTP_201_CREATED)
def crear_partida(
    partida_data: PartidaCreate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Crear una nueva partida.

    - Con API Key: Puede crear partidas para cualquier usuario
    - Con Token: Solo puede crear partidas para sí mismo
    """
    usuario = db.query(Usuario).filter(Usuario.id == partida_data.id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario especificado no existe",
        )

    validate_user_ownership(auth, partida_data.id_usuario)

    nueva_partida = Partida(id=str(uuid.uuid4()), id_usuario=partida_data.id_usuario)

    db.add(nueva_partida)
    db.commit()
    db.refresh(nueva_partida)

    log_with_context(
        "info",
        "Partida creada",
        partida_id=nueva_partida.id,
        usuario_id=nueva_partida.id_usuario,
    )

    return nueva_partida


@router.get(
    "",
    response_model=List[PartidaResponse],
    dependencies=[Depends(require_api_key_only)],
)
def listar_partidas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de todas las partidas. Requiere API Key."""
    partidas = db.query(Partida).offset(skip).limit(limit).all()
    return partidas


@router.get("/{partida_id}", response_model=PartidaResponse)
def obtener_partida(
    partida_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener una partida por ID.

    - Con API Key: Puede ver cualquier partida
    - Con Token: Solo puede ver sus propias partidas
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")

    validate_user_ownership(auth, partida.id_usuario)

    return partida


@router.put("/{partida_id}", response_model=PartidaResponse)
def actualizar_partida(
    partida_id: str,
    partida_data: PartidaUpdate,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Actualizar una partida existente.

    - Con API Key: Puede actualizar cualquier partida
    - Con Token: Solo puede actualizar sus propias partidas
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")

    validate_user_ownership(auth, partida.id_usuario)

    update_data = partida_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(partida, field, value)

    db.commit()
    db.refresh(partida)

    log_with_context("info", "Partida actualizada", partida_id=partida.id)

    return partida


@router.delete(
    "/{partida_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key_only)],
)
def eliminar_partida(partida_id: str, db: Session = Depends(get_db)):
    """Eliminar una partida. Requiere API Key."""
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida no encontrada")

    db.delete(partida)
    db.commit()

    log_with_context("info", "Partida eliminada", partida_id=partida_id)
