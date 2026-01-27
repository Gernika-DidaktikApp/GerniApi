#!/bin/bash

# Script simplificado para generar datos de prueba

echo "=================================================="
echo "  GENERADOR DE DATOS DE PRUEBA - GERNIBIDE"
echo "=================================================="
echo ""

# Verificar que el servidor esté corriendo
echo "Verificando servidor local..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ ERROR: El servidor no está corriendo"
    echo ""
    echo "Por favor, inicia el servidor primero:"
    echo "  make dev"
    echo ""
    exit 1
fi

echo "✓ Servidor local detectado"
echo ""

# Ejecutar el generador de datos con Python
cd "$(dirname "$0")/.."
python3 -c "
import requests
import random
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000'

# Nombres para usuarios
NOMBRES = ['Ana', 'Juan', 'María', 'Pedro', 'Laura', 'Carlos', 'Sofía', 'Miguel', 'Elena', 'David']
APELLIDOS = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez']

print('Generando usuarios de prueba...\n')

usuarios_creados = []

# Crear 30 usuarios
for i in range(1, 31):
    nombre = random.choice(NOMBRES)
    apellido = random.choice(APELLIDOS)
    username = f'user{i:03d}'

    response = requests.post(
        f'{BASE_URL}/api/v1/usuarios',
        json={
            'username': username,
            'nombre': nombre,
            'apellido': apellido,
            'password': 'test1234',
        },
    )

    if response.status_code == 201:
        data = response.json()
        usuarios_creados.append(data)
        print(f'  ✓ {username} - {nombre} {apellido}')
    else:
        # Usuario puede ya existir
        pass

print(f'\n✓ Usuarios creados: {len(usuarios_creados)}')

# Generar partidas en los últimos 30 días
print('\nGenerando actividad de los últimos 30 días...\n')

partidas_totales = 0

for dia in range(30):
    dias_atras = 29 - dia
    fecha = datetime.now() - timedelta(days=dias_atras)

    # Algunos usuarios juegan ese día
    num_activos = random.randint(3, min(15, len(usuarios_creados)))
    usuarios_dia = random.sample(usuarios_creados, k=num_activos) if usuarios_creados else []

    partidas_dia = 0

    for usuario in usuarios_dia:
        # Login
        login_resp = requests.post(
            f'{BASE_URL}/api/v1/auth/login-app',
            json={'username': usuario['username'], 'password': 'test1234'}
        )

        if login_resp.status_code == 200:
            token = login_resp.json()['access_token']

            # Crear 1-3 partidas por usuario
            num_partidas = random.randint(1, 3)
            for _ in range(num_partidas):
                partida_resp = requests.post(
                    f'{BASE_URL}/api/v1/partidas',
                    headers={'Authorization': f'Bearer {token}'},
                    json={'id_usuario': usuario['id']}
                )

                if partida_resp.status_code == 201:
                    partidas_dia += 1
                    partidas_totales += 1

    print(f'  {fecha.strftime(\"%Y-%m-%d\")}: {num_activos} usuarios, {partidas_dia} partidas')

print(f'\n================================================')
print(f'  ✓ DATOS GENERADOS EXITOSAMENTE')
print(f'================================================')
print(f'Usuarios totales: {len(usuarios_creados)}')
print(f'Partidas totales: {partidas_totales}')
print(f'\nAhora puedes ver las estadísticas en:')
print(f'  http://localhost:8000/statistics')
print(f'================================================')
"

echo ""
echo "Listo! Recarga la página de estadísticas."
