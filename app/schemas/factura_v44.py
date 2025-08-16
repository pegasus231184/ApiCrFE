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

class CodigoComercial(BaseModel):
    tipo: str = Field(..., max_length=2, description="Tipo de código comercial")
    codigo: str = Field(..., max_length=20, description="Código comercial")

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

class Exoneracion(BaseModel):
    tipo_documento: str = Field(..., max_length=2)
    numero_documento: str = Field(..., max_length=40)
    nombre_institucion: str = Field(..., max_length=160)
    fecha_emision: datetime
    porcentaje_exoneracion: Decimal = Field(..., ge=0, le=100)
    monto_exoneracion: Decimal = Field(..., ge=0)

class Impuesto(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=2)
    codigo_tarifa: str = Field(..., min_length=2, max_length=8)
    tarifa: Decimal = Field(..., ge=0)
    monto: Decimal = Field(..., ge=0)
    exoneracion: Optional[Exoneracion] = None

class Descuento(BaseModel):
    monto: Decimal = Field(..., ge=0)
    naturaleza: str = Field(..., max_length=80)

class LineaDetalle(BaseModel):
    numero_linea: int = Field(..., ge=1, le=1000)
    codigo_cabys: str = Field(..., min_length=13, max_length=13, description="Código CABYS de 13 dígitos")
    codigo_comercial: Optional[CodigoComercial] = None
    cantidad: Decimal = Field(..., gt=0)
    unidad_medida: str = Field(..., max_length=15)
    unidad_medida_comercial: Optional[str] = Field(None, max_length=20)
    detalle: str = Field(..., min_length=3, max_length=200)
    precio_unitario: Decimal = Field(..., ge=0)
    monto_total: Decimal = Field(..., ge=0)
    descuento: Optional[Descuento] = None
    subtotal: Decimal = Field(..., ge=0)
    impuestos: Optional[List[Impuesto]] = []
    impuesto_neto: Optional[Decimal] = Field(None, ge=0)
    monto_total_linea: Decimal = Field(..., ge=0)
    
    @validator('codigo_cabys')
    def validate_codigo_cabys(cls, v):
        if len(v) != 13:
            raise ValueError('El código CABYS debe tener exactamente 13 caracteres')
        if not v.isdigit():
            raise ValueError('El código CABYS debe contener solo dígitos')
        return v

class OtroCargo(BaseModel):
    tipo_documento: str = Field(..., max_length=2)
    numero_identidad_tercero: str = Field(..., max_length=20)
    nombre_tercero: str = Field(..., max_length=100)
    detalle: str = Field(..., max_length=1000)
    porcentaje: Optional[Decimal] = Field(None, ge=0, le=100)
    monto_cargo: Decimal = Field(..., ge=0)

class ResumenFactura(BaseModel):
    codigo_tipo_moneda: TipoMoneda = TipoMoneda.CRC
    tipo_cambio: Decimal = Field(default=Decimal('1.00000'), ge=0)
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

class InformacionReferencia(BaseModel):
    tipo_doc: str = Field(..., max_length=2)
    numero: str = Field(..., max_length=50)
    fecha_emision: datetime
    codigo: str = Field(..., max_length=2)
    razon: str = Field(..., max_length=180)

class FacturaElectronicaV44(BaseModel):
    clave: Optional[str] = Field(None, min_length=50, max_length=50)
    proveedor_sistemas: str = Field(..., max_length=20, description="Cédula del proveedor de sistemas")
    codigo_actividad_emisor: str = Field(..., min_length=6, max_length=6)
    codigo_actividad_receptor: Optional[str] = Field(None, min_length=6, max_length=6)
    numero_consecutivo: str = Field(..., min_length=20, max_length=20)
    fecha_emision: datetime
    emisor: Emisor
    receptor: Optional[Receptor] = None
    condicion_venta: str = Field(..., min_length=2, max_length=2)
    condicion_venta_otros: Optional[str] = Field(None, min_length=5, max_length=100)
    plazo_credito: Optional[int] = Field(None, ge=0, le=99999)
    medio_pago: List[str] = Field(..., min_items=1)
    detalles_servicio: List[LineaDetalle] = Field(..., min_items=1, max_items=1000)
    otros_cargos: Optional[List[OtroCargo]] = []
    resumen_factura: ResumenFactura
    informacion_referencia: Optional[List[InformacionReferencia]] = []
    normativa: str = Field(default="4.4")
    otros: Optional[str] = None

    @validator('clave')
    def validate_clave(cls, v):
        if v and len(v) != 50:
            raise ValueError('La clave debe tener exactamente 50 caracteres')
        return v
    
    @validator('condicion_venta_otros')
    def validate_condicion_venta_otros(cls, v, values):
        if 'condicion_venta' in values and values['condicion_venta'] == '99' and not v:
            raise ValueError('condicion_venta_otros es obligatorio cuando condicion_venta es "99"')
        return v

class FacturaCreateV44(BaseModel):
    proveedor_sistemas: str = Field(..., max_length=20)
    codigo_actividad_emisor: str = Field(..., min_length=6, max_length=6)
    codigo_actividad_receptor: Optional[str] = Field(None, min_length=6, max_length=6)
    emisor: Emisor
    receptor: Optional[Receptor] = None
    condicion_venta: str = Field(..., min_length=2, max_length=2)
    condicion_venta_otros: Optional[str] = Field(None, min_length=5, max_length=100)
    plazo_credito: Optional[int] = Field(None, ge=0, le=99999)
    medio_pago: List[str] = Field(..., min_items=1)
    detalles_servicio: List[LineaDetalle] = Field(..., min_items=1, max_items=1000)
    otros_cargos: Optional[List[OtroCargo]] = []
    resumen_factura: ResumenFactura
    informacion_referencia: Optional[List[InformacionReferencia]] = []

class FacturaResponse(BaseModel):
    clave: str
    numero_consecutivo: str
    fecha_emision: datetime
    estado: str
    xml_firmado: Optional[str] = None
    pdf_url: Optional[str] = None
    mensaje_hacienda: Optional[str] = None
    email_enviado: Optional[bool] = None
    message_id_email: Optional[str] = None