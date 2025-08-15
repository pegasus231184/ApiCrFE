# 📮 Manual de Postman - API Facturación CR

## 🚀 Configuración Inicial

### 1. Importar Colección
1. Abrir Postman
2. Ir a `File` > `Import`
3. Crear nueva colección llamada "API Facturación CR"
4. Configurar variable de entorno

### 2. Variables de Entorno
Crear un Environment con estas variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8001` | URL base del API |
| `api_version` | `v1` | Versión del API |
| `clave_ejemplo` | `50624112024123456789012345678901234567890123456789` | Clave de prueba |

## 📋 Colección de Requests

### 🏠 1. Health & Info

#### Health Check
```
GET {{base_url}}/health
```

#### API Info
```
GET {{base_url}}/
```

### 📄 2. Crear Documentos

#### 2.1 Crear Factura Electrónica
```
POST {{base_url}}/api/{{api_version}}/facturas
Content-Type: application/json

{
  "emisor": {
    "nombre": "{{$randomCompanyName}}",
    "identificacion_tipo": "02",
    "identificacion_numero": "3101234567",
    "nombre_comercial": "TechCorp CR",
    "ubicacion": {
      "provincia": "1",
      "canton": "01",
      "distrito": "01",
      "barrio": "Centro",
      "otras_senas": "Edificio Central, Oficina 301"
    },
    "telefono": {
      "codigo_pais": "506",
      "numero": "{{$randomPhoneNumber}}"
    },
    "correo_electronico": "{{$randomEmail}}"
  },
  "receptor": {
    "nombre": "{{$randomFullName}}",
    "identificacion_tipo": "01",
    "identificacion_numero": "123456789",
    "ubicacion": {
      "provincia": "2",
      "canton": "03",
      "distrito": "02",
      "otras_senas": "Casa #25, portón azul"
    },
    "correo_electronico": "{{$randomEmail}}"
  },
  "condicion_venta": "01",
  "medio_pago": ["01"],
  "detalles_servicio": [
    {
      "numero_linea": 1,
      "codigo": "PROD001",
      "cantidad": {{$randomInt}},
      "unidad_medida": "Unid",
      "detalle": "{{$randomProductName}}",
      "precio_unitario": 50000,
      "monto_total": 100000,
      "subtotal": 100000,
      "impuestos": [
        {
          "codigo": "01",
          "codigo_tarifa": "08",
          "tarifa": 13.00,
          "monto": 13000
        }
      ],
      "monto_total_linea": 113000
    }
  ],
  "resumen_factura": {
    "codigo_tipo_moneda": "CRC",
    "total_mercaderias_gravadas": 100000,
    "total_gravado": 100000,
    "total_venta": 100000,
    "total_venta_neta": 100000,
    "total_impuesto": 13000,
    "total_comprobante": 113000
  },
  "codigo_actividad": "620200"
}
```

**Tests (Tab Tests)**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has clave", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('clave');
    
    // Guardar clave para otros requests
    pm.environment.set("ultima_clave", jsonData.clave);
});

pm.test("Clave has correct length", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.clave).to.have.lengthOf(50);
});

pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

#### 2.2 Crear Tiquete Electrónico
```
POST {{base_url}}/api/{{api_version}}/facturas/tiquetes
Content-Type: application/json

{
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
      "detalle": "{{$randomProductName}}",
      "precio_unitario": 1500,
      "monto_total": 4500,
      "subtotal": 4500,
      "monto_total_linea": 5085
    }
  ],
  "resumen_factura": {
    "codigo_tipo_moneda": "CRC",
    "total_venta": 4500,
    "total_venta_neta": 4500,
    "total_impuesto": 585,
    "total_comprobante": 5085
  },
  "codigo_actividad": "471101"
}
```

#### 2.3 Crear Nota de Crédito
```
POST {{base_url}}/api/{{api_version}}/facturas/notas-credito
Content-Type: application/json

{
  "nota_data": {
    "emisor": {
      "nombre": "{{$randomCompanyName}}",
      "identificacion_tipo": "02",
      "identificacion_numero": "3101234567",
      "ubicacion": {
        "provincia": "1",
        "canton": "01",
        "distrito": "01"
      },
      "correo_electronico": "{{$randomEmail}}"
    },
    "receptor": {
      "nombre": "{{$randomFullName}}",
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
        "detalle": "Devolución por defecto",
        "precio_unitario": 50000,
        "monto_total": 50000,
        "subtotal": 50000,
        "monto_total_linea": 56500
      }
    ],
    "resumen_factura": {
      "codigo_tipo_moneda": "CRC",
      "total_venta": 50000,
      "total_venta_neta": 50000,
      "total_impuesto": 6500,
      "total_comprobante": 56500
    },
    "codigo_actividad": "620200"
  },
  "factura_referencia": "{{ultima_clave}}",
  "motivo": "Producto defectuoso - Autorización #DEV-{{$randomInt}}"
}
```

### 📊 3. Consultas

#### 3.1 Consultar Documento por Clave
```
GET {{base_url}}/api/{{api_version}}/documentos/{{ultima_clave}}
```

**Tests**:
```javascript
pm.test("Document found", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('clave');
    pm.expect(jsonData.clave).to.eql(pm.environment.get("ultima_clave"));
});
```

#### 3.2 Listar Documentos
```
GET {{base_url}}/api/{{api_version}}/documentos
```

#### 3.3 Listar con Filtros
```
GET {{base_url}}/api/{{api_version}}/documentos?tipo_documento=01&limit=10&offset=0
```

#### 3.4 Reenviar Documento
```
POST {{base_url}}/api/{{api_version}}/documentos/{{ultima_clave}}/reenviar
```

### 🔧 4. Utilidades

#### 4.1 Obtener Esquemas
```
GET {{base_url}}/api/{{api_version}}/utils/esquemas
```

#### 4.2 Generar Consecutivo
```
GET {{base_url}}/api/{{api_version}}/facturas/consecutivos/01
```

**Tests**:
```javascript
pm.test("Consecutivo generated", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('consecutivo');
    pm.expect(jsonData.consecutivo).to.have.lengthOf(20);
    
    // Guardar para uso posterior
    pm.environment.set("ultimo_consecutivo", jsonData.consecutivo);
});
```

#### 4.3 Generar Clave
```
POST {{base_url}}/api/{{api_version}}/utils/generar-clave
Content-Type: application/json

{
  "cedula_emisor": "3101234567",
  "tipo_documento": "01",
  "fecha_emision": "{{$isoTimestamp}}"
}
```

#### 4.4 Info Certificado
```
GET {{base_url}}/api/{{api_version}}/utils/info-certificado
```

### 📄 5. Gestión de Archivos

#### 5.1 Firmar XML
```
POST {{base_url}}/api/{{api_version}}/utils/firmar
Content-Type: multipart/form-data

[Body > form-data]
Key: xml_file | Type: File | Value: [seleccionar archivo XML]
```

#### 5.2 Validar XML
```
POST {{base_url}}/api/{{api_version}}/utils/validar
Content-Type: multipart/form-data

[Body > form-data]
Key: xml_file | Type: File | Value: [seleccionar archivo XML]
Key: tipo_documento | Type: Text | Value: factura
```

#### 5.3 Verificar Firma
```
POST {{base_url}}/api/{{api_version}}/utils/verificar-firma
Content-Type: multipart/form-data

[Body > form-data]
Key: xml_file | Type: File | Value: [seleccionar archivo XML firmado]
```

## 🧪 Testing Automatizado

### Pre-request Scripts Útiles

#### Generar Datos Aleatorios
```javascript
// Generar identificación aleatoria
pm.environment.set("random_id", Math.floor(Math.random() * 999999999).toString().padStart(9, '0'));

// Generar cédula jurídica
pm.environment.set("random_juridica", "310" + Math.floor(Math.random() * 9999999).toString().padStart(7, '0'));

// Fecha actual ISO
pm.environment.set("current_date", new Date().toISOString().split('T')[0]);
```

#### Configurar Headers Globales
```javascript
pm.request.headers.add({
    key: 'User-Agent',
    value: 'Postman-API-Test/1.0'
});
```

### Tests Globales

#### Test Suite para Validaciones Comunes
```javascript
// Test común para todos los endpoints
pm.test("Content-Type header is present", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(3000);
});

// Validar estructura de error
if (pm.response.code >= 400) {
    pm.test("Error response has detail", function () {
        var jsonData = pm.response.json();
        pm.expect(jsonData).to.have.property('detail');
    });
}
```

## 🔄 Workflows de Testing

### Workflow 1: Ciclo Completo de Facturación
1. **Obtener Consecutivo** → `GET /consecutivos/01`
2. **Crear Factura** → `POST /facturas`
3. **Consultar Estado** → `GET /documentos/{clave}`
4. **Generar PDF** → `GET /documentos/{clave}/pdf`

### Workflow 2: Proceso de Devolución
1. **Crear Factura Original** → `POST /facturas`
2. **Crear Nota de Crédito** → `POST /notas-credito`
3. **Verificar Ambos Documentos** → `GET /documentos`

### Workflow 3: Validación de XML
1. **Generar XML** → `POST /facturas`
2. **Descargar XML** → `GET /documentos/{clave}/xml`
3. **Validar XML** → `POST /utils/validar`
4. **Verificar Firma** → `POST /utils/verificar-firma`

## 📊 Collection Runner

### Configurar Runner
1. Ir a `Collections` > `Run collection`
2. Seleccionar Environment
3. Configurar:
   - **Iterations**: 5
   - **Delay**: 1000ms
   - **Data**: Usar CSV con datos de prueba

### Datos CSV de Ejemplo
```csv
empresa_nombre,empresa_cedula,cliente_nombre,cliente_cedula,producto,precio
"Tech Solutions SA","3101111111","Juan Pérez","123456789","Laptop",500000
"Consultores CR","3102222222","María González","987654321","Servicio",75000
"Digital Corp","3103333333","Carlos Rodríguez","456789123","Software",120000
```

## 📈 Monitoring & Newman

### Exportar Colección
1. `Collections` > `...` > `Export`
2. Seleccionar `Collection v2.1`
3. Guardar como `facturacion-cr.postman_collection.json`

### Ejecutar con Newman
```bash
# Instalar Newman
npm install -g newman

# Ejecutar colección
newman run facturacion-cr.postman_collection.json \
  --environment facturacion-environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

# Con datos CSV
newman run facturacion-cr.postman_collection.json \
  --environment facturacion-environment.json \
  --data test-data.csv \
  --iteration-count 10
```

## 🔍 Debugging

### Console Logging
```javascript
// En Tests o Pre-request Scripts
console.log("Request URL:", pm.request.url.toString());
console.log("Response Body:", pm.response.json());
console.log("Environment Variable:", pm.environment.get("ultima_clave"));
```

### Visualización de Respuestas
```javascript
// En Tests
pm.test("Visualize response", function () {
    var template = `
    <h2>Respuesta del Documento</h2>
    <table>
        <tr><td><strong>Clave:</strong></td><td>{{clave}}</td></tr>
        <tr><td><strong>Estado:</strong></td><td>{{estado}}</td></tr>
        <tr><td><strong>Fecha:</strong></td><td>{{fecha_emision}}</td></tr>
        <tr><td><strong>Total:</strong></td><td>{{total}}</td></tr>
    </table>
    `;
    
    var jsonData = pm.response.json();
    pm.visualizer.set(template, jsonData);
});
```

## ⚡ Tips y Trucos

### 1. Variables Dinámicas
```javascript
// Timestamp actual
{{$timestamp}}

// GUID
{{$guid}}

// Número aleatorio
{{$randomInt}}

// Datos fake
{{$randomCompanyName}}
{{$randomEmail}}
{{$randomPhoneNumber}}
```

### 2. Assertions Avanzadas
```javascript
// Validar schema JSON
var schema = {
    "type": "object",
    "properties": {
        "clave": {"type": "string", "minLength": 50, "maxLength": 50},
        "estado": {"type": "string"},
        "fecha_emision": {"type": "string"}
    },
    "required": ["clave", "estado"]
};

pm.test("Schema is valid", function () {
    pm.response.to.have.jsonSchema(schema);
});
```

### 3. Cleanup después de Tests
```javascript
// En Tests de último request del folder
pm.test("Cleanup test data", function () {
    pm.environment.unset("ultima_clave");
    pm.environment.unset("ultimo_consecutivo");
});
```

---

**📮 Tip**: Usar Postman Interceptor para debuggear requests desde el navegador y sincronizar con la colección de Postman.