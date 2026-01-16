from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.usuario import Usuario
from app.models.clase import Clase
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.utils.security import hash_password
from app.logging import log_info, log_warning, log_db_operation

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario."""
    # Validar que el username no exista
    existe = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
    if existe:
        log_warning("Intento de crear usuario con username duplicado", username=usuario_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso"
        )

    # Validar que la clase existe si se proporciona
    if usuario_data.id_clase:
        clase = db.query(Clase).filter(Clase.id == usuario_data.id_clase).first()
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe"
            )

    # Crear usuario con UUID generado
    nuevo_usuario = Usuario(
        id=str(uuid.uuid4()),
        username=usuario_data.username,
        nombre=usuario_data.nombre,
        apellido=usuario_data.apellido,
        password=hash_password(usuario_data.password),
        id_clase=usuario_data.id_clase
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    log_db_operation("CREATE", "usuario", nuevo_usuario.id, username=nuevo_usuario.username)

    return nuevo_usuario

@router.get("", response_model=List[UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de usuarios."""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: str, db: Session = Depends(get_db)):
    """Obtener un usuario por ID."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(usuario_id: str, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualizar un usuario existente."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Validar username único si se está actualizando
    if usuario_data.username and usuario_data.username != usuario.username:
        existe = db.query(Usuario).filter(Usuario.username == usuario_data.username).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está en uso"
            )

    # Validar clase si se proporciona
    if usuario_data.id_clase:
        clase = db.query(Clase).filter(Clase.id == usuario_data.id_clase).first()
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La clase especificada no existe"
            )

    # Actualizar campos proporcionados
    update_data = usuario_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)

    log_db_operation("UPDATE", "usuario", usuario.id, campos_actualizados=list(update_data.keys()))

    return usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    """Eliminar un usuario."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    db.delete(usuario)
    db.commit()

    log_db_operation("DELETE", "usuario", usuario_id)
