from jinja2 import Template
from datetime import datetime
from app.schemas.factura import FacturaElectronica
import secrets
import string

class XMLGeneratorOfficial:
    """
    Generador XML que sigue exactamente el formato oficial de Hacienda Costa Rica
    Basado en documentos reales como 003101460479-FE-19800028010000005488.xml
    """
    def __init__(self):
        self.factura_template = Template("""<?xml version="1.0" encoding="utf-8"?><FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica" xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/FacturaElectronica_V4.3.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#"><Clave>{{ clave }}</Clave><CodigoActividad>{{ codigo_actividad }}</CodigoActividad><NumeroConsecutivo>{{ numero_consecutivo }}</NumeroConsecutivo><FechaEmision>{{ fecha_emision }}</FechaEmision><Emisor><Nombre>{{ emisor.nombre }}</Nombre><Identificacion><Tipo>{{ emisor.identificacion_tipo }}</Tipo><Numero>{{ emisor.identificacion_numero }}</Numero></Identificacion>{% if emisor.nombre_comercial %}<NombreComercial>{{ emisor.nombre_comercial }}</NombreComercial>{% endif %}<Ubicacion><Provincia>{{ emisor.ubicacion.provincia }}</Provincia><Canton>{{ emisor.ubicacion.canton }}</Canton><Distrito>{{ emisor.ubicacion.distrito }}</Distrito>{% if emisor.ubicacion.barrio %}<Barrio>{{ emisor.ubicacion.barrio }}</Barrio>{% endif %}{% if emisor.ubicacion.otras_senas %}<OtrasSenas>{{ emisor.ubicacion.otras_senas }}</OtrasSenas>{% endif %}</Ubicacion>{% if emisor.telefono %}<Telefono><CodigoPais>{{ emisor.telefono.codigo_pais }}</CodigoPais><NumTelefono>{{ emisor.telefono.numero }}</NumTelefono></Telefono>{% endif %}<CorreoElectronico>{{ emisor.correo_electronico }}</CorreoElectronico></Emisor>{% if receptor %}<Receptor><Nombre>{{ receptor.nombre }}</Nombre>{% if receptor.identificacion_tipo and receptor.identificacion_numero %}<Identificacion><Tipo>{{ receptor.identificacion_tipo }}</Tipo><Numero>{{ receptor.identificacion_numero }}</Numero></Identificacion>{% endif %}{% if receptor.correo_electronico %}<CorreoElectronico>{{ receptor.correo_electronico }}</CorreoElectronico>{% endif %}</Receptor>{% endif %}<CondicionVenta>{{ condicion_venta }}</CondicionVenta>{% for medio in medio_pago %}<MedioPago>{{ medio }}</MedioPago>{% endfor %}{% if detalles_servicio %}<DetalleServicio>{% for detalle in detalles_servicio %}<LineaDetalle><NumeroLinea>{{ detalle.numero_linea }}</NumeroLinea>{% if detalle.codigo %}<Codigo>{{ detalle.codigo }}</Codigo>{% endif %}<Cantidad>{{ "%.3f"|format(detalle.cantidad) }}</Cantidad><UnidadMedida>{{ detalle.unidad_medida }}</UnidadMedida><Detalle>{{ detalle.detalle }}</Detalle><PrecioUnitario>{{ "%.5f"|format(detalle.precio_unitario) }}</PrecioUnitario><MontoTotal>{{ "%.5f"|format(detalle.monto_total) }}</MontoTotal><SubTotal>{{ "%.5f"|format(detalle.subtotal) }}</SubTotal>{% if detalle.base_imponible %}<BaseImponible>{{ "%.5f"|format(detalle.base_imponible) }}</BaseImponible>{% endif %}{% if detalle.impuestos %}{% for impuesto in detalle.impuestos %}<Impuesto><Codigo>{{ impuesto.codigo }}</Codigo><CodigoTarifa>{{ impuesto.codigo_tarifa }}</CodigoTarifa><Tarifa>{{ "%.2f"|format(impuesto.tarifa) }}</Tarifa><Monto>{{ "%.5f"|format(impuesto.monto) }}</Monto></Impuesto>{% endfor %}{% endif %}{% if detalle.impuesto_neto %}<ImpuestoNeto>{{ "%.5f"|format(detalle.impuesto_neto) }}</ImpuestoNeto>{% endif %}<MontoTotalLinea>{{ "%.5f"|format(detalle.monto_total_linea) }}</MontoTotalLinea></LineaDetalle>{% endfor %}</DetalleServicio>{% endif %}<ResumenFactura><CodigoTipoMoneda><CodigoMoneda>{{ resumen_factura.codigo_tipo_moneda }}</CodigoMoneda><TipoCambio>1.00000</TipoCambio></CodigoTipoMoneda>{% if resumen_factura.total_servicios_gravados is defined %}<TotalServGravados>{{ "%.5f"|format(resumen_factura.total_servicios_gravados) }}</TotalServGravados>{% endif %}{% if resumen_factura.total_servicios_exentos is defined %}<TotalServExentos>{{ "%.5f"|format(resumen_factura.total_servicios_exentos) }}</TotalServExentos>{% endif %}{% if resumen_factura.total_servicios_exonerados is defined %}<TotalServExonerado>{{ "%.5f"|format(resumen_factura.total_servicios_exonerados) }}</TotalServExonerado>{% endif %}{% if resumen_factura.total_mercaderias_gravadas is defined %}<TotalMercanciasGravadas>{{ "%.5f"|format(resumen_factura.total_mercaderias_gravadas) }}</TotalMercanciasGravadas>{% endif %}{% if resumen_factura.total_mercaderias_exentas is defined %}<TotalMercanciasExentas>{{ "%.5f"|format(resumen_factura.total_mercaderias_exentas) }}</TotalMercanciasExentas>{% endif %}{% if resumen_factura.total_mercaderias_exoneradas is defined %}<TotalMercExonerada>{{ "%.5f"|format(resumen_factura.total_mercaderias_exoneradas) }}</TotalMercExonerada>{% endif %}{% if resumen_factura.total_gravado is defined %}<TotalGravado>{{ "%.5f"|format(resumen_factura.total_gravado) }}</TotalGravado>{% endif %}{% if resumen_factura.total_exento is defined %}<TotalExento>{{ "%.5f"|format(resumen_factura.total_exento) }}</TotalExento>{% endif %}{% if resumen_factura.total_exonerado is defined %}<TotalExonerado>{{ "%.5f"|format(resumen_factura.total_exonerado) }}</TotalExonerado>{% endif %}<TotalVenta>{{ "%.5f"|format(resumen_factura.total_venta) }}</TotalVenta><TotalVentaNeta>{{ "%.5f"|format(resumen_factura.total_venta_neta) }}</TotalVentaNeta>{% if resumen_factura.total_impuesto is defined %}<TotalImpuesto>{{ "%.5f"|format(resumen_factura.total_impuesto) }}</TotalImpuesto>{% endif %}{% if resumen_factura.total_iva_devuelto is defined %}<TotalIVADevuelto>{{ "%.5f"|format(resumen_factura.total_iva_devuelto) }}</TotalIVADevuelto>{% endif %}{% if resumen_factura.total_otros_cargos is defined %}<TotalOtrosCargos>{{ "%.5f"|format(resumen_factura.total_otros_cargos) }}</TotalOtrosCargos>{% endif %}<TotalComprobante>{{ "%.5f"|format(resumen_factura.total_comprobante) }}</TotalComprobante></ResumenFactura>{{ firma_digital }}</FacturaElectronica>""")
        
    def generar_xml_factura(self, factura: FacturaElectronica) -> str:
        """
        Generar XML de factura siguiendo formato oficial de Hacienda
        """
        # Calcular totales automáticamente si no están definidos
        resumen_calculado = self.calcular_resumen_oficial(factura)
        
        # Actualizar detalles con impuestos automáticos
        detalles_completos = self.completar_detalles_linea(factura.detalles_servicio)
        
        # Generar firma digital simulada
        firma_digital = self.generar_firma_digital_simulada(factura.clave)
        
        xml = self.factura_template.render(
            clave=factura.clave,
            codigo_actividad=factura.codigo_actividad,
            numero_consecutivo=factura.numero_consecutivo,
            fecha_emision=factura.fecha_emision.strftime('%Y-%m-%dT%H:%M:%S-06:00'),
            emisor=factura.emisor,
            receptor=factura.receptor,
            condicion_venta=factura.condicion_venta,
            medio_pago=factura.medio_pago,
            detalles_servicio=detalles_completos,
            resumen_factura=resumen_calculado,
            firma_digital=firma_digital
        )
        
        return xml
    
    def calcular_resumen_oficial(self, factura: FacturaElectronica) -> dict:
        """
        Calcular resumen de factura siguiendo formato oficial
        """
        # Usar el resumen proporcionado como base
        resumen = factura.resumen_factura.model_dump()
        
        # Agregar campos obligatorios del formato oficial
        if 'total_servicios_gravados' not in resumen:
            resumen['total_servicios_gravados'] = resumen.get('total_venta', 0)
        
        if 'total_servicios_exentos' not in resumen:
            resumen['total_servicios_exentos'] = 0.00000
            
        if 'total_servicios_exonerados' not in resumen:
            resumen['total_servicios_exonerados'] = 0.00000
            
        if 'total_mercaderias_gravadas' not in resumen:
            resumen['total_mercaderias_gravadas'] = 0.00000
            
        if 'total_mercaderias_exentas' not in resumen:
            resumen['total_mercaderias_exentas'] = 0.00000
            
        if 'total_mercaderias_exoneradas' not in resumen:
            resumen['total_mercaderias_exoneradas'] = 0.00000
            
        if 'total_gravado' not in resumen:
            resumen['total_gravado'] = resumen.get('total_venta', 0)
            
        if 'total_exento' not in resumen:
            resumen['total_exento'] = 0.00000
            
        if 'total_exonerado' not in resumen:
            resumen['total_exonerado'] = 0.00000
            
        if 'total_iva_devuelto' not in resumen:
            resumen['total_iva_devuelto'] = 0.00000
            
        if 'total_otros_cargos' not in resumen:
            resumen['total_otros_cargos'] = 0.00000
        
        return resumen
    
    def completar_detalles_linea(self, detalles):
        """
        Completar detalles de línea con impuestos automáticos
        """
        detalles_completos = []
        
        for detalle in detalles:
            detalle_dict = detalle.model_dump()
            
            # Agregar base imponible si no existe
            if 'base_imponible' not in detalle_dict:
                detalle_dict['base_imponible'] = detalle_dict.get('subtotal', detalle_dict.get('monto_total', 0))
            
            # Agregar impuestos automáticos (IVA 13%)
            if 'impuestos' not in detalle_dict or not detalle_dict['impuestos']:
                base_imponible = detalle_dict['base_imponible']
                impuesto_monto = round(base_imponible * 0.13, 5)
                
                detalle_dict['impuestos'] = [{
                    'codigo': '01',  # IVA
                    'codigo_tarifa': '08',  # 13%
                    'tarifa': 13.00,
                    'monto': impuesto_monto
                }]
                
                detalle_dict['impuesto_neto'] = impuesto_monto
                
                # Recalcular monto total línea
                if detalle_dict['monto_total_linea'] == detalle_dict['subtotal']:
                    detalle_dict['monto_total_linea'] = detalle_dict['subtotal'] + impuesto_monto
            
            detalles_completos.append(detalle_dict)
        
        return detalles_completos
    
    def generar_firma_digital_simulada(self, clave: str) -> str:
        """
        Generar una firma digital simulada para desarrollo
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="Signature-{timestamp}"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315" /><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" /><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" /></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" /><ds:DigestValue>CERTIFICADO_OFICIAL_310277607903_{timestamp}</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>FIRMA_DIGITAL_SIMULADA_DESARROLLO_{clave[:20]}</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>CERTIFICADO_OFICIAL_HACIENDA_COSTA_RICA</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature>'

# Instancia global
xml_generator_official = XMLGeneratorOfficial()