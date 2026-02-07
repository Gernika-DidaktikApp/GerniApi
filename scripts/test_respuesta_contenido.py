"""
Script para probar la restricción de actualizar respuesta_contenido
solo cuando la actividad está completada
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import requests  # noqa: E402

from app.config import settings  # noqa: E402

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = settings.api_key


def test_respuesta_contenido_restriction():
    """Test: Solo se puede actualizar respuesta_contenido cuando está completada"""

    headers = {"X-API-Key": API_KEY}

    print("=" * 70)
    print("TEST: Restricción de respuesta_contenido")
    print("=" * 70)

    # 1. Obtener un usuario y partida para pruebas
    print("\n1. Obteniendo usuario de prueba...")
    response = requests.get(f"{BASE_URL}/usuarios", headers=headers)
    usuarios = response.json()
    if not usuarios:
        print("❌ No hay usuarios. Crea uno primero con crear_clase_alumnos.py")
        return

    usuario = usuarios[0]
    usuario_id = usuario["id"]
    print(f"✅ Usuario: {usuario['username']} ({usuario_id})")

    # 2. Obtener o crear partida activa
    print("\n2. Obteniendo/creando partida activa...")
    response = requests.post(
        f"{BASE_URL}/partidas/activa/usuario/{usuario_id}/obtener-o-crear",
        headers=headers,
    )
    partida = response.json()
    partida_id = partida["id"]
    print(f"✅ Partida: {partida_id}")

    # 3. Obtener un punto y actividad
    print("\n3. Obteniendo punto y actividad...")
    response = requests.get(f"{BASE_URL}/puntos", headers=headers)
    puntos = response.json()
    if not puntos:
        print("❌ No hay puntos. Crea contenido primero.")
        return

    punto = puntos[0]
    punto_id = punto["id"]

    response = requests.get(f"{BASE_URL}/actividades", headers=headers)
    actividades = response.json()
    actividad = next((a for a in actividades if a["id_punto"] == punto_id), None)

    if not actividad:
        print("❌ No hay actividades para este punto.")
        return

    actividad_id = actividad["id"]
    print(f"✅ Punto: {punto['nombre']} ({punto_id})")
    print(f"✅ Actividad: {actividad['enunciado'][:50]}... ({actividad_id})")

    # 4. Iniciar actividad
    print("\n4. Iniciando actividad...")
    response = requests.post(
        f"{BASE_URL}/actividad-progreso/iniciar",
        json={
            "id_juego": partida_id,
            "id_punto": punto_id,
            "id_actividad": actividad_id,
        },
        headers=headers,
    )

    if response.status_code == 201:
        progreso = response.json()
        progreso_id = progreso["id"]
        print(f"✅ ActividadProgreso creado: {progreso_id}")
        print(f"   Estado: {progreso['estado']}")
    elif response.status_code == 400 and "Ya existe" in response.json().get("detail", ""):
        # Ya existe, buscar el progreso existente
        print("⚠️  Ya existe progreso en curso, buscando...")
        response = requests.get(f"{BASE_URL}/actividad-progreso", headers=headers)
        progresos = response.json()
        progreso = next(
            (
                p
                for p in progresos
                if p["id_juego"] == partida_id
                and p["id_actividad"] == actividad_id
                and p["estado"] == "en_progreso"
            ),
            None,
        )
        if progreso:
            progreso_id = progreso["id"]
            print(f"✅ Usando progreso existente: {progreso_id}")
        else:
            print("❌ No se pudo encontrar progreso en curso")
            return
    else:
        print(f"❌ Error iniciando actividad: {response.status_code}")
        print(response.json())
        return

    # 5. INTENTAR actualizar respuesta_contenido mientras está EN_PROGRESO (debe fallar)
    print("\n5. Intentando actualizar respuesta_contenido (estado: en_progreso)...")
    response = requests.put(
        f"{BASE_URL}/actividad-progreso/{progreso_id}",
        json={"respuesta_contenido": "Mi respuesta antes de completar"},
        headers=headers,
    )

    if response.status_code == 400:
        error = response.json()
        print(f"✅ Error esperado: {error['detail']}")
    else:
        print("❌ Se permitió actualizar respuesta_contenido en estado en_progreso!")
        print(f"   Status: {response.status_code}")

    # 6. Completar la actividad CON respuesta_contenido
    print("\n6. Completando actividad con respuesta_contenido...")
    response = requests.put(
        f"{BASE_URL}/actividad-progreso/{progreso_id}/completar",
        json={
            "puntuacion": 8.5,
            "respuesta_contenido": "Mi respuesta al completar la actividad",
        },
        headers=headers,
    )

    if response.status_code == 200:
        progreso = response.json()
        print("✅ Actividad completada")
        print(f"   Estado: {progreso['estado']}")
        print(f"   Puntuación: {progreso['puntuacion']}")
        print(f"   Respuesta: {progreso['respuesta_contenido']}")
    else:
        print(f"❌ Error completando actividad: {response.status_code}")
        print(response.json())
        return

    # 7. AHORA sí actualizar respuesta_contenido (debe funcionar)
    print("\n7. Actualizando respuesta_contenido (estado: completado)...")
    response = requests.put(
        f"{BASE_URL}/actividad-progreso/{progreso_id}",
        json={"respuesta_contenido": "Respuesta actualizada después de completar"},
        headers=headers,
    )

    if response.status_code == 200:
        progreso = response.json()
        print("✅ respuesta_contenido actualizado correctamente")
        print(f"   Nueva respuesta: {progreso['respuesta_contenido']}")
    else:
        print(f"❌ Error actualizando: {response.status_code}")
        print(response.json())

    # 8. Verificar que se puede actualizar otros campos
    print("\n8. Verificando que se pueden actualizar otros campos...")
    response = requests.put(
        f"{BASE_URL}/actividad-progreso/{progreso_id}",
        json={"puntuacion": 9.0},
        headers=headers,
    )

    if response.status_code == 200:
        progreso = response.json()
        print(f"✅ Puntuación actualizada: {progreso['puntuacion']}")
    else:
        print(f"❌ Error: {response.status_code}")

    print("\n" + "=" * 70)
    print("TEST COMPLETADO")
    print("=" * 70)


if __name__ == "__main__":
    test_respuesta_contenido_restriction()
