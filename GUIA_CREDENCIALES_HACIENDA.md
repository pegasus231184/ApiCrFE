# 🔑 Guía para Obtener Credenciales API de Hacienda

## 📋 **Información de tu Empresa**
- **Empresa**: SIMPLEXITY CONSULTING LIMITADA
- **Cédula Jurídica**: 3-102-776079
- **Certificado**: ✅ Ya configurado (310277607903.p12)

## 🎯 **Objetivo**
Obtener `CLIENT_ID` y `CLIENT_SECRET` para que tu API pueda enviar facturas automáticamente a Hacienda.

---

## 📍 **PASO 1: Acceder al Portal ATV**

### **URL Principal:**
https://www.hacienda.go.cr/ATV/ComprobanteElectronico/

### **Opciones de acceso:**
1. **Portal Contribuyentes**: https://atv.hacienda.go.cr/ATV/frmLogin.aspx
2. **Portal Desarrolladores**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/frmAPIConsultas.aspx

---

## 📝 **PASO 2: Registro/Login en el Sistema**

### **Si es primera vez:**
1. Ir a **"Registro de Usuario"**
2. Usar cédula jurídica: **3-102-776079**
3. Proporcionar datos del representante legal
4. Verificar email corporativo

### **Datos necesarios:**
- Cédula jurídica: **3-102-776079**
- Nombre empresa: **SIMPLEXITY CONSULTING LIMITADA**
- Representante legal (nombre y cédula)
- Email corporativo
- Teléfono de contacto

---

## 🔧 **PASO 3: Solicitar Credenciales API**

### **Navegar a:**
- **Sección**: "Servicios Web" o "API de Integración"
- **Subsección**: "Credenciales para Desarrolladores"

### **Información a proporcionar:**

#### **Datos de la Aplicación:**
```
Nombre de la aplicación: API Facturación SIMPLEXITY
Descripción: Sistema de facturación electrónica para SIMPLEXITY CONSULTING LIMITADA
Tipo de integración: API REST
Ambiente solicitado: SANDBOX (para pruebas)
Volumen estimado: [X] facturas por mes
```

#### **Datos Técnicos:**
```
URL de callback (opcional): http://localhost:8001/webhook/hacienda
IP del servidor: [Tu IP pública]
Certificado digital: 310277607903.p12 (YA CONFIGURADO)
```

#### **Contacto Técnico:**
```
Nombre: [Tu nombre]
Email: [Tu email]
Teléfono: [Tu teléfono]
Rol: Desarrollador/Administrador técnico
```

---

## 📞 **PASO 4: Contactos para Soporte**

### **Si necesitas ayuda:**

#### **Soporte Técnico ATV:**
- **Teléfono**: 2539-4357
- **Email**: atv@hacienda.go.cr
- **Horario**: Lunes a viernes, 8:00 AM - 4:30 PM

#### **Consultas específicas de API:**
- **Email**: soporteapi@hacienda.go.cr
- **Documentación**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/

### **Información a mencionar en la llamada:**
```
"Hola, soy [tu nombre] de SIMPLEXITY CONSULTING LIMITADA, 
cédula jurídica 3-102-776079. 

Necesito obtener credenciales CLIENT_ID y CLIENT_SECRET 
para integrar nuestro sistema de facturación con el API 
de comprobantes electrónicos.

Ya tenemos el certificado digital configurado: 310277607903.p12
y necesitamos las credenciales para el ambiente SANDBOX."
```

---

## ⏱️ **PASO 5: Tiempos de Respuesta**

### **Tiempos estimados:**
- **Solicitud en línea**: 2-5 días hábiles
- **Solicitud telefónica**: 1-3 días hábiles  
- **Casos urgentes**: Mismo día (mencionar urgencia)

### **Qué esperar:**
Recibirás un email con:
```json
{
  "client_id": "simplexity_sandbox_abc123",
  "client_secret": "def456ghi789jkl012mno345",
  "ambiente": "sandbox",
  "url_token": "https://api.comprobanteselectronicos.go.cr/testwcf/oauth/token",
  "url_envio": "https://api.comprobanteselectronicos.go.cr/testwcf/recepcion"
}
```

