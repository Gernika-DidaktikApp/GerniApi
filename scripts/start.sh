#!/bin/bash
set -e

echo "Aplicando migraciones..."
alembic upgrade head

echo "Iniciando servidor..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
