# Makefile para GerniApi
# Comandos útiles para desarrollo

.PHONY: dev install install-dev test lint format clean

# Servidor de desarrollo con hot-reload
dev:
	@echo "🌳 Iniciando GerniApi en modo desarrollo..."
	@echo "📍 Páginas web disponibles:"
	@echo "   - Inicio: http://localhost:8000/"
	@echo "   - Login: http://localhost:8000/login"
	@echo "   - Dashboard: http://localhost:8000/dashboard"
	@echo "   - Estadísticas: http://localhost:8000/statistics"
	@echo "   - Uso del Juego: http://localhost:8000/statistics/gameplay"
	@echo "   - Aprendizaje: http://localhost:8000/statistics/learning"
	@echo "   - Mi Clase: http://localhost:8000/dashboard/teacher"
	@echo ""
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo "🛑 Presiona Ctrl+C para detener"
	@echo ""
	.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Instalar dependencias de producción
install:
	@echo "📦 Instalando dependencias de producción..."
	pip install -r requirements.txt

# Instalar dependencias de desarrollo (incluye linters)
install-dev:
	@echo "📦 Instalando dependencias de desarrollo..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Ejecutar tests
test:
	@echo "🧪 Ejecutando tests..."
	pytest

# Ejecutar linters (verificación)
lint:
	@echo "🔍 Ejecutando linters..."
	@echo "  → Black (verificando formato)..."
	black --check --diff app tests
	@echo "\n  → isort (verificando imports)..."
	isort --check-only --diff app tests
	@echo "\n  → Ruff (verificando código)..."
	ruff check app tests
	@echo "\n✅ Todos los linters pasaron correctamente!"

# Formatear código automáticamente
format:
	@echo "✨ Formateando código..."
	@echo "  → Black (formateando archivos)..."
	black app tests
	@echo "  → isort (ordenando imports)..."
	isort app tests
	@echo "\n✅ Código formateado correctamente!"

# Limpiar archivos temporales
clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov coverage.xml .coverage
