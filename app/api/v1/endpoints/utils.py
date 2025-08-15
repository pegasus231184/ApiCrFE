from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any
from app.services.xml_signer_simple import signer
from app.services.xml_validator import XMLValidator
from app.services.hacienda_client import HaciendaClient
from lxml import etree

router = APIRouter()
xml_validator = XMLValidator()

@router.post("/firmar", summary="Firmar Documento XML")
async def firmar_xml(xml_file: UploadFile = File(...)):
    """
    Firmar digitalmente un documento XML.
    
    - **xml_file**: Archivo XML a firmar
    """
    if not xml_file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un XML")
    
    try:
        xml_content = await xml_file.read()
        xml_string = xml_content.decode('utf-8')
        
        xml_firmado = signer.firmar_xml(xml_string)
        
        return {
            "archivo_original": xml_file.filename,
            "firmado": True,
            "xml_firmado": xml_firmado,
            "mensaje": "Documento firmado exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al firmar XML: {str(e)}")

@router.post("/validar", summary="Validar XML contra Esquema")
async def validar_xml(
    xml_file: UploadFile = File(...),
    tipo_documento: str = "factura"
):
    """
    Validar un documento XML contra los esquemas XSD oficiales.
    
    - **xml_file**: Archivo XML a validar
    - **tipo_documento**: Tipo de documento (factura, nota_credito, nota_debito, tiquete)
    """
    if not xml_file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un XML")
    
    try:
        xml_content = await xml_file.read()
        xml_string = xml_content.decode('utf-8')
        
        es_valido, errores = xml_validator.validar_contra_xsd(xml_string, tipo_documento)
        
        return {
            "archivo": xml_file.filename,
            "tipo_documento": tipo_documento,
            "valido": es_valido,
            "errores": errores if not es_valido else [],
            "mensaje": "XML válido" if es_valido else "XML contiene errores"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar XML: {str(e)}")

@router.post("/verificar-firma", summary="Verificar Firma Digital")
async def verificar_firma(xml_file: UploadFile = File(...)):
    """
    Verificar la firma digital de un documento XML.
    """
    if not xml_file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un XML")
    
    try:
        xml_content = await xml_file.read()
        xml_string = xml_content.decode('utf-8')
        
        es_valida = signer.verificar_firma(xml_string)
        
        return {
            "archivo": xml_file.filename,
            "firma_valida": es_valida,
            "mensaje": "Firma válida" if es_valida else "Firma inválida o no encontrada"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar firma: {str(e)}")

@router.get("/info-certificado", summary="Información del Certificado")
async def info_certificado():
    """
    Obtener información del certificado digital configurado.
    """
    try:
        info = signer.obtener_info_certificado()
        return {
            "certificado_configurado": bool(info),
            "informacion": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener info del certificado: {str(e)}")

@router.get("/esquemas", summary="Listar Esquemas XSD Disponibles")
async def listar_esquemas():
    """
    Listar los esquemas XSD disponibles para validación.
    """
    esquemas = {
        "factura": "FacturaElectronicaV44.xsd",
        "nota_credito": "NotaCreditoElectronicaV44.xsd", 
        "nota_debito": "NotaDebitoElectronicaV44.xsd",
        "tiquete": "TiqueteElectronicoV44.xsd",
        "factura_exportacion": "FacturaElectronicaExportacionV44.xsd"
    }
    
    return {
        "version": "4.4",
        "esquemas_disponibles": esquemas,
        "url_oficial": "https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.4/"
    }

@router.post("/generar-clave", summary="Generar Clave de Documento")
async def generar_clave(
    cedula_emisor: str,
    tipo_documento: str,
    fecha_emision: str = None
):
    """
    Generar una clave única para un documento electrónico.
    
    - **cedula_emisor**: Cédula del emisor (persona física o jurídica)
    - **tipo_documento**: 01=Factura, 02=ND, 03=NC, 04=Tiquete
    - **fecha_emision**: Fecha en formato YYYY-MM-DD (opcional, usa fecha actual)
    """
    from app.services.xml_generator import XMLGenerator
    from datetime import datetime
    
    generator = XMLGenerator()
    
    if fecha_emision:
        try:
            fecha = datetime.strptime(fecha_emision, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido, use YYYY-MM-DD")
    else:
        fecha = datetime.now()
    
    # Generar consecutivo de ejemplo
    import uuid
    consecutivo_base = {
        "01": "00100001010000000001",  # Factura
        "02": "00200001010000000001",  # Nota Débito  
        "03": "00300001010000000001",  # Nota Crédito
        "04": "00400001010000000001"   # Tiquete
    }
    
    if tipo_documento not in consecutivo_base:
        raise HTTPException(status_code=400, detail="Tipo de documento inválido")
    
    consecutivo = f"{consecutivo_base[tipo_documento]}{str(uuid.uuid4().int)[:8]}"
    
    clave = generator.generar_clave(
        pais="506",
        dia=fecha.strftime("%d"),
        mes=fecha.strftime("%m"),
        año=fecha.strftime("%y"),
        cedula_emisor=cedula_emisor,
        consecutivo=consecutivo,
        situacion="1"
    )
    
    return {
        "clave": clave,
        "consecutivo": consecutivo,
        "fecha_emision": fecha.isoformat(),
        "tipo_documento": tipo_documento,
        "cedula_emisor": cedula_emisor
    }

@router.get("/test-hacienda", summary="Probar Conexión con Hacienda")
async def test_hacienda():
    """
    Probar la autenticación y conexión con el API de Hacienda.
    """
    try:
        client = HaciendaClient()
        
        # Intentar obtener token
        token = await client.obtener_token()
        
        return {
            "conexion_exitosa": True,
            "autenticacion": "exitosa",
            "token_obtenido": bool(token),
            "base_url": client.base_url,
            "client_id": client.client_id,
            "username": client.username,
            "sandbox": client.sandbox,
            "mensaje": "Conexión con Hacienda establecida correctamente"
        }
        
    except Exception as e:
        return {
            "conexion_exitosa": False,
            "autenticacion": "fallida",
            "error": str(e),
            "mensaje": "Error al conectar con Hacienda"
        }