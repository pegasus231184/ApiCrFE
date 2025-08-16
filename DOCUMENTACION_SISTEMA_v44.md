# API de Facturación Electrónica Costa Rica v4.4

## Descripción General

Sistema completo de facturación electrónica desarrollado con FastAPI que cumple con la normativa v4.4 del Ministerio de Hacienda de Costa Rica. El sistema permite generar, validar, firmar digitalmente y enviar documentos electrónicos oficiales.

## Características Principales

- ✅ **Cumplimiento total con normativa v4.4** del Ministerio de Hacienda
- ✅ **5 tipos de documentos electrónicos** soportados (Facturas, Notas de Crédito, Notas de Débito, Tiquetes, Facturas de Exportación)
- ✅ **Generación XML oficial** siguiendo formato exacto de Hacienda
- ✅ **Validación XSD** contra esquemas oficiales
- ✅ **Firma digital PKCS#12** con certificados oficiales
- ✅ **Integración completa con API de Hacienda** (sandbox y producción)
- ✅ **Generación de PDFs profesionales** con códigos QR
- ✅ **Envío automático por email** con AWS SES
- ✅ **Arquitectura dockerizada** con PostgreSQL y Redis
- ✅ **API RESTful** completamente documentada

## Arquitectura del Sistema

### Tecnologías Utilizadas

- **Backend**: FastAPI (Python 3.11)
- **Base de datos**: PostgreSQL 14
- **Cache**: Redis 7
- **Servidor web**: Nginx
- **Contenedores**: Docker & Docker Compose
- **Validación XML**: lxml con esquemas XSD oficiales
- **Firma digital**: cryptography + xmlsec
- **PDF**: ReportLab con códigos QR
- **Email**: Amazon SES
- **Autenticación Hacienda**: OAuth 2.0

### Estructura de Directorios

```
ApiCrFE/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── facturas.py          # Endpoints v4.3 (legacy)
│   │   ├── facturas_v44.py      # Endpoints v4.4 oficiales
│   │   ├── documentos.py        # Gestión de documentos
│   │   ├── emails.py            # Servicios de correo
│   │   └── utils.py             # Utilidades
│   ├── core/
│   │   └── config.py            # Configuración central
│   ├── schemas/
│   │   ├── factura.py           # Esquemas v4.3 (legacy)
│   │   └── factura_v44.py       # Esquemas v4.4 oficiales
│   └── services/
│       ├── xml_generator_v44.py     # Generador XML oficial v4.4
│       ├── xsd_validator.py         # Validador XSD oficial
│       ├── pdf_generator_official.py # Generador PDF profesional
│       ├── email_service.py         # Servicio de correos AWS SES
│       ├── xml_signer_simple.py     # Firmador digital
│       └── hacienda_client.py       # Cliente API Hacienda
├── certificados/
│   └── 310277607903.p12        # Certificado oficial Hacienda
├── Referencias/
│   ├── FacturaElectronicaV4.4.xsd   # Esquema oficial
│   └── 003101460479-FE-*.xml        # Ejemplos oficiales
├── docker-compose.yml          # Orquestación de contenedores
├── Dockerfile                  # Imagen de la aplicación
├── requirements.txt           # Dependencias Python
└── .env                      # Variables de entorno
```

## Componentes Principales v4.4

### 1. Generador XML v4.4 (`xml_generator_v44.py`)

**Características:**
- Formato compacto sin espacios en blanco (como documentos oficiales)
- Cumplimiento estricto con XSD de Hacienda
- Soporte completo para todos los campos v4.4
- Manejo correcto de códigos CABYS de 13 dígitos
- Precisión decimal de 5 dígitos para valores monetarios
- Inclusión obligatoria del campo `ProveedorSistemas`

**Uso:**
```python
from app.services.xml_generator_v44 import xml_generator_v44

xml_content = xml_generator_v44.generar_xml_factura(datos_factura)
```

### 2. Validador XSD (`xsd_validator.py`)

**Características:**
- Validación contra esquemas oficiales XSD de Hacienda
- Reporte detallado de errores de validación
- Soporte para múltiples tipos de documentos
- Carga automática de esquemas desde `Referencias/`

**Uso:**
```python
from app.services.xsd_validator import xsd_validator

resultado = xsd_validator.validate_and_report(xml_content)
if not resultado['valido']:
    print(f"Errores: {resultado['errores']}")
```

### 3. Generador PDF Oficial (`pdf_generator_official.py`)

**Características:**
- Diseño profesional matching facturas comerciales
- Códigos QR con clave del documento
- Logos de empresa y headers oficiales
- Tablas detalladas de productos/servicios
- Resumen financiero completo
- Cumplimiento con formato visual estándar

**Uso:**
```python
from app.services.pdf_generator_official import pdf_generator_official

pdf_bytes = pdf_generator_official.generar_pdf_factura(xml_content)
```

