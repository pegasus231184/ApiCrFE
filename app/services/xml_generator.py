from jinja2 import Template
from datetime import datetime
from app.schemas.factura import FacturaElectronica
import secrets
import string

class XMLGenerator:
    def __init__(self):
        self.factura_template = Template("""<?xml version="1.0" encoding="UTF-8"?>
<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronicaV44" 
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                   xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronicaV44 https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/FacturaElectronicaV44.xsd">
    <Clave>{{ clave }}</Clave>
    <CodigoActividad>{{ codigo_actividad }}</CodigoActividad>
    <NumeroConsecutivo>{{ numero_consecutivo }}</NumeroConsecutivo>
    <FechaEmision>{{ fecha_emision }}</FechaEmision>
    <Emisor>
        <Nombre>{{ emisor.nombre }}</Nombre>
        <Identificacion>
            <Tipo>{{ emisor.identificacion_tipo }}</Tipo>
            <Numero>{{ emisor.identificacion_numero }}</Numero>
        </Identificacion>
        {% if emisor.nombre_comercial %}
        <NombreComercial>{{ emisor.nombre_comercial }}</NombreComercial>
        {% endif %}
        <Ubicacion>
            <Provincia>{{ emisor.ubicacion.provincia }}</Provincia>
            <Canton>{{ emisor.ubicacion.canton }}</Canton>
            <Distrito>{{ emisor.ubicacion.distrito }}</Distrito>
            {% if emisor.ubicacion.barrio %}
            <Barrio>{{ emisor.ubicacion.barrio }}</Barrio>
            {% endif %}
            {% if emisor.ubicacion.otras_senas %}
            <OtrasSenas>{{ emisor.ubicacion.otras_senas }}</OtrasSenas>
            {% endif %}
        </Ubicacion>
        {% if emisor.telefono %}
        <Telefono>
            <CodigoPais>{{ emisor.telefono.codigo_pais }}</CodigoPais>
            <NumTelefono>{{ emisor.telefono.numero }}</NumTelefono>
        </Telefono>
        {% endif %}
        <CorreoElectronico>{{ emisor.correo_electronico }}</CorreoElectronico>
    </Emisor>
    {% if receptor %}
    <Receptor>
        <Nombre>{{ receptor.nombre }}</Nombre>
        {% if receptor.identificacion_tipo and receptor.identificacion_numero %}
        <Identificacion>
            <Tipo>{{ receptor.identificacion_tipo }}</Tipo>
            <Numero>{{ receptor.identificacion_numero }}</Numero>
        </Identificacion>
        {% endif %}
        {% if receptor.ubicacion %}
        <Ubicacion>
            <Provincia>{{ receptor.ubicacion.provincia }}</Provincia>
            <Canton>{{ receptor.ubicacion.canton }}</Canton>
            <Distrito>{{ receptor.ubicacion.distrito }}</Distrito>
            {% if receptor.ubicacion.otras_senas %}
            <OtrasSenas>{{ receptor.ubicacion.otras_senas }}</OtrasSenas>
            {% endif %}
        </Ubicacion>
        {% endif %}
        {% if receptor.correo_electronico %}
        <CorreoElectronico>{{ receptor.correo_electronico }}</CorreoElectronico>
        {% endif %}
    </Receptor>
    {% endif %}
    <CondicionVenta>{{ condicion_venta }}</CondicionVenta>
    {% if plazo_credito %}
    <PlazoCredito>{{ plazo_credito }}</PlazoCredito>
    {% endif %}
    {% for medio in medio_pago %}
    <MedioPago>{{ medio }}</MedioPago>
    {% endfor %}
    {% if detalles_servicio %}
    <DetalleServicio>
        {% for detalle in detalles_servicio %}
        <LineaDetalle>
            <NumeroLinea>{{ detalle.numero_linea }}</NumeroLinea>
            {% if detalle.codigo %}
            <Codigo>
                <Tipo>01</Tipo>
                <Codigo>{{ detalle.codigo }}</Codigo>
            </Codigo>
            {% endif %}
            <Cantidad>{{ detalle.cantidad }}</Cantidad>
            <UnidadMedida>{{ detalle.unidad_medida }}</UnidadMedida>
            <Detalle>{{ detalle.detalle }}</Detalle>
            <PrecioUnitario>{{ detalle.precio_unitario }}</PrecioUnitario>
            <MontoTotal>{{ detalle.monto_total }}</MontoTotal>
            {% if detalle.descuento_monto %}
            <Descuento>
                <MontoDescuento>{{ detalle.descuento_monto }}</MontoDescuento>
                <NaturalezaDescuento>{{ detalle.descuento_naturaleza or 'Descuento comercial' }}</NaturalezaDescuento>
            </Descuento>
            {% endif %}
            <SubTotal>{{ detalle.subtotal }}</SubTotal>
            {% if detalle.impuestos %}
            {% for impuesto in detalle.impuestos %}
            <Impuesto>
                <Codigo>{{ impuesto.codigo }}</Codigo>
                <CodigoTarifa>{{ impuesto.codigo_tarifa }}</CodigoTarifa>
                <Tarifa>{{ impuesto.tarifa }}</Tarifa>
                <Monto>{{ impuesto.monto }}</Monto>
            </Impuesto>
            {% endfor %}
            {% endif %}
            <MontoTotalLinea>{{ detalle.monto_total_linea }}</MontoTotalLinea>
        </LineaDetalle>
        {% endfor %}
    </DetalleServicio>
    {% endif %}
    <ResumenFactura>
        <CodigoTipoMoneda>
            <CodigoMoneda>{{ resumen_factura.codigo_tipo_moneda }}</CodigoMoneda>
            <TipoCambio>1.00000</TipoCambio>
        </CodigoTipoMoneda>
        {% if resumen_factura.total_servicios_gravados %}
        <TotalServGravados>{{ resumen_factura.total_servicios_gravados }}</TotalServGravados>
        {% endif %}
        {% if resumen_factura.total_servicios_exentos %}
        <TotalServExentos>{{ resumen_factura.total_servicios_exentos }}</TotalServExentos>
        {% endif %}
        {% if resumen_factura.total_servicios_exonerados %}
        <TotalServExonerado>{{ resumen_factura.total_servicios_exonerados }}</TotalServExonerado>
        {% endif %}
        {% if resumen_factura.total_mercaderias_gravadas %}
        <TotalMercanciasGravadas>{{ resumen_factura.total_mercaderias_gravadas }}</TotalMercanciasGravadas>
        {% endif %}
        {% if resumen_factura.total_mercaderias_exentas %}
        <TotalMercanciasExentas>{{ resumen_factura.total_mercaderias_exentas }}</TotalMercanciasExentas>
        {% endif %}
        {% if resumen_factura.total_mercaderias_exoneradas %}
        <TotalMercExonerada>{{ resumen_factura.total_mercaderias_exoneradas }}</TotalMercExonerada>
        {% endif %}
        {% if resumen_factura.total_gravado %}
        <TotalGravado>{{ resumen_factura.total_gravado }}</TotalGravado>
        {% endif %}
        {% if resumen_factura.total_exento %}
        <TotalExento>{{ resumen_factura.total_exento }}</TotalExento>
        {% endif %}
        {% if resumen_factura.total_exonerado %}
        <TotalExonerado>{{ resumen_factura.total_exonerado }}</TotalExonerado>
        {% endif %}
        <TotalVenta>{{ resumen_factura.total_venta }}</TotalVenta>
        {% if resumen_factura.total_descuentos %}
        <TotalDescuentos>{{ resumen_factura.total_descuentos }}</TotalDescuentos>
        {% endif %}
        <TotalVentaNeta>{{ resumen_factura.total_venta_neta }}</TotalVentaNeta>
        {% if resumen_factura.total_impuesto %}
        <TotalImpuesto>{{ resumen_factura.total_impuesto }}</TotalImpuesto>
        {% endif %}
        <TotalComprobante>{{ resumen_factura.total_comprobante }}</TotalComprobante>
    </ResumenFactura>
    <Normativa>
        <NumeroResolucion>DGT-R-48-2016</NumeroResolucion>
        <FechaResolucion>07-10-2016 01:00:00</FechaResolucion>
    </Normativa>
</FacturaElectronica>""")

    def generar_clave(self, pais: str, dia: str, mes: str, año: str, 
                     cedula_emisor: str, consecutivo: str, 
                     situacion: str = "1", codigo_seguridad: str = None) -> str:
        if not codigo_seguridad:
            codigo_seguridad = ''.join(secrets.choice(string.digits) for _ in range(8))
        
        clave = f"{pais}{dia}{mes}{año}{cedula_emisor}{consecutivo}{situacion}{codigo_seguridad}"
        return clave

    def generar_xml_factura(self, factura: FacturaElectronica) -> str:
        if not factura.clave:
            fecha = factura.fecha_emision
            factura.clave = self.generar_clave(
                pais="506",
                dia=fecha.strftime("%d"),
                mes=fecha.strftime("%m"),
                año=fecha.strftime("%y"),
                cedula_emisor=factura.emisor.identificacion_numero,
                consecutivo=factura.numero_consecutivo,
                situacion="1"
            )
        
        return self.factura_template.render(
            clave=factura.clave,
            codigo_actividad=factura.codigo_actividad,
            numero_consecutivo=factura.numero_consecutivo,
            fecha_emision=factura.fecha_emision.strftime("%Y-%m-%dT%H:%M:%S-06:00"),
            emisor=factura.emisor,
            receptor=factura.receptor,
            condicion_venta=factura.condicion_venta,
            plazo_credito=factura.plazo_credito,
            medio_pago=factura.medio_pago,
            detalles_servicio=factura.detalles_servicio,
            resumen_factura=factura.resumen_factura
        )