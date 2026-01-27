#!/usr/bin/env python3
"""
Script para listar todos los eventos con sus IDs
"""

import os

import requests

# Configuración
BASE_URL = "https://gernibide.up.railway.app"
# BASE_URL = "http://localhost:8000"  # Para pruebas locales

API_KEY = os.environ.get("API_KEY", "X4vVLE23CQaQOLMdpoRZaIZGkVbPoFVKvvWedQj2HuE")

# IDs de actividades
ACTIVIDADES = {
    "arbol": "05a05a04-f045-48cf-8ec3-e28d14eec63f",
    "picasso": "d66f036b-c0d3-4765-a64b-dd3643c84c19",
    "fronton": "31d03477-7125-47e2-bad3-63e9c85e17ad",
    "mercado": "b85e8a14-caa9-4fc4-8d18-b3010f51cd0a",
    "bunkers": "a233c17d-75a8-417d-8862-d0e1550fe59e",
}


def obtener_todos_eventos() -> list:
    """Obtiene todos los eventos"""
    response = requests.get(
        f"{BASE_URL}/api/v1/eventos",
        headers={"X-API-Key": API_KEY},
    )
    if response.status_code == 200:
        return response.json()
    print(f"Error: {response.status_code} - {response.text}")
    return []


def main():
    if not API_KEY:
        print("Error: API_KEY no configurada")
        print("Usa: API_KEY=tu_api_key python3 scripts/listar_eventos.py")
        return

    print("=" * 80)
    print("   EVENTOS DE GERNIBIDE - IDs")
    print("=" * 80)

    # Obtener todos los eventos
    todos_eventos = obtener_todos_eventos()

    # Agrupar por actividad
    eventos_por_actividad = {}
    for evento in todos_eventos:
        id_act = evento.get("id_actividad")
        if id_act not in eventos_por_actividad:
            eventos_por_actividad[id_act] = []
        eventos_por_actividad[id_act].append(evento)

    for actividad_nombre, id_actividad in ACTIVIDADES.items():
        print(f"\n## {actividad_nombre.upper()}")
        print(f"ID Actividad: {id_actividad}")
        print("-" * 60)

        eventos = eventos_por_actividad.get(id_actividad, [])
        if eventos:
            for evento in eventos:
                print(f"  - {evento['nombre']}")
                print(f"    ID: {evento['id']}")
        else:
            print("  (sin eventos)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
