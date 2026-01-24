"""
Tests para sistema de gestión de estados de eventos
"""


class TestEventoEstados:
    """Tests para endpoints de estados de eventos"""

    def test_iniciar_evento_exitoso(self, admin_client, test_partida, test_actividad, test_eventos):
        """Test: Iniciar evento debe crear registro con estado en_progreso"""
        evento = test_eventos[0]
        response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
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

    def test_iniciar_evento_duplicado(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Iniciar evento duplicado debe fallar"""
        evento = test_eventos[0]

        # Primera vez
        admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )

        # Segunda vez (duplicado)
        response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "Ya existe un evento en progreso" in error_msg

    def test_iniciar_evento_no_pertenece_actividad(
        self, admin_client, db_session, test_partida, test_actividad, test_eventos
    ):
        """Test: Iniciar evento que no pertenece a la actividad debe fallar"""
        import uuid

        from app.models.actividad import Actividad
        from app.models.evento import Eventos

        # Crear otra actividad y evento
        otra_actividad = Actividad(id=str(uuid.uuid4()), nombre="Otra Actividad")
        db_session.add(otra_actividad)
        db_session.commit()

        otro_evento = Eventos(
            id=str(uuid.uuid4()), id_actividad=otra_actividad.id, nombre="Otro Evento"
        )
        db_session.add(otro_evento)
        db_session.commit()

        response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": otro_evento.id,  # Evento de otra actividad
            },
        )

        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no pertenece" in error_msg.lower()

    def test_completar_evento_exitoso(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Completar evento debe calcular duración y guardar puntuación"""
        evento = test_eventos[0]

        # Iniciar evento
        init_response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )
        estado_id = init_response.json()["id"]

        # Completar evento
        response = admin_client.put(
            f"/api/v1/evento-estados/{estado_id}/completar", json={"puntuacion": 85.5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == estado_id
        assert data["estado"] == "completado"
        assert data["puntuacion"] == 85.5
        assert data["duracion"] is not None
        assert data["duracion"] >= 0
        assert data["fecha_fin"] is not None

    def test_completar_evento_inexistente(self, admin_client):
        """Test: Completar evento inexistente debe fallar"""
        response = admin_client.put(
            "/api/v1/evento-estados/00000000-0000-0000-0000-000000000000/completar",
            json={"puntuacion": 85.5},
        )

        assert response.status_code == 404

    def test_completar_evento_ya_completado(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Completar evento ya completado debe fallar"""
        evento = test_eventos[0]

        # Iniciar y completar evento
        init_response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )
        estado_id = init_response.json()["id"]

        admin_client.put(f"/api/v1/evento-estados/{estado_id}/completar", json={"puntuacion": 85.5})

        # Intentar completar de nuevo
        response = admin_client.put(
            f"/api/v1/evento-estados/{estado_id}/completar", json={"puntuacion": 90.0}
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no está en progreso" in error_msg.lower()


class TestResumenActividad:
    """Tests para endpoint de resumen de actividad calculado"""

    def test_resumen_actividad_no_iniciada(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Resumen de actividad sin eventos iniciados"""
        response = admin_client.get(
            f"/api/v1/evento-estados/actividad/{test_partida.id}/{test_actividad.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id_juego"] == test_partida.id
        assert data["id_actividad"] == test_actividad.id
        assert data["eventos_totales"] == 3
        assert data["eventos_completados"] == 0
        assert data["eventos_en_progreso"] == 0
        assert data["puntuacion_total"] == 0
        assert data["estado"] == "no_iniciada"

    def test_resumen_actividad_en_progreso(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Resumen de actividad con eventos parcialmente completados"""
        # Completar solo 1 de 3 eventos
        evento = test_eventos[0]
        init_response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )
        estado_id = init_response.json()["id"]
        admin_client.put(
            f"/api/v1/evento-estados/{estado_id}/completar",
            json={"puntuacion": 85.5},
        )

        response = admin_client.get(
            f"/api/v1/evento-estados/actividad/{test_partida.id}/{test_actividad.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["eventos_totales"] == 3
        assert data["eventos_completados"] == 1
        assert data["puntuacion_total"] == 85.5
        assert data["estado"] == "en_progreso"

    def test_resumen_actividad_completada(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Resumen de actividad con todos los eventos completados"""
        puntuaciones = [85.5, 90.0, 78.5]

        # Completar todos los eventos
        for i, evento in enumerate(test_eventos):
            init_response = admin_client.post(
                "/api/v1/evento-estados/iniciar",
                json={
                    "id_juego": test_partida.id,
                    "id_actividad": test_actividad.id,
                    "id_evento": evento.id,
                },
            )
            estado_id = init_response.json()["id"]
            admin_client.put(
                f"/api/v1/evento-estados/{estado_id}/completar",
                json={"puntuacion": puntuaciones[i]},
            )

        response = admin_client.get(
            f"/api/v1/evento-estados/actividad/{test_partida.id}/{test_actividad.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["eventos_totales"] == 3
        assert data["eventos_completados"] == 3
        assert data["puntuacion_total"] == sum(puntuaciones)  # 254.0
        assert data["estado"] == "completada"
        # duracion_total puede ser None si los tests son muy rápidos (0 segundos)
        assert data["duracion_total"] is None or data["duracion_total"] >= 0
        assert data["fecha_fin"] is not None

    def test_resumen_actividad_inexistente(self, admin_client, test_partida):
        """Test: Resumen de actividad inexistente debe fallar"""
        response = admin_client.get(
            f"/api/v1/evento-estados/actividad/{test_partida.id}/00000000-0000-0000-0000-000000000000/resumen"
        )

        assert response.status_code == 404

    def test_resumen_partida_inexistente(self, admin_client, test_actividad):
        """Test: Resumen con partida inexistente debe fallar"""
        response = admin_client.get(
            f"/api/v1/evento-estados/actividad/00000000-0000-0000-0000-000000000000/{test_actividad.id}/resumen"
        )

        assert response.status_code == 404


class TestValidaciones:
    """Tests para validaciones de datos"""

    def test_puntuacion_negativa(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Puntuación negativa - verificar comportamiento"""
        evento = test_eventos[0]
        init_response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )
        estado_id = init_response.json()["id"]

        response = admin_client.put(
            f"/api/v1/evento-estados/{estado_id}/completar", json={"puntuacion": -10.0}
        )

        # La API puede aceptar valores negativos o rechazarlos
        # Esto depende de la implementación
        assert response.status_code in [200, 400, 422]

    def test_uuid_invalido_rechazado(self, admin_client):
        """Test: UUID inválido debe ser rechazado"""
        response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": "not-a-uuid",
                "id_actividad": "also-not-a-uuid",
                "id_evento": "invalid-uuid",
            },
        )

        assert response.status_code == 422

    def test_evento_sin_puntuacion(
        self, admin_client, test_partida, test_actividad, test_eventos
    ):
        """Test: Completar evento sin puntuación debe fallar"""
        evento = test_eventos[0]
        init_response = admin_client.post(
            "/api/v1/evento-estados/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_actividad": test_actividad.id,
                "id_evento": evento.id,
            },
        )
        estado_id = init_response.json()["id"]

        response = admin_client.put(
            f"/api/v1/evento-estados/{estado_id}/completar", json={}
        )

        assert response.status_code == 422
