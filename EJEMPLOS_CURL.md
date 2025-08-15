# 🔧 Ejemplos de Comandos cURL - API Facturación CR

## 🏠 Endpoints Básicos

### Health Check
```bash
curl http://localhost:8001/health
```

### Información del API
```bash
curl http://localhost:8001/
```

## 📋 Crear Documentos Electrónicos

### 1. Factura Electrónica Completa
```bash
curl -X POST "http://localhost:8001/api/v1/facturas" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {
      "nombre": "Tecnología Avanzada S.A.",
      "identificacion_tipo": "02",
      "identificacion_numero": "3101234567",
      "nombre_comercial": "TechCorp",
      "ubicacion": {
        "provincia": "1",
        "canton": "01",
        "distrito": "01",
        "barrio": "Centro",
        "otras_senas": "Edificio Central, Piso 3"
      },
      "telefono": {
        "codigo_pais": "506",
        "numero": "22345678"
      },
      "correo_electronico": "facturacion@techcorp.cr"
    },
    "receptor": {
      "nombre": "Juan Pérez González",
      "identificacion_tipo": "01",
      "identificacion_numero": "123456789",
      "ubicacion": {
        "provincia": "2",
        "canton": "03",
        "distrito": "02",
        "otras_senas": "Casa #25, portón azul"
      },
      "correo_electronico": "juan.perez@email.com"
    },
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [
      {
        "numero_linea": 1,
        "codigo": "PROD001",
        "cantidad": 2,
        "unidad_medida": "Unid",
        "detalle": "Laptop Dell Inspiron 15",
        "precio_unitario": 450000,
        "monto_total": 900000,
        "subtotal": 900000,
        "impuestos": [
          {
            "codigo": "01",
            "codigo_tarifa": "08",
            "tarifa": 13.00,
            "monto": 117000
          }
        ],
        "monto_total_linea": 1017000
      },
      {
        "numero_linea": 2,
        "codigo": "SERV001",
        "cantidad": 1,
        "unidad_medida": "Sp",
        "detalle": "Instalación y configuración de software",
        "precio_unitario": 50000,
        "monto_total": 50000,
        "subtotal": 50000,
        "impuestos": [
          {
            "codigo": "01",
            "codigo_tarifa": "08",
            "tarifa": 13.00,
            "monto": 6500
          }
        ],
        "monto_total_linea": 56500
      }
    ],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_mercaderias_gravadas": 900000,
      "total_servicios_gravados": 50000,
      "total_gravado": 950000,
      "total_venta": 950000,
      "total_venta_neta": 950000,
      "total_impuesto": 123500,
      "total_comprobante": 1073500
    },
    "codigo_actividad": "620200"
  }'
```

### 2. Tiquete Electrónico (Consumidor Final)
```bash
curl -X POST "http://localhost:8001/api/v1/facturas/tiquetes" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {
      "nombre": "Supermercado La Esquina",
      "identificacion_tipo": "02",
      "identificacion_numero": "3102987654",
      "ubicacion": {
        "provincia": "1",
        "canton": "01",
        "distrito": "03"
      },
      "correo_electronico": "ventas@laesquina.cr"
    },
    "condicion_venta": "01",
    "medio_pago": ["02"],
    "detalles_servicio": [
      {
        "numero_linea": 1,
        "cantidad": 3,
        "unidad_medida": "Unid",
        "detalle": "Coca Cola 600ml",
        "precio_unitario": 800,
        "monto_total": 2400,
        "subtotal": 2400,
        "monto_total_linea": 2712
      }
    ],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_venta": 2400,
      "total_venta_neta": 2400,
      "total_impuesto": 312,
      "total_comprobante": 2712
    },
    "codigo_actividad": "471101"
  }'
```

