#!/usr/bin/env python3
"""
Script para generar datos de prueba directamente en la base de datos
Sin necesidad de tener el servidor corriendo
"""

import sys
import uuid
import random
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, '/Users/warapacheco/Documents/DM25-26/DidaktikApp/API/GerniApi')

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models.actividad import Actividad
from app.models.evento import Eventos
from app.models.juego import Partida
from app.models.evento_estado import EventoEstado


def crear_actividades_eventos(db):
    """Crea actividades y eventos si no existen"""
    actividades_data = [
        ("Árbol del Gernika", [
            "Ubicación del árbol",
            "Historia del árbol",
            "Significado simbólico"
        ]),
        ("Museo de la Paz", [
            "Entrada al museo",
            "Exposición principal",
            "Sala audiovisual"
        ]),
        ("Refugio Antiaéreo", [
            "Acceso al refugio",
            "Recorrido interior",
            "Historia del bombardeo"
        ]),
        ("Casa de Juntas", [
            "Exterior del edificio",
            "Sala de juntas",
            "Árbol sagrado"
        ]),
        ("Parque de los Pueblos", [
            "Entrada del parque",
            "Esculturas",
            "Zonas verdes"
        ])
    ]

    actividades = []

    for nombre_act, eventos_nombres in actividades_data:
        # Buscar o crear actividad
        actividad = db.query(Actividad).filter(Actividad.nombre == nombre_act).first()

        if not actividad:
            actividad = Actividad(
                id=str(uuid.uuid4()),
                nombre=nombre_act
            )
            db.add(actividad)
            db.flush()

        actividades.append(actividad)

        # Crear eventos para esta actividad
        for nombre_evt in eventos_nombres:
            evento = db.query(Eventos).filter(
                Eventos.nombre == nombre_evt,
                Eventos.id_actividad == actividad.id
            ).first()

            if not evento:
                evento = Eventos(
                    id=str(uuid.uuid4()),
                    id_actividad=actividad.id,
                    nombre=nombre_evt
                )
                db.add(evento)

    db.commit()
    print(f"   ✅ {len(actividades)} actividades con eventos creadas")

    return actividades


def generar_partidas_y_eventos(db, usuarios, actividades, dias=14):
    """Genera partidas y eventos de estado para los últimos N días"""

    estados_posibles = ["completado", "en_progreso", "abandonado"]
    partidas_creadas = 0
    eventos_creados = 0

    now = datetime.now()

    for usuario in usuarios:
        # Cada usuario tiene entre 3-8 partidas en los últimos días
        num_partidas = random.randint(3, 8)

        for _ in range(num_partidas):
            # Fecha aleatoria en los últimos N días
            dias_atras = random.randint(0, dias - 1)
            fecha_inicio = now - timedelta(days=dias_atras, hours=random.randint(0, 23))

            # Estado de la partida
            estado_partida = random.choice(["completada", "en_progreso", "abandonada"])

            # Duración en segundos (10-45 minutos)
            duracion = random.randint(600, 2700) if estado_partida == "completada" else None

            # Crear partida
            partida = Partida(
                id=str(uuid.uuid4()),
                id_usuario=usuario.id,
                fecha_inicio=fecha_inicio,
                duracion=duracion,
                estado=estado_partida
            )
            db.add(partida)
            db.flush()
            partidas_creadas += 1

            # Crear eventos para esta partida
            # Seleccionar 1-3 actividades aleatorias
            actividades_partida = random.sample(actividades, k=random.randint(1, min(3, len(actividades))))

            for actividad in actividades_partida:
                # Obtener eventos de esta actividad
                eventos = db.query(Eventos).filter(Eventos.id_actividad == actividad.id).all()

                for evento in eventos:
                    # No crear evento estado para todas las actividades
                    if random.random() > 0.3:  # 70% probabilidad de crear evento
                        continue

                    # Estado del evento (más probable completado si partida completada)
                    if estado_partida == "completada":
                        estado_evento = random.choices(
                            ["completado", "en_progreso", "abandonado"],
                            weights=[0.8, 0.1, 0.1]
                        )[0]
                    elif estado_partida == "en_progreso":
                        estado_evento = random.choices(
                            ["completado", "en_progreso", "abandonado"],
                            weights=[0.4, 0.5, 0.1]
                        )[0]
                    else:
                        estado_evento = "abandonado"

                    # Duración del evento (2-10 minutos)
                    duracion_evento = random.randint(120, 600) if estado_evento == "completado" else None

                    # Puntuación (5-10 si completado)
                    puntuacion = round(random.uniform(5.0, 10.0), 1) if estado_evento == "completado" else None

                    # Fecha fin
                    fecha_fin = fecha_inicio + timedelta(seconds=duracion_evento) if duracion_evento else None

                    # Crear evento estado
                    evento_estado = EventoEstado(
                        id=str(uuid.uuid4()),
                        id_juego=partida.id,
                        id_actividad=actividad.id,
                        id_evento=evento.id,
                        fecha_inicio=fecha_inicio + timedelta(minutes=random.randint(1, 10)),
                        duracion=duracion_evento,
                        fecha_fin=fecha_fin,
                        estado=estado_evento,
                        puntuacion=puntuacion
                    )
                    db.add(evento_estado)
                    eventos_creados += 1

    db.commit()
    print(f"   ✅ {partidas_creadas} partidas creadas")
    print(f"   ✅ {eventos_creados} eventos de estado creados")


def main():
    print("\n🔧 Generando datos de prueba...")

    db = SessionLocal()

    try:
        # Obtener usuarios (alumnos)
        usuarios = db.query(Usuario).filter(Usuario.id_clase.isnot(None)).all()

        if not usuarios:
            print("\n❌ Error: No hay alumnos en la base de datos")
            print("   Ejecuta primero: python3 scripts/crear_clase_alumnos.py")
            sys.exit(1)

        print(f"   Encontrados {len(usuarios)} alumnos")

        # Crear actividades y eventos
        actividades = crear_actividades_eventos(db)

        # Generar partidas y eventos de estado
        generar_partidas_y_eventos(db, usuarios, actividades, dias=14)

        print(f"\n✅ Datos generados exitosamente!")
        print(f"\n🌐 Ahora puedes:")
        print(f"   1. Iniciar el servidor: make dev")
        print(f"   2. Login: http://localhost:8000/login")
        print(f"      Username: admin")
        print(f"      Password: admin123")
        print(f"   3. Ver dashboard: http://localhost:8000/dashboard/teacher")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("📊 GENERAR DATOS DE PRUEBA - GerniBide API")
    print("=" * 60)

    main()

    print("\n" + "=" * 60)
