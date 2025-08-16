from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
from app.services.pdf_generator import pdf_generator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EnviarEmailRequest(BaseModel):
    destinatario: EmailStr
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    incluir_pdf: bool = True
    incluir_xml: bool = True

class EmailResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    destinatario: str
    tipo_documento: Optional[str] = None
    consecutivo: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None

@router.post("/enviar-factura/{clave}", response_model=EmailResponse, summary="Enviar Factura por Email")
async def enviar_factura_email(
    clave: str,
    email_request: EnviarEmailRequest,
    background_tasks: BackgroundTasks
):
    """
    Enviar factura por correo electrónico con XML y PDF adjuntos usando Amazon SES.
    
    - **clave**: Clave única de la factura (50 caracteres)
    - **destinatario**: Email del destinatario
    - **cc**: Lista opcional de correos en copia
    - **bcc**: Lista opcional de correos en copia oculta
    - **incluir_pdf**: Si incluir archivo PDF (default: True)
    - **incluir_xml**: Si incluir archivo XML (default: True)
    """
    try:
        # Validar clave
        if len(clave) != 50:
            raise HTTPException(
                status_code=400, 
                detail="La clave debe tener exactamente 50 caracteres"
            )
        
        # Buscar la factura (simulación - en implementación real buscarías en BD)
        # Por ahora simularemos que tenemos los datos
        datos_factura = {
            'clave': clave,
            'numero_consecutivo': clave[21:41],  # Extraer consecutivo de la clave
            'fecha_emision': '2025-08-15T20:00:00',
            'estado': 'enviada'
        }
        
        # Simular XML (en implementación real lo obtendrías de la BD)
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronicaV44">
    <Clave>{clave}</Clave>
    <NumeroConsecutivo>{datos_factura['numero_consecutivo']}</NumeroConsecutivo>
    <FechaEmision>{datos_factura['fecha_emision']}</FechaEmision>
    <Emisor>
        <Nombre>Empresa Test Completo S.A.</Nombre>
        <Identificacion>
            <Tipo>02</Tipo>
            <Numero>310277607903</Numero>
        </Identificacion>
        <Ubicacion>
            <Provincia>1</Provincia>
            <Canton>01</Canton>
            <Distrito>01</Distrito>
        </Ubicacion>
        <CorreoElectronico>facturacion@empresatest.cr</CorreoElectronico>
    </Emisor>
    <Receptor>
        <Nombre>Cliente Test</Nombre>
        <Identificacion>
            <Tipo>01</Tipo>
            <Numero>123456789</Numero>
        </Identificacion>
        <CorreoElectronico>{email_request.destinatario}</CorreoElectronico>
    </Receptor>
    <DetalleServicio>
        <LineaDetalle>
            <NumeroLinea>1</NumeroLinea>
            <Cantidad>1</Cantidad>
            <UnidadMedida>Unid</UnidadMedida>
            <Detalle>Servicio de prueba</Detalle>
            <PrecioUnitario>10000</PrecioUnitario>
            <MontoTotal>10000</MontoTotal>
            <SubTotal>10000</SubTotal>
            <MontoTotalLinea>11300</MontoTotalLinea>
        </LineaDetalle>
    </DetalleServicio>
    <ResumenFactura>
        <TotalVenta>10000</TotalVenta>
        <TotalImpuesto>1300</TotalImpuesto>
        <TotalComprobante>11300</TotalComprobante>
    </ResumenFactura>
</FacturaElectronica>'''
        
        # Generar PDF si se solicita
        pdf_content = None
        if email_request.incluir_pdf:
            try:
                pdf_content = pdf_generator.generar_pdf_factura(xml_content, datos_factura)
                logger.info(f"✅ PDF generado para factura {clave}")
            except Exception as e:
                logger.error(f"❌ Error generando PDF: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generando PDF: {str(e)}"
                )
        
        # Enviar email en background
        background_tasks.add_task(
            enviar_email_background,
            email_request.destinatario,
            datos_factura,
            xml_content if email_request.incluir_xml else None,
            pdf_content,
            email_request.cc,
            email_request.bcc
        )
        
        return EmailResponse(
            success=True,
            destinatario=email_request.destinatario,
            tipo_documento=pdf_generator.obtener_tipo_documento(datos_factura['numero_consecutivo']),
            consecutivo=datos_factura['numero_consecutivo'],
            message="Email enviado en segundo plano"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en enviar_factura_email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

async def enviar_email_background(
    destinatario: str,
    datos_factura: dict,
    xml_content: Optional[str],
    pdf_content: Optional[bytes],
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
):
    """Tarea en background para enviar el email"""
    try:
        resultado = await email_service.enviar_factura_email(
            destinatario=destinatario,
            datos_factura=datos_factura,
            xml_content=xml_content or "",
            pdf_content=pdf_content or b"",
            cc=cc,
            bcc=bcc
        )
        
        if resultado['success']:
            logger.info(f"✅ Email enviado exitosamente a {destinatario}. MessageId: {resultado.get('message_id')}")
        else:
            logger.error(f"❌ Error enviando email a {destinatario}: {resultado.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error en tarea background de email: {e}")

@router.get("/configuracion", summary="Verificar Configuración SES")
async def verificar_configuracion_ses():
    """
    Verificar la configuración de Amazon SES.
    
    Retorna información sobre la configuración actual, cuotas y estadísticas.
    """
    try:
        config = await email_service.verificar_configuracion()
        return config
    except Exception as e:
        logger.error(f"❌ Error verificando configuración SES: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verificando configuración: {str(e)}"
        )

@router.post("/test", summary="Enviar Email de Prueba")
async def enviar_email_prueba(
    destinatario: EmailStr = Query(..., description="Email de destino para la prueba"),
    background_tasks: BackgroundTasks = None
):
    """
    Enviar un email de prueba para verificar la configuración de SES.
    """
    try:
        # Datos de prueba
        datos_prueba = {
            'clave': '50624112024310277607901001000012345678901234567890',
            'numero_consecutivo': '01001000012345678901',
            'fecha_emision': '2025-08-15T20:00:00',
            'estado': 'prueba'
        }
        
        xml_prueba = '''<?xml version="1.0" encoding="UTF-8"?>
<FacturaElectronica xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronicaV44">
    <Clave>50624112024310277607901001000012345678901234567890</Clave>
    <NumeroConsecutivo>01001000012345678901</NumeroConsecutivo>
    <FechaEmision>2025-08-15T20:00:00</FechaEmision>
    <Emisor>
        <Nombre>Empresa de Prueba S.A.</Nombre>
        <CorreoElectronico>noreply@simplexityla.com</CorreoElectronico>
    </Emisor>
    <DetalleServicio>
        <LineaDetalle>
            <NumeroLinea>1</NumeroLinea>
            <Cantidad>1</Cantidad>
            <Detalle>Email de prueba del sistema</Detalle>
            <PrecioUnitario>1000</PrecioUnitario>
            <MontoTotalLinea>1130</MontoTotalLinea>
        </LineaDetalle>
    </DetalleServicio>
    <ResumenFactura>
        <TotalComprobante>1130</TotalComprobante>
    </ResumenFactura>
</FacturaElectronica>'''
        
        # Generar PDF de prueba
        pdf_prueba = pdf_generator.generar_pdf_factura(xml_prueba, datos_prueba)
        
        # Enviar email
        resultado = await email_service.enviar_factura_email(
            destinatario=destinatario,
            datos_factura=datos_prueba,
            xml_content=xml_prueba,
            pdf_content=pdf_prueba
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de prueba: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando email de prueba: {str(e)}"
        )