### 3. Nota de Crédito
```bash
curl -X POST "http://localhost:8001/api/v1/facturas/notas-credito" \
  -H "Content-Type: application/json" \
  -d '{
    "nota_data": {
      "emisor": {
        "nombre": "Tecnología Avanzada S.A.",
        "identificacion_tipo": "02",
        "identificacion_numero": "3101234567",
        "ubicacion": {
          "provincia": "1",
          "canton": "01",
          "distrito": "01"
        },
        "correo_electronico": "facturacion@techcorp.cr"
      },
      "receptor": {
        "nombre": "Juan Pérez González",
        "identificacion_tipo": "01",
        "identificacion_numero": "123456789"
      },
      "condicion_venta": "01",
      "medio_pago": ["01"],
      "detalles_servicio": [
        {
          "numero_linea": 1,
          "cantidad": 1,
          "unidad_medida": "Unid",
          "detalle": "Devolución producto defectuoso",
          "precio_unitario": 450000,
          "monto_total": 450000,
          "subtotal": 450000,
          "monto_total_linea": 508500
        }
      ],
      "resumen_factura": {
        "codigo_tipo_moneda": "CRC",
        "total_venta": 450000,
        "total_venta_neta": 450000,
        "total_impuesto": 58500,
        "total_comprobante": 508500
      },
      "codigo_actividad": "620200"
    },
    "factura_referencia": "50624112024123456789012345678901234567890123456789",
    "motivo": "Producto defectuoso, autorización de devolución #DEV-2024-001"
  }'
```

## 📊 Consultas y Reportes

### Consultar Estado de Documento
```bash
# Consultar documento específico
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789"
```

### Listar Documentos con Filtros
```bash
# Listar todos los documentos
curl "http://localhost:8001/api/v1/documentos"

# Con filtros de fecha
curl "http://localhost:8001/api/v1/documentos?fecha_inicio=2024-01-01&fecha_fin=2024-12-31"

# Por tipo de documento
curl "http://localhost:8001/api/v1/documentos?tipo_documento=01&limit=20"

# Por estado
curl "http://localhost:8001/api/v1/documentos?estado=aceptado&offset=0&limit=50"

# Filtros combinados
curl "http://localhost:8001/api/v1/documentos?fecha_inicio=2024-11-01&tipo_documento=01&estado=aceptado&limit=10"
```

### Reenviar Documento a Hacienda
```bash
curl -X POST "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789/reenviar"
```

### Anular Documento
```bash
curl -X DELETE "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "motivo": "Factura emitida por error, solicitud de anulación autorizada por cliente"
  }'
```

## 🔧 Utilidades

### Obtener Consecutivos
```bash
# Factura
curl "http://localhost:8001/api/v1/facturas/consecutivos/01"

# Nota de Débito
curl "http://localhost:8001/api/v1/facturas/consecutivos/02"

# Nota de Crédito
curl "http://localhost:8001/api/v1/facturas/consecutivos/03"

# Tiquete
curl "http://localhost:8001/api/v1/facturas/consecutivos/04"
```

### Generar Clave Única
```bash
# Generar clave para factura
curl -X POST "http://localhost:8001/api/v1/utils/generar-clave" \
  -H "Content-Type: application/json" \
  -d '{
    "cedula_emisor": "3101234567",
    "tipo_documento": "01",
    "fecha_emision": "2024-11-24"
  }'

# Generar clave para nota de crédito
curl -X POST "http://localhost:8001/api/v1/utils/generar-clave" \
  -H "Content-Type: application/json" \
  -d '{
    "cedula_emisor": "3101234567",
    "tipo_documento": "03"
  }'
```

### Validar XML
```bash
# Validar factura
curl -X POST "http://localhost:8001/api/v1/utils/validar" \
  -F "xml_file=@factura_ejemplo.xml" \
  -F "tipo_documento=factura"

# Validar nota de crédito
curl -X POST "http://localhost:8001/api/v1/utils/validar" \
  -F "xml_file=@nota_credito.xml" \
  -F "tipo_documento=nota_credito"
```

