"""Script de migración: Marcar partidas con 19+ actividades como completadas.

Este script busca todas las partidas que tienen 19 o más actividades completadas
y las marca como "completada", estableciendo fecha_fin y duracion.

IMPORTANTE: Este es un script de migración de datos que se ejecuta UNA VEZ.
No es parte del flujo normal de la aplicación.

Uso:
    python scripts/migrate_complete_partidas.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.database import SessionLocal
from app.models.actividad_progreso import ActividadProgreso
from app.models.juego import Partida


def migrate_complete_partidas():
    """Migrar partidas existentes con 19+ actividades a estado completado."""
    db = SessionLocal()

    try:
        # Obtener todas las partidas en progreso
        partidas = db.query(Partida).filter(Partida.estado == "en_progreso").all()

        print(f"📊 Encontradas {len(partidas)} partidas en progreso")
        print("=" * 60)

        updated_count = 0

        for partida in partidas:
            # Contar actividades completadas para esta partida
            total_completadas = (
                db.query(ActividadProgreso)
                .filter(
                    ActividadProgreso.id_juego == partida.id,
                    ActividadProgreso.estado == "completado",
                )
                .count()
            )

            # Si tiene 19 o más actividades completadas, marcar como completada
            if total_completadas >= 19:
                print(f"✅ Partida {partida.id}: {total_completadas} actividades completadas")

                # Actualizar estado
                partida.estado = "completada"

                # Establecer fecha_fin (usar la fecha de la última actividad completada)
                ultima_actividad = (
                    db.query(ActividadProgreso)
                    .filter(
                        ActividadProgreso.id_juego == partida.id,
                        ActividadProgreso.estado == "completado",
                    )
                    .order_by(ActividadProgreso.fecha_fin.desc())
                    .first()
                )

                if ultima_actividad and ultima_actividad.fecha_fin:
                    partida.fecha_fin = ultima_actividad.fecha_fin
                else:
                    # Si no hay fecha_fin en las actividades, usar ahora
                    partida.fecha_fin = datetime.now()

                # Calcular duración
                if partida.fecha_inicio and partida.fecha_fin:
                    duracion_segundos = int(
                        (partida.fecha_fin - partida.fecha_inicio).total_seconds()
                    )
                    partida.duracion = duracion_segundos
                    print(f"   Duración: {duracion_segundos / 60:.1f} minutos")

                updated_count += 1
            else:
                print(
                    f"⏭️  Partida {partida.id}: {total_completadas} actividades (< 19, mantener en progreso)"
                )

        # Commit de todos los cambios
        if updated_count > 0:
            db.commit()
            print("=" * 60)
            print(f"✨ Migración completada: {updated_count} partidas actualizadas")
        else:
            print("=" * 60)
            print("ℹ️  No hay partidas que actualizar")

        # Limpiar cache de estadísticas
        from app.services.gameplay_statistics_service import GameplayStatisticsService

        GameplayStatisticsService.clear_cache()
        print("🗑️  Cache de estadísticas limpiado")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la migración: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Iniciando migración de partidas completadas...")
    print()
    migrate_complete_partidas()
