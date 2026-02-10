"""Servicio de estadísticas de usuarios.

Calcula métricas de progreso y actividad de usuarios para
mostrar en el perfil de la app móvil.

Autor: Gernibide
"""

from datetime import datetime, timedelta

from app.repositories.actividad_progreso_repository import ActividadProgresoRepository
from app.repositories.partida_repository import PartidaRepository
from app.repositories.punto_repository import PuntoRepository
from app.schemas.usuario import UsuarioStatsResponse


class UsuarioStatsService:
    """Servicio para calcular estadísticas de usuarios.

    Separa la lógica compleja de estadísticas del CRUD básico
    de usuarios, facilitando testing y mantenimiento.
    """

    def __init__(
        self,
        partida_repo: PartidaRepository,
        actividad_repo: ActividadProgresoRepository,
        punto_repo: PuntoRepository,
    ):
        """Inicializa el servicio.

        Args:
            partida_repo: Repositorio de partidas.
            actividad_repo: Repositorio de progreso de actividades.
            punto_repo: Repositorio de puntos/módulos.
        """
        self.partida_repo = partida_repo
        self.actividad_repo = actividad_repo
        self.punto_repo = punto_repo

    def obtener_estadisticas(self, usuario_id: str) -> UsuarioStatsResponse:
        """Calcula estadísticas completas del usuario.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Estadísticas del usuario incluyendo:
            - Actividades completadas
            - Racha de días consecutivos
            - Módulos completados
            - Fecha de última partida
            - Total de puntos acumulados
        """
        # 1. Actividades completadas
        actividades_completadas = self.actividad_repo.count_completed_by_user(usuario_id)

        # 2. Racha de días consecutivos
        racha_dias = self._calcular_racha_dias(usuario_id)

        # 3. Módulos completados
        modulos_completados = self.punto_repo.get_completed_modules_by_user(usuario_id)

        # 4. Última partida
        ultima_partida = self.partida_repo.get_last_partida_date(usuario_id)

        # 5. Total puntos
        total_puntos = self.actividad_repo.sum_points_by_user(usuario_id)

        return UsuarioStatsResponse(
            actividades_completadas=actividades_completadas,
            racha_dias=racha_dias,
            modulos_completados=modulos_completados,
            ultima_partida=ultima_partida,
            total_puntos_acumulados=float(total_puntos),
        )

    def _calcular_racha_dias(self, usuario_id: str) -> int:
        """Calcula días consecutivos de juego desde hoy hacia atrás.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Número de días consecutivos de juego.
        """
        fechas_juego = self.partida_repo.get_distinct_dates_for_user(usuario_id)

        if not fechas_juego:
            return 0

        hoy = datetime.now().date()
        fechas_set = set(fechas_juego)

        # Calcular racha desde hoy hacia atrás
        racha = 0
        fecha_actual = hoy
        while fecha_actual in fechas_set:
            racha += 1
            fecha_actual -= timedelta(days=1)

        return racha
