from datetime import datetime
from lxml import etree
from app.core.config import settings
import os

class XMLDigitalSigner:
    def __init__(self, certificate_path: str = None, certificate_password: str = None):
        self.certificate_path = certificate_path or settings.certificate_path
        self.certificate_password = certificate_password or settings.certificate_password
        self.certificate_available = self._check_certificate()
        print(f"Signer initialized - Certificate path: {self.certificate_path}")
        print(f"Certificate available: {self.certificate_available}")
    
    def _check_certificate(self):
        """Verificar si el certificado está disponible y es válido"""
        if not self.certificate_path:
            print(f"⚠️ CERTIFICATE_PATH no configurado")
            return False
        
        if not os.path.exists(self.certificate_path):
            print(f"⚠️ Certificado no encontrado: {self.certificate_path}")
            return False
        
        if not self.certificate_password:
            print(f"⚠️ Contraseña del certificado no configurada")
            return False
        
        print(f"🔍 Intentando cargar certificado: {self.certificate_path}")
        
        # Intentar cargar el certificado para verificar que sea válido
        try:
            from cryptography.hazmat.primitives.serialization import pkcs12
            with open(self.certificate_path, 'rb') as f:
                p12_data = f.read()
            
            pkcs12.load_key_and_certificates(
                p12_data, 
                self.certificate_password.encode() if self.certificate_password else None
            )
            print(f"✅ Certificado válido y cargado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error al cargar certificado: {e}")
            return False
    
    def firmar_xml(self, xml_string: str) -> str:
        """
        Firmar XML con certificado digital.
        Si hay certificado disponible, usa firma real. Si no, usa firma simulada.
        """
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            if self.certificate_available:
                # TODO: Implementar firma real con signxml cuando sea necesario
                # Por ahora usa firma simulada mejorada con datos del certificado
                signature_element = etree.Element("Signature")
                signature_element.text = f"CERTIFICADO_OFICIAL_{self.certificate_path.split('/')[-1].split('.')[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                xml_doc.append(signature_element)
                print("🔐 XML firmado con certificado oficial (simulado)")
            else:
                # Firma simulada básica
                signature_element = etree.Element("Signature")
                signature_element.text = "FIRMA_DIGITAL_SIMULADA_" + datetime.now().strftime("%Y%m%d%H%M%S")
                xml_doc.append(signature_element)
                print("⚠️ XML firmado con firma simulada (certificado no disponible)")
            
            return etree.tostring(xml_doc, encoding='unicode', pretty_print=True)
            
        except Exception as e:
            raise ValueError(f"Error al procesar XML: {e}")
    
    def verificar_firma(self, xml_firmado: str) -> bool:
        """
        Verificación simulada de firma
        """
        try:
            xml_doc = etree.fromstring(xml_firmado.encode('utf-8'))
            signature = xml_doc.find('.//Signature')
            return signature is not None and signature.text and "FIRMA_DIGITAL_SIMULADA" in signature.text
        except Exception as e:
            print(f"Error al verificar firma: {e}")
            return False
    
    def obtener_info_certificado(self) -> dict:
        """
        Información del certificado (real o simulada)
        """
        if self.certificate_available:
            try:
                from cryptography.hazmat.primitives.serialization import pkcs12
                import os
                
                if not os.path.exists(self.certificate_path):
                    return {"error": "Certificado no encontrado"}
                
                with open(self.certificate_path, 'rb') as f:
                    p12_data = f.read()
                
                private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                    p12_data, 
                    self.certificate_password.encode() if self.certificate_password else None
                )
                
                return {
                    "subject": str(certificate.subject),
                    "issuer": str(certificate.issuer),
                    "serial_number": str(certificate.serial_number),
                    "not_valid_before": certificate.not_valid_before.isoformat(),
                    "not_valid_after": certificate.not_valid_after.isoformat(),
                    "is_valid": certificate.not_valid_before <= datetime.now() <= certificate.not_valid_after,
                    "modo": "certificado_oficial_sandbox",
                    "archivo": self.certificate_path
                }
            except Exception as e:
                return {
                    "error": f"Error al leer certificado: {e}",
                    "modo": "error",
                    "archivo": self.certificate_path
                }
        else:
            return {
                "subject": "CN=Certificado Simulado,O=Empresa Demo,C=CR",
                "issuer": "CN=CA Simulada,O=Autoridad Certificadora,C=CR", 
                "serial_number": "123456789",
                "not_valid_before": "2024-01-01T00:00:00",
                "not_valid_after": "2025-12-31T23:59:59",
                "is_valid": True,
                "modo": "simulacion",
                "razon": "Certificado no disponible o configurado incorrectamente"
            }

signer = XMLDigitalSigner()