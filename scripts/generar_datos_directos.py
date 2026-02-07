#!/usr/bin/env python3
"""
Script para generar datos de prueba directamente en la base de datos
Sin necesidad de tener el servidor corriendo
"""

import random
import sys
import uuid
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, '/Users/warapacheco/Documents/DM25-26/DidaktikApp/API/GerniApi')

from app.database import SessionLocal
from app.models.actividad import Actividad
from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida
from app.models.punto import Punto
from app.models.usuario import Usuario


def crear_puntos_actividades(db):
    """Crea puntos y actividades si no existen"""
    puntos_data = [
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

    puntos = []

    for nombre_punto, actividades_nombres in puntos_data:
        # Buscar o crear punto
        punto = db.query(Punto).filter(Punto.nombre == nombre_punto).first()

        if not punto:
            punto = Punto(
                id=str(uuid.uuid4()),
                nombre=nombre_punto
            )
            db.add(punto)
            db.flush()

        puntos.append(punto)

        # Crear actividades para este punto
        for nombre_act in actividades_nombres:
            actividad = db.query(Actividad).filter(
                Actividad.nombre == nombre_act,
                Actividad.id_punto == punto.id
            ).first()

            if not actividad:
                actividad = Actividad(
                    id=str(uuid.uuid4()),
                    id_punto=punto.id,
                    nombre=nombre_act
                )
                db.add(actividad)

    db.commit()
    print(f"   ✅ {len(puntos)} puntos con actividades creados")

    return puntos


def generar_partidas_y_progreso(db, usuarios, puntos, dias=14):
    """Genera partidas y progreso de actividades para los últimos N días"""

    partidas_creadas = 0
    progreso_creado = 0

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

            # Crear progreso para esta partida
            # Seleccionar 1-3 puntos aleatorios
            puntos_partida = random.sample(puntos, k=random.randint(1, min(3, len(puntos))))

            for punto in puntos_partida:
                # Obtener actividades de este punto
                actividades = db.query(Actividad).filter(Actividad.id_punto == punto.id).all()

                for actividad in actividades:
                    # No crear progreso para todas las actividades
                    if random.random() > 0.3:  # 70% probabilidad de crear progreso
                        continue

                    # Estado del progreso (más probable completado si partida completada)
                    if estado_partida == "completada":
                        estado_progreso = random.choices(
                            ["completado", "en_progreso", "abandonado"],
                            weights=[0.8, 0.1, 0.1]
                        )[0]
                    elif estado_partida == "en_progreso":
                        estado_progreso = random.choices(
                            ["completado", "en_progreso", "abandonado"],
                            weights=[0.4, 0.5, 0.1]
                        )[0]
                    else:
                        estado_progreso = "abandonado"

                    # Duración de la actividad (2-10 minutos)
                    duracion_actividad = random.randint(120, 600) if estado_progreso == "completado" else None

                    # Puntuación (5-10 si completado)
                    puntuacion = round(random.uniform(5.0, 10.0), 1) if estado_progreso == "completado" else None

                    # Fecha fin
                    fecha_fin = fecha_inicio + timedelta(seconds=duracion_actividad) if duracion_actividad else None

                    # Crear progreso de actividad
                    actividad_progreso = ActividadProgreso(
                        id=str(uuid.uuid4()),
                        id_juego=partida.id,
                        id_punto=punto.id,
                        id_actividad=actividad.id,
                        fecha_inicio=fecha_inicio + timedelta(minutes=random.randint(1, 10)),
                        duracion=duracion_actividad,
                        fecha_fin=fecha_fin,
                        estado=estado_progreso,
                        puntuacion=puntuacion
                    )
                    db.add(actividad_progreso)
                    progreso_creado += 1

    db.commit()
    print(f"   ✅ {partidas_creadas} partidas creadas")
    print(f"   ✅ {progreso_creado} registros de progreso creados")


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

        # Crear puntos y actividades
        puntos = crear_puntos_actividades(db)

        # Generar partidas y progreso de actividades
        generar_partidas_y_progreso(db, usuarios, puntos, dias=14)

        print("\n✅ Datos generados exitosamente!")
        print("\n🌐 Ahora puedes:")
        print("   1. Iniciar el servidor: make dev")
        print("   2. Login: http://localhost:8000/login")
        print("      Username: admin")
        print("      Password: admin123")
        print("   3. Ver dashboard: http://localhost:8000/dashboard/teacher")

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