### Firmar XML
```bash
curl -X POST "http://localhost:8001/api/v1/utils/firmar" \
  -F "xml_file=@documento_sin_firmar.xml"
```

### Verificar Firma Digital
```bash
curl -X POST "http://localhost:8001/api/v1/utils/verificar-firma" \
  -F "xml_file=@documento_firmado.xml"
```

### Información del Certificado
```bash
curl "http://localhost:8001/api/v1/utils/info-certificado"
```

### Esquemas XSD Disponibles
```bash
curl "http://localhost:8001/api/v1/utils/esquemas"
```

## 📄 Descargas

### Obtener XML de Documento
```bash
# XML firmado
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789/xml?firmado=true"

# XML sin firmar
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789/xml?firmado=false"
```

### Generar PDF
```bash
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789/pdf"
```

## 🧪 Ejemplos de Prueba

### Script de Prueba Completo
```bash
#!/bin/bash

API_BASE="http://localhost:8001"

echo "🏥 Health Check..."
curl -s "$API_BASE/health" | jq

echo -e "\n📋 Listar esquemas disponibles..."
curl -s "$API_BASE/api/v1/utils/esquemas" | jq

echo -e "\n🎯 Generar consecutivo..."
CONSECUTIVO=$(curl -s "$API_BASE/api/v1/facturas/consecutivos/01" | jq -r '.consecutivo')
echo "Consecutivo generado: $CONSECUTIVO"

echo -e "\n📄 Crear factura de prueba..."
FACTURA_RESPONSE=$(curl -s -X POST "$API_BASE/api/v1/facturas" \
  -H "Content-Type: application/json" \
  -d '{
    "emisor": {
      "nombre": "Empresa Demo",
      "identificacion_tipo": "02",
      "identificacion_numero": "3101234567",
      "ubicacion": {"provincia": "1", "canton": "01", "distrito": "01"},
      "correo_electronico": "demo@empresa.cr"
    },
    "condicion_venta": "01",
    "medio_pago": ["01"],
    "detalles_servicio": [{
      "numero_linea": 1,
      "cantidad": 1,
      "unidad_medida": "Unid",
      "detalle": "Producto de prueba",
      "precio_unitario": 1000,
      "monto_total": 1000,
      "subtotal": 1000,
      "monto_total_linea": 1130
    }],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_venta": 1000,
      "total_venta_neta": 1000,
      "total_impuesto": 130,
      "total_comprobante": 1130
    },
    "codigo_actividad": "123456"
  }')

echo "$FACTURA_RESPONSE" | jq

CLAVE=$(echo "$FACTURA_RESPONSE" | jq -r '.clave')
echo -e "\n🔍 Consultar documento creado..."
curl -s "$API_BASE/api/v1/documentos/$CLAVE" | jq

echo -e "\n✅ Prueba completada!"
```

### Guardar en archivo y ejecutar
```bash
# Guardar script
cat > test_api.sh << 'EOF'
[contenido del script anterior]
EOF

# Dar permisos de ejecución
chmod +x test_api.sh

# Ejecutar
./test_api.sh
```

## 🔍 Debugging

### Ver Headers de Respuesta
```bash
curl -I "http://localhost:8001/health"
```

### Modo Verbose
```bash
curl -v "http://localhost:8001/api/v1/utils/esquemas"
```

### Guardar Respuesta en Archivo
```bash
curl "http://localhost:8001/api/v1/documentos/50624112024123456789012345678901234567890123456789" \
  -o documento_respuesta.json
```

### Timing de Requests
```bash
curl -w "@curl-format.txt" -s "http://localhost:8001/api/v1/facturas/consecutivos/01"

# Donde curl-format.txt contiene:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                      ----------\n
#           time_total:  %{time_total}\n
```

---

**💡 Tip**: Instalar `jq` para formatear respuestas JSON:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# Uso
curl "http://localhost:8001/api/v1/utils/esquemas" | jq
```