---

## 🔧 **PASO 6: Configurar Credenciales**

### **Cuando recibas las credenciales:**

#### **Actualizar .env:**
```bash
# Cambiar estas líneas:
HACIENDA_CLIENT_ID=simplexity_sandbox_abc123
HACIENDA_CLIENT_SECRET=def456ghi789jkl012mno345
HACIENDA_SANDBOX=true
```

#### **Reiniciar API:**
```bash
docker-compose down
docker-compose up -d
```

#### **Probar conexión:**
```bash
curl "http://localhost:8001/api/v1/utils/info-certificado"
```

---

## 🧪 **PASO 7: Pruebas de Integración**

### **Primera prueba - Crear factura:**
```bash
curl -X POST "http://localhost:8001/api/v1/facturas" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {
      "nombre": "SIMPLEXITY CONSULTING LIMITADA",
      "identificacion_tipo": "02",
      "identificacion_numero": "3102776079",
      "ubicacion": {"provincia": "1", "canton": "01", "distrito": "01"},
      "correo_electronico": "facturacion@simplexity.cr"
    },
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [{
      "numero_linea": 1,
      "cantidad": 1,
      "unidad_medida": "Sp",
      "detalle": "Consultoría de prueba",
      "precio_unitario": 10000,
      "monto_total": 10000,
      "subtotal": 10000,
      "monto_total_linea": 11300
    }],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_servicios_gravados": 10000,
      "total_venta": 10000,
      "total_venta_neta": 10000,
      "total_impuesto": 1300,
      "total_comprobante": 11300
    },
    "codigo_actividad": "620200"
  }'
```

### **Verificar envío:**
```bash
# La respuesta debe mostrar:
{
  "estado": "enviando"  # ← Enviándose a Hacienda automáticamente
}
```

### **Consultar estado:**
```bash
curl "http://localhost:8001/api/v1/documentos/{clave}"

# Debe mostrar:
{
  "estado": "aceptado",  # ← Hacienda aceptó la factura
  "mensaje_hacienda": "Documento procesado correctamente"
}
```

---

## 🎯 **Checklist de Proceso**

- [ ] 📋 Registrarse en portal ATV
- [ ] 🔑 Solicitar credenciales SANDBOX
- [ ] ⏱️ Esperar respuesta (2-5 días)
- [ ] 📧 Recibir CLIENT_ID y CLIENT_SECRET
- [ ] ⚙️ Configurar en .env
- [ ] 🔄 Reiniciar API
- [ ] 🧪 Hacer prueba de factura
- [ ] ✅ Verificar integración completa

---

## 🚨 **Si tienes problemas:**

### **Errores comunes:**
1. **"Empresa no registrada"** → Completar registro ATV primero
2. **"Certificado no válido"** → Ya tienes esto resuelto ✅
3. **"Datos incompletos"** → Verificar representante legal
4. **"Demora en respuesta"** → Llamar por teléfono para acelerar

### **Datos de respaldo:**
- Certificado: **310277607903.p12** ✅
- Empresa: **SIMPLEXITY CONSULTING LIMITADA**
- Cédula: **3-102-776079**
- Sistema: **API REST con FastAPI**

---

## 📱 **Script de Llamada**

**Para cuando llames por teléfono:**

```
"Buenos días, habla [tu nombre] de SIMPLEXITY CONSULTING LIMITADA.

Nuestra cédula jurídica es 3-102-776079.

Necesito obtener credenciales CLIENT_ID y CLIENT_SECRET para 
integrar nuestro sistema de facturación electrónica con el 
API de Hacienda.

Ya tenemos configurado nuestro certificado digital 
(número 310277607903) y el sistema está funcionando.

Solo nos faltan las credenciales para poder enviar facturas 
automáticamente al ambiente SANDBOX.

¿Podrían ayudarme con el proceso o darme el procedimiento 
exacto a seguir?"
```

---

**🎯 ¿Empezamos con el registro en el portal o prefieres que te ayude a llamar directamente?**