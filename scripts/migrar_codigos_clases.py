#!/usr/bin/env python3
"""Script para generar códigos a clases existentes que no tienen.

Este script debe ejecutarse UNA VEZ después de agregar el campo codigo al modelo Clase.
Genera códigos únicos de 6 caracteres para todas las clases que tienen codigo=NULL.

Autor: Gernibide
"""

from app.database import SessionLocal
from app.logging import log_info, log_warning
from app.models.clase import Clase
from app.utils.security import generar_codigo_clase


def migrar_codigos():
    """Genera códigos únicos para todas las clases sin código."""
    db = SessionLocal()

    try:
        # Obtener clases sin código
        clases_sin_codigo = db.query(Clase).filter(Clase.codigo.is_(None)).all()

        if not clases_sin_codigo:
            log_info("No hay clases sin código. Migración completa.")
            return

        log_info(
            "Iniciando migración de códigos",
            total_clases=len(clases_sin_codigo),
        )

        # Obtener códigos ya existentes para evitar duplicados
        codigos_existentes = {
            codigo for (codigo,) in db.query(Clase.codigo).filter(Clase.codigo.isnot(None)).all()
        }

        # Generar códigos únicos
        codigos_generados = 0
        for clase in clases_sin_codigo:
            # Generar código único
            codigo = generar_codigo_clase()
            while codigo in codigos_existentes:
                codigo = generar_codigo_clase()

            # Asignar código a la clase
            clase.codigo = codigo
            codigos_existentes.add(codigo)
            codigos_generados += 1

            log_info(
                "Código generado",
                clase_id=clase.id,
                clase_nombre=clase.nombre,
                codigo=codigo,
            )

        # Commit de todos los cambios
        db.commit()

        log_info(
            "Migración completada exitosamente",
            codigos_generados=codigos_generados,
        )

    except Exception as e:
        db.rollback()
        log_warning("Error durante migración", error=str(e))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("   MIGRACIÓN DE CÓDIGOS DE CLASES - GERNIBIDE")
    print("=" * 60)
    print()

    migrar_codigos()

    print()
    print("=" * 60)
    print("   MIGRACIÓN COMPLETADA")
    print("=" * 60)
