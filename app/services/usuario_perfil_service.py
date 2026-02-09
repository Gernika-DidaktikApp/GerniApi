"""Servicio de perfil y progreso detallado del usuario para app móvil.

Calcula información completa del progreso del usuario incluyendo
todas las actividades (completadas y no completadas) organizadas por punto.

Autor: Gernibide
"""

from datetime import datetime, timedelta

from app.repositories.actividad_progreso_repository import ActividadProgresoRepository
from app.repositories.actividad_repository import ActividadRepository
from app.repositories.partida_repository import PartidaRepository
from app.repositories.punto_repository import PuntoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import (
    ActividadDetalle,
    EstadisticasGenerales,
    PerfilProgreso,
    PuntoProgreso,
)


class UsuarioPerfilService:
    """Servicio para calcular el progreso completo del usuario.

    Genera información detallada del perfil y progreso, incluyendo
    todas las actividades por punto (completadas y no completadas).
    """

    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        partida_repo: PartidaRepository,
        punto_repo: PuntoRepository,
        actividad_repo: ActividadRepository,
        actividad_progreso_repo: ActividadProgresoRepository,
    ):
        """Inicializa el servicio.

        Args:
            usuario_repo: Repositorio de usuarios.
            partida_repo: Repositorio de partidas.
            punto_repo: Repositorio de puntos.
            actividad_repo: Repositorio de actividades.
            actividad_progreso_repo: Repositorio de progreso de actividades.
        """
        self.usuario_repo = usuario_repo
        self.partida_repo = partida_repo
        self.punto_repo = punto_repo
        self.actividad_repo = actividad_repo
        self.actividad_progreso_repo = actividad_progreso_repo

    def obtener_perfil_progreso(self, usuario_id: str) -> PerfilProgreso:
        """Obtiene el perfil y progreso completo del usuario.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Información completa de perfil, estadísticas y progreso por punto.

        Note:
            La validación de existencia del usuario debe hacerse en el router.
        """
        # Obtener usuario (asumimos que ya se validó su existencia en el router)
        usuario = self.usuario_repo.get_by_id(usuario_id)

        # 1. Obtener progreso por punto
        puntos_progreso = self._obtener_progreso_por_punto(usuario_id)

        # 2. Calcular estadísticas generales
        estadisticas = self._calcular_estadisticas_generales(usuario_id, puntos_progreso)

        return PerfilProgreso(
            usuario=usuario,
            estadisticas=estadisticas,
            puntos=puntos_progreso,
        )

    def _obtener_progreso_por_punto(self, usuario_id: str) -> list[PuntoProgreso]:
        """Obtiene el progreso detallado de todos los puntos.

        Args:
            usuario_id: ID del usuario.

        Returns:
            Lista de progreso por cada punto con sus actividades.
        """
        # Obtener todos los puntos usando repositorio
        puntos = self.punto_repo.get_all_ordered()

        resultado = []

        for punto in puntos:
            # Obtener todas las actividades del punto usando repositorio
            actividades = self.actividad_repo.get_all_by_punto(punto.id)

            if not actividades:
                continue

            # Obtener progreso de actividades del usuario para este punto usando repositorio
            progresos = self.actividad_progreso_repo.get_progreso_by_punto_and_user(
                punto.id, usuario_id
            )

            # Construir detalles de actividades
            actividades_detalle = []
            actividades_completadas = 0
            puntos_obtenidos = 0.0

            for actividad in actividades:
                progreso = progresos.get(actividad.id)

                if progreso:
                    estado = progreso.estado
                    if estado == "completado":
                        actividades_completadas += 1
                        puntos_obtenidos += progreso.puntuacion or 0.0

                    detalle = ActividadDetalle(
                        id_actividad=actividad.id,
                        nombre_actividad=actividad.nombre,
                        estado=estado,
                        puntuacion=progreso.puntuacion,
                        fecha_completado=progreso.fecha_fin,
                        duracion_segundos=progreso.duracion,
                    )
                else:
                    # Actividad no iniciada
                    detalle = ActividadDetalle(
                        id_actividad=actividad.id,
                        nombre_actividad=actividad.nombre,
                        estado="no_iniciada",
                        puntuacion=None,
                        fecha_completado=None,
                        duracion_segundos=None,
                    )

                actividades_detalle.append(detalle)

            # Determinar estado del punto
            total_actividades = len(actividades)
            if actividades_completadas == 0:
                estado_punto = "no_iniciado"
            elif actividades_completadas == total_actividades:
                estado_punto = "completado"
            else:
                estado_punto = "en_progreso"

            # Calcular porcentaje
            porcentaje = (
                (actividades_completadas / total_actividades * 100)
                if total_actividades > 0
                else 0.0
            )

            punto_progreso = PuntoProgreso(
                id_punto=punto.id,
                nombre_punto=punto.nombre,
                total_actividades=total_actividades,
                actividades_completadas=actividades_completadas,
                porcentaje_completado=round(porcentaje, 2),
                puntos_obtenidos=round(puntos_obtenidos, 2),
                estado=estado_punto,
                actividades=actividades_detalle,
            )

            resultado.append(punto_progreso)

        return resultado

    def _calcular_estadisticas_generales(
        self, usuario_id: str, progreso_por_punto: list[PuntoProgreso]
    ) -> EstadisticasGenerales:
        """Calcula las estadísticas generales del usuario.

        Args:
            usuario_id: ID del usuario.
            progreso_por_punto: Lista de progreso por punto ya calculada.

        Returns:
            Estadísticas generales.
        """
        # Total de actividades y completadas
        total_actividades_disponibles = sum(p.total_actividades for p in progreso_por_punto)
        actividades_completadas = sum(p.actividades_completadas for p in progreso_por_punto)

        # Porcentaje global
        porcentaje_global = (
            (actividades_completadas / total_actividades_disponibles * 100)
            if total_actividades_disponibles > 0
            else 0.0
        )

        # Puntos totales
        total_puntos_acumulados = sum(p.puntos_obtenidos for p in progreso_por_punto)

        # Puntos completados (módulos al 100%)
        puntos_completados = sum(1 for p in progreso_por_punto if p.estado == "completado")

        # Última partida
        ultima_partida = self.partida_repo.get_last_partida_date(usuario_id)

        # Racha de días
        racha_dias = self._calcular_racha_dias(usuario_id)

        return EstadisticasGenerales(
            total_actividades_disponibles=total_actividades_disponibles,
            actividades_completadas=actividades_completadas,
            porcentaje_progreso_global=round(porcentaje_global, 2),
            total_puntos_acumulados=round(total_puntos_acumulados, 2),
            racha_dias=racha_dias,
            ultima_partida=ultima_partida,
            puntos_completados=puntos_completados,
            total_puntos_disponibles=len(progreso_por_punto),
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
