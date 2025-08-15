# 🔐 Configuración Certificado Oficial de Hacienda

## ✅ **Estado Actual**

Tu certificado oficial **310277607903.p12** ya está copiado en el proyecto:
- 📁 **Ubicación**: `certificados/310277607903.p12`
- 📊 **Tamaño**: 6.5KB
- 🔐 **Tipo**: Certificado oficial del Ministerio de Hacienda de Costa Rica

## 🚀 **Pasos para Activar Facturación Real**

### 1. **Configurar Contraseña del Certificado**

Necesitas la contraseña que te proporcionó Hacienda cuando generaste el certificado.

#### Probar la contraseña:
```bash
# Desde la carpeta del proyecto
openssl pkcs12 -in certificados/310277607903.p12 -noout -info

# Te pedirá la contraseña. Si es correcta, mostrará info del certificado
```

#### Una vez que confirmes la contraseña:
```bash
# Editar archivo .env
nano .env

# Cambiar esta línea:
CERTIFICATE_PASSWORD=SOLICITAR_PASSWORD

# Por tu contraseña real:
CERTIFICATE_PASSWORD=tu_password_real_aqui
```

### 2. **Obtener Credenciales de Hacienda**

Necesitas registrarte en el portal de Hacienda para obtener:

#### **CLIENT_ID y CLIENT_SECRET**:
1. Ir a: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/
2. Registrar tu empresa en el sistema ATV
3. Solicitar credenciales para API
4. Te proporcionarán:
   - `CLIENT_ID`: Identificador único de tu empresa
   - `CLIENT_SECRET`: Clave secreta para autenticación OAuth2

#### Actualizar en .env:
```bash
# Cambiar estas líneas en .env:
HACIENDA_CLIENT_ID=tu_client_id_real_aqui
HACIENDA_CLIENT_SECRET=tu_client_secret_real_aqui
```

### 3. **Configurar Ambiente de Producción**

#### Para usar el ambiente REAL de Hacienda:
```bash
# En .env, cambiar:
HACIENDA_SANDBOX=false
```

#### Para seguir en modo de pruebas (recomendado al inicio):
```bash
# Mantener:
HACIENDA_SANDBOX=true
```

### 4. **Reiniciar el API con Certificado**

```bash
# Parar servicios
docker-compose down

# Reconstruir con nueva configuración
docker-compose build

# Levantar servicios
docker-compose up -d

# Verificar logs
docker-compose logs -f api
```

## 🧪 **Verificar Configuración**

### Endpoint de verificación de certificado:
```bash
curl "http://localhost:8001/api/v1/utils/info-certificado"
```

### Respuesta esperada con certificado válido:
```json
{
  "certificado_configurado": true,
  "informacion": {
    "subject": "CN=310277607903,O=Tu Empresa,C=CR",
    "issuer": "CN=CA Autorizada Hacienda,O=Ministerio Hacienda,C=CR",
    "serial_number": "123456789",
    "not_valid_before": "2024-01-01T00:00:00",
    "not_valid_after": "2025-12-31T23:59:59",
    "is_valid": true,
    "modo": "certificado_oficial"
  }
}
```

## 🔍 **Troubleshooting**

### ❌ **Error: "Contraseña incorrecta"**
- Verificar que la contraseña sea exactamente la que te dio Hacienda
- No debe tener espacios extra al inicio o final
- Distingue mayúsculas y minúsculas

### ❌ **Error: "Certificado no encontrado"**
- Verificar que el archivo esté en `certificados/310277607903.p12`
- Verificar permisos del archivo: `ls -la certificados/`

### ❌ **Error: "CLIENT_ID inválido"**
- Verificar credenciales en el portal de Hacienda
- Confirmar que la empresa esté registrada en ATV
- Verificar que no haya espacios extra en las credenciales

### ⚠️ **Certificado válido pero errores de envío**
- Verificar que `HACIENDA_SANDBOX=true` para pruebas
- Confirmar que la empresa tenga permisos de facturación
- Revisar que los datos del XML cumplan normativa v4.4

## 📋 **Checklist de Configuración**

- [ ] ✅ Certificado copiado: `certificados/310277607903.p12`
- [ ] 🔐 Contraseña configurada en `.env`
- [ ] 🆔 CLIENT_ID obtenido de Hacienda
- [ ] 🔑 CLIENT_SECRET obtenido de Hacienda
- [ ] ⚙️ Variables actualizadas en `.env`
- [ ] 🐳 Docker reiniciado con nueva configuración
- [ ] 🧪 Endpoint de verificación funciona
- [ ] 📄 Facturas de prueba se generan correctamente

## 🚀 **Próximos Pasos después de Configuración**

1. **Probar en Sandbox**:
   ```bash
   # Crear factura de prueba
   curl -X POST "http://localhost:8001/api/v1/facturas" \
     -H "Content-Type: application/json" \
     -d '{...}'  # Usar datos de ejemplo
   ```

2. **Verificar envío a Hacienda**:
   ```bash
   # Consultar estado
   curl "http://localhost:8001/api/v1/documentos/{clave}"
   ```

3. **Cuando todo funcione en Sandbox**:
   - Cambiar `HACIENDA_SANDBOX=false`
   - Hacer pruebas finales
   - ¡Comenzar facturación real!

## 📞 **Soporte**

### **Si necesitas ayuda con:**
- **Contraseña del certificado**: Contactar a quien generó el certificado en tu empresa
- **Credenciales de Hacienda**: Portal de Hacienda o soporte técnico ATV
- **Configuración del API**: Revisar logs con `docker-compose logs api`

### **Recursos oficiales:**
- **Portal ATV**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/
- **Documentación técnica**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/
- **Esquemas XSD v4.4**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/

---

**🔐 Con tu certificado oficial configurado podrás:**
- ✅ Firmar documentos con validez legal
- ✅ Enviar facturas reales a Hacienda
- ✅ Cumplir normativa de facturación electrónica
- ✅ Integrar con sistemas contables y ERP