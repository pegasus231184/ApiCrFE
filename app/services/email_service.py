import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Inicializar servicio de correo con Amazon SES"""
        self.aws_region = settings.aws_region
        self.from_email = settings.ses_from_email
        self.from_name = settings.ses_from_name
        
        try:
            # Inicializar cliente SES
            self.ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            logger.info(f"✅ Amazon SES client initialized for region: {self.aws_region}")
        except Exception as e:
            logger.error(f"❌ Error initializing SES client: {e}")
            self.ses_client = None
    
    async def enviar_factura_email(
        self,
        destinatario: str,
        datos_factura: Dict[str, Any],
        xml_content: str,
        pdf_content: bytes,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enviar factura por correo electrónico con XML y PDF adjuntos
        
        Args:
            destinatario: Email del destinatario
            datos_factura: Datos de la factura
            xml_content: Contenido XML de la factura
            pdf_content: Contenido PDF generado
            cc: Lista de correos en copia
            bcc: Lista de correos en copia oculta
            
        Returns:
            Dict con resultado del envío
        """
        if not self.ses_client:
            return {
                'success': False,
                'error': 'Amazon SES client not configured',
                'message_id': None
            }
        
        try:
            # Crear mensaje MIME
            msg = MIMEMultipart()
            
            # Headers del correo (usando formato simple para evitar problemas de encoding)
            msg['From'] = self.from_email
            msg['To'] = destinatario
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Asunto personalizado según tipo de documento
            tipo_doc = self.obtener_tipo_documento(datos_factura.get('numero_consecutivo', ''))
            msg['Subject'] = f"{tipo_doc} - {datos_factura.get('numero_consecutivo', 'N/A')}"
            
            # Cuerpo del correo
            body_html = self.crear_cuerpo_email(datos_factura, tipo_doc)
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))
            
            # Adjuntar XML si se proporciona
            if xml_content:
                xml_attachment = MIMEApplication(xml_content.encode('utf-8'), _subtype='xml')
                xml_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=f"factura_{datos_factura.get('numero_consecutivo', 'N/A')}.xml"
                )
                msg.attach(xml_attachment)
            
            # Adjuntar PDF si se proporciona
            if pdf_content and len(pdf_content) > 0:
                pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition', 
                    'attachment', 
                    filename=f"factura_{datos_factura.get('numero_consecutivo', 'N/A')}.pdf"
                )
                msg.attach(pdf_attachment)
            
            # Preparar destinatarios
            destinations = [destinatario]
            if cc:
                destinations.extend(cc)
            if bcc:
                destinations.extend(bcc)
            
            # Enviar correo usando send_raw_email para adjuntos
            response = self.ses_client.send_raw_email(
                Source=self.from_email,
                Destinations=destinations,
                RawMessage={'Data': msg.as_string()}
            )
            
            message_id = response['MessageId']
            logger.info(f"✅ Email sent successfully. MessageId: {message_id}")
            
            return {
                'success': True,
                'message_id': message_id,
                'destinatario': destinatario,
                'tipo_documento': tipo_doc,
                'consecutivo': datos_factura.get('numero_consecutivo')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"❌ SES ClientError: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error': f"SES Error: {error_code}",
                'message': error_message,
                'message_id': None
            }
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            return {
                'success': False,
                'error': 'AWS credentials not configured',
                'message': 'Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY',
                'message_id': None
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email: {e}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'message': str(e),
                'message_id': None
            }
    
    def obtener_tipo_documento(self, consecutivo: str) -> str:
        """Obtener tipo de documento basado en el consecutivo"""
        if consecutivo.startswith('01'):
            return "Factura Electrónica"
        elif consecutivo.startswith('02'):
            return "Nota de Débito"
        elif consecutivo.startswith('03'):
            return "Nota de Crédito"
        elif consecutivo.startswith('04'):
            return "Tiquete Electrónico"
        elif consecutivo.startswith('05'):
            return "Factura de Exportación"
        else:
            return "Documento Electrónico"
    
    def crear_cuerpo_email(self, datos_factura: Dict[str, Any], tipo_doc: str) -> str:
        """Crear cuerpo HTML del correo electrónico"""
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                .header {{ 
                    background-color: #1f4e79; 
                    color: white; 
                    padding: 20px; 
                    text-align: center; 
                    border-radius: 5px 5px 0 0; 
                }}
                .content {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 0 0 5px 5px; 
                }}
                .info-box {{ 
                    background-color: white; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-left: 4px solid #1f4e79; 
                    border-radius: 3px; 
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 20px; 
                    font-size: 12px; 
                    color: #666; 
                }}
                .clave {{ 
                    font-family: monospace; 
                    background-color: #e9ecef; 
                    padding: 5px; 
                    border-radius: 3px; 
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{tipo_doc}</h1>
                <p>Sistema de Facturación Electrónica Costa Rica v4.4</p>
            </div>
            
            <div class="content">
                <h2>Estimado(a) Cliente,</h2>
                
                <p>Le adjuntamos su <strong>{tipo_doc.lower()}</strong> en formato electrónico, 
                según la normativa vigente del Ministerio de Hacienda de Costa Rica.</p>
                
                <div class="info-box">
                    <h3>Información del Documento</h3>
                    <p><strong>Consecutivo:</strong> {datos_factura.get('numero_consecutivo', 'N/A')}</p>
                    <p><strong>Fecha de Emisión:</strong> {datos_factura.get('fecha_emision', 'N/A')[:19]}</p>
                    <p><strong>Clave:</strong> <span class="clave">{datos_factura.get('clave', 'N/A')}</span></p>
                    <p><strong>Estado:</strong> {datos_factura.get('estado', 'N/A').title()}</p>
                </div>
                
                <div class="info-box">
                    <h3>Archivos Adjuntos</h3>
                    <ul>
                        <li><strong>XML:</strong> Documento electrónico oficial para validación en Hacienda</li>
                        <li><strong>PDF:</strong> Representación imprimible del documento</li>
                    </ul>
                </div>
                
                <p><strong>Importante:</strong> Conserve estos archivos para sus registros contables y 
                para cualquier verificación que pueda requerir el Ministerio de Hacienda.</p>
                
                <p>Si tiene alguna consulta sobre este documento, no dude en contactarnos.</p>
                
                <p>Saludos cordiales,<br>
                <strong>Equipo de Facturación Electrónica</strong></p>
            </div>
            
            <div class="footer">
                <p>Este correo fue generado automáticamente por el Sistema de Facturación Electrónica CR v4.4</p>
                <p>Para soporte técnico: allan.martinez@simplexityla.com</p>
            </div>
        </body>
        </html>
        '''
        return html
    
    async def verificar_configuracion(self) -> Dict[str, Any]:
        """Verificar configuración de Amazon SES"""
        if not self.ses_client:
            return {
                'configurado': False,
                'error': 'Cliente SES no inicializado'
            }
        
        try:
            # Verificar cuota de envío
            response = self.ses_client.get_send_quota()
            
            # Verificar estadísticas de envío
            stats = self.ses_client.get_send_statistics()
            
            return {
                'configurado': True,
                'region': self.aws_region,
                'from_email': self.from_email,
                'cuota_diaria': response.get('Max24HourSend'),
                'enviados_24h': response.get('SentLast24Hours'),
                'tasa_envio': response.get('MaxSendRate'),
                'estadisticas_disponibles': len(stats.get('SendDataPoints', []))
            }
            
        except Exception as e:
            return {
                'configurado': False,
                'error': str(e)
            }

# Instancia global del servicio de email
email_service = EmailService()