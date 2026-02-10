#!/usr/bin/env python3
"""
Script para crear una clase con alumnos de prueba
"""

import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, "/Users/warapacheco/Documents/DM25-26/DidaktikApp/API/GerniApi")

from app.database import SessionLocal
from app.models.clase import Clase
from app.models.profesor import Profesor
from app.models.usuario import Usuario
from app.utils.security import hash_password


def crear_clase_con_alumnos():
    """Crea una clase y alumnos de prueba"""
    print("\n🔧 Configurando clase y alumnos de prueba...")

    db = SessionLocal()

    try:
        # Buscar el profesor admin
        profesor = db.query(Profesor).filter(Profesor.username == "admin").first()

        if not profesor:
            print("\n❌ Error: No se encontró el profesor 'admin'")
            print("   Ejecuta primero: python3 scripts/crear_profesor.py")
            sys.exit(1)

        print(f"   Profesor encontrado: {profesor.nombre} {profesor.apellido}")

        # Crear clase si no existe
        clase = (
            db.query(Clase)
            .filter(Clase.id_profesor == profesor.id, Clase.nombre == "4º A - Primaria")
            .first()
        )

        if not clase:
            clase = Clase(id=str(uuid.uuid4()), id_profesor=profesor.id, nombre="4º A - Primaria")
            db.add(clase)
            db.commit()
            db.refresh(clase)
            print(f"   ✅ Clase creada: {clase.nombre}")
        else:
            print(f"   Clase existente: {clase.nombre}")

        # Lista de alumnos
        alumnos_data = [
            ("Aitor", "Etxebarria"),
            ("Ane", "Ugarte"),
            ("Mikel", "Aguirre"),
            ("Leire", "Mendizabal"),
            ("Unai", "Goikoetxea"),
            ("Nerea", "Arrieta"),
            ("Jon", "Zabala"),
            ("Irati", "Elizondo"),
            ("Eneko", "Arana"),
            ("Maialen", "Berasategui"),
        ]

        alumnos_creados = 0

        for nombre, apellido in alumnos_data:
            username = f"{nombre.lower()}.{apellido.lower()}"

            # Verificar si ya existe
            existing = db.query(Usuario).filter(Usuario.username == username).first()

            if not existing:
                alumno = Usuario(
                    id=str(uuid.uuid4()),
                    username=username,
                    nombre=nombre,
                    apellido=apellido,
                    password=hash_password("alumno123"),
                    id_clase=clase.id,
                    creation=datetime.now(),
                    top_score=0,
                )
                db.add(alumno)
                alumnos_creados += 1

        db.commit()

        # Contar total de alumnos en la clase
        total_alumnos = db.query(Usuario).filter(Usuario.id_clase == clase.id).count()

        print("\n✅ Configuración completada!")
        print(f"   Clase: {clase.nombre}")
        print(f"   Profesor: {profesor.nombre} {profesor.apellido}")
        print(f"   Total alumnos: {total_alumnos}")
        print(f"   Nuevos alumnos creados: {alumnos_creados}")

        if alumnos_creados > 0:
            print("\n📝 Credenciales de alumnos:")
            print("   Username: [nombre].[apellido] (ej: aitor.etxebarria)")
            print("   Password: alumno123")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🏫 CREAR CLASE Y ALUMNOS - GerniBide API")
    print("=" * 60)

    crear_clase_con_alumnos()

    print("\n" + "=" * 60)
