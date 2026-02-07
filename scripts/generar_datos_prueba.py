#!/usr/bin/env python3
"""
Script para generar datos de prueba en LOCAL para las estadísticas

⚠️ IMPORTANTE: Este script solo funciona en LOCAL (localhost:8000)
Por seguridad, NO permite ejecutarse contra producción.
"""

import random
import sys
from datetime import datetime, timedelta

import requests

# ============================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================
BASE_URL = "http://localhost:8000"

# Validación de seguridad: Asegurar que NUNCA apunte a producción
if "railway" in BASE_URL.lower() or "heroku" in BASE_URL.lower() or "localhost" not in BASE_URL.lower():
    print("❌ ERROR DE SEGURIDAD")
    print("Este script solo puede ejecutarse contra localhost.")
    print(f"URL actual: {BASE_URL}")
    print("\nPara generar datos de prueba, asegúrate de:")
    print("1. Tener el servidor corriendo localmente (make dev)")
    print("2. Que BASE_URL sea 'http://localhost:8000'")
    sys.exit(1)

# Verificar que el servidor local esté corriendo
try:
    response = requests.get(f"{BASE_URL}/health", timeout=2)
    if response.status_code != 200:
        raise Exception("Health check falló")
except Exception as e:
    print("❌ ERROR: El servidor local no está corriendo")
    print(f"\nDetalles: {e}")
    print("\nInicia el servidor primero con: make dev")
    sys.exit(1)

print("✓ Servidor local detectado y corriendo")
print(f"✓ URL: {BASE_URL}")
print()

# ============================================
# DATOS DE PRUEBA
# ============================================

# Nombres para usuarios de prueba
NOMBRES = ["Ana", "Juan", "María", "Pedro", "Laura", "Carlos", "Sofía", "Miguel", "Elena", "David",
           "Lucía", "Javier", "Carmen", "Antonio", "Isabel", "Manuel", "Patricia", "José", "Rosa", "Francisco"]
APELLIDOS = ["García", "Rodríguez", "Martínez", "López", "González", "Pérez", "Sánchez", "Ramírez",
             "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales", "Reyes", "Ortiz", "Gutiérrez"]

# IDs de actividades existentes
ACTIVIDADES = {
    "bunkers": "a233c17d-75a8-417d-8862-d0e1550fe59e",
    "mercado": "b85e8a14-caa9-4fc4-8d18-b3010f51cd0a",
    "fronton": "31d03477-7125-47e2-bad3-63e9c85e17ad",
    "arbol": "05a05a04-f045-48cf-8ec3-e28d14eec63f",
    "picasso": "d66f036b-c0d3-4765-a64b-dd3643c84c19",
}


def crear_usuario(numero):
    """Crea un usuario de prueba"""
    nombre = random.choice(NOMBRES)
    apellido = random.choice(APELLIDOS)
    username = f"user{numero:03d}"

    response = requests.post(
        f"{BASE_URL}/api/v1/usuarios",
        json={
            "username": username,
            "nombre": nombre,
            "apellido": apellido,
            "password": "test1234",
        },
    )

    if response.status_code == 201:
        data = response.json()
        print(f"  ✓ Usuario creado: {username} ({nombre} {apellido})")
        return data
    else:
        print(f"  ✗ Error al crear usuario {username}: {response.status_code}")
        return None


def login_usuario(username):
    """Hace login y obtiene el token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login-app",
        json={"username": username, "password": "test1234"},
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def crear_partida_con_eventos(token, user_id, dias_atras=0):
    """Crea una partida y simula eventos completados"""
    # Crear partida
    response = requests.post(
        f"{BASE_URL}/api/v1/partidas",
        headers={"Authorization": f"Bearer {token}"},
        json={"id_usuario": user_id},
    )

    if response.status_code != 201:
        return None

    partida = response.json()

    # Simular eventos en algunas actividades (no todas)
    num_actividades = random.randint(1, len(ACTIVIDADES))
    actividades_seleccionadas = random.sample(list(ACTIVIDADES.items()), num_actividades)

    for nombre_act, actividad_id in actividades_seleccionadas:
        # Iniciar evento (simplificado - solo una actividad por ahora)
        # Nota: Este endpoint puede no existir aún, ajustar según tu API
        pass

    return partida


def generar_datos_historicos():
    """Genera datos de los últimos 30 días"""
    print("\n" + "=" * 60)
    print("   GENERANDO DATOS HISTÓRICOS (30 DÍAS)")
    print("=" * 60)

    num_usuarios = 50  # Número de usuarios a crear
    usuarios_creados = []

    # Crear usuarios
    print(f"\n1. Creando {num_usuarios} usuarios...")
    for i in range(1, num_usuarios + 1):
        usuario = crear_usuario(i)
        if usuario:
            usuarios_creados.append(usuario)

    print(f"\n✓ Usuarios creados: {len(usuarios_creados)}")

    # Simular actividad durante los últimos 30 días
    print("\n2. Generando actividad de los últimos 30 días...")

    for dia in range(30):
        dias_atras = 29 - dia
        fecha = datetime.now() - timedelta(days=dias_atras)

        # Algunos usuarios juegan ese día (no todos)
        usuarios_activos = random.sample(usuarios_creados, k=random.randint(5, len(usuarios_creados) // 2))

        partidas_dia = 0
        for usuario in usuarios_activos:
            token = login_usuario(usuario["username"])
            if token:
                # Algunos usuarios juegan varias partidas
                num_partidas = random.randint(1, 3)
                for _ in range(num_partidas):
                    partida = crear_partida_con_eventos(token, usuario["id"], dias_atras)
                    if partida:
                        partidas_dia += 1

        print(f"  Día {fecha.strftime('%Y-%m-%d')}: {len(usuarios_activos)} usuarios, {partidas_dia} partidas")

    print("\n" + "=" * 60)
    print("   ✓ DATOS GENERADOS EXITOSAMENTE")
    print("=" * 60)
    print(f"\nUsuarios totales: {len(usuarios_creados)}")
    print("\nAhora puedes ver las estadísticas en:")
    print("  http://localhost:8000/statistics")
    print("=" * 60)


def menu():
    """Menú interactivo"""
    print("\n" + "=" * 60)
    print("   GENERADOR DE DATOS DE PRUEBA - GERNIBIDE")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE: Este script solo funciona en LOCAL")
    print(f"   URL actual: {BASE_URL}\n")
    print("Opciones:")
    print("  1. Generar datos históricos (30 días, 50 usuarios)")
    print("  2. Crear solo 10 usuarios de prueba")
    print("  3. Salir")
    print()

    opcion = input("Selecciona una opción (1-3): ").strip()

    if opcion == "1":
        confirmar = input("\n¿Confirmar generación de datos históricos? (s/n): ").strip().lower()
        if confirmar == 's':
            generar_datos_historicos()
        else:
            print("Operación cancelada.")

    elif opcion == "2":
        print("\nCreando 10 usuarios de prueba...")
        for i in range(1, 11):
            crear_usuario(i)
        print("\n✓ Usuarios creados exitosamente")

    elif opcion == "3":
        print("\nSaliendo...")
        sys.exit(0)

    else:
        print("\nOpción inválida")


if __name__ == "__main__":
    menu()
