from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enum import Enum

class TipoMoneda(str, Enum):
    CRC = "CRC"
    USD = "USD"
    EUR = "EUR"

class TipoDocumento(str, Enum):
    FACTURA_ELECTRONICA = "01"
    NOTA_DEBITO = "02"
    NOTA_CREDITO = "03"
    TIQUETE_ELECTRONICO = "04"
    FACTURA_EXPORTACION = "05"

class Telefono(BaseModel):
    codigo_pais: str = Field(..., min_length=1, max_length=3)
    numero: str = Field(..., min_length=8, max_length=20)

class Ubicacion(BaseModel):
    provincia: str = Field(..., min_length=1, max_length=2)
    canton: str = Field(..., min_length=1, max_length=2)
    distrito: str = Field(..., min_length=1, max_length=2)
    barrio: Optional[str] = Field(None, max_length=100)
    otras_senas: Optional[str] = Field(None, max_length=300)

class Emisor(BaseModel):
    nombre: str = Field(..., max_length=100)
    identificacion_tipo: str = Field(..., min_length=2, max_length=2)
    identificacion_numero: str = Field(..., min_length=9, max_length=20)
    nombre_comercial: Optional[str] = Field(None, max_length=80)
    ubicacion: Ubicacion
    telefono: Optional[Telefono] = None
    fax: Optional[Telefono] = None
    correo_electronico: str = Field(..., max_length=160)

class Receptor(BaseModel):
    nombre: str = Field(..., max_length=100)
    identificacion_tipo: Optional[str] = Field(None, min_length=2, max_length=2)
    identificacion_numero: Optional[str] = Field(None, min_length=9, max_length=20)
    nombre_comercial: Optional[str] = Field(None, max_length=80)
    ubicacion: Optional[Ubicacion] = None
    telefono: Optional[Telefono] = None
    fax: Optional[Telefono] = None
    correo_electronico: Optional[str] = Field(None, max_length=160)

class Impuesto(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=2)
    codigo_tarifa: str = Field(..., min_length=2, max_length=8)
    tarifa: Decimal = Field(..., ge=0)
    monto: Decimal = Field(..., ge=0)
    exoneracion_tipo_documento: Optional[str] = None
    exoneracion_numero_documento: Optional[str] = None
    exoneracion_nombre_institucion: Optional[str] = None
    exoneracion_fecha_emision: Optional[datetime] = None
    exoneracion_porcentaje_exoneracion: Optional[Decimal] = None
    exoneracion_monto_exoneracion: Optional[Decimal] = None

class LineaDetalle(BaseModel):
    numero_linea: int = Field(..., ge=1)
    codigo: Optional[str] = Field(None, max_length=20)
    codigo_comercial_tipo: Optional[str] = None
    codigo_comercial_codigo: Optional[str] = None
    cantidad: Decimal = Field(..., gt=0)
    unidad_medida: str = Field(..., max_length=20)
    unidad_medida_comercial: Optional[str] = Field(None, max_length=20)
    detalle: str = Field(..., max_length=200)
    precio_unitario: Decimal = Field(..., ge=0)
    monto_total: Decimal = Field(..., ge=0)
    descuento_monto: Optional[Decimal] = Field(None, ge=0)
    descuento_naturaleza: Optional[str] = None
    subtotal: Decimal = Field(..., ge=0)
    base_imponible: Optional[Decimal] = Field(None, ge=0)
    impuestos: Optional[List[Impuesto]] = []
    impuesto_neto: Optional[Decimal] = Field(None, ge=0)
    monto_total_linea: Decimal = Field(..., ge=0)

class ResumenFactura(BaseModel):
    codigo_tipo_moneda: TipoMoneda
    total_servicios_gravados: Optional[Decimal] = Field(None, ge=0)
    total_servicios_exentos: Optional[Decimal] = Field(None, ge=0)
    total_servicios_exonerados: Optional[Decimal] = Field(None, ge=0)
    total_mercaderias_gravadas: Optional[Decimal] = Field(None, ge=0)
    total_mercaderias_exentas: Optional[Decimal] = Field(None, ge=0)
    total_mercaderias_exoneradas: Optional[Decimal] = Field(None, ge=0)
    total_gravado: Optional[Decimal] = Field(None, ge=0)
    total_exento: Optional[Decimal] = Field(None, ge=0)
    total_exonerado: Optional[Decimal] = Field(None, ge=0)
    total_venta: Decimal = Field(..., ge=0)
    total_descuentos: Optional[Decimal] = Field(None, ge=0)
    total_venta_neta: Decimal = Field(..., ge=0)
    total_impuesto: Optional[Decimal] = Field(None, ge=0)
    total_iva_devuelto: Optional[Decimal] = Field(None, ge=0)
    total_otros_cargos: Optional[Decimal] = Field(None, ge=0)
    total_comprobante: Decimal = Field(..., ge=0)

class FacturaElectronica(BaseModel):
    clave: Optional[str] = Field(None, min_length=50, max_length=50)
    codigo_actividad: str = Field(..., min_length=6, max_length=6)
    numero_consecutivo: str = Field(..., min_length=20, max_length=20)
    fecha_emision: datetime
    emisor: Emisor
    receptor: Optional[Receptor] = None
    condicion_venta: str = Field(..., min_length=2, max_length=2)
    plazo_credito: Optional[str] = Field(None, min_length=1, max_length=10)
    medio_pago: List[str] = Field(..., min_items=1)
    detalles_servicio: Optional[List[LineaDetalle]] = []
    otros_cargos: Optional[List[dict]] = []
    resumen_factura: ResumenFactura
    informacion_referencia: Optional[List[dict]] = []
    normativa: str = Field(default="4.4")
    otros: Optional[str] = None

    @validator('clave')
    def validate_clave(cls, v):
        if v and len(v) != 50:
            raise ValueError('La clave debe tener exactamente 50 caracteres')
        return v

class FacturaCreate(BaseModel):
    emisor: Emisor
    receptor: Optional[Receptor] = None
    condicion_venta: str
    plazo_credito: Optional[str] = None
    medio_pago: List[str]
    detalles_servicio: List[LineaDetalle]
    resumen_factura: ResumenFactura
    codigo_actividad: str

class FacturaResponse(BaseModel):
    clave: str
    numero_consecutivo: str
    fecha_emision: datetime
    estado: str
    xml_firmado: Optional[str] = None
    pdf_url: Optional[str] = None
    mensaje_hacienda: Optional[str] = None