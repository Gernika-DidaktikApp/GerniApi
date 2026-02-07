#!/usr/bin/env python3
"""
Script para crear un profesor de prueba en la base de datos local
Solo funciona contra localhost para mayor seguridad
"""

import sys
import uuid
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, '/Users/warapacheco/Documents/DM25-26/DidaktikApp/API/GerniApi')

from app.database import SessionLocal
from app.models.profesor import Profesor
from app.utils.security import hash_password


def crear_profesor_prueba(
    username: str = "admin",
    password: str = "admin123",
    nombre: str = "Profesor",
    apellido: str = "Admin"
):
    """
    Crea un profesor de prueba en la base de datos

    Args:
        username: Nombre de usuario
        password: Contraseña (será hasheada)
        nombre: Nombre del profesor
        apellido: Apellido del profesor
    """
    print("\n🔧 Creando profesor de prueba...")
    print(f"   Username: {username}")
    print(f"   Nombre: {nombre} {apellido}")

    db = SessionLocal()

    try:
        # Verificar si ya existe
        existing = db.query(Profesor).filter(Profesor.username == username).first()
        if existing:
            print(f"\n⚠️  El profesor '{username}' ya existe en la base de datos")
            print(f"   ID: {existing.id}")
            print(f"   Nombre: {existing.nombre} {existing.apellido}")

            # Preguntar si quiere actualizar la contraseña
            respuesta = input("\n¿Deseas actualizar la contraseña? (s/n): ")
            if respuesta.lower() == 's':
                existing.password = hash_password(password)
                db.commit()
                print(f"\n✅ Contraseña actualizada para '{username}'")
            else:
                print("\n✅ Profesor existente sin cambios")

            db.close()
            return

        # Crear nuevo profesor
        profesor = Profesor(
            id=str(uuid.uuid4()),
            username=username,
            nombre=nombre,
            apellido=apellido,
            password=hash_password(password),
            created=datetime.now()
        )

        db.add(profesor)
        db.commit()
        db.refresh(profesor)

        print("\n✅ Profesor creado exitosamente!")
        print(f"   ID: {profesor.id}")
        print(f"   Username: {profesor.username}")
        print(f"   Nombre: {profesor.nombre} {profesor.apellido}")
        print("\n📝 Credenciales de acceso:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("\n🌐 Accede en: http://localhost:8000/login")

    except Exception as e:
        print(f"\n❌ Error al crear profesor: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🎓 CREAR PROFESOR DE PRUEBA - GerniBide API")
    print("=" * 60)

    # Verificar si se pasaron argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("\nUso:")
            print("  python scripts/crear_profesor.py                    # Crea profesor por defecto (admin/admin123)")
            print("  python scripts/crear_profesor.py <username> <pass>  # Crea profesor con credenciales personalizadas")
            print("  python scripts/crear_profesor.py <user> <pass> <nombre> <apellido>  # Completo")
            print("\nEjemplo:")
            print("  python scripts/crear_profesor.py teacher pass123")
            print("  python scripts/crear_profesor.py maria garcia123 María García")
            sys.exit(0)

        # Modo personalizado
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "admin123"
        nombre = sys.argv[3] if len(sys.argv) > 3 else "Profesor"
        apellido = sys.argv[4] if len(sys.argv) > 4 else "Prueba"

        crear_profesor_prueba(username, password, nombre, apellido)
    else:
        # Modo por defecto
        print("\n📌 Creando profesor con credenciales por defecto")
        print("   (Usa -h para ver opciones de personalización)")
        crear_profesor_prueba()

    print("\n" + "=" * 60)
