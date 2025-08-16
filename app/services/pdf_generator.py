from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from io import BytesIO
from datetime import datetime
from typing import Dict, Any
import xml.etree.ElementTree as ET

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1f4e79'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=HexColor('#1f4e79'),
            alignment=TA_LEFT,
            spaceAfter=10
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT
        )
        
        self.right_style = ParagraphStyle(
            'CustomRight',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        )
    
    def generar_pdf_factura(self, xml_content: str, datos_factura: Dict[str, Any]) -> bytes:
        """Generar PDF de factura a partir del XML y datos"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=inch, leftMargin=inch,
                              topMargin=inch, bottomMargin=inch)
        
        # Parsear XML para extraer datos
        root = ET.fromstring(xml_content)
        ns = {'fe': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronicaV44'}
        
        # Construir contenido del PDF
        story = []
        
        # Título principal
        tipo_doc = self.obtener_tipo_documento(datos_factura.get('numero_consecutivo', ''))
        story.append(Paragraph(f"{tipo_doc}", self.title_style))
        story.append(Spacer(1, 20))
        
        # Información de la empresa emisora
        story.append(Paragraph("INFORMACIÓN DEL EMISOR", self.header_style))
        emisor_data = self.extraer_datos_emisor(root, ns)
        story.extend(self.crear_seccion_emisor(emisor_data))
        story.append(Spacer(1, 15))
        
        # Información del receptor
        if root.find('.//fe:Receptor', ns) is not None:
            story.append(Paragraph("INFORMACIÓN DEL RECEPTOR", self.header_style))
            receptor_data = self.extraer_datos_receptor(root, ns)
            story.extend(self.crear_seccion_receptor(receptor_data))
            story.append(Spacer(1, 15))
        
        # Detalles de la factura
        story.append(Paragraph("INFORMACIÓN DE LA FACTURA", self.header_style))
        info_factura = [
            ['Clave:', datos_factura.get('clave', 'N/A')],
            ['Consecutivo:', datos_factura.get('numero_consecutivo', 'N/A')],
            ['Fecha Emisión:', datos_factura.get('fecha_emision', 'N/A')[:19]],
            ['Estado:', datos_factura.get('estado', 'N/A')]
        ]
        
        info_table = Table(info_factura, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Detalles de servicios/productos
        story.append(Paragraph("DETALLE DE SERVICIOS/PRODUCTOS", self.header_style))
        detalles_table = self.crear_tabla_detalles(root, ns)
        story.append(detalles_table)
        story.append(Spacer(1, 20))
        
        # Resumen financiero
        story.append(Paragraph("RESUMEN FINANCIERO", self.header_style))
        resumen_table = self.crear_tabla_resumen(root, ns)
        story.append(resumen_table)
        story.append(Spacer(1, 30))
        
        # Pie de página
        story.append(Paragraph("Documento generado automáticamente por API Facturación Electrónica CR", 
                             self.normal_style))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                             self.normal_style))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def obtener_tipo_documento(self, consecutivo: str) -> str:
        """Obtener tipo de documento basado en el consecutivo"""
        if consecutivo.startswith('01'):
            return "FACTURA ELECTRÓNICA"
        elif consecutivo.startswith('02'):
            return "NOTA DE DÉBITO"
        elif consecutivo.startswith('03'):
            return "NOTA DE CRÉDITO"
        elif consecutivo.startswith('04'):
            return "TIQUETE ELECTRÓNICO"
        elif consecutivo.startswith('05'):
            return "FACTURA DE EXPORTACIÓN"
        else:
            return "DOCUMENTO ELECTRÓNICO"
    
    def extraer_datos_emisor(self, root, ns):
        """Extraer datos del emisor del XML"""
        emisor = root.find('.//fe:Emisor', ns)
        if emisor is None:
            return {}
        
        return {
            'nombre': emisor.find('fe:Nombre', ns).text if emisor.find('fe:Nombre', ns) is not None else 'N/A',
            'identificacion': self.get_identificacion(emisor, ns),
            'ubicacion': self.get_ubicacion(emisor, ns),
            'correo': emisor.find('fe:CorreoElectronico', ns).text if emisor.find('fe:CorreoElectronico', ns) is not None else 'N/A'
        }
    
    def extraer_datos_receptor(self, root, ns):
        """Extraer datos del receptor del XML"""
        receptor = root.find('.//fe:Receptor', ns)
        if receptor is None:
            return {}
        
        return {
            'nombre': receptor.find('fe:Nombre', ns).text if receptor.find('fe:Nombre', ns) is not None else 'N/A',
            'identificacion': self.get_identificacion(receptor, ns),
            'ubicacion': self.get_ubicacion(receptor, ns),
            'correo': receptor.find('fe:CorreoElectronico', ns).text if receptor.find('fe:CorreoElectronico', ns) is not None else 'N/A'
        }
    
    def get_identificacion(self, elemento, ns):
        """Obtener identificación de un elemento"""
        id_elem = elemento.find('fe:Identificacion', ns)
        if id_elem is not None:
            tipo = id_elem.find('fe:Tipo', ns)
            numero = id_elem.find('fe:Numero', ns)
            if tipo is not None and numero is not None:
                return f"{tipo.text} - {numero.text}"
        return 'N/A'
    
    def get_ubicacion(self, elemento, ns):
        """Obtener ubicación de un elemento"""
        ubicacion = elemento.find('fe:Ubicacion', ns)
        if ubicacion is not None:
            provincia = ubicacion.find('fe:Provincia', ns)
            canton = ubicacion.find('fe:Canton', ns)
            distrito = ubicacion.find('fe:Distrito', ns)
            
            if all(x is not None for x in [provincia, canton, distrito]):
                return f"Provincia: {provincia.text}, Cantón: {canton.text}, Distrito: {distrito.text}"
        return 'N/A'
    
    def crear_seccion_emisor(self, datos):
        """Crear sección de datos del emisor"""
        seccion = []
        info_emisor = [
            ['Nombre:', datos.get('nombre', 'N/A')],
            ['Identificación:', datos.get('identificacion', 'N/A')],
            ['Ubicación:', datos.get('ubicacion', 'N/A')],
            ['Correo:', datos.get('correo', 'N/A')]
        ]
        
        emisor_table = Table(info_emisor, colWidths=[2*inch, 4*inch])
        emisor_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        seccion.append(emisor_table)
        return seccion
    
    def crear_seccion_receptor(self, datos):
        """Crear sección de datos del receptor"""
        seccion = []
        info_receptor = [
            ['Nombre:', datos.get('nombre', 'N/A')],
            ['Identificación:', datos.get('identificacion', 'N/A')],
            ['Ubicación:', datos.get('ubicacion', 'N/A')],
            ['Correo:', datos.get('correo', 'N/A')]
        ]
        
        receptor_table = Table(info_receptor, colWidths=[2*inch, 4*inch])
        receptor_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        seccion.append(receptor_table)
        return seccion
    
    def crear_tabla_detalles(self, root, ns):
        """Crear tabla de detalles de productos/servicios"""
        detalles = root.findall('.//fe:LineaDetalle', ns)
        
        headers = ['#', 'Cantidad', 'Descripción', 'Precio Unit.', 'Total Línea']
        data = [headers]
        
        for detalle in detalles:
            numero = detalle.find('fe:NumeroLinea', ns).text if detalle.find('fe:NumeroLinea', ns) is not None else '1'
            cantidad = detalle.find('fe:Cantidad', ns).text if detalle.find('fe:Cantidad', ns) is not None else '1'
            descripcion = detalle.find('fe:Detalle', ns).text if detalle.find('fe:Detalle', ns) is not None else 'N/A'
            precio = detalle.find('fe:PrecioUnitario', ns).text if detalle.find('fe:PrecioUnitario', ns) is not None else '0'
            total = detalle.find('fe:MontoTotalLinea', ns).text if detalle.find('fe:MontoTotalLinea', ns) is not None else '0'
            
            data.append([numero, cantidad, descripcion, f"₡{precio}", f"₡{total}"])
        
        table = Table(data, colWidths=[0.5*inch, 0.8*inch, 3*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        
        return table
    
    def crear_tabla_resumen(self, root, ns):
        """Crear tabla de resumen financiero"""
        resumen = root.find('.//fe:ResumenFactura', ns)
        if resumen is None:
            return Table([['No hay datos de resumen disponibles']])
        
        total_venta = resumen.find('fe:TotalVenta', ns)
        total_impuesto = resumen.find('fe:TotalImpuesto', ns)
        total_comprobante = resumen.find('fe:TotalComprobante', ns)
        
        data = []
        if total_venta is not None:
            data.append(['Subtotal:', f"₡{total_venta.text}"])
        if total_impuesto is not None:
            data.append(['Impuestos:', f"₡{total_impuesto.text}"])
        if total_comprobante is not None:
            data.append(['TOTAL:', f"₡{total_comprobante.text}"])
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        return table

# Instancia global del generador de PDF
pdf_generator = PDFGenerator()