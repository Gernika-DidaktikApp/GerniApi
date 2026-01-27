# Makefile para GerniApi
# Comandos útiles para desarrollo

.PHONY: dev install test clean

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

# Instalar dependencias
install:
	@echo "📦 Instalando dependencias..."
	pip install -r requirements.txt

# Ejecutar tests
test:
	@echo "🧪 Ejecutando tests..."
	.venv/bin/pytest

# Limpiar archivos temporales
clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