### 4. Esquemas Pydantic v4.4 (`factura_v44.py`)

**Modelos principales:**
- `FacturaElectronicaV44`: Modelo completo de factura
- `EmisorV44` / `ReceptorV44`: Información de emisor y receptor
- `LineaDetalle`: Líneas de detalle con validación CABYS
- `ResumenFactura`: Totales y cálculos financieros
- `InformacionReferencia`: Referencias a otros documentos

**Validaciones incluidas:**
- Códigos CABYS exactamente 13 dígitos
- Formatos de identificación válidos
- Rangos de valores monetarios
- Campos obligatorios según normativa

### 5. Endpoints API v4.4 (`facturas_v44.py`)

**Endpoints disponibles:**

#### `POST /api/v1/facturas-v44/`
Crear factura electrónica v4.4 completa.

**Parámetros:**
- `factura_data`: Datos de la factura (FacturaCreateV44)
- `firmar`: Bool - Firmar digitalmente (default: true)
- `enviar_hacienda`: Bool - Enviar a Hacienda (default: true)
- `enviar_email`: Bool - Enviar por correo (default: true)

**Respuesta:**
```json
{
  "clave": "50614112024010146047900100001000000048714414873",
  "numero_consecutivo": "00100001000000004871",
  "fecha_emision": "2024-11-14T10:30:00",
  "estado": "enviando",
  "xml_firmado": "<?xml version=\"1.0\"...",
  "email_enviado": true,
  "message_id_email": "0000014a-f4d6-4f39-8bb7-example"
}
```

#### `POST /api/v1/facturas-v44/notas-credito`
Crear nota de crédito v4.4.

#### `GET /api/v1/facturas-v44/validar-xsd`
Verificar configuración del validador XSD.

## Configuración y Despliegue

### Variables de Entorno (`.env`)

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379

# Hacienda API
HACIENDA_BASE_URL=https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/
HACIENDA_TOKEN_URL=https://idp.comprobanteselectronicos.go.cr/auth/realms/cr-dte/protocol/openid-connect/token
HACIENDA_CLIENT_ID=your_client_id
HACIENDA_CLIENT_SECRET=your_secret
HACIENDA_USERNAME=your_username
HACIENDA_PASSWORD=your_password
HACIENDA_SANDBOX=true

# Certificado digital
CERTIFICATE_PATH=/app/certificados/310277607903.p12
CERTIFICATE_PASSWORD=your_cert_password

# Amazon SES
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@yourdomain.com
SES_FROM_NAME=API Facturacion Electronica CR

# Sistema
PROVEEDOR_SISTEMAS=310277607903
```

### Despliegue con Docker

```bash
# Clonar repositorio
git clone https://github.com/yourusername/ApiCrFE.git
cd ApiCrFE

# Configurar variables de entorno
cp .env.example .env
# Editar .env con sus credenciales

# Levantar servicios
docker-compose up -d

# Verificar logs
docker-compose logs -f api
```

### Acceso a la Documentación

- **API Docs (Swagger)**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## Flujo de Procesamiento v4.4

### 1. Creación de Documento

```mermaid
graph TD
    A[Datos de entrada] --> B[Validación Pydantic]
    B --> C[Obtener consecutivo de Hacienda]
    C --> D[Generar clave única]
    D --> E[Crear XML v4.4]
    E --> F[Validar contra XSD]
    F --> G[Firmar digitalmente]
    G --> H[Generar PDF]
    H --> I[Enviar a Hacienda]
    I --> J[Enviar por email]
    J --> K[Respuesta API]
```

### 2. Validaciones Implementadas

- **Estructura XML**: Validación contra XSD oficial
- **Códigos CABYS**: 13 dígitos exactos
- **Identificaciones**: Formato y dígito verificador
- **Montos**: Precisión decimal y rangos válidos
- **Fechas**: Formato ISO y validez
- **Firmas digitales**: Certificado válido y estructura correcta

### 3. Integración con Hacienda

- **Autenticación**: OAuth 2.0 con refresh tokens
- **Envío**: API REST con XML firmado
- **Consultas**: Estado de documentos y respuestas
- **Sandbox**: Entorno de pruebas completo

## Casos de Uso

### Ejemplo 1: Factura Electrónica Simple

```python
import requests

factura_data = {
    "codigo_actividad_emisor": "722010",
    "codigo_actividad_receptor": "722010", 
    "emisor": {
        "identificacion_tipo": "02",
        "identificacion_numero": "3101460479",
        "nombre": "EMPRESA EJEMPLO SA",
        "telefono": "22334455",
        "correo_electronico": "empresa@ejemplo.com"
    },
    "receptor": {
        "identificacion_tipo": "01", 
        "identificacion_numero": "123456789",
        "nombre": "CLIENTE EJEMPLO",
        "correo_electronico": "cliente@ejemplo.com"
    },
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [{
        "numero_linea": 1,
        "codigo_cabys": "1234567890123",
        "detalle": "Servicio de ejemplo",
        "unidad_medida": "Sp",
        "cantidad": 1.00000,
        "precio_unitario": 10000.00000,
        "total_linea": 10000.00000
    }],
    "resumen_factura": {
        "total_servicios": 10000.00000,
        "total_gravado": 10000.00000,
        "total_impuestos": 1300.00000,
        "total_comprobante": 11300.00000
    }
}

