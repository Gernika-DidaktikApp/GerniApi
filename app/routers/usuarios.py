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

router = APIRouter(
    prefix="/usuarios",
    tags=["👥 Usuarios"],
    responses={
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Error de validación"}
    }
)

@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema con su información básica y contraseña hasheada."
)
def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    ## Crear Nuevo Usuario

    Registra un nuevo usuario en el sistema.

    ### Validaciones
    - El username debe ser único
    - Si se proporciona id_clase, la clase debe existir
    - La contraseña se hashea automáticamente con bcrypt

    ### Retorna
    Los datos del usuario creado (sin la contraseña)
    """
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

@router.get(
    "",
    response_model=List[UsuarioResponse],
    summary="Listar usuarios",
    description="Obtiene una lista paginada de todos los usuarios registrados."
)
def listar_usuarios(
    skip: int = Field(0, ge=0, description="Número de registros a saltar (para paginación)"),
    limit: int = Field(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """
    ## Listar Todos los Usuarios

    Retorna una lista paginada de usuarios.

    ### Paginación
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros (default: 100, max: 1000)

    ### Ejemplo
    - Para obtener los primeros 10: `?skip=0&limit=10`
    - Para obtener la segunda página: `?skip=10&limit=10`
    """
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario",
    description="Obtiene los detalles de un usuario específico por su ID."
)
def obtener_usuario(
    usuario_id: str = Field(..., description="ID único del usuario (UUID)"),
    db: Session = Depends(get_db)
):
    """
    ## Obtener Usuario por ID

    Retorna los detalles completos de un usuario específico.

    ### Parámetros
    - **usuario_id**: ID único del usuario (UUID)

    ### Errores
    - **404**: Si el usuario no existe
    """
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
