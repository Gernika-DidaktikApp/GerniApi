"""Repositorio para operaciones de Audit Log en la base de datos.

Abstrae el acceso a datos de audit logs, desacoplando la lógica
de negocio de los detalles de implementación de SQLAlchemy.

Autor: Gernibide
"""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Repositorio para gestionar operaciones de lectura de Audit Logs.

    Los audit logs son de solo lectura - se crean automáticamente
    por el sistema y no se pueden modificar ni eliminar manualmente.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def get_by_id(self, log_id: str) -> AuditLog | None:
        """Obtiene un audit log por ID.

        Args:
            log_id: ID del audit log.

        Returns:
            AuditLog si existe, None si no.
        """
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def get_by_usuario(self, usuario_id: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Obtiene audit logs de un usuario específico.

        Args:
            usuario_id: ID del usuario.
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de audit logs del usuario, ordenados por timestamp descendente.
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.usuario_id == usuario_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_profesor(self, profesor_id: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        """Obtiene audit logs de un profesor específico.

        Args:
            profesor_id: ID del profesor.
            skip: Número de registros a saltar.
            limit: Número máximo de registros.

        Returns:
            Lista de audit logs del profesor, ordenados por timestamp descendente.
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.profesor_id == profesor_id)
            .order_by(AuditLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        tipo: str | None = None,
        accion: str | None = None,
        usuario_id: str | None = None,
        profesor_id: str | None = None,
    ) -> list[AuditLog]:
        """Obtiene audit logs con filtros opcionales.

        Args:
            skip: Número de registros a saltar.
            limit: Número máximo de registros.
            tipo: Filtro por tipo ('web' o 'app').
            accion: Filtro por acción específica.
            usuario_id: Filtro por usuario.
            profesor_id: Filtro por profesor.

        Returns:
            Lista de audit logs filtrados, ordenados por timestamp descendente.
        """
        query = self.db.query(AuditLog)

        # Aplicar filtros
        if tipo:
            query = query.filter(AuditLog.tipo == tipo)
        if accion:
            query = query.filter(AuditLog.accion == accion)
        if usuario_id:
            query = query.filter(AuditLog.usuario_id == usuario_id)
        if profesor_id:
            query = query.filter(AuditLog.profesor_id == profesor_id)

        # Ordenar por timestamp descendente (más recientes primero)
        query = query.order_by(AuditLog.timestamp.desc())

        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    def create(self, audit_log: AuditLog) -> AuditLog:
        """Crea un nuevo audit log.

        Args:
            audit_log: Instancia de AuditLog a crear.

        Returns:
            AuditLog creado con datos actualizados.
        """
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
