"""Tests unitarios para UsuarioStatsService.

Tests aislados del servicio de estadísticas de usuarios,
usando mocks para los repositorios (sin base de datos).

Autor: Gernibide
"""

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import Mock

from app.services.usuario_stats_service import UsuarioStatsService


class TestUsuarioStatsService:
    """Tests unitarios para estadísticas de usuarios"""

    def test_estadisticas_usuario_sin_actividad(self):
        """Test: Estadísticas de usuario sin ninguna actividad"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        # Simular usuario sin actividad
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = None
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.actividades_completadas == 0
        assert resultado.racha_dias == 0
        assert resultado.modulos_completados == []
        assert resultado.ultima_partida is None
        assert resultado.total_puntos_acumulados == 0.0

    def test_estadisticas_con_actividades_completadas(self):
        """Test: Estadísticas con actividades completadas"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        mock_actividad_repo.count_completed_by_user.return_value = 5
        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_punto_repo.get_completed_modules_by_user.return_value = ["Módulo 1", "Módulo 2"]
        mock_partida_repo.get_last_partida_date.return_value = datetime.now()
        mock_actividad_repo.sum_points_by_user.return_value = 450.5

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.actividades_completadas == 5
        assert len(resultado.modulos_completados) == 2
        assert resultado.total_puntos_acumulados == 450.5

    def test_calcular_racha_dias_sin_partidas(self):
        """Test: Racha de días es 0 si no hay partidas"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = None
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.racha_dias == 0

    def test_calcular_racha_dias_consecutivos_desde_hoy(self):
        """Test: Racha de días consecutivos desde hoy hacia atrás"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        anteayer = hoy - timedelta(days=2)

        # Usuario jugó hoy, ayer y anteayer (racha = 3)
        mock_partida_repo.get_distinct_dates_for_user.return_value = [
            hoy,
            ayer,
            anteayer,
        ]

        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = datetime.now()
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.racha_dias == 3

    def test_calcular_racha_dias_interrumpida(self):
        """Test: Racha se interrumpe si falta un día"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        hoy = date.today()
        hace_2_dias = hoy - timedelta(days=2)
        hace_3_dias = hoy - timedelta(days=3)

        # Usuario jugó hoy, hace 2 días y hace 3 días (falta ayer)
        # Racha = 1 (solo hoy)
        mock_partida_repo.get_distinct_dates_for_user.return_value = [
            hoy,
            hace_2_dias,
            hace_3_dias,
        ]

        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = datetime.now()
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.racha_dias == 1  # Solo hoy

    def test_calcular_racha_dias_no_incluye_hoy(self):
        """Test: Racha es 0 si no jugó hoy"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        ayer = date.today() - timedelta(days=1)
        anteayer = date.today() - timedelta(days=2)

        # Usuario jugó ayer y anteayer, pero NO hoy
        mock_partida_repo.get_distinct_dates_for_user.return_value = [
            ayer,
            anteayer,
        ]

        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = datetime.now() - timedelta(days=1)
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.racha_dias == 0  # No jugó hoy

    def test_modulos_completados_lista_nombres(self):
        """Test: Lista de módulos completados correcta"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        modulos = ["Introducción", "Variables", "Funciones", "Clases"]
        mock_punto_repo.get_completed_modules_by_user.return_value = modulos

        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_partida_repo.get_last_partida_date.return_value = None
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert len(resultado.modulos_completados) == 4
        assert "Variables" in resultado.modulos_completados
        assert "Clases" in resultado.modulos_completados

    def test_ultima_partida_con_fecha(self):
        """Test: Última partida retorna datetime correcto"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        ultima_fecha = datetime(2024, 1, 15, 10, 30, 0)
        mock_partida_repo.get_last_partida_date.return_value = ultima_fecha

        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.ultima_partida == ultima_fecha

    def test_puntos_acumulados_formato_float(self):
        """Test: Puntos acumulados retorna float"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        mock_actividad_repo.sum_points_by_user.return_value = 1234.56

        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = None

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        resultado = service.obtener_estadisticas(usuario_id)

        # Assert
        assert resultado.total_puntos_acumulados == 1234.56
        assert isinstance(resultado.total_puntos_acumulados, float)

    def test_llamadas_a_repositorios_correctas(self):
        """Test: Verifica que se llaman todos los repositorios con ID correcto"""
        # Arrange
        mock_partida_repo = Mock()
        mock_actividad_repo = Mock()
        mock_punto_repo = Mock()

        mock_partida_repo.get_distinct_dates_for_user.return_value = []
        mock_actividad_repo.count_completed_by_user.return_value = 0
        mock_punto_repo.get_completed_modules_by_user.return_value = []
        mock_partida_repo.get_last_partida_date.return_value = None
        mock_actividad_repo.sum_points_by_user.return_value = 0.0

        service = UsuarioStatsService(mock_partida_repo, mock_actividad_repo, mock_punto_repo)
        usuario_id = str(uuid.uuid4())

        # Act
        service.obtener_estadisticas(usuario_id)

        # Assert
        mock_actividad_repo.count_completed_by_user.assert_called_once_with(usuario_id)
        mock_partida_repo.get_distinct_dates_for_user.assert_called_once_with(usuario_id)
        mock_punto_repo.get_completed_modules_by_user.assert_called_once_with(usuario_id)
        mock_partida_repo.get_last_partida_date.assert_called_once_with(usuario_id)
        mock_actividad_repo.sum_points_by_user.assert_called_once_with(usuario_id)
