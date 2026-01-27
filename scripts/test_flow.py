#!/usr/bin/env python3
"""
Script de prueba para el flujo completo:
1. Registrar usuario
2. Iniciar sesión
3. Crear partida
4. Iniciar actividades
"""

import random
import string

import requests

# Configuración
# BASE_URL = "https://gernibide.up.railway.app"  # Railway - ¡NO USAR EN PRUEBAS!
BASE_URL = "http://localhost:8000"  # Para pruebas locales

# IDs de actividades
ACTIVIDADES = {
    "bunkers": "a233c17d-75a8-417d-8862-d0e1550fe59e",
    "mercado": "b85e8a14-caa9-4fc4-8d18-b3010f51cd0a",
    "fronton": "31d03477-7125-47e2-bad3-63e9c85e17ad",
    "arbol": "05a05a04-f045-48cf-8ec3-e28d14eec63f",
    "picasso": "d66f036b-c0d3-4765-a64b-dd3643c84c19",
}


def generar_username():
    """Genera un username aleatorio para pruebas"""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"test_{suffix}"


def registrar_usuario(username, password="test1234"):
    """Registra un nuevo usuario"""
    print(f"\n{'='*50}")
    print("1. REGISTRO DE USUARIO")
    print(f"{'='*50}")

    response = requests.post(
        f"{BASE_URL}/api/v1/usuarios",
        json={
            "username": username,
            "nombre": "Test",
            "apellido": "User",
            "password": password,
        },
    )

    if response.status_code == 201:
        data = response.json()
        print(f"✓ Usuario registrado: {data['username']}")
        print(f"  ID: {data['id']}")
        return data
    else:
        print(f"✗ Error al registrar: {response.status_code}")
        print(f"  Detalle: {response.json()}")
        return None


def iniciar_sesion(username, password="test1234"):
    """Inicia sesión y obtiene el token"""
    print(f"\n{'='*50}")
    print("2. INICIO DE SESIÓN")
    print(f"{'='*50}")

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login-app",
        json={"username": username, "password": password},
    )

    if response.status_code == 200:
        data = response.json()
        print("✓ Login exitoso")
        print(f"  Token: {data['access_token'][:50]}...")
        print(f"  User ID: {data['user_id']}")
        print(f"  Nombre: {data['nombre']} {data['apellido']}")
        return data
    else:
        print(f"✗ Error en login: {response.status_code}")
        print(f"  Detalle: {response.json()}")
        return None


def crear_partida(token, user_id):
    """Crea una nueva partida"""
    print(f"\n{'='*50}")
    print("3. CREAR PARTIDA")
    print(f"{'='*50}")

    response = requests.post(
        f"{BASE_URL}/api/v1/partidas",
        headers={"Authorization": f"Bearer {token}"},
        json={"id_usuario": user_id},
    )

    if response.status_code == 201:
        data = response.json()
        print("✓ Partida creada")
        print(f"  ID: {data['id']}")
        print(f"  Estado: {data['estado']}")
        print(f"  Fecha inicio: {data['fecha_inicio']}")
        return data
    else:
        print(f"✗ Error al crear partida: {response.status_code}")
        print(f"  Detalle: {response.json()}")
        return None


def iniciar_actividad(token, partida_id, actividad_id, nombre_actividad):
    """Inicia una actividad"""
    response = requests.post(
        f"{BASE_URL}/api/v1/actividad-estados/iniciar",
        headers={"Authorization": f"Bearer {token}"},
        json={"id_juego": partida_id, "id_actividad": actividad_id},
    )

    if response.status_code == 201:
        data = response.json()
        print(f"  ✓ {nombre_actividad}: Estado ID = {data['id']}")
        return data
    else:
        error = response.json()
        print(f"  ✗ {nombre_actividad}: {error.get('detail', error)}")
        return None


def iniciar_todas_actividades(token, partida_id):
    """Inicia todas las actividades"""
    print(f"\n{'='*50}")
    print("4. INICIAR ACTIVIDADES")
    print(f"{'='*50}")

    estados = {}
    for nombre, actividad_id in ACTIVIDADES.items():
        estado = iniciar_actividad(token, partida_id, actividad_id, nombre)
        if estado:
            estados[nombre] = estado

    return estados


def main():
    print("\n" + "=" * 60)
    print("   SCRIPT DE PRUEBA - GERNIBIDE API")
    print("=" * 60)
    print(f"URL: {BASE_URL}")

    # 1. Registrar usuario
    username = generar_username()
    password = "test1234"

    usuario = registrar_usuario(username, password)
    if not usuario:
        print("\n❌ Fallo en registro. Abortando.")
        return

    # 2. Iniciar sesión
    login_data = iniciar_sesion(username, password)
    if not login_data:
        print("\n❌ Fallo en login. Abortando.")
        return

    token = login_data["access_token"]
    user_id = login_data["user_id"]

    # 3. Crear partida
    partida = crear_partida(token, user_id)
    if not partida:
        print("\n❌ Fallo al crear partida. Abortando.")
        return

    # 4. Iniciar actividades
    estados = iniciar_todas_actividades(token, partida["id"])

    # Resumen
    print(f"\n{'='*60}")
    print("   RESUMEN")
    print("=" * 60)
    print(f"Usuario: {username}")
    print(f"User ID: {user_id}")
    print(f"Partida ID: {partida['id']}")
    print(f"Actividades iniciadas: {len(estados)}/{len(ACTIVIDADES)}")
    print("\nToken para usar en otras pruebas:")
    print(f"{token}")
    print("=" * 60)


if __name__ == "__main__":
    main()
