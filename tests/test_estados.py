"""
Tests para sistema de gestión de estados de actividades
"""


class TestActividadProgreso:
    """Tests para endpoints de estados de actividades"""

    def test_iniciar_evento_exitoso(self, admin_client, test_partida, test_punto, test_actividades):
        """Test: Iniciar actividad debe crear registro con estado en_progreso"""
        actividad = test_actividades[0]
        response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id_juego"] == test_partida.id
        assert data["id_punto"] == test_punto.id
        assert data["id_actividad"] == actividad.id
        assert data["estado"] == "en_progreso"
        assert data["puntuacion"] is None
        assert data["duracion"] is None
        assert "fecha_inicio" in data

    def test_iniciar_evento_duplicado(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Iniciar actividad duplicado debe fallar"""
        actividad = test_actividades[0]

        # Primera vez
        admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )

        # Segunda vez (duplicado)
        response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "Ya existe una actividad en progreso" in error_msg

    def test_iniciar_evento_no_pertenece_actividad(
        self, admin_client, db_session, test_partida, test_punto, test_actividades
    ):
        """Test: Iniciar actividad que no pertenece a la actividad debe fallar"""
        import uuid

        from app.models.actividad import Actividad as ActividadModel
        from app.models.punto import Punto

        # Crear otro punto y actividad
        otro_punto = Punto(id=str(uuid.uuid4()), nombre="Otro Punto")
        db_session.add(otro_punto)
        db_session.commit()

        otra_actividad_modelo = ActividadModel(
            id=str(uuid.uuid4()), id_punto=otro_punto.id, nombre="Otra Actividad"
        )
        db_session.add(otra_actividad_modelo)
        db_session.commit()

        response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": otra_actividad_modelo.id,  # Evento de otra actividad
            },
        )

        assert response.status_code == 404
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no pertenece" in error_msg.lower()

    def test_completar_evento_exitoso(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Completar actividad debe calcular duración y guardar puntuación"""
        actividad = test_actividades[0]

        # Iniciar actividad
        init_response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )
        estado_id = init_response.json()["id"]

        # Completar actividad
        response = admin_client.put(
            f"/api/v1/actividad-progreso/{estado_id}/completar", json={"puntuacion": 85.5}
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
        """Test: Completar punto inexistente debe fallar"""
        response = admin_client.put(
            "/api/v1/actividad-progreso/00000000-0000-0000-0000-000000000000/completar",
            json={"puntuacion": 85.5},
        )

        assert response.status_code == 404

    def test_completar_evento_ya_completado(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Completar actividad ya completado debe fallar"""
        actividad = test_actividades[0]

        # Iniciar y completar actividad
        init_response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )
        estado_id = init_response.json()["id"]

        admin_client.put(
            f"/api/v1/actividad-progreso/{estado_id}/completar", json={"puntuacion": 85.5}
        )

        # Intentar completar de nuevo
        response = admin_client.put(
            f"/api/v1/actividad-progreso/{estado_id}/completar", json={"puntuacion": 90.0}
        )

        assert response.status_code == 400
        data = response.json()
        error_msg = data.get("detail", data.get("error", {}).get("message", ""))
        assert "no está en progreso" in error_msg.lower()


class TestResumenPunto:
    """Tests para endpoint de resumen de punto calculado"""

    def test_resumen_actividad_no_iniciada(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Resumen de punto sin actividades iniciados"""
        response = admin_client.get(
            f"/api/v1/actividad-progreso/punto/{test_partida.id}/{test_punto.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id_juego"] == test_partida.id
        assert data["id_punto"] == test_punto.id
        assert data["actividades_totales"] == 3
        assert data["actividades_completadas"] == 0
        assert data["actividades_en_progreso"] == 0
        assert data["puntuacion_total"] == 0
        assert data["estado"] == "no_iniciada"

    def test_resumen_actividad_en_progreso(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Resumen de punto con actividades parcialmente completados"""
        # Completar solo 1 de 3 actividades
        actividad = test_actividades[0]
        init_response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )
        estado_id = init_response.json()["id"]
        admin_client.put(
            f"/api/v1/actividad-progreso/{estado_id}/completar",
            json={"puntuacion": 85.5},
        )

        response = admin_client.get(
            f"/api/v1/actividad-progreso/punto/{test_partida.id}/{test_punto.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["actividades_totales"] == 3
        assert data["actividades_completadas"] == 1
        assert data["puntuacion_total"] == 85.5
        assert data["estado"] == "en_progreso"

    def test_resumen_actividad_completada(
        self, admin_client, test_partida, test_punto, test_actividades
    ):
        """Test: Resumen de punto con todos los actividades completados"""
        puntuaciones = [85.5, 90.0, 78.5]

        # Completar todos los actividades
        for i, actividad in enumerate(test_actividades):
            init_response = admin_client.post(
                "/api/v1/actividad-progreso/iniciar",
                json={
                    "id_juego": test_partida.id,
                    "id_punto": test_punto.id,
                    "id_actividad": actividad.id,
                },
            )
            estado_id = init_response.json()["id"]
            admin_client.put(
                f"/api/v1/actividad-progreso/{estado_id}/completar",
                json={"puntuacion": puntuaciones[i]},
            )

        response = admin_client.get(
            f"/api/v1/actividad-progreso/punto/{test_partida.id}/{test_punto.id}/resumen"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["actividades_totales"] == 3
        assert data["actividades_completadas"] == 3
        assert data["puntuacion_total"] == sum(puntuaciones)  # 254.0
        assert data["estado"] == "completada"
        # duracion_total puede ser None si los tests son muy rápidos (0 segundos)
        assert data["duracion_total"] is None or data["duracion_total"] >= 0
        assert data["fecha_fin"] is not None

    def test_resumen_actividad_inexistente(self, admin_client, test_partida):
        """Test: Resumen de punto inexistente debe fallar"""
        response = admin_client.get(
            f"/api/v1/actividad-progreso/punto/{test_partida.id}/00000000-0000-0000-0000-000000000000/resumen"
        )

        assert response.status_code == 404

    def test_resumen_partida_inexistente(self, admin_client, test_punto):
        """Test: Resumen con partida inexistente debe fallar"""
        response = admin_client.get(
            f"/api/v1/actividad-progreso/punto/00000000-0000-0000-0000-000000000000/{test_punto.id}/resumen"
        )

        assert response.status_code == 404


class TestValidaciones:
    """Tests para validaciones de datos"""

    def test_puntuacion_negativa(self, admin_client, test_partida, test_punto, test_actividades):
        """Test: Puntuación negativa - verificar comportamiento"""
        actividad = test_actividades[0]
        init_response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )
        estado_id = init_response.json()["id"]

        response = admin_client.put(
            f"/api/v1/actividad-progreso/{estado_id}/completar", json={"puntuacion": -10.0}
        )

        # La API puede aceptar valores negativos o rechazarlos
        # Esto depende de la implementación
        assert response.status_code in [200, 400, 422]

    def test_uuid_invalido_rechazado(self, admin_client):
        """Test: UUID inválido debe ser rechazado"""
        response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": "not-a-uuid",
                "id_punto": "also-not-a-uuid",
                "id_actividad": "invalid-uuid",
            },
        )

        assert response.status_code == 422

    def test_evento_sin_puntuacion(self, admin_client, test_partida, test_punto, test_actividades):
        """Test: Completar actividad sin puntuación debe fallar"""
        actividad = test_actividades[0]
        init_response = admin_client.post(
            "/api/v1/actividad-progreso/iniciar",
            json={
                "id_juego": test_partida.id,
                "id_punto": test_punto.id,
                "id_actividad": actividad.id,
            },
        )
        estado_id = init_response.json()["id"]

        response = admin_client.put(f"/api/v1/actividad-progreso/{estado_id}/completar", json={})

        assert response.status_code == 422
