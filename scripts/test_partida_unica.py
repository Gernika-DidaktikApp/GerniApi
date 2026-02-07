"""
Script para probar la restricción de una partida activa por usuario
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


def test_partida_unica():
    """Test de restricción: un usuario solo puede tener una partida activa"""

    headers = {"X-API-Key": API_KEY}

    print("=" * 60)
    print("TEST: Restricción de Partida Única por Usuario")
    print("=" * 60)

    # 1. Crear un usuario de prueba
    print("\n1. Creando usuario de prueba...")
    usuario_data = {
        "username": "test_partida_unica",
        "nombre": "Test",
        "apellido": "Usuario",
        "password": "test123",
    }

    response = requests.post(f"{BASE_URL}/usuarios", json=usuario_data)

    if response.status_code == 201:
        usuario = response.json()
        usuario_id = usuario["id"]
        print(f"✅ Usuario creado: {usuario_id}")
    elif response.status_code == 400 and "ya existe" in response.json().get("detail", ""):
        # El usuario ya existe, obtenerlo
        print("⚠️  Usuario ya existe, obteniendo...")
        response = requests.get(f"{BASE_URL}/usuarios", headers=headers)
        usuarios = response.json()
        usuario = next(u for u in usuarios if u["username"] == "test_partida_unica")
        usuario_id = usuario["id"]
        print(f"✅ Usuario obtenido: {usuario_id}")
    else:
        print(f"❌ Error creando usuario: {response.status_code}")
        print(response.json())
        return

    # 2. Intentar obtener partida activa (no debería existir)
    print("\n2. Intentando obtener partida activa...")
    response = requests.get(
        f"{BASE_URL}/partidas/activa/usuario/{usuario_id}", headers=headers
    )

    if response.status_code == 404:
        print("✅ Confirmado: No hay partida activa (esperado)")
    else:
        partida = response.json()
        print(f"⚠️  Ya existe partida activa: {partida['id']}")
        usuario_id = partida["id_usuario"]

    # 3. Crear primera partida (usando obtener-o-crear)
    print("\n3. Creando/obteniendo primera partida...")
    response = requests.post(
        f"{BASE_URL}/partidas/activa/usuario/{usuario_id}/obtener-o-crear",
        headers=headers,
    )

    if response.status_code == 200:
        partida1 = response.json()
        partida1_id = partida1["id"]
        print(f"✅ Partida activa: {partida1_id}")
        print(f"   Estado: {partida1['estado']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return

    # 4. Intentar crear segunda partida (debería fallar)
    print("\n4. Intentando crear segunda partida (debe fallar)...")
    partida_data = {"id_usuario": usuario_id}
    response = requests.post(f"{BASE_URL}/partidas", json=partida_data, headers=headers)

    if response.status_code == 400:
        error = response.json()
        print(f"✅ Error esperado: {error['detail']}")
    else:
        print("❌ Se pudo crear segunda partida! (No debería permitirse)")
        print(response.json())

    # 5. Verificar que obtener-o-crear retorna la misma partida
    print("\n5. Verificando que obtener-o-crear retorna la misma partida...")
    response = requests.post(
        f"{BASE_URL}/partidas/activa/usuario/{usuario_id}/obtener-o-crear",
        headers=headers,
    )

    if response.status_code == 200:
        partida2 = response.json()
        if partida2["id"] == partida1_id:
            print(f"✅ Retorna la misma partida: {partida2['id']}")
        else:
            print("❌ Retornó partida diferente!")
            print(f"   Partida 1: {partida1_id}")
            print(f"   Partida 2: {partida2['id']}")
    else:
        print(f"❌ Error: {response.status_code}")

    # 6. Finalizar partida
    print("\n6. Finalizando partida activa...")
    update_data = {"estado": "completado"}
    response = requests.put(
        f"{BASE_URL}/partidas/{partida1_id}", json=update_data, headers=headers
    )

    if response.status_code == 200:
        print("✅ Partida finalizada")
    else:
        print(f"❌ Error finalizando partida: {response.status_code}")

    # 7. Intentar crear nueva partida (ahora debería funcionar)
    print("\n7. Creando nueva partida (ahora debe funcionar)...")
    response = requests.post(f"{BASE_URL}/partidas", json=partida_data, headers=headers)

    if response.status_code == 201:
        nueva_partida = response.json()
        print(f"✅ Nueva partida creada: {nueva_partida['id']}")
        print(f"   Estado: {nueva_partida['estado']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())

    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    test_partida_unica()
