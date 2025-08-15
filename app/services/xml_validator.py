from lxml import etree
import os
from typing import Tuple, List
from app.core.config import settings

class XMLValidator:
    def __init__(self):
        self.xsd_path = os.path.join(os.path.dirname(__file__), "..", "xsd")
        self.esquemas = {
            "factura": "FacturaElectronicaV44.xsd",
            "nota_credito": "NotaCreditoElectronicaV44.xsd",
            "nota_debito": "NotaDebitoElectronicaV44.xsd", 
            "tiquete": "TiqueteElectronicoV44.xsd",
            "factura_exportacion": "FacturaElectronicaExportacionV44.xsd"
        }
    
    def validar_contra_xsd(self, xml_string: str, tipo_documento: str) -> Tuple[bool, List[str]]:
        """
        Validar un XML contra el esquema XSD correspondiente
        
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_errores)
        """
        if tipo_documento not in self.esquemas:
            return False, [f"Tipo de documento no soportado: {tipo_documento}"]
        
        xsd_file = self.esquemas[tipo_documento]
        xsd_path = os.path.join(self.xsd_path, xsd_file)
        
        if not os.path.exists(xsd_path):
            return False, [f"Esquema XSD no encontrado: {xsd_path}"]
        
        try:
            # Cargar esquema XSD
            with open(xsd_path, 'r', encoding='utf-8') as f:
                xsd_doc = etree.parse(f)
                xsd_schema = etree.XMLSchema(xsd_doc)
            
            # Parsear XML a validar
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            # Validar
            if xsd_schema.validate(xml_doc):
                return True, []
            else:
                errores = []
                for error in xsd_schema.error_log:
                    errores.append(f"Línea {error.line}: {error.message}")
                return False, errores
                
        except etree.XMLSyntaxError as e:
            return False, [f"Error de sintaxis XML: {str(e)}"]
        except Exception as e:
            return False, [f"Error durante validación: {str(e)}"]
    
    def validar_estructura_basica(self, xml_string: str) -> Tuple[bool, List[str]]:
        """
        Validación básica de estructura XML sin esquema
        """
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            errores = []
            
            # Verificar elementos básicos requeridos
            elementos_requeridos = ['Clave', 'NumeroConsecutivo', 'FechaEmision', 'Emisor']
            
            for elemento in elementos_requeridos:
                if xml_doc.find(f".//{elemento}") is None:
                    errores.append(f"Elemento requerido no encontrado: {elemento}")
            
            # Verificar formato de clave
            clave_elem = xml_doc.find('.//Clave')
            if clave_elem is not None:
                clave = clave_elem.text
                if not clave or len(clave) != 50:
                    errores.append("La clave debe tener exactamente 50 caracteres")
                elif not clave.isdigit():
                    errores.append("La clave debe contener solo números")
            
            return len(errores) == 0, errores
            
        except etree.XMLSyntaxError as e:
            return False, [f"Error de sintaxis XML: {str(e)}"]
        except Exception as e:
            return False, [f"Error durante validación: {str(e)}"]
    
    def extraer_datos_basicos(self, xml_string: str) -> dict:
        """
        Extraer datos básicos de un XML de documento electrónico
        """
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            # Remover namespace para simplificar búsqueda
            for elem in xml_doc.getiterator():
                if not hasattr(elem.tag, 'find'): continue
                i = elem.tag.find('}')
                if i >= 0:
                    elem.tag = elem.tag[i+1:]
            
            datos = {}
            
            # Extraer datos básicos
            elementos = {
                'clave': './/Clave',
                'numero_consecutivo': './/NumeroConsecutivo', 
                'fecha_emision': './/FechaEmision',
                'emisor_nombre': './/Emisor/Nombre',
                'emisor_cedula': './/Emisor/Identificacion/Numero',
                'receptor_nombre': './/Receptor/Nombre',
                'total_comprobante': './/ResumenFactura/TotalComprobante'
            }
            
            for campo, xpath in elementos.items():
                elem = xml_doc.find(xpath)
                datos[campo] = elem.text if elem is not None else None
            
            return datos
            
        except Exception as e:
            return {'error': f"Error extrayendo datos: {str(e)}"}
    
    def listar_esquemas_disponibles(self) -> dict:
        """
        Listar esquemas XSD disponibles
        """
        esquemas_info = {}
        
        for tipo, archivo in self.esquemas.items():
            ruta_completa = os.path.join(self.xsd_path, archivo)
            esquemas_info[tipo] = {
                'archivo': archivo,
                'ruta': ruta_completa,
                'existe': os.path.exists(ruta_completa)
            }
        
        return esquemas_info