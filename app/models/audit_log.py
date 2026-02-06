from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.database import Base


class AuditLog(Base):
    """
    Clase base para audit logs usando herencia polimórfica.
    Registra acciones de usuarios desde diferentes plataformas (web, app).
    """

    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    usuario_id = Column(String(36), ForeignKey("usuario.id"), nullable=True)
    profesor_id = Column(String(36), ForeignKey("profesor.id"), nullable=True)
    accion = Column(String(100), nullable=False, index=True)
    detalles = Column(Text, nullable=True)
    tipo = Column(String(20), nullable=False, index=True)  # Discriminador: 'web' o 'app'

    # Campos específicos de cada tipo (nullable porque dependen del tipo)
    # LogWeb:
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    browser = Column(String(100), nullable=True)

    # LogApp:
    device_type = Column(String(50), nullable=True)
    app_version = Column(String(20), nullable=True)
    device_id = Column(String(100), nullable=True)

    __mapper_args__ = {"polymorphic_on": tipo, "polymorphic_identity": "audit_log"}

    def get_description(self) -> str:
        """
        Polimorfismo: Método base que puede ser sobrescrito por subclases.
        Retorna una descripción legible del evento.
        """
        usuario = f"Usuario {self.usuario_id}" if self.usuario_id else f"Profesor {self.profesor_id}"
        return f"{self.accion} - {usuario} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class AuditLogWeb(AuditLog):
    """
    Audit log para acciones realizadas desde la aplicación web.
    Hereda de AuditLog y añade comportamiento específico para web.
    """

    __mapper_args__ = {"polymorphic_identity": "web"}

    def get_description(self) -> str:
        """
        Polimorfismo: Implementación específica para logs web.
        Incluye información del navegador y IP.
        """
        usuario = f"Usuario {self.usuario_id}" if self.usuario_id else f"Profesor {self.profesor_id}"
        browser_info = f"desde {self.browser}" if self.browser else "desde web"
        ip_info = f" ({self.ip_address})" if self.ip_address else ""
        return f"🌐 {self.accion} - {usuario} {browser_info}{ip_info}"


class AuditLogApp(AuditLog):
    """
    Audit log para acciones realizadas desde la aplicación móvil.
    Hereda de AuditLog y añade comportamiento específico para app.
    """

    __mapper_args__ = {"polymorphic_identity": "app"}

    def get_description(self) -> str:
        """
        Polimorfismo: Implementación específica para logs de app móvil.
        Incluye información del dispositivo y versión de la app.
        """
        usuario = f"Usuario {self.usuario_id}" if self.usuario_id else f"Profesor {self.profesor_id}"
        device_info = f"desde {self.device_type}" if self.device_type else "desde app"
        version_info = f" v{self.app_version}" if self.app_version else ""
        return f"📱 {self.accion} - {usuario} {device_info}{version_info}"
