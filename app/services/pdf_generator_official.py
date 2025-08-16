from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from io import BytesIO
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFGeneratorOfficial:
    """
    Generador PDF oficial siguiendo el formato del Ministerio de Hacienda de Costa Rica
    Basado en facturas reales de empresas costarricenses
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='TituloFactura',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1,  # Centrado
            spaceAfter=12
        ))
        
        # Estilo para información de empresa
        self.styles.add(ParagraphStyle(
            name='InfoEmpresa',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=1,  # Centrado
            spaceAfter=6
        ))
        
        # Estilo para datos del documento
        self.styles.add(ParagraphStyle(
            name='DatosDocumento',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            alignment=0,  # Izquierda
            spaceAfter=3
        ))
        
        # Estilo para texto pequeño
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=0
        ))
    
    def generar_pdf_factura(self, xml_content: str, datos_adicionales: Dict[str, Any] = None) -> bytes:
        """
        Generar PDF de factura a partir del XML oficial
        
        Args:
            xml_content: XML de la factura
            datos_adicionales: Datos adicionales para el PDF
            
        Returns:
            bytes: Contenido del PDF generado
        """
        try:
            # Parsear XML
            datos_factura = self._parsear_xml(xml_content)
            
            # Crear PDF en memoria
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  rightMargin=20*mm, leftMargin=20*mm,
                                  topMargin=20*mm, bottomMargin=20*mm)
            
            # Construir contenido del PDF
            story = []
            
            # Encabezado de la empresa
            story.extend(self._crear_encabezado_empresa(datos_factura))
            
            # Información del documento
            story.extend(self._crear_info_documento(datos_factura))
            
            # Datos del emisor y receptor
            story.extend(self._crear_datos_emisor_receptor(datos_factura))
            
            # Detalle de productos/servicios
            story.extend(self._crear_detalle_servicios(datos_factura))
            
            # Resumen financiero
            story.extend(self._crear_resumen_financiero(datos_factura))
            
            # Pie de página con información legal
            story.extend(self._crear_pie_pagina(datos_factura))
            
            # Construir PDF
            doc.build(story)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generado exitosamente. Tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise
    
    def _parsear_xml(self, xml_content: str) -> Dict[str, Any]:
        """Parsear XML y extraer datos para el PDF"""
        try:
            # Limpiar namespace del XML para facilitar el parseo
            xml_clean = xml_content.replace(' xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica"', '')
            xml_clean = xml_clean.replace(' xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica"', '')
            
            root = ET.fromstring(xml_clean)
            
            datos = {
                'clave': self._get_text(root, 'Clave'),
                'numero_consecutivo': self._get_text(root, 'NumeroConsecutivo'),
                'fecha_emision': self._get_text(root, 'FechaEmision'),
                'codigo_actividad': self._get_text(root, 'CodigoActividadEmisor') or self._get_text(root, 'CodigoActividad'),
                'condicion_venta': self._get_text(root, 'CondicionVenta'),
                'medio_pago': [mp.text for mp in root.findall('.//MedioPago')],
                
                # Datos del emisor
                'emisor': self._parsear_emisor(root),
                
                # Datos del receptor
                'receptor': self._parsear_receptor(root),
                
                # Detalle de servicios
                'detalles': self._parsear_detalle_servicios(root),
                
                # Resumen financiero
                'resumen': self._parsear_resumen_factura(root)
            }
            
            return datos
            
        except Exception as e:
            logger.error(f"Error parseando XML: {e}")
            raise
    
    def _get_text(self, element, tag_name: str) -> str:
        """Obtener texto de un elemento XML"""
        elem = element.find(f'.//{tag_name}')
        return elem.text if elem is not None else ""
    
    def _parsear_emisor(self, root) -> Dict[str, Any]:
        """Parsear datos del emisor"""
        emisor_elem = root.find('.//Emisor')
        if emisor_elem is None:
            return {}
        
        ubicacion = {}
        ubicacion_elem = emisor_elem.find('.//Ubicacion')
        if ubicacion_elem is not None:
            ubicacion = {
                'provincia': self._get_text(ubicacion_elem, 'Provincia'),
                'canton': self._get_text(ubicacion_elem, 'Canton'),
                'distrito': self._get_text(ubicacion_elem, 'Distrito'),
                'otras_senas': self._get_text(ubicacion_elem, 'OtrasSenas')
            }
        
        telefono = {}
        telefono_elem = emisor_elem.find('.//Telefono')
        if telefono_elem is not None:
            telefono = {
                'codigo_pais': self._get_text(telefono_elem, 'CodigoPais'),
                'numero': self._get_text(telefono_elem, 'NumTelefono')
            }
        
        return {
            'nombre': self._get_text(emisor_elem, 'Nombre'),
            'nombre_comercial': self._get_text(emisor_elem, 'NombreComercial'),
            'identificacion_tipo': self._get_text(emisor_elem, 'Tipo'),
            'identificacion_numero': self._get_text(emisor_elem, 'Numero'),
            'correo_electronico': self._get_text(emisor_elem, 'CorreoElectronico'),
            'ubicacion': ubicacion,
            'telefono': telefono
        }
    
    def _parsear_receptor(self, root) -> Dict[str, Any]:
        """Parsear datos del receptor"""
        receptor_elem = root.find('.//Receptor')
        if receptor_elem is None:
            return {}
        
        return {
            'nombre': self._get_text(receptor_elem, 'Nombre'),
            'identificacion_tipo': self._get_text(receptor_elem, 'Tipo'),
            'identificacion_numero': self._get_text(receptor_elem, 'Numero'),
            'correo_electronico': self._get_text(receptor_elem, 'CorreoElectronico')
        }
    
    def _parsear_detalle_servicios(self, root) -> List[Dict[str, Any]]:
        """Parsear detalle de servicios"""
        detalles = []
        
        for linea in root.findall('.//LineaDetalle'):
            detalle = {
                'numero_linea': self._get_text(linea, 'NumeroLinea'),
                'codigo': self._get_text(linea, 'Codigo') or self._get_text(linea, 'CodigoCABYS'),
                'cantidad': self._get_text(linea, 'Cantidad'),
                'unidad_medida': self._get_text(linea, 'UnidadMedida'),
                'detalle': self._get_text(linea, 'Detalle'),
                'precio_unitario': self._get_text(linea, 'PrecioUnitario'),
                'monto_total': self._get_text(linea, 'MontoTotal'),
                'subtotal': self._get_text(linea, 'SubTotal'),
                'monto_total_linea': self._get_text(linea, 'MontoTotalLinea')
            }
            detalles.append(detalle)
        
        return detalles
    
    def _parsear_resumen_factura(self, root) -> Dict[str, Any]:
        """Parsear resumen de factura"""
        resumen_elem = root.find('.//ResumenFactura')
        if resumen_elem is None:
            return {}
        
        return {
            'codigo_moneda': self._get_text(resumen_elem, 'CodigoMoneda'),
            'tipo_cambio': self._get_text(resumen_elem, 'TipoCambio'),
            'total_venta': self._get_text(resumen_elem, 'TotalVenta'),
            'total_venta_neta': self._get_text(resumen_elem, 'TotalVentaNeta'),
            'total_impuesto': self._get_text(resumen_elem, 'TotalImpuesto'),
            'total_comprobante': self._get_text(resumen_elem, 'TotalComprobante'),
            'total_gravado': self._get_text(resumen_elem, 'TotalGravado'),
            'total_exento': self._get_text(resumen_elem, 'TotalExento')
        }
    
    def _crear_encabezado_empresa(self, datos: Dict[str, Any]) -> List:
        """Crear encabezado de la empresa"""
        story = []
        
        # Título del documento
        tipo_documento = self._obtener_tipo_documento(datos['numero_consecutivo'])
        story.append(Paragraph(f"<b>{tipo_documento}</b>", self.styles['TituloFactura']))
        
        # Información de la empresa
        emisor = datos.get('emisor', {})
        if emisor.get('nombre'):
            story.append(Paragraph(f"<b>{emisor['nombre']}</b>", self.styles['InfoEmpresa']))
        
        if emisor.get('nombre_comercial'):
            story.append(Paragraph(emisor['nombre_comercial'], self.styles['InfoEmpresa']))
        
        # Cédula jurídica
        if emisor.get('identificacion_numero'):
            story.append(Paragraph(f"Cédula Jurídica: {emisor['identificacion_numero']}", self.styles['InfoEmpresa']))
        
        # Dirección
        ubicacion = emisor.get('ubicacion', {})
        if ubicacion.get('otras_senas'):
            story.append(Paragraph(ubicacion['otras_senas'], self.styles['InfoEmpresa']))
        
        # Teléfono y email
        telefono = emisor.get('telefono', {})
        if telefono.get('numero'):
            telefono_completo = f"+{telefono.get('codigo_pais', '506')} {telefono['numero']}"
            story.append(Paragraph(f"Tel: {telefono_completo}", self.styles['InfoEmpresa']))
        
        if emisor.get('correo_electronico'):
            story.append(Paragraph(f"Email: {emisor['correo_electronico']}", self.styles['InfoEmpresa']))
        
        story.append(Spacer(1, 12))
        
        return story
    
    def _crear_info_documento(self, datos: Dict[str, Any]) -> List:
        """Crear información del documento"""
        story = []
        
        # Tabla con información del documento
        data = [
            ['Número:', datos.get('numero_consecutivo', '')],
            ['Fecha:', self._formatear_fecha(datos.get('fecha_emision', ''))],
            ['Clave:', datos.get('clave', '')],
            ['Condición de Venta:', self._obtener_condicion_venta(datos.get('condicion_venta', ''))],
            ['Medio de Pago:', ', '.join(self._obtener_medios_pago(datos.get('medio_pago', [])))]
        ]
        
        table = Table(data, colWidths=[40*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        return story
    
    def _crear_datos_emisor_receptor(self, datos: Dict[str, Any]) -> List:
        """Crear tabla con datos del emisor y receptor"""
        story = []
        
        receptor = datos.get('receptor', {})
        
        # Crear tabla de dos columnas
        data = [
            ['<b>DATOS DEL RECEPTOR</b>', ''],
            ['Nombre:', receptor.get('nombre', '')],
            ['Identificación:', f"{receptor.get('identificacion_numero', '')}"],
            ['Email:', receptor.get('correo_electronico', '')]
        ]
        
        table = Table(data, colWidths=[40*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        return story
    
    def _crear_detalle_servicios(self, datos: Dict[str, Any]) -> List:
        """Crear tabla de detalle de servicios"""
        story = []
        
        # Título de la sección
        story.append(Paragraph("<b>DETALLE DE PRODUCTOS/SERVICIOS</b>", self.styles['Heading2']))
        
        # Encabezados de la tabla
        headers = ['#', 'Descripción', 'Cant.', 'U.M.', 'Precio Unit.', 'Total Línea']
        data = [headers]
        
        # Agregar detalles
        detalles = datos.get('detalles', [])
        for detalle in detalles:
            fila = [
                detalle.get('numero_linea', ''),
                detalle.get('detalle', ''),
                self._formatear_numero(detalle.get('cantidad', '0')),
                detalle.get('unidad_medida', ''),
                self._formatear_moneda(detalle.get('precio_unitario', '0')),
                self._formatear_moneda(detalle.get('monto_total_linea', '0'))
            ]
            data.append(fila)
        
        # Crear tabla
        table = Table(data, colWidths=[10*mm, 80*mm, 15*mm, 15*mm, 25*mm, 25*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        return story
    
    def _crear_resumen_financiero(self, datos: Dict[str, Any]) -> List:
        """Crear resumen financiero"""
        story = []
        
        resumen = datos.get('resumen', {})
        
        # Tabla de resumen financiero
        data = [
            ['Subtotal:', self._formatear_moneda(resumen.get('total_venta', '0'))],
            ['Total Gravado:', self._formatear_moneda(resumen.get('total_gravado', '0'))],
            ['Total Exento:', self._formatear_moneda(resumen.get('total_exento', '0'))],
            ['Total Impuestos:', self._formatear_moneda(resumen.get('total_impuesto', '0'))],
            ['', ''],
            ['TOTAL A PAGAR:', self._formatear_moneda(resumen.get('total_comprobante', '0'))]
        ]
        
        table = Table(data, colWidths=[40*mm, 30*mm], hAlign='RIGHT')
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _crear_pie_pagina(self, datos: Dict[str, Any]) -> List:
        """Crear pie de página con información legal"""
        story = []
        
        # Código QR con la clave
        if datos.get('clave'):
            qr_code = self._crear_codigo_qr(datos['clave'])
            story.append(qr_code)
            story.append(Spacer(1, 6))
        
        # Información legal
        info_legal = [
            "Documento electrónico generado según normativa v4.4 del Ministerio de Hacienda de Costa Rica",
            f"Clave numérica: {datos.get('clave', '')}",
            "Para verificar la validez de este documento ingrese a: https://tribunet.hacienda.go.cr/ConsultaRUT/"
        ]
        
        for texto in info_legal:
            story.append(Paragraph(texto, self.styles['TextoPequeno']))
        
        return story
    
    def _crear_codigo_qr(self, clave: str) -> Drawing:
        """Crear código QR con la clave del documento"""
        qr_widget = QrCodeWidget(clave)
        bounds = qr_widget.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Escalar QR a tamaño apropiado
        qr_scale = 60  # 60 puntos de ancho
        scale = qr_scale / width
        
        drawing = Drawing(qr_scale, qr_scale)
        drawing.add(qr_widget)
        drawing.scale(scale, scale)
        
        return drawing
    
    def _obtener_tipo_documento(self, numero_consecutivo: str) -> str:
        """Obtener tipo de documento basado en el consecutivo"""
        if numero_consecutivo.startswith('01'):
            return "FACTURA ELECTRÓNICA"
        elif numero_consecutivo.startswith('02'):
            return "NOTA DE DÉBITO ELECTRÓNICA"
        elif numero_consecutivo.startswith('03'):
            return "NOTA DE CRÉDITO ELECTRÓNICA"
        elif numero_consecutivo.startswith('04'):
            return "TIQUETE ELECTRÓNICO"
        elif numero_consecutivo.startswith('05'):
            return "FACTURA DE EXPORTACIÓN ELECTRÓNICA"
        else:
            return "DOCUMENTO ELECTRÓNICO"
    
    def _obtener_condicion_venta(self, codigo: str) -> str:
        """Obtener descripción de condición de venta"""
        condiciones = {
            '01': 'Contado',
            '02': 'Crédito',
            '03': 'Consignación',
            '04': 'Apartado',
            '05': 'Arrendamiento con opción de compra',
            '99': 'Otros'
        }
        return condiciones.get(codigo, codigo)
    
    def _obtener_medios_pago(self, codigos: List[str]) -> List[str]:
        """Obtener descripción de medios de pago"""
        medios = {
            '01': 'Efectivo',
            '02': 'Tarjeta',
            '03': 'Cheque',
            '04': 'Transferencia',
            '05': 'Recaudado por terceros',
            '99': 'Otros'
        }
        return [medios.get(codigo, codigo) for codigo in codigos]
    
    def _formatear_fecha(self, fecha_str: str) -> str:
        """Formatear fecha para mostrar en PDF"""
        try:
            # Parsear fecha ISO
            if 'T' in fecha_str:
                fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00').replace('-06:00', ''))
                return fecha.strftime('%d/%m/%Y %H:%M')
            else:
                return fecha_str
        except:
            return fecha_str
    
    def _formatear_numero(self, numero_str: str) -> str:
        """Formatear número para mostrar en PDF"""
        try:
            num = float(numero_str)
            if num == int(num):
                return str(int(num))
            else:
                return f"{num:.3f}"
        except:
            return numero_str
    
    def _formatear_moneda(self, monto_str: str) -> str:
        """Formatear monto como moneda costarricense"""
        try:
            monto = float(monto_str)
            return f"CRC {monto:,.2f}"
        except:
            return f"CRC {monto_str}"

# Instancia global
pdf_generator_official = PDFGeneratorOfficial()