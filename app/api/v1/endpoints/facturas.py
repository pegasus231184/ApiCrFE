from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.schemas.factura import FacturaCreate, FacturaResponse, FacturaElectronica
from app.services.xml_generator import XMLGenerator
from app.services.xml_signer_simple import signer
from app.services.hacienda_client import HaciendaClient
import uuid
from datetime import datetime

router = APIRouter()
xml_generator = XMLGenerator()
hacienda_client = HaciendaClient()

@router.post("/", response_model=FacturaResponse, summary="Crear Factura Electrónica")
async def crear_factura(
    factura_data: FacturaCreate,
    background_tasks: BackgroundTasks,
    firmar: bool = True,
    enviar_hacienda: bool = True
):
    """
    Crear una nueva factura electrónica según normativa v4.4 del Ministerio de Hacienda de Costa Rica.
    
    - **factura_data**: Datos de la factura a crear
    - **firmar**: Si se debe firmar digitalmente el documento (default: True)
    - **enviar_hacienda**: Si se debe enviar automáticamente a Hacienda (default: True)
    
    Retorna la clave única del documento y el estado actual.
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo("01")
        
        factura = FacturaElectronica(
            codigo_actividad=factura_data.codigo_actividad,
            numero_consecutivo=consecutivo,
            fecha_emision=datetime.now(),
            emisor=factura_data.emisor,
            receptor=factura_data.receptor,
            condicion_venta=factura_data.condicion_venta,
            plazo_credito=factura_data.plazo_credito,
            medio_pago=factura_data.medio_pago,
            detalles_servicio=factura_data.detalles_servicio,
            resumen_factura=factura_data.resumen_factura
        )
        
        xml_sin_firmar = xml_generator.generar_xml_factura(factura)
        
        xml_firmado = None
        if firmar:
            try:
                xml_firmado = signer.firmar_xml(xml_sin_firmar)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error al firmar documento: {str(e)}")
        
        if enviar_hacienda and xml_firmado:
            background_tasks.add_task(enviar_a_hacienda, factura.clave, xml_firmado)
        
        return FacturaResponse(
            clave=factura.clave,
            numero_consecutivo=consecutivo,
            fecha_emision=factura.fecha_emision,
            estado="generada" if not enviar_hacienda else "enviando",
            xml_firmado=xml_firmado if firmar else xml_sin_firmar
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear factura: {str(e)}")

@router.post("/notas-credito", response_model=FacturaResponse, summary="Crear Nota de Crédito")
async def crear_nota_credito(
    nota_data: FacturaCreate,
    factura_referencia: str,
    motivo: str,
    firmar: bool = True,
    enviar_hacienda: bool = True
):
    """
    Crear una nota de crédito electrónica.
    
    - **nota_data**: Datos de la nota de crédito
    - **factura_referencia**: Clave de la factura que se está creditando
    - **motivo**: Motivo de la nota de crédito
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo("03")
        
        nota = FacturaElectronica(
            codigo_actividad=nota_data.codigo_actividad,
            numero_consecutivo=consecutivo,
            fecha_emision=datetime.now(),
            emisor=nota_data.emisor,
            receptor=nota_data.receptor,
            condicion_venta=nota_data.condicion_venta,
            medio_pago=nota_data.medio_pago,
            detalles_servicio=nota_data.detalles_servicio,
            resumen_factura=nota_data.resumen_factura
        )
        
        xml_sin_firmar = xml_generator.generar_xml_factura(nota)
        
        xml_firmado = None
        if firmar:
            xml_firmado = signer.firmar_xml(xml_sin_firmar)
        
        return FacturaResponse(
            clave=nota.clave,
            numero_consecutivo=consecutivo,
            fecha_emision=nota.fecha_emision,
            estado="generada",
            xml_firmado=xml_firmado if firmar else xml_sin_firmar
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear nota de crédito: {str(e)}")

@router.post("/tiquetes", response_model=FacturaResponse, summary="Crear Tiquete Electrónico")
async def crear_tiquete(
    tiquete_data: FacturaCreate,
    firmar: bool = True,
    enviar_hacienda: bool = True
):
    """
    Crear un tiquete electrónico (para ventas de consumidor final).
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo("04")
        
        tiquete = FacturaElectronica(
            codigo_actividad=tiquete_data.codigo_actividad,
            numero_consecutivo=consecutivo,
            fecha_emision=datetime.now(),
            emisor=tiquete_data.emisor,
            receptor=None,  # Los tiquetes no requieren receptor
            condicion_venta=tiquete_data.condicion_venta,
            medio_pago=tiquete_data.medio_pago,
            detalles_servicio=tiquete_data.detalles_servicio,
            resumen_factura=tiquete_data.resumen_factura
        )
        
        xml_sin_firmar = xml_generator.generar_xml_factura(tiquete)
        
        xml_firmado = None
        if firmar:
            xml_firmado = signer.firmar_xml(xml_sin_firmar)
        
        return FacturaResponse(
            clave=tiquete.clave,
            numero_consecutivo=consecutivo,
            fecha_emision=tiquete.fecha_emision,
            estado="generada",
            xml_firmado=xml_firmado if firmar else xml_sin_firmar
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear tiquete: {str(e)}")

@router.post("/notas-debito", response_model=FacturaResponse, summary="Crear Nota de Débito")
async def crear_nota_debito(
    nota_data: FacturaCreate,
    factura_referencia: str,
    motivo: str,
    firmar: bool = True,
    enviar_hacienda: bool = True
):
    """
    Crear una nota de débito electrónica.
    
    - **nota_data**: Datos de la nota de débito
    - **factura_referencia**: Clave de la factura que se está debitando
    - **motivo**: Motivo de la nota de débito
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo("02")
        
        nota = FacturaElectronica(
            codigo_actividad=nota_data.codigo_actividad,
            numero_consecutivo=consecutivo,
            fecha_emision=datetime.now(),
            emisor=nota_data.emisor,
            receptor=nota_data.receptor,
            condicion_venta=nota_data.condicion_venta,
            medio_pago=nota_data.medio_pago,
            detalles_servicio=nota_data.detalles_servicio,
            resumen_factura=nota_data.resumen_factura
        )
        
        xml_sin_firmar = xml_generator.generar_xml_factura(nota)
        
        xml_firmado = None
        if firmar:
            xml_firmado = signer.firmar_xml(xml_sin_firmar)
        
        return FacturaResponse(
            clave=nota.clave,
            numero_consecutivo=consecutivo,
            fecha_emision=nota.fecha_emision,
            estado="generada",
            xml_firmado=xml_firmado if firmar else xml_sin_firmar
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear nota de débito: {str(e)}")

@router.post("/facturas-exportacion", response_model=FacturaResponse, summary="Crear Factura de Exportación")
async def crear_factura_exportacion(
    factura_data: FacturaCreate,
    background_tasks: BackgroundTasks,
    firmar: bool = True,
    enviar_hacienda: bool = True
):
    """
    Crear una factura de exportación electrónica.
    
    - **factura_data**: Datos de la factura de exportación
    - **firmar**: Si se debe firmar digitalmente el documento (default: True)
    - **enviar_hacienda**: Si se debe enviar automáticamente a Hacienda (default: True)
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo("05")
        
        factura = FacturaElectronica(
            codigo_actividad=factura_data.codigo_actividad,
            numero_consecutivo=consecutivo,
            fecha_emision=datetime.now(),
            emisor=factura_data.emisor,
            receptor=factura_data.receptor,
            condicion_venta=factura_data.condicion_venta,
            plazo_credito=factura_data.plazo_credito,
            medio_pago=factura_data.medio_pago,
            detalles_servicio=factura_data.detalles_servicio,
            resumen_factura=factura_data.resumen_factura
        )
        
        xml_sin_firmar = xml_generator.generar_xml_factura(factura)
        
        xml_firmado = None
        if firmar:
            try:
                xml_firmado = signer.firmar_xml(xml_sin_firmar)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error al firmar documento: {str(e)}")
        
        if enviar_hacienda and xml_firmado:
            background_tasks.add_task(enviar_a_hacienda, factura.clave, xml_firmado)
        
        return FacturaResponse(
            clave=factura.clave,
            numero_consecutivo=consecutivo,
            fecha_emision=factura.fecha_emision,
            estado="generada" if not enviar_hacienda else "enviando",
            xml_firmado=xml_firmado if firmar else xml_sin_firmar
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear factura de exportación: {str(e)}")

async def enviar_a_hacienda(clave: str, xml_firmado: str):
    """
    Tarea en background para enviar documento a Hacienda
    """
    try:
        resultado = await hacienda_client.enviar_documento(clave, xml_firmado)
        print(f"Documento {clave} enviado a Hacienda: {resultado}")
    except Exception as e:
        print(f"Error al enviar documento {clave} a Hacienda: {e}")

@router.get("/consecutivos/{tipo_documento}", summary="Obtener Próximo Consecutivo")
async def obtener_consecutivo(tipo_documento: str):
    """
    Obtener el próximo número consecutivo para un tipo de documento desde Hacienda.
    
    - **tipo_documento**: 01=Factura, 02=Nota Débito, 03=Nota Crédito, 04=Tiquete
    """
    try:
        consecutivo = await hacienda_client.obtener_consecutivo(tipo_documento)
        
        return {
            "tipo_documento": tipo_documento,
            "consecutivo": consecutivo,
            "timestamp": datetime.now().isoformat(),
            "fuente": "hacienda_api"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo consecutivo: {str(e)}")