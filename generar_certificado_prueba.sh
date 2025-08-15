#!/bin/bash

# Script para generar certificado de prueba para desarrollo
# NO USAR EN PRODUCCIÓN - Solo para testing local

echo "🔐 Generando certificado de prueba para desarrollo..."

# Crear directorio de certificados si no existe
mkdir -p certificados

# Configuración del certificado
EMPRESA="Empresa Demo S.A."
CEDULA="3101234567"
EMAIL="demo@empresa.cr"
PAIS="CR"
PROVINCIA="San Jose"
CIUDAD="San Jose"
PASSWORD="demo123456"

echo "📋 Configuración del certificado:"
echo "   Empresa: $EMPRESA"
echo "   Cédula: $CEDULA"
echo "   Email: $EMAIL"
echo "   Password: $PASSWORD"
echo ""

# Generar clave privada
echo "🔑 Generando clave privada..."
openssl genrsa -out certificados/demo_private.key 2048

# Generar certificado auto-firmado
echo "📜 Generando certificado auto-firmado..."
openssl req -new -x509 -key certificados/demo_private.key \
    -out certificados/demo_cert.crt -days 365 \
    -subj "/C=$PAIS/ST=$PROVINCIA/L=$CIUDAD/O=$EMPRESA/OU=IT/CN=$CEDULA/emailAddress=$EMAIL"

# Generar archivo .p12 (PKCS#12)
echo "📦 Generando archivo .p12..."
openssl pkcs12 -export \
    -out certificados/certificado_demo.p12 \
    -inkey certificados/demo_private.key \
    -in certificados/demo_cert.crt \
    -name "Certificado Demo - $EMPRESA" \
    -passout pass:$PASSWORD

# Verificar el certificado generado
echo "✅ Verificando certificado..."
openssl pkcs12 -in certificados/certificado_demo.p12 -noout -info -passin pass:$PASSWORD

echo ""
echo "🎉 ¡Certificado de prueba generado exitosamente!"
echo ""
echo "📁 Archivos generados en certificados/:"
echo "   📄 demo_private.key       - Clave privada"
echo "   📄 demo_cert.crt          - Certificado público"
echo "   📦 certificado_demo.p12   - Certificado empaquetado (USAR ESTE)"
echo ""
echo "🔐 Credenciales:"
echo "   Archivo: certificados/certificado_demo.p12"
echo "   Password: $PASSWORD"
echo ""
echo "⚙️ Para usar en Docker, actualizar docker-compose.yml:"
echo "   CERTIFICATE_PATH=/app/certificados/certificado_demo.p12"
echo "   CERTIFICATE_PASSWORD=$PASSWORD"
echo ""
echo "⚠️ IMPORTANTE: Este certificado es SOLO para desarrollo local."
echo "   Para producción necesitas un certificado oficial del Ministerio de Hacienda."