# 🧾 API Facturación Electrónica Costa Rica v4.4

API REST completa para generar, firmar y enviar documentos electrónicos según la normativa v4.4 del Ministerio de Hacienda de Costa Rica. Construida con **FastAPI** e incluye documentación **Swagger** automática.

## ⚠️ IMPORTANTE - SEGURIDAD

**NUNCA subas credenciales reales a Git!** Este repositorio incluye:
- `.env.example` - Plantilla de configuración (SIN credenciales reales)
- `.gitignore` - Excluye archivos sensibles
- `certificados/` - Carpeta excluida de Git

**Para usar en producción:**
1. Copia `.env.example` a `.env`
2. Obtén credenciales oficiales del Ministerio de Hacienda
3. Configura tu certificado digital (.p12)

## 🚀 Características

- ✅ **Generación de XML** según esquemas oficiales v4.4
- ✅ **Firma digital** de documentos con certificado .p12
- ✅ **Validación contra XSD** oficiales del Ministerio de Hacienda
- ✅ **Integración completa** con API de Hacienda (sandbox y producción)
- ✅ **Documentación Swagger** automática en `/docs`
- ✅ **Base de datos PostgreSQL** para persistencia
- ✅ **Redis** para caché y colas de procesamiento
- ✅ **Docker** para despliegue fácil
- ✅ **Endpoints REST** para todos los tipos de documento

## 📋 Tipos de Documento Soportados

| Tipo | Código | Endpoint |
|------|--------|----------|
| Factura Electrónica | 01 | `POST /api/v1/facturas` |
| Nota de Débito | 02 | `POST /api/v1/facturas/notas-debito` |
| Nota de Crédito | 03 | `POST /api/v1/facturas/notas-credito` |
| Tiquete Electrónico | 04 | `POST /api/v1/facturas/tiquetes` |

## 🛠️ Instalación

### Opción 1: Docker (Recomendado)

```bash
# Clonar repositorio
git clone <repo-url>
cd ApiCrFE

# Copiar variables de entorno
cp .env.example .env

# Editar configuración
nano .env

# Iniciar con Docker
docker-compose up -d
```

### Opción 2: Instalación Local

```bash
# Requisitos del sistema
# - Python 3.10+
# - PostgreSQL 14+
# - Redis 6+

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn main:app --reload
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/facturacion_cr
REDIS_URL=redis://localhost:6379

# API Ministerio de Hacienda
HACIENDA_CLIENT_ID=tu_client_id
HACIENDA_CLIENT_SECRET=tu_client_secret
HACIENDA_SANDBOX=true  # false para producción

# Certificado digital
CERTIFICATE_PATH=/ruta/al/certificado.p12
CERTIFICATE_PASSWORD=password_certificado
```

### Certificado Digital

1. Obtener certificado `.p12` del proveedor autorizado
2. Colocar en carpeta `certificados/`
3. Configurar ruta en `.env`

### Esquemas XSD

1. Descargar esquemas oficiales desde:
   ```
   https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/
   ```
2. Colocar archivos `.xsd` en `app/xsd/`

## 📖 Uso del API

### Swagger UI

Acceder a la documentación interactiva:
```
http://localhost:8000/docs
```

### Ejemplo: Crear Factura

```bash
curl -X POST \"http://localhost:8000/api/v1/facturas\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"emisor\": {
      \"nombre\": \"Empresa Ejemplo S.A.\",
      \"identificacion_tipo\": \"02\",
      \"identificacion_numero\": \"3101234567\",
      \"ubicacion\": {
        \"provincia\": \"1\",
        \"canton\": \"01\",
        \"distrito\": \"01\"
      },
      \"correo_electronico\": \"facturacion@empresa.com\"
    },
    \"receptor\": {
      \"nombre\": \"Cliente Final\",
      \"identificacion_tipo\": \"01\",
      \"identificacion_numero\": \"123456789\"
    },
    \"condicion_venta\": \"01\",
    \"medio_pago\": [\"01\"],
    \"detalles_servicio\": [
      {
        \"numero_linea\": 1,
        \"cantidad\": 1,
        \"unidad_medida\": \"Unid\",
        \"detalle\": \"Producto de ejemplo\",
        \"precio_unitario\": 10000,
        \"monto_total\": 10000,
        \"subtotal\": 10000,
        \"monto_total_linea\": 11300
      }
    ],
    \"resumen_factura\": {
      \"codigo_tipo_moneda\": \"CRC\",
      \"total_venta\": 10000,
      \"total_venta_neta\": 10000,
      \"total_impuesto\": 1300,
      \"total_comprobante\": 11300
    },
    \"codigo_actividad\": \"123456\"
  }'
```

### Respuesta

```json
{
  \"clave\": \"50624112024123456789012345678901234567890123456789\",
  \"numero_consecutivo\": \"00100001010000000001000001\",
  \"fecha_emision\": \"2024-11-24T10:30:00\",
  \"estado\": \"enviando\",
  \"xml_firmado\": \"<?xml version='1.0' encoding='UTF-8'?>...\"
}
```

## 🔍 Endpoints Principales

### Documentos

- `GET /api/v1/documentos/{clave}` - Consultar estado
- `GET /api/v1/documentos` - Listar documentos  
- `POST /api/v1/documentos/{clave}/reenviar` - Reenviar a Hacienda
- `DELETE /api/v1/documentos/{clave}` - Anular documento
- `GET /api/v1/documentos/{clave}/pdf` - Generar PDF
- `GET /api/v1/documentos/{clave}/xml` - Obtener XML

### Utilidades

- `POST /api/v1/utils/firmar` - Firmar XML manualmente
- `POST /api/v1/utils/validar` - Validar contra XSD
- `POST /api/v1/utils/verificar-firma` - Verificar firma digital
- `GET /api/v1/utils/info-certificado` - Info del certificado
- `POST /api/v1/utils/generar-clave` - Generar clave única

### Consecutivos

- `GET /api/v1/facturas/consecutivos/{tipo}` - Obtener próximo consecutivo

## 🏥 Monitoreo

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Ver logs del contenedor
docker-compose logs -f api

# Logs de base de datos
docker-compose logs -f db
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app

# Solo tests de integración
pytest -m integration
```

## 📁 Estructura del Proyecto

```
ApiCrFE/
├── app/
│   ├── api/v1/endpoints/     # Endpoints REST
│   ├── core/                 # Configuración
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Modelos Pydantic
│   ├── services/            # Lógica de negocio
│   ├── utils/               # Utilidades
│   └── xsd/                 # Esquemas XSD v4.4
├── alembic/                 # Migraciones DB
├── tests/                   # Pruebas
├── certificados/            # Certificados digitales
├── docker-compose.yml       # Orquestación Docker
├── Dockerfile              # Imagen de aplicación
├── requirements.txt        # Dependencias Python
└── README.md              # Esta documentación
```

## 🔐 Seguridad

- **HTTPS** obligatorio en producción
- **Certificados digitales** protegidos con password
- **Variables sensibles** en archivos `.env`
- **Validación** de entrada con Pydantic
- **Rate limiting** en endpoints públicos
- **Logs de auditoría** para todas las operaciones

## 🤝 Contribuir

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🆘 Soporte

### Documentación Oficial

- [Normativa Hacienda CR](https://www.hacienda.go.cr/ATV/ComprobanteElectronico/frmConsultaRecepcion.aspx)
- [Esquemas XSD v4.4](https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Troubleshooting

**Error: Certificado no válido**
```bash
# Verificar certificado
openssl pkcs12 -info -in certificado.p12
```

**Error: Conexión a Hacienda**
```bash
# Verificar conectividad
curl -I https://api.comprobanteselectronicos.go.cr
```

**Error: Base de datos**
```bash
# Recrear migraciones
alembic stamp head
alembic revision --autogenerate -m \"Initial migration\"
alembic upgrade head
```

### Contacto

- **Issues**: [GitHub Issues](https://github.com/pegasus231184/ApiCrFE/issues)
- **Email**: allan.martinez@simplexityla.com
- **LinkedIn**: [Perfil del desarrollador](https://github.com/pegasus231184/ApiCrFE)

---

**🇨🇷 Hecho en Costa Rica** | **⚡ Powered by FastAPI** | **📋 Normativa v4.4**