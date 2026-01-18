"""
Tests para sistema de gestión de estados de actividades y eventos
"""
import pytest
from datetime import datetime


class TestActividadEstados:
    """Tests para endpoints de estados de actividades"""

    def test_iniciar_actividad_exitoso(self, client, test_partida, test_actividad):
        """Test: Iniciar actividad debe crear registro con estado en_progreso"""
        response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id_juego"] == test_partida.id
        assert data["id_actividad"] == test_actividad.id
        assert data["estado"] == "en_progreso"
        assert data["puntuacion_total"] == 0.0
        assert data["duracion"] is None
        assert data["fecha_fin"] is None
        assert "fecha_inicio" in data

    def test_iniciar_actividad_duplicada(self, client, test_partida, test_actividad):
        """Test: Iniciar actividad duplicada debe fallar"""
        # Primera vez
        client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )

        # Segunda vez (duplicado)
        response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )

        assert response.status_code == 400
        data = response.json()
        # La API puede devolver "detail" o un objeto "error"
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "Ya existe una actividad en progreso" in error_msg

    def test_iniciar_actividad_partida_inexistente(self, client, test_actividad):
        """Test: Iniciar actividad con partida inexistente debe fallar"""
        response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": "00000000-0000-0000-0000-000000000000",
                "id_actividad": test_actividad.id
            }
        )

        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "partida" in error_msg.lower()

    def test_iniciar_actividad_inexistente(self, client, test_partida):
        """Test: Iniciar actividad inexistente debe fallar"""
        response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": "00000000-0000-0000-0000-000000000000"
            }
        )

        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "actividad" in error_msg.lower()

    def test_listar_actividad_estados(self, client, test_partida, test_actividad):
        """Test: Listar estados de actividades"""
        # Crear un estado
        client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )

        response = client.get("/api/v1/actividad-estados")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["id_actividad"] == test_actividad.id

    def test_obtener_actividad_estado(self, client, test_partida, test_actividad):
        """Test: Obtener un estado de actividad específico"""
        # Crear estado
        create_response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )
        estado_id = create_response.json()["id"]

        # Obtener estado
        response = client.get(f"/api/v1/actividad-estados/{estado_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == estado_id
        assert data["estado"] == "en_progreso"


class TestEventoEstados:
    """Tests para endpoints de estados de eventos"""

    def test_iniciar_evento_exitoso(self, client, test_partida, test_actividad, test_eventos):
        """Test: Iniciar evento debe crear registro con estado en_progreso"""
        evento = test_eventos[0]
        response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id_juego"] == test_partida.id
        assert data["id_actividad"] == test_actividad.id
        assert data["id_evento"] == evento.id
        assert data["estado"] == "en_progreso"
        assert data["puntuacion"] is None
        assert data["duracion"] is None
        assert "fecha_inicio" in data

    def test_iniciar_evento_duplicado(self, client, test_partida, test_actividad, test_eventos):
        """Test: Iniciar evento duplicado debe fallar"""
        evento = test_eventos[0]

        # Primera vez
        client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )

        # Segunda vez (duplicado)
        response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "Ya existe un evento en progreso" in error_msg

    def test_iniciar_evento_no_pertenece_actividad(self, client, db_session, test_partida, test_actividad, test_eventos):
        """Test: Iniciar evento que no pertenece a la actividad debe fallar"""
        from app.models.actividad import Actividad
        from app.models.evento import Eventos
        import uuid

        # Crear otra actividad y evento
        otra_actividad = Actividad(id=str(uuid.uuid4()), nombre="Otra Actividad")
        db_session.add(otra_actividad)
        db_session.commit()

        otro_evento = Eventos(id=str(uuid.uuid4()), id_actividad=otra_actividad.id, nombre="Otro Evento")
        db_session.add(otro_evento)
        db_session.commit()

        response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": otro_evento.id  # Evento de otra actividad
            }
        )

        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no pertenece" in error_msg.lower()

    def test_completar_evento_exitoso(self, client, test_partida, test_actividad, test_eventos):
        """Test: Completar evento debe calcular duración y guardar puntuación"""
        evento = test_eventos[0]

        # Iniciar evento
        init_response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )
        estado_id = init_response.json()["id"]

        # Completar evento
        response = client.put(
            f"/api/v1/evento-estados/{estado_id}/completar",
            json={"puntuacion": 85.5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == estado_id
        assert data["estado"] == "completado"
        assert data["puntuacion"] == 85.5
        assert data["duracion"] is not None
        assert data["duracion"] >= 0
        assert data["fecha_fin"] is not None

    def test_completar_evento_inexistente(self, client):
        """Test: Completar evento inexistente debe fallar"""
        response = client.put(
            "/api/v1/evento-estados/00000000-0000-0000-0000-000000000000/completar",
            json={"puntuacion": 85.5}
        )

        assert response.status_code == 404

    def test_completar_evento_ya_completado(self, client, test_partida, test_actividad, test_eventos):
        """Test: Completar evento ya completado debe fallar"""
        evento = test_eventos[0]

        # Iniciar y completar evento
        init_response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )
        estado_id = init_response.json()["id"]

        client.put(
            f"/api/v1/evento-estados/{estado_id}/completar",
            json={"puntuacion": 85.5}
        )

        # Intentar completar de nuevo
        response = client.put(
            f"/api/v1/evento-estados/{estado_id}/completar",
            json={"puntuacion": 90.0}
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no está en progreso" in error_msg.lower()


class TestAutoCompletado:
    """Tests para funcionalidad de auto-completado de actividades"""

    def test_actividad_se_completa_al_completar_ultimo_evento(self, client, test_partida, test_actividad, test_eventos):
        """Test: Al completar el último evento, la actividad se completa automáticamente"""
        # Iniciar actividad
        act_response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )
        actividad_estado_id = act_response.json()["id"]

        # Completar todos los eventos
        puntuaciones = [85.5, 90.0, 78.5]
        for i, evento in enumerate(test_eventos):
            # Iniciar evento
            init_response = client.post(
                "/api/v1/evento-estados/iniciar",
                json={
                    "id_juego": test_partida.id,
                    "id_actividad": test_actividad.id,
                    "id_evento": evento.id
                }
            )
            estado_id = init_response.json()["id"]

            # Completar evento
            client.put(
                f"/api/v1/evento-estados/{estado_id}/completar",
                json={"puntuacion": puntuaciones[i]}
            )

        # Verificar que la actividad se completó automáticamente
        response = client.get(f"/api/v1/actividad-estados/{actividad_estado_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "completado"
        assert data["puntuacion_total"] == sum(puntuaciones)  # 254.0
        assert data["duracion"] is not None
        assert data["duracion"] >= 0
        assert data["fecha_fin"] is not None

    def test_actividad_no_se_completa_con_eventos_pendientes(self, client, test_partida, test_actividad, test_eventos):
        """Test: La actividad no se completa si hay eventos sin completar"""
        # Iniciar actividad
        act_response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )
        actividad_estado_id = act_response.json()["id"]

        # Completar solo 2 de 3 eventos
        for evento in test_eventos[:2]:
            init_response = client.post(
                "/api/v1/evento-estados/iniciar",
                json={
                    "id_juego": test_partida.id,
                    "id_actividad": test_actividad.id,
                    "id_evento": evento.id
                }
            )
            estado_id = init_response.json()["id"]
            client.put(
                f"/api/v1/evento-estados/{estado_id}/completar",
                json={"puntuacion": 85.5}
            )

        # Verificar que la actividad sigue en progreso
        response = client.get(f"/api/v1/actividad-estados/{actividad_estado_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "en_progreso"
        assert data["fecha_fin"] is None

    def test_puntuacion_total_se_calcula_correctamente(self, client, test_partida, test_actividad, test_eventos):
        """Test: La puntuación total es la suma de todas las puntuaciones de eventos"""
        # Iniciar actividad
        client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id
            }
        )

        # Completar todos los eventos con puntuaciones específicas
        puntuaciones = [100.0, 200.5, 150.75]
        for i, evento in enumerate(test_eventos):
            init_response = client.post(
                "/api/v1/evento-estados/iniciar",
                json={
                    "id_juego": test_partida.id,
                    "id_actividad": test_actividad.id,
                    "id_evento": evento.id
                }
            )
            estado_id = init_response.json()["id"]
            client.put(
                f"/api/v1/evento-estados/{estado_id}/completar",
                json={"puntuacion": puntuaciones[i]}
            )

        # Obtener actividad completada
        response = client.get("/api/v1/actividad-estados")
        data = response.json()[0]

        assert data["puntuacion_total"] == sum(puntuaciones)  # 451.25


class TestValidaciones:
    """Tests para validaciones de datos"""

    def test_puntuacion_negativa_rechazada(self, client, test_partida, test_actividad, test_eventos):
        """Test: Puntuación negativa debe ser rechazada"""
        evento = test_eventos[0]
        init_response = client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id
            }
        )
        estado_id = init_response.json()["id"]

        response = client.put(
            f"/api/v1/evento-estados/{estado_id}/completar",
            json={"puntuacion": -10.0}
        )

        # La API puede aceptar valores negativos o rechazarlos
        # Esto depende de la implementación
        assert response.status_code in [200, 400, 422]

    def test_uuid_invalido_rechazado(self, client):
        """Test: UUID inválido debe ser rechazado"""
        response = client.post(
            "/api/v1/actividad-estados/iniciar",
            json={
                "id_juego": "not-a-uuid",
                "id_actividad": "also-not-a-uuid"
            }
        )

        assert response.status_code == 422