response = requests.post(
    "http://localhost:8001/api/v1/facturas-v44/",
    json=factura_data
)

print(response.json())
```

### Ejemplo 2: Nota de Crédito

```python
nota_data = {
    # ... datos similares a factura
}

response = requests.post(
    "http://localhost:8001/api/v1/facturas-v44/notas-credito",
    json=nota_data,
    params={
        "factura_referencia": "50614112024010146047900100001000000048714414873",
        "motivo": "Error en facturación"
    }
)
```

## Monitoreo y Logs

### Logs de Aplicación

```bash
# Ver logs en tiempo real
docker-compose logs -f api

# Logs específicos
docker-compose logs api | grep "ERROR"
docker-compose logs api | grep "XML generado"
docker-compose logs api | grep "Email enviado"
```

### Métricas Importantes

- **Documentos generados por día**
- **Tasa de éxito en envíos a Hacienda**
- **Emails enviados exitosamente**
- **Errores de validación XSD**
- **Tiempo de respuesta promedio**

## Solución de Problemas

### Problemas Comunes

**1. Error de validación XSD**
```
Solución: Verificar que el XML sigue exactamente el formato oficial
- Revisar códigos CABYS (13 dígitos)
- Verificar estructura de elementos
- Validar tipos de datos y rangos
```

**2. Error de firma digital**
```
Solución: Verificar certificado PKCS#12
- Contraseña correcta
- Certificado no vencido
- Permisos de archivo correctos
```

**3. Error en envío de email**
```
Solución: Verificar configuración AWS SES
- Credenciales correctas
- Región configurada
- Email verificado en SES
```

**4. Error de conexión con Hacienda**
```
Solución: Verificar credenciales OAuth
- Client ID y Secret correctos
- Usuario y contraseña válidos
- URL de sandbox/producción correcta
```

### Comandos de Diagnóstico

```bash
# Verificar estado de contenedores
docker-compose ps

# Verificar conectividad con Hacienda
curl -X GET "http://localhost:8001/api/v1/utils/test-hacienda-connection"

# Verificar configuración XSD
curl -X GET "http://localhost:8001/api/v1/facturas-v44/validar-xsd"

# Verificar configuración de email
curl -X GET "http://localhost:8001/api/v1/emails/verificar-configuracion"
```

## Migración de v4.3 a v4.4

### Principales Diferencias

1. **Campo ProveedorSistemas**: Ahora obligatorio
2. **Códigos CABYS**: Exactamente 13 dígitos
3. **Precisión decimal**: 5 dígitos para montos
4. **Estructura XML**: Formato compacto sin espacios
5. **Validación XSD**: Más estricta

### Pasos de Migración

1. Actualizar esquemas de datos
2. Modificar validaciones de códigos CABYS
3. Ajustar generación XML al formato compacto
4. Implementar validación XSD v4.4
5. Actualizar endpoints para usar v4.4
6. Probar con documentos oficiales de referencia

## Seguridad

### Medidas Implementadas

- **Validación de entrada**: Pydantic schemas
- **Sanitización XML**: Prevención de inyección
- **Certificados seguros**: Almacenamiento protegido
- **Comunicación HTTPS**: TLS para API de Hacienda
- **Variables de entorno**: Credenciales no hardcodeadas
- **Contenedores**: Aislamiento de servicios

### Buenas Prácticas

- Rotar credenciales regularmente
- Monitorear intentos de acceso
- Mantener logs de auditoría
- Actualizar dependencias de seguridad
- Realizar backups de certificados

## Contacto y Soporte

- **Desarrollador**: Allan Martínez
- **Email**: allan.martinez@simplexityla.com
- **Repositorio**: https://github.com/yourusername/ApiCrFE
- **Documentación Hacienda**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/

---

## Historial de Versiones

### v4.4.0 (2024-11-14)
- ✅ Implementación completa de normativa v4.4
- ✅ Generador XML oficial con formato exacto
- ✅ Validación XSD contra esquemas oficiales
- ✅ Generador PDF profesional con QR codes
- ✅ Integración completa con AWS SES
- ✅ 5 tipos de documentos electrónicos
- ✅ Arquitectura dockerizada completa

### v4.3.0 (2024-10-01)
- Implementación inicial con normativa v4.3
- Integración básica con API de Hacienda
- Generación XML y firma digital
- Documentación base

---

*Documento generado automáticamente por el Sistema de Facturación Electrónica CR v4.4*