from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.services.hacienda_client import HaciendaClient

router = APIRouter()
hacienda_client = HaciendaClient()

@router.get("/{clave}", summary="Consultar Estado de Documento")
async def consultar_documento(clave: str):
    """
    Consultar el estado de un documento electrónico en el sistema de Hacienda.
    
    - **clave**: Clave única del documento de 50 caracteres
    """
    if len(clave) != 50:
        raise HTTPException(status_code=400, detail="La clave debe tener exactamente 50 caracteres")
    
    try:
        estado = await hacienda_client.consultar_estado(clave)
        return {
            "clave": clave,
            "estado": estado.get("ind-estado", "desconocido"),
            "fecha_procesamiento": estado.get("fecha-procesamiento"),
            "mensaje_hacienda": estado.get("mensaje-hacienda"),
            "respuesta_xml": estado.get("respuesta-xml")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar documento: {str(e)}")

@router.get("/", summary="Listar Documentos")
async def listar_documentos(
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    tipo_documento: Optional[str] = Query(None, description="Tipo: 01=Factura, 02=ND, 03=NC, 04=Tiquete"),
    estado: Optional[str] = Query(None, description="Estado del documento"),
    limit: int = Query(50, description="Número máximo de resultados", le=200),
    offset: int = Query(0, description="Número de registros a saltar")
):
    """
    Listar documentos electrónicos con filtros opcionales.
    """
    if not fecha_inicio:
        fecha_inicio = datetime.now() - timedelta(days=30)
    if not fecha_fin:
        fecha_fin = datetime.now()
    
    # Aquí iría la lógica para consultar la base de datos
    # Por ahora retornamos datos de ejemplo
    documentos_ejemplo = [
        {
            "clave": "506241120241234567890123456789012345678901234567",
            "tipo_documento": "01",
            "numero_consecutivo": "00100001010000000001000001",
            "fecha_emision": "2024-11-24T10:30:00",
            "estado": "aceptado",
            "monto_total": 115000.00,
            "receptor_nombre": "Cliente Ejemplo S.A."
        }
    ]
    
    return {
        "documentos": documentos_ejemplo,
        "total": 1,
        "limit": limit,
        "offset": offset,
        "filtros": {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "tipo_documento": tipo_documento,
            "estado": estado
        }
    }

@router.post("/{clave}/reenviar", summary="Reenviar Documento a Hacienda")
async def reenviar_documento(clave: str):
    """
    Reenviar un documento electrónico al sistema de Hacienda.
    """
    if len(clave) != 50:
        raise HTTPException(status_code=400, detail="La clave debe tener exactamente 50 caracteres")
    
    try:
        # Aquí buscaríamos el XML en la base de datos
        # Por ahora simulamos el reenvío
        resultado = await hacienda_client.reenviar_documento(clave)
        return {
            "clave": clave,
            "estado": "reenviado",
            "mensaje": "Documento reenviado exitosamente",
            "fecha_reenvio": datetime.now().isoformat(),
            "respuesta_hacienda": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reenviar documento: {str(e)}")

@router.delete("/{clave}", summary="Anular Documento")
async def anular_documento(clave: str, motivo: str):
    """
    Anular un documento electrónico.
    
    - **clave**: Clave del documento a anular
    - **motivo**: Motivo de la anulación
    """
    if len(clave) != 50:
        raise HTTPException(status_code=400, detail="La clave debe tener exactamente 50 caracteres")
    
    if not motivo or len(motivo.strip()) < 10:
        raise HTTPException(status_code=400, detail="El motivo debe tener al menos 10 caracteres")
    
    try:
        # Aquí iría la lógica para generar la anulación
        return {
            "clave": clave,
            "estado": "anulado",
            "motivo": motivo,
            "fecha_anulacion": datetime.now().isoformat(),
            "mensaje": "Documento anulado exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al anular documento: {str(e)}")

@router.get("/{clave}/pdf", summary="Descargar PDF del Comprobante")
async def descargar_pdf(clave: str):
    """
    Generar y descargar el PDF de un documento electrónico.
    """
    if len(clave) != 50:
        raise HTTPException(status_code=400, detail="La clave debe tener exactamente 50 caracteres")
    
    try:
        # Aquí iría la lógica para generar el PDF
        return {
            "clave": clave,
            "pdf_url": f"/api/v1/documentos/{clave}/download",
            "pdf_generado": True,
            "fecha_generacion": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

@router.get("/{clave}/xml", summary="Obtener XML del Documento")
async def obtener_xml(clave: str, firmado: bool = True):
    """
    Obtener el XML de un documento electrónico.
    
    - **clave**: Clave del documento
    - **firmado**: Si se debe retornar el XML firmado (default: True)
    """
    if len(clave) != 50:
        raise HTTPException(status_code=400, detail="La clave debe tener exactamente 50 caracteres")
    
    try:
        # Aquí buscaríamos el XML en la base de datos
        return {
            "clave": clave,
            "xml_disponible": True,
            "firmado": firmado,
            "xml_content": "<?xml version='1.0' encoding='UTF-8'?>...",  # XML real aquí
            "fecha_generacion": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener XML: {str(e)}")