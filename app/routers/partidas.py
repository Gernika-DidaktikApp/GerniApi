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


@router.get("/activa/usuario/{usuario_id}", response_model=PartidaResponse)
def obtener_partida_activa(
    usuario_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener la partida activa del usuario.

    - Con API Key: Puede ver la partida activa de cualquier usuario
    - Con Token: Solo puede ver su propia partida activa

    Retorna la partida con estado 'en_progreso', o 404 si no existe.
    """
    validate_user_ownership(auth, usuario_id)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario especificado no existe",
        )

    partida_activa = (
        db.query(Partida)
        .filter(
            Partida.id_usuario == usuario_id,
            Partida.estado == "en_progreso",
        )
        .first()
    )

    if not partida_activa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene una partida activa",
        )

    return partida_activa


@router.post("/activa/usuario/{usuario_id}/obtener-o-crear", response_model=PartidaResponse)
def obtener_o_crear_partida_activa(
    usuario_id: str,
    db: Session = Depends(get_db),
    auth: AuthResult = Depends(require_auth),
):
    """
    Obtener la partida activa del usuario, o crear una nueva si no existe.

    - Con API Key: Puede gestionar partidas de cualquier usuario
    - Con Token: Solo puede gestionar su propia partida

    Si el usuario tiene una partida activa, la retorna.
    Si no, crea una nueva partida automáticamente.
    """
    validate_user_ownership(auth, usuario_id)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario especificado no existe",
        )

    # Buscar partida activa
    partida_activa = (
        db.query(Partida)
        .filter(
            Partida.id_usuario == usuario_id,
            Partida.estado == "en_progreso",
        )
        .first()
    )

    if partida_activa:
        log_with_context(
            "info",
            "Partida activa encontrada",
            partida_id=partida_activa.id,
            usuario_id=usuario_id,
        )
        return partida_activa

    # Si no existe, crear nueva partida
    nueva_partida = Partida(id=str(uuid.uuid4()), id_usuario=usuario_id)

    db.add(nueva_partida)
    db.commit()
    db.refresh(nueva_partida)

    log_with_context(
        "info",
        "Nueva partida activa creada",
        partida_id=nueva_partida.id,
        usuario_id=usuario_id,
    )

    return nueva_partida


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

    Restricción: Un usuario solo puede tener una partida activa a la vez.
    """
    usuario = db.query(Usuario).filter(Usuario.id == partida_data.id_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario especificado no existe",
        )

    validate_user_ownership(auth, partida_data.id_usuario)

    # Verificar si el usuario ya tiene una partida activa
    partida_activa = (
        db.query(Partida)
        .filter(
            Partida.id_usuario == partida_data.id_usuario,
            Partida.estado == "en_progreso",
        )
        .first()
    )

    if partida_activa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario ya tiene una partida activa (ID: {partida_activa.id}). Debe finalizarla antes de crear una nueva.",
        )

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

    # Auto-calculate duration if fecha_fin is provided and duration is not
    if "fecha_fin" in update_data and update_data["fecha_fin"] is not None:
        if "duracion" not in update_data or update_data["duracion"] is None:
            # Calculate duration in seconds
            duracion_segundos = int((update_data["fecha_fin"] - partida.fecha_inicio).total_seconds())
            update_data["duracion"] = duracion_segundos

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
