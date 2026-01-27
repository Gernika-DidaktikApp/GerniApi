#!/bin/bash

# Script para configurar el sistema de login de GerniBide
# Crea un profesor de prueba y verifica la configuración

echo "=============================================="
echo "🔐 CONFIGURACIÓN DE LOGIN - GerniBide API"
echo "=============================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ Error: Ejecuta este script desde el directorio raíz del proyecto${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Este script creará un profesor de prueba para poder hacer login${NC}"
echo ""
echo "Credenciales por defecto:"
echo "  - Username: admin"
echo "  - Password: admin123"
echo ""

read -p "¿Deseas continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}⚠️  Operación cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🔧 Creando profesor de prueba...${NC}"
echo ""

# Ejecutar el script de Python
python3 scripts/crear_profesor.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Configuración completada!${NC}"
    echo ""
    echo "================================================"
    echo "📝 INSTRUCCIONES DE USO"
    echo "================================================"
    echo ""
    echo "1. Inicia el servidor si no está corriendo:"
    echo "   make dev"
    echo ""
    echo "2. Accede a la página de login:"
    echo "   http://localhost:8000/login"
    echo ""
    echo "3. Ingresa las credenciales:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "4. Serás redirigido al dashboard tras login exitoso"
    echo ""
    echo "================================================"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Error al crear el profesor${NC}"
    echo "Verifica que la base de datos esté configurada correctamente"
    exit 1
fi
