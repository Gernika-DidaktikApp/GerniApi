#!/usr/bin/env python3
"""
Script para crear eventos para cada actividad en GerniBide
"""

import os

import requests

# Configuración
BASE_URL = "https://gernibide.up.railway.app"
# BASE_URL = "http://localhost:8000"  # Para pruebas locales

# API Key (obtener de variable de entorno o pedir)
API_KEY = os.environ.get("API_KEY", "X4vVLE23CQaQOLMdpoRZaIZGkVbPoFVKvvWedQj2HuE")

# IDs de actividades existentes
ACTIVIDADES = {
    "arbol": "05a05a04-f045-48cf-8ec3-e28d14eec63f",
    "picasso": "d66f036b-c0d3-4765-a64b-dd3643c84c19",
    "fronton": "31d03477-7125-47e2-bad3-63e9c85e17ad",
    "mercado": "b85e8a14-caa9-4fc4-8d18-b3010f51cd0a",
    "bunkers": "a233c17d-75a8-417d-8862-d0e1550fe59e",
}

# Eventos a crear por actividad
EVENTOS = {
    "arbol": [
        "Audio quiz",
        "Plaza Puzzle",
        "Nire Arbola",
    ],
    "picasso": [
        "Colorea la paz",
        "Observa y adivina",
        "Mi mensaje para el mundo",
    ],
    "fronton": [
        "Información del fronton",
        "Pelota Dantzan",
        "Valores del equipo",
        "Tu valor del equipo",
    ],
    "mercado": [
        "Plaza Video",
        "Conoce el mercado",
        "Adivina el verso",
        "Misión fotográfica",
    ],
    "bunkers": [
        "Soinu Jokoa",
        "Bake murala",
        "Hausnarketa",
    ],
}


def crear_evento(nombre: str, id_actividad: str) -> dict | None:
    """Crea un evento para una actividad"""
    response = requests.post(
        f"{BASE_URL}/api/v1/eventos",
        headers={"X-API-Key": API_KEY},
        json={"nombre": nombre, "id_actividad": id_actividad},
    )

    if response.status_code == 201:
        return response.json()
    else:
        print(f"  Error: {response.status_code} - {response.json()}")
        return None


def main():
    if not API_KEY:
        print("Error: API_KEY no configurada")
        print("Usa: API_KEY=tu_api_key python3 scripts/crear_eventos.py")
        return

    print("=" * 60)
    print("   CREAR EVENTOS - GERNIBIDE")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print()

    total_creados = 0
    total_errores = 0

    for actividad_nombre, eventos in EVENTOS.items():
        id_actividad = ACTIVIDADES[actividad_nombre]
        print(f"\n{actividad_nombre.upper()} ({id_actividad[:8]}...)")
        print("-" * 40)

        for evento_nombre in eventos:
            resultado = crear_evento(evento_nombre, id_actividad)
            if resultado:
                print(f"  ✓ {evento_nombre} (ID: {resultado['id'][:8]}...)")
                total_creados += 1
            else:
                print(f"  ✗ {evento_nombre}")
                total_errores += 1

    print()
    print("=" * 60)
    print(f"RESUMEN: {total_creados} creados, {total_errores} errores")
    print("=" * 60)


if __name__ == "__main__":
    main()
