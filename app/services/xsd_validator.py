from lxml import etree
import logging
from typing import Dict, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)

class XSDValidator:
    """
    Validador XML contra el esquema XSD oficial v4.4 del Ministerio de Hacienda
    """
    
    def __init__(self, xsd_path: str = None):
        """
        Inicializar validador XSD
        
        Args:
            xsd_path: Ruta al archivo XSD. Si no se especifica, usa el oficial v4.4
        """
        if xsd_path is None:
            # Ruta por defecto al XSD oficial v4.4
            xsd_path = "Referencias/FacturaElectronica_V4.4.xsd.xml"
        
        self.xsd_path = xsd_path
        self.schema = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Cargar el esquema XSD"""
        try:
            if not os.path.exists(self.xsd_path):
                logger.warning(f"Archivo XSD no encontrado en: {self.xsd_path}")
                logger.warning("Validación XSD deshabilitada")
                return
            
            with open(self.xsd_path, 'r', encoding='utf-8') as xsd_file:
                xsd_doc = etree.parse(xsd_file)
                self.schema = etree.XMLSchema(xsd_doc)
            
            logger.info(f"Esquema XSD v4.4 cargado exitosamente desde: {self.xsd_path}")
            
        except Exception as e:
            logger.error(f"Error cargando esquema XSD: {e}")
            logger.warning("Validación XSD deshabilitada")
            self.schema = None
    
    def validate_xml(self, xml_content: str) -> Tuple[bool, List[str]]:
        """
        Validar XML contra el esquema XSD
        
        Args:
            xml_content: Contenido XML a validar
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_de_errores)
        """
        if self.schema is None:
            return True, ["Validación XSD no disponible - esquema no cargado"]
        
        try:
            # Parsear XML
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            
            # Validar contra esquema
            is_valid = self.schema.validate(xml_doc)
            
            if is_valid:
                logger.info("XML válido según esquema XSD v4.4")
                return True, []
            else:
                # Recopilar errores
                errors = []
                for error in self.schema.error_log:
                    error_msg = f"Línea {error.line}: {error.message}"
                    errors.append(error_msg)
                    logger.error(f"Error XSD: {error_msg}")
                
                return False, errors
                
        except etree.XMLSyntaxError as e:
            error_msg = f"Error de sintaxis XML: {e}"
            logger.error(error_msg)
            return False, [error_msg]
        
        except Exception as e:
            error_msg = f"Error validando XML: {e}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def validate_and_report(self, xml_content: str) -> Dict[str, any]:
        """
        Validar XML y retornar reporte detallado
        
        Args:
            xml_content: Contenido XML a validar
            
        Returns:
            Dict con resultado de validación
        """
        is_valid, errors = self.validate_xml(xml_content)
        
        return {
            'valido': is_valid,
            'errores': errors,
            'total_errores': len(errors),
            'esquema_disponible': self.schema is not None,
            'esquema_path': self.xsd_path
        }
    
    def get_schema_info(self) -> Dict[str, any]:
        """
        Obtener información sobre el esquema cargado
        
        Returns:
            Dict con información del esquema
        """
        return {
            'esquema_cargado': self.schema is not None,
            'ruta_xsd': self.xsd_path,
            'version': '4.4' if self.schema else None,
            'namespace': 'https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica' if self.schema else None
        }

# Instancia global del validador
xsd_validator = XSDValidator()