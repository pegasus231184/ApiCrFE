import os
from lxml import etree
from signxml import XMLSigner, XMLVerifier
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from datetime import datetime
from app.core.config import settings

class XMLDigitalSigner:
    def __init__(self, certificate_path: str = None, certificate_password: str = None):
        self.certificate_path = certificate_path or settings.certificate_path
        self.certificate_password = certificate_password or settings.certificate_password
        self.private_key = None
        self.certificate = None
        self._load_certificate()
    
    def _load_certificate(self):
        if not self.certificate_path or not os.path.exists(self.certificate_path):
            raise FileNotFoundError(f"Certificado no encontrado en: {self.certificate_path}")
        
        with open(self.certificate_path, 'rb') as cert_file:
            p12_data = cert_file.read()
        
        try:
            self.private_key, self.certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data, 
                self.certificate_password.encode() if self.certificate_password else None
            )
        except Exception as e:
            raise ValueError(f"Error al cargar el certificado: {e}")
    
    def firmar_xml(self, xml_string: str) -> str:
        if not self.private_key or not self.certificate:
            raise ValueError("Certificado no cargado correctamente")
        
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            
            signed_root = XMLSigner(
                method=XMLSigner.Methods.enveloped,
                signature_algorithm="rsa-sha256",
                digest_algorithm="sha256",
                c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
            ).sign(
                xml_doc, 
                key=self.private_key,
                cert=self.certificate
            )
            
            return etree.tostring(signed_root, encoding='unicode', pretty_print=True)
            
        except Exception as e:
            raise ValueError(f"Error al firmar el XML: {e}")
    
    def verificar_firma(self, xml_firmado: str) -> bool:
        try:
            xml_doc = etree.fromstring(xml_firmado.encode('utf-8'))
            XMLVerifier().verify(xml_doc).signed_xml
            return True
        except Exception as e:
            print(f"Error al verificar firma: {e}")
            return False
    
    def obtener_info_certificado(self) -> dict:
        if not self.certificate:
            return {}
        
        return {
            "subject": self.certificate.subject.rfc4514_string(),
            "issuer": self.certificate.issuer.rfc4514_string(),
            "serial_number": str(self.certificate.serial_number),
            "not_valid_before": self.certificate.not_valid_before.isoformat(),
            "not_valid_after": self.certificate.not_valid_after.isoformat(),
            "is_valid": self.certificate.not_valid_before <= datetime.now() <= self.certificate.not_valid_after
        }

signer = XMLDigitalSigner()