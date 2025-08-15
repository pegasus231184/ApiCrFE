# 📖 Guía de Uso - API Facturación Electrónica Costa Rica v4.4

## 🚀 Inicio Rápido

### 1. Acceso al API
- **URL Base**: http://localhost:8001
- **Documentación Swagger**: http://localhost:8001/docs
- **Documentación ReDoc**: http://localhost:8001/redoc

### 2. Health Check
```bash
curl http://localhost:8001/health
# Respuesta: {"status":"healthy"}
```

## 📋 Endpoints Principales

### 🧾 Creación de Documentos

#### Crear Factura Electrónica
**Endpoint**: `POST /api/v1/facturas`

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8001/api/v1/facturas" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {
      "nombre": "Empresa Demo S.A.",
      "identificacion_tipo": "02",
      "identificacion_numero": "3101234567",
      "ubicacion": {
        "provincia": "1",
        "canton": "01",
        "distrito": "01"
      },
      "correo_electronico": "facturacion@empresa.com"
    },
    "receptor": {
      "nombre": "Cliente Ejemplo",
      "identificacion_tipo": "01",
      "identificacion_numero": "123456789"
    },
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [
      {
        "numero_linea": 1,
        "cantidad": 2,
        "unidad_medida": "Unid",
        "detalle": "Producto de ejemplo",
        "precio_unitario": 5000,
        "monto_total": 10000,
        "subtotal": 10000,
        "monto_total_linea": 11300
      }
    ],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_venta": 10000,
      "total_venta_neta": 10000,
      "total_impuesto": 1300,
      "total_comprobante": 11300
    },
    "codigo_actividad": "123456"
  }'
```

**Respuesta exitosa**:
```json
{
  "clave": "50624112024123456789012345678901234567890123456789",
  "numero_consecutivo": "00100001010000000001000001",
  "fecha_emision": "2024-11-24T10:30:00",
  "estado": "enviando",
  "xml_firmado": "<?xml version='1.0' encoding='UTF-8'?>..."
}
```

#### Crear Nota de Crédito
**Endpoint**: `POST /api/v1/facturas/notas-credito`

```bash
curl -X POST "http://localhost:8001/api/v1/facturas/notas-credito" \
  -H "Content-Type: application/json" \
  -d '{
    "nota_data": {
      "emisor": {...},
      "receptor": {...},
      "condicion_venta": "01",
      "medio_pago": ["01"],
      "detalles_servicio": [...],
      "resumen_factura": {...},
      "codigo_actividad": "123456"
    },
    "factura_referencia": "50624112024123456789012345678901234567890123456789",
    "motivo": "Error en facturación original"
  }'
```

#### Crear Tiquete Electrónico
**Endpoint**: `POST /api/v1/facturas/tiquetes`

```bash
curl -X POST "http://localhost:8001/api/v1/facturas/tiquetes" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {...},
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [...],
    "resumen_factura": {...},
    "codigo_actividad": "123456"
  }'
```

### 📊 Consulta de Documentos

#### Consultar Estado de Documento
**Endpoint**: `GET /api/v1/documentos/{clave}`

```bash
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789"
```

**Respuesta**:
```json
{
  "clave": "50624112024123456789012345678901234567890123456789",
  "estado": "aceptado",
  "fecha_procesamiento": "2024-11-24T10:35:00",
  "mensaje_hacienda": "Documento procesado correctamente",
  "respuesta_xml": "<?xml version='1.0'...>"
}
```

#### Listar Documentos
**Endpoint**: `GET /api/v1/documentos`

```bash
# Listar todos los documentos
curl "http://localhost:8001/api/v1/documentos"

# Con filtros
curl "http://localhost:8001/api/v1/documentos?fecha_inicio=2024-01-01&tipo_documento=01&limit=10"
```

### 🔧 Utilidades

#### Obtener Esquemas XSD Disponibles
```bash
curl "http://localhost:8001/api/v1/utils/esquemas"
```

**Respuesta**:
```json
{
  "version": "4.4",
  "esquemas_disponibles": {
    "factura": "FacturaElectronicaV44.xsd",
    "nota_credito": "NotaCreditoElectronicaV44.xsd",
    "nota_debito": "NotaDebitoElectronicaV44.xsd",
    "tiquete": "TiqueteElectronicoV44.xsd",
    "factura_exportacion": "FacturaElectronicaExportacionV44.xsd"
  },
  "url_oficial": "https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/"
}
```

#### Generar Clave Única
```bash
curl -X POST "http://localhost:8001/api/v1/utils/generar-clave" \
  -H "Content-Type: application/json" \
  -d '{
    "cedula_emisor": "3101234567",
    "tipo_documento": "01",
    "fecha_emision": "2024-11-24"
  }'
```

#### Validar XML contra XSD
```bash
curl -X POST "http://localhost:8001/api/v1/utils/validar" \
  -F "xml_file=@documento.xml" \
  -F "tipo_documento=factura"
```

#### Firmar XML
```bash
curl -X POST "http://localhost:8001/api/v1/utils/firmar" \
  -F "xml_file=@documento.xml"
```

#### Obtener Consecutivo
```bash
# Para factura (tipo 01)
curl "http://localhost:8001/api/v1/facturas/consecutivos/01"

# Para nota de crédito (tipo 03)  
curl "http://localhost:8001/api/v1/facturas/consecutivos/03"
```

## 🔧 Códigos de Referencia

### Tipos de Documento
| Código | Tipo |
|--------|------|
| 01 | Factura Electrónica |
| 02 | Nota de Débito |
| 03 | Nota de Crédito |
| 04 | Tiquete Electrónico |
| 05 | Factura de Exportación |

### Tipos de Identificación
| Código | Tipo |
|--------|------|
| 01 | Cédula Física |
| 02 | Cédula Jurídica |
| 03 | DIMEX |
| 04 | NITE |

### Condiciones de Venta
| Código | Descripción |
|--------|-------------|
| 01 | Contado |
| 02 | Crédito |
| 03 | Consignación |
| 04 | Apartado |
| 05 | Arrendamiento con opción de compra |
| 06 | Arrendamiento en función financiera |
| 99 | Otros |

### Medios de Pago
| Código | Descripción |
|--------|-------------|
| 01 | Efectivo |
| 02 | Tarjeta |
| 03 | Cheque |
| 04 | Transferencia |
| 05 | Recaudado por terceros |
| 99 | Otros |

## 📱 Uso desde Swagger UI

### 1. Acceder a Swagger
Navegar a: http://localhost:8001/docs

### 2. Probar Endpoints
1. Hacer clic en cualquier endpoint
2. Hacer clic en "Try it out"
3. Llenar los parámetros requeridos
4. Hacer clic en "Execute"
5. Ver la respuesta

### 3. Ver Modelos de Datos
- Scroll hacia abajo en Swagger
- Ver sección "Schemas"
- Expandir cualquier modelo para ver estructura

## ⚠️ Manejo de Errores

### Errores Comunes

#### Error 400 - Bad Request
```json
{
  "detail": "La clave debe tener exactamente 50 caracteres"
}
```

#### Error 404 - Not Found
```json
{
  "detail": "Documento no encontrado"
}
```

#### Error 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "emisor", "nombre"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Error 500 - Internal Server Error
```json
{
  "detail": "Error al procesar el documento: mensaje específico del error"
}
```

## 🎯 Casos de Uso Comunes

### Caso 1: Facturación Básica
1. Generar consecutivo: `GET /api/v1/facturas/consecutivos/01`
2. Crear factura: `POST /api/v1/facturas`
3. Consultar estado: `GET /api/v1/documentos/{clave}`

### Caso 2: Nota de Crédito por Error
1. Identificar factura original
2. Crear nota de crédito: `POST /api/v1/facturas/notas-credito`
3. Verificar aceptación en Hacienda

### Caso 3: Validación de XML Externo
1. Validar estructura: `POST /api/v1/utils/validar`
2. Firmar documento: `POST /api/v1/utils/firmar`
3. Enviar a Hacienda manualmente

## 🔐 Configuración Avanzada

### Variables de Entorno
```bash
# Modo sandbox (para pruebas)
HACIENDA_SANDBOX=true

# Credenciales de Hacienda
HACIENDA_CLIENT_ID=tu_client_id
HACIENDA_CLIENT_SECRET=tu_client_secret

# Certificado digital
CERTIFICATE_PATH=/ruta/al/certificado.p12
CERTIFICATE_PASSWORD=password_certificado
```

### Modo Producción
1. Cambiar `HACIENDA_SANDBOX=false`
2. Configurar certificado digital real
3. Usar credenciales de producción
4. Activar HTTPS en nginx

## 📞 Troubleshooting

### Problema: Contenedor API no inicia
```bash
# Ver logs
docker-compose logs api

# Reiniciar
docker-compose restart api
```

### Problema: Error de conexión a base de datos
```bash
# Verificar PostgreSQL
docker-compose logs db

# Recrear volumen si es necesario
docker-compose down -v
docker-compose up -d
```

### Problema: Certificado no válido
- Verificar que el archivo .p12 existe
- Confirmar que la contraseña es correcta
- Revisar permisos del archivo

## 📈 Monitoreo

### Health Checks
```bash
# API
curl http://localhost:8001/health

# Base de datos (a través del API)
curl http://localhost:8001/api/v1/utils/info-certificado
```

### Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Solo API
docker-compose logs -f api

# Solo base de datos
docker-compose logs -f db
```

## 🔄 Actualizaciones

### Actualizar el código
```bash
# Bajar servicios
docker-compose down

# Reconstruir imagen
docker-compose build

# Levantar servicios
docker-compose up -d
```

### Backup de base de datos
```bash
# Crear backup
docker exec apicrfe-db-1 pg_dump -U facturacion_user facturacion_cr > backup.sql

# Restaurar backup
docker exec -i apicrfe-db-1 psql -U facturacion_user facturacion_cr < backup.sql
```

## 📚 Recursos Adicionales

- **Documentación oficial**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/
- **Esquemas XSD v4.4**: https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Swagger Editor**: https://editor.swagger.io/

---

**🇨🇷 API Facturación Electrónica Costa Rica v4.4** | **⚡ Powered by FastAPI** | **🐳 Dockerized**