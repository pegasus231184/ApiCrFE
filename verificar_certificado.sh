#!/bin/bash

# Script para verificar certificado oficial de Hacienda

CERT_PATH="certificados/310277607903.p12"

echo "🔐 Verificando certificado oficial de Hacienda..."
echo "📁 Archivo: $CERT_PATH"
echo ""

if [ ! -f "$CERT_PATH" ]; then
    echo "❌ Error: Certificado no encontrado en $CERT_PATH"
    exit 1
fi

echo "📊 Información del archivo:"
ls -lh "$CERT_PATH"
echo ""

echo "🔍 Para verificar el certificado, necesitas la contraseña."
echo "💡 La contraseña te la proporcionó Hacienda cuando generaste el certificado."
echo ""
echo "🧪 Puedes probar la contraseña con este comando:"
echo "   openssl pkcs12 -in $CERT_PATH -noout -info"
echo ""
echo "📋 Una vez que tengas la contraseña correcta:"
echo "   1. Actualiza CERTIFICATE_PASSWORD en el archivo .env"
echo "   2. Reinicia el contenedor Docker"
echo "   3. El API podrá firmar documentos reales"
echo ""

# Intentar obtener información básica sin contraseña
echo "🔍 Información básica del certificado:"
file "$CERT_PATH"
echo ""

echo "⚠️ IMPORTANTE:"
echo "   - Este es un certificado OFICIAL de Hacienda"
echo "   - NO lo compartas ni lo subas a repositorios públicos"
echo "   - Úsalo solo en tu entorno de desarrollo/producción seguro"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Obtener credenciales CLIENT_ID y CLIENT_SECRET de Hacienda"
echo "   2. Configurar la contraseña del certificado"
echo "   3. Cambiar HACIENDA_SANDBOX=false para producción"