from sqlalchemy import Column, Integer, String, DateTime, Text, Decimal, Boolean, JSON
from sqlalchemy.sql import func
from app.models.database import Base

class DocumentoElectronico(Base):
    __tablename__ = "documentos_electronicos"
    
    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), unique=True, index=True, nullable=False)
    tipo_documento = Column(String(2), nullable=False)  # 01=Factura, 02=ND, 03=NC, 04=Tiquete
    numero_consecutivo = Column(String(20), nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Datos del emisor
    emisor_nombre = Column(String(100), nullable=False)
    emisor_cedula = Column(String(20), nullable=False)
    emisor_email = Column(String(160))
    
    # Datos del receptor
    receptor_nombre = Column(String(100))
    receptor_cedula = Column(String(20))
    receptor_email = Column(String(160))
    
    # Montos
    total_gravado = Column(Decimal(18, 5))
    total_exento = Column(Decimal(18, 5))
    total_exonerado = Column(Decimal(18, 5))
    total_venta = Column(Decimal(18, 5), nullable=False)
    total_descuentos = Column(Decimal(18, 5))
    total_venta_neta = Column(Decimal(18, 5), nullable=False)
    total_impuesto = Column(Decimal(18, 5))
    total_comprobante = Column(Decimal(18, 5), nullable=False)
    
    # Código de moneda
    codigo_moneda = Column(String(3), default="CRC")
    tipo_cambio = Column(Decimal(18, 5), default=1.00000)
    
    # XML y estado
    xml_sin_firmar = Column(Text)
    xml_firmado = Column(Text)
    estado_local = Column(String(20), default="generado")  # generado, firmado, enviado, error
    estado_hacienda = Column(String(20))  # aceptado, rechazado, procesando, etc.
    mensaje_hacienda = Column(Text)
    respuesta_hacienda = Column(JSON)
    
    # Intentos de envío
    intentos_envio = Column(Integer, default=0)
    ultimo_intento = Column(DateTime)
    
    # Flags
    es_anulado = Column(Boolean, default=False)
    motivo_anulacion = Column(Text)
    fecha_anulacion = Column(DateTime)
    
    # Información adicional
    condicion_venta = Column(String(2))
    plazo_credito = Column(String(10))
    medio_pago = Column(JSON)  # Lista de medios de pago
    
    # Referencias (para notas de crédito/débito)
    documento_referencia = Column(String(50))  # Clave del documento original
    tipo_referencia = Column(String(2))
    motivo_referencia = Column(Text)
    
    def __repr__(self):
        return f"<DocumentoElectronico(clave='{self.clave}', tipo='{self.tipo_documento}', estado='{self.estado_local}')>"

class LogEnvio(Base):
    __tablename__ = "logs_envio"
    
    id = Column(Integer, primary_key=True, index=True)
    clave_documento = Column(String(50), nullable=False, index=True)
    fecha_intento = Column(DateTime, default=func.now())
    tipo_operacion = Column(String(20), nullable=False)  # envio, consulta, reenvio
    
    # Request
    url_endpoint = Column(String(200))
    headers_request = Column(JSON)
    payload_request = Column(Text)
    
    # Response
    codigo_respuesta = Column(Integer)
    headers_response = Column(JSON)
    payload_response = Column(Text)
    tiempo_respuesta_ms = Column(Integer)
    
    # Resultado
    exitoso = Column(Boolean, default=False)
    mensaje_error = Column(Text)
    
    def __repr__(self):
        return f"<LogEnvio(clave='{self.clave_documento}', operacion='{self.tipo_operacion}', exitoso={self.exitoso})>"