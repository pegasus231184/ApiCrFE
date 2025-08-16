from jinja2 import Template
from datetime import datetime
from typing import Dict, Any, List
import logging
from app.core.reference_data import validar_ubicacion, validar_moneda, MONEDAS_OFICIALES

logger = logging.getLogger(__name__)

class XMLGeneratorV44:
    """
    Generador XML oficial para Facturación Electrónica v4.4 del Ministerio de Hacienda de Costa Rica
    Basado en el XSD oficial FacturaElectronica_V4.4.xsd.xml
    """
    
    def __init__(self):
        # Template compacto sin espacios siguiendo el formato oficial
        self.factura_template = Template("""<?xml version="1.0" encoding="utf-8"?><FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica" xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/FacturaElectronica_V4.4.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><Clave>{{ clave }}</Clave><ProveedorSistemas>{{ proveedor_sistemas }}</ProveedorSistemas><CodigoActividadEmisor>{{ codigo_actividad_emisor }}</CodigoActividadEmisor>{% if codigo_actividad_receptor %}<CodigoActividadReceptor>{{ codigo_actividad_receptor }}</CodigoActividadReceptor>{% endif %}<NumeroConsecutivo>{{ numero_consecutivo }}</NumeroConsecutivo><FechaEmision>{{ fecha_emision }}</FechaEmision><Emisor><Nombre>{{ emisor.nombre }}</Nombre><Identificacion><Tipo>{{ emisor.identificacion_tipo }}</Tipo><Numero>{{ emisor.identificacion_numero }}</Numero></Identificacion>{% if emisor.nombre_comercial %}<NombreComercial>{{ emisor.nombre_comercial }}</NombreComercial>{% endif %}<Ubicacion><Provincia>{{ emisor.ubicacion.provincia }}</Provincia><Canton>{{ emisor.ubicacion.canton }}</Canton><Distrito>{{ emisor.ubicacion.distrito }}</Distrito>{% if emisor.ubicacion.barrio %}<Barrio>{{ emisor.ubicacion.barrio }}</Barrio>{% endif %}{% if emisor.ubicacion.otras_senas %}<OtrasSenas>{{ emisor.ubicacion.otras_senas }}</OtrasSenas>{% endif %}</Ubicacion>{% if emisor.telefono %}<Telefono><CodigoPais>{{ emisor.telefono.codigo_pais }}</CodigoPais><NumTelefono>{{ emisor.telefono.numero }}</NumTelefono></Telefono>{% endif %}<CorreoElectronico>{{ emisor.correo_electronico }}</CorreoElectronico></Emisor>{% if receptor %}<Receptor><Nombre>{{ receptor.nombre }}</Nombre>{% if receptor.identificacion_tipo and receptor.identificacion_numero %}<Identificacion><Tipo>{{ receptor.identificacion_tipo }}</Tipo><Numero>{{ receptor.identificacion_numero }}</Numero></Identificacion>{% endif %}{% if receptor.correo_electronico %}<CorreoElectronico>{{ receptor.correo_electronico }}</CorreoElectronico>{% endif %}</Receptor>{% endif %}<CondicionVenta>{{ condicion_venta }}</CondicionVenta>{% if plazo_credito %}<PlazoCredito>{{ plazo_credito }}</PlazoCredito>{% endif %}{% for medio in medio_pago %}<MedioPago>{{ medio }}</MedioPago>{% endfor %}<DetalleServicio>{% for detalle in detalles_servicio %}<LineaDetalle><NumeroLinea>{{ detalle.numero_linea }}</NumeroLinea><CodigoCABYS>{{ detalle.codigo_cabys }}</CodigoCABYS>{% if detalle.codigo_comercial %}<CodigoComercial><Tipo>{{ detalle.codigo_comercial.tipo or '01' }}</Tipo><Codigo>{{ detalle.codigo_comercial.codigo }}</Codigo></CodigoComercial>{% endif %}<Cantidad>{{ "%.3f"|format(detalle.cantidad) }}</Cantidad><UnidadMedida>{{ detalle.unidad_medida }}</UnidadMedida>{% if detalle.unidad_medida_comercial %}<UnidadMedidaComercial>{{ detalle.unidad_medida_comercial }}</UnidadMedidaComercial>{% endif %}<Detalle>{{ detalle.detalle }}</Detalle><PrecioUnitario>{{ "%.5f"|format(detalle.precio_unitario) }}</PrecioUnitario><MontoTotal>{{ "%.5f"|format(detalle.monto_total) }}</MontoTotal>{% if detalle.descuento %}<Descuento><MontoDescuento>{{ "%.5f"|format(detalle.descuento.monto) }}</MontoDescuento><NaturalezaDescuento>{{ detalle.descuento.naturaleza }}</NaturalezaDescuento></Descuento>{% endif %}<SubTotal>{{ "%.5f"|format(detalle.subtotal) }}</SubTotal>{% if detalle.impuestos %}{% for impuesto in detalle.impuestos %}<Impuesto><Codigo>{{ impuesto.codigo }}</Codigo><CodigoTarifa>{{ impuesto.codigo_tarifa }}</CodigoTarifa><Tarifa>{{ "%.2f"|format(impuesto.tarifa) }}</Tarifa><Monto>{{ "%.5f"|format(impuesto.monto) }}</Monto>{% if impuesto.exoneracion %}<Exoneracion><TipoDocumento>{{ impuesto.exoneracion.tipo_documento }}</TipoDocumento><NumeroDocumento>{{ impuesto.exoneracion.numero_documento }}</NumeroDocumento><NombreInstitucion>{{ impuesto.exoneracion.nombre_institucion }}</NombreInstitucion><FechaEmision>{{ impuesto.exoneracion.fecha_emision }}</FechaEmision><PorcentajeExoneracion>{{ impuesto.exoneracion.porcentaje_exoneracion }}</PorcentajeExoneracion><MontoExoneracion>{{ "%.5f"|format(impuesto.exoneracion.monto_exoneracion) }}</MontoExoneracion></Exoneracion>{% endif %}</Impuesto>{% endfor %}<ImpuestoNeto>{{ "%.5f"|format(detalle.impuesto_neto) }}</ImpuestoNeto>{% endif %}<MontoTotalLinea>{{ "%.5f"|format(detalle.monto_total_linea) }}</MontoTotalLinea></LineaDetalle>{% endfor %}</DetalleServicio>{% if otros_cargos %}<OtrosCargos>{% for cargo in otros_cargos %}<TipoDocumento>{{ cargo.tipo_documento }}</TipoDocumento><NumeroIdentidadTercero>{{ cargo.numero_identidad_tercero }}</NumeroIdentidadTercero><NombreTercero>{{ cargo.nombre_tercero }}</NombreTercero><Detalle>{{ cargo.detalle }}</Detalle><Porcentaje>{{ cargo.porcentaje }}</Porcentaje><MontoCargo>{{ "%.5f"|format(cargo.monto_cargo) }}</MontoCargo>{% endfor %}</OtrosCargos>{% endif %}<ResumenFactura><CodigoTipoMoneda><CodigoMoneda>{{ resumen.codigo_tipo_moneda }}</CodigoMoneda><TipoCambio>{{ "%.5f"|format(resumen.tipo_cambio) }}</TipoCambio></CodigoTipoMoneda>{% if resumen.total_servicios_gravados is defined %}<TotalServGravados>{{ "%.5f"|format(resumen.total_servicios_gravados) }}</TotalServGravados>{% endif %}{% if resumen.total_servicios_exentos is defined %}<TotalServExentos>{{ "%.5f"|format(resumen.total_servicios_exentos) }}</TotalServExentos>{% endif %}{% if resumen.total_servicios_exonerados is defined %}<TotalServExonerado>{{ "%.5f"|format(resumen.total_servicios_exonerados) }}</TotalServExonerado>{% endif %}{% if resumen.total_mercaderias_gravadas is defined %}<TotalMercanciasGravadas>{{ "%.5f"|format(resumen.total_mercaderias_gravadas) }}</TotalMercanciasGravadas>{% endif %}{% if resumen.total_mercaderias_exentas is defined %}<TotalMercanciasExentas>{{ "%.5f"|format(resumen.total_mercaderias_exentas) }}</TotalMercanciasExentas>{% endif %}{% if resumen.total_mercaderias_exoneradas is defined %}<TotalMercExonerada>{{ "%.5f"|format(resumen.total_mercaderias_exoneradas) }}</TotalMercExonerada>{% endif %}{% if resumen.total_gravado is defined %}<TotalGravado>{{ "%.5f"|format(resumen.total_gravado) }}</TotalGravado>{% endif %}{% if resumen.total_exento is defined %}<TotalExento>{{ "%.5f"|format(resumen.total_exento) }}</TotalExento>{% endif %}{% if resumen.total_exonerado is defined %}<TotalExonerado>{{ "%.5f"|format(resumen.total_exonerado) }}</TotalExonerado>{% endif %}<TotalVenta>{{ "%.5f"|format(resumen.total_venta) }}</TotalVenta>{% if resumen.total_descuentos is defined %}<TotalDescuentos>{{ "%.5f"|format(resumen.total_descuentos) }}</TotalDescuentos>{% endif %}<TotalVentaNeta>{{ "%.5f"|format(resumen.total_venta_neta) }}</TotalVentaNeta>{% if resumen.total_impuesto is defined %}<TotalImpuesto>{{ "%.5f"|format(resumen.total_impuesto) }}</TotalImpuesto>{% endif %}{% if resumen.total_iva_devuelto is defined %}<TotalIVADevuelto>{{ "%.5f"|format(resumen.total_iva_devuelto) }}</TotalIVADevuelto>{% endif %}{% if resumen.total_otros_cargos is defined %}<TotalOtrosCargos>{{ "%.5f"|format(resumen.total_otros_cargos) }}</TotalOtrosCargos>{% endif %}<TotalComprobante>{{ "%.5f"|format(resumen.total_comprobante) }}</TotalComprobante></ResumenFactura>{% if informacion_referencia %}<InformacionReferencia>{% for ref in informacion_referencia %}<TipoDoc>{{ ref.tipo_doc }}</TipoDoc><Numero>{{ ref.numero }}</Numero><FechaEmision>{{ ref.fecha_emision }}</FechaEmision><Codigo>{{ ref.codigo }}</Codigo><Razon>{{ ref.razon }}</Razon>{% endfor %}</InformacionReferencia>{% endif %}{{ firma_digital }}</FacturaElectronica>""")
    
    def generar_xml_factura(self, data: Dict[str, Any]) -> str:
        """
        Generar XML de factura siguiendo especificación oficial v4.4
        
        Args:
            data: Diccionario con todos los datos de la factura
            
        Returns:
            str: XML de factura en formato oficial v4.4
        """
        try:
            # Validar campos obligatorios
            self._validar_campos_obligatorios(data)
            
            # Procesar y completar datos
            data_procesada = self._procesar_datos(data)
            
            # Generar XML
            xml = self.factura_template.render(**data_procesada)
            
            logger.info(f"XML v4.4 generado exitosamente para clave: {data_procesada.get('clave', 'N/A')}")
            return xml
            
        except Exception as e:
            logger.error(f"Error generando XML v4.4: {e}")
            raise
    
    def _validar_campos_obligatorios(self, data: Dict[str, Any]) -> None:
        """Validar que todos los campos obligatorios estén presentes"""
        campos_obligatorios = [
            'clave', 'proveedor_sistemas', 'codigo_actividad_emisor', 
            'numero_consecutivo', 'fecha_emision', 'emisor', 'condicion_venta',
            'medio_pago', 'detalles_servicio', 'resumen_factura'
        ]
        
        for campo in campos_obligatorios:
            if campo not in data or data[campo] is None:
                raise ValueError(f"Campo obligatorio faltante: {campo}")
        
        # Validar ubicación del emisor con datos oficiales
        if 'emisor' in data and 'ubicacion' in data['emisor']:
            ubicacion = data['emisor']['ubicacion']
            if all(k in ubicacion for k in ['provincia', 'canton', 'distrito']):
                es_valida, mensaje = validar_ubicacion(
                    ubicacion['provincia'],
                    ubicacion['canton'], 
                    ubicacion['distrito']
                )
                if not es_valida:
                    logger.warning(f"⚠️ Ubicación del emisor: {mensaje}")
        
        # Validar detalles de servicio
        if not data['detalles_servicio'] or len(data['detalles_servicio']) == 0:
            raise ValueError("Debe incluir al menos una línea de detalle")
        
        # Validar códigos CABYS
        for i, detalle in enumerate(data['detalles_servicio']):
            if 'codigo_cabys' not in detalle:
                raise ValueError(f"Línea {i+1}: Campo 'codigo_cabys' es obligatorio")
            if len(detalle['codigo_cabys']) != 13:
                raise ValueError(f"Línea {i+1}: codigo_cabys debe tener exactamente 13 caracteres")
    
    def _procesar_datos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar y completar datos para el template"""
        data_procesada = data.copy()
        
        # Procesar fecha de emisión
        if isinstance(data_procesada['fecha_emision'], datetime):
            data_procesada['fecha_emision'] = data_procesada['fecha_emision'].strftime('%Y-%m-%dT%H:%M:%S-06:00')
        
        # Completar detalles de servicio
        data_procesada['detalles_servicio'] = self._completar_detalles_servicio(data['detalles_servicio'])
        
        # Completar resumen de factura
        data_procesada['resumen'] = self._completar_resumen_factura(data['resumen_factura'])
        
        # Generar firma digital
        data_procesada['firma_digital'] = self._generar_firma_digital(data['clave'])
        
        # Asegurar que todos los valores numéricos no sean None
        self._limpiar_valores_none(data_procesada)
        
        return data_procesada
        
    def _limpiar_valores_none(self, data: Dict[str, Any]):
        """Limpiar valores None que pueden causar errores en el template"""
        # Limpiar detalles de servicio
        if 'detalles_servicio' in data:
            for detalle in data['detalles_servicio']:
                for key, value in detalle.items():
                    if value is None and key in ['cantidad', 'precio_unitario', 'monto_total', 'subtotal', 'impuesto_neto', 'monto_total_linea']:
                        detalle[key] = 0.0
                if 'impuestos' in detalle and detalle['impuestos']:
                    for impuesto in detalle['impuestos']:
                        for key, value in impuesto.items():
                            if value is None and key in ['tarifa', 'monto']:
                                impuesto[key] = 0.0
        
        # Limpiar resumen
        if 'resumen' in data:
            for key, value in data['resumen'].items():
                if value is None:
                    data['resumen'][key] = 0.0
    
    def _completar_detalles_servicio(self, detalles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Completar detalles de servicio con campos calculados"""
        detalles_completos = []
        
        for detalle in detalles:
            detalle_completo = detalle.copy()
            
            # Agregar código CABYS por defecto si no existe
            if 'codigo_cabys' not in detalle_completo:
                detalle_completo['codigo_cabys'] = '8411000000000'  # Código genérico para servicios
            
            # Calcular subtotal si no existe
            if 'subtotal' not in detalle_completo:
                from decimal import Decimal
                cantidad = Decimal(str(detalle_completo['cantidad']))
                precio = Decimal(str(detalle_completo['precio_unitario']))
                subtotal = cantidad * precio
                if 'descuento' in detalle_completo and detalle_completo['descuento']:
                    descuento = Decimal(str(detalle_completo['descuento'].get('monto', 0)))
                    subtotal -= descuento
                detalle_completo['subtotal'] = float(subtotal)
            
            # Calcular impuestos automáticamente si no existen
            if 'impuestos' not in detalle_completo or not detalle_completo['impuestos']:
                from decimal import Decimal
                subtotal_decimal = Decimal(str(detalle_completo['subtotal']))
                impuesto_monto = float(subtotal_decimal * Decimal('0.13'))  # IVA 13%
                detalle_completo['impuestos'] = [{
                    'codigo': '01',  # IVA
                    'codigo_tarifa': '08',  # 13%
                    'tarifa': 13.00,
                    'monto': impuesto_monto
                }]
                detalle_completo['impuesto_neto'] = impuesto_monto
            else:
                total_impuestos = sum(imp.get('monto', 0) or 0 for imp in detalle_completo['impuestos'])
                detalle_completo['impuesto_neto'] = total_impuestos
            
            # Calcular monto total línea
            if 'monto_total_linea' not in detalle_completo:
                subtotal = detalle_completo.get('subtotal', 0) or 0
                impuesto_neto = detalle_completo.get('impuesto_neto', 0) or 0
                detalle_completo['monto_total_linea'] = subtotal + impuesto_neto
            
            detalles_completos.append(detalle_completo)
        
        return detalles_completos
    
    def _completar_resumen_factura(self, resumen: Dict[str, Any]) -> Dict[str, Any]:
        """Completar resumen de factura con campos obligatorios"""
        resumen_completo = resumen.copy()
        
        # Validar y asignar código de moneda
        codigo_moneda = resumen_completo.get('codigo_tipo_moneda', 'CRC')
        es_valida, mensaje = validar_moneda(codigo_moneda)
        if not es_valida:
            logger.warning(f"⚠️ Código de moneda: {mensaje}. Usando CRC por defecto.")
            codigo_moneda = 'CRC'
        
        # Valores por defecto para campos obligatorios
        defaults = {
            'codigo_tipo_moneda': codigo_moneda,
            'tipo_cambio': 1.00000,
            'total_servicios_gravados': resumen.get('total_venta', 0) or 0.00000,
            'total_servicios_exentos': 0.00000,
            'total_servicios_exonerados': 0.00000,
            'total_mercaderias_gravadas': 0.00000,
            'total_mercaderias_exentas': 0.00000,
            'total_mercaderias_exoneradas': 0.00000,
            'total_gravado': resumen.get('total_venta', 0) or 0.00000,
            'total_exento': 0.00000,
            'total_exonerado': 0.00000,
            'total_descuentos': 0.00000,
            'total_impuesto': resumen.get('total_impuestos', 0) or 0.00000,
            'total_iva_devuelto': 0.00000,
            'total_otros_cargos': 0.00000
        }
        
        for campo, valor_default in defaults.items():
            if campo not in resumen_completo:
                resumen_completo[campo] = valor_default
        
        return resumen_completo
    
    def _generar_firma_digital(self, clave: str) -> str:
        """Generar firma digital simulada para desarrollo"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="Signature-{timestamp}"><!-- Firma digital simulada para desarrollo --></ds:Signature>'

# Instancia global
xml_generator_v44 = XMLGeneratorV44()