from fastapi import APIRouter
from typing import Dict, Any, List
from app.core.reference_data import (
    UBICACIONES_CR, 
    MONEDAS_OFICIALES, 
    validar_ubicacion, 
    validar_moneda,
    obtener_info_ubicacion
)

router = APIRouter()

@router.get("/ubicaciones", summary="Obtener códigos oficiales de ubicación")
async def obtener_ubicaciones():
    """
    Obtener todos los códigos oficiales de ubicación de Costa Rica
    según datos del Ministerio de Hacienda v4.4
    """
    return {
        "title": "Códigos de Ubicación de Costa Rica v4.4",
        "source": "Ministerio de Hacienda - Codificacionubicacion_V4.4.xlsx",
        "data": UBICACIONES_CR
    }

@router.get("/ubicaciones/{provincia_codigo}", summary="Obtener información de provincia")
async def obtener_provincia(provincia_codigo: str):
    """
    Obtener información detallada de una provincia específica
    """
    if provincia_codigo not in UBICACIONES_CR:
        return {
            "error": f"Provincia '{provincia_codigo}' no encontrada",
            "provincias_validas": list(UBICACIONES_CR.keys())
        }
    
    return {
        "provincia": provincia_codigo,
        "data": UBICACIONES_CR[provincia_codigo]
    }

@router.get("/ubicaciones/{provincia_codigo}/{canton_codigo}", summary="Obtener información de cantón")
async def obtener_canton(provincia_codigo: str, canton_codigo: str):
    """
    Obtener información detallada de un cantón específico
    """
    info = obtener_info_ubicacion(provincia_codigo, canton_codigo)
    
    if not info:
        return {
            "error": f"Provincia '{provincia_codigo}' no encontrada"
        }
    
    if "canton" not in info:
        return {
            "error": f"Cantón '{canton_codigo}' no encontrado en provincia {provincia_codigo}",
            "cantones_validos": list(UBICACIONES_CR[provincia_codigo]["cantones"].keys())
        }
    
    return {
        "provincia": info["provincia"],
        "canton": info["canton"],
        "distritos": UBICACIONES_CR[provincia_codigo]["cantones"][canton_codigo]["distritos"]
    }

@router.post("/ubicaciones/validar", summary="Validar códigos de ubicación")
async def validar_ubicacion_endpoint(ubicacion: Dict[str, str]):
    """
    Validar códigos de ubicación según datos oficiales
    
    Body:
    ```json
    {
        "provincia": "01",
        "canton": "01", 
        "distrito": "01"
    }
    ```
    """
    provincia = ubicacion.get("provincia", "")
    canton = ubicacion.get("canton", "")
    distrito = ubicacion.get("distrito", "")
    
    es_valida, mensaje = validar_ubicacion(provincia, canton, distrito)
    
    result = {
        "valida": es_valida,
        "mensaje": mensaje if not es_valida else "Ubicación válida"
    }
    
    if es_valida:
        info = obtener_info_ubicacion(provincia, canton, distrito)
        result["informacion"] = info
    
    return result

@router.get("/monedas", summary="Obtener códigos oficiales de moneda")
async def obtener_monedas():
    """
    Obtener todos los códigos oficiales de moneda según ISO 4217
    """
    return {
        "title": "Códigos de Moneda ISO 4217",
        "source": "Ministerio de Hacienda - Codigodemoneda_V4.4.pdf",
        "total_monedas": len(MONEDAS_OFICIALES),
        "data": MONEDAS_OFICIALES
    }

@router.get("/monedas/{codigo}", summary="Obtener información de moneda específica")
async def obtener_moneda(codigo: str):
    """
    Obtener información de una moneda específica
    """
    codigo_upper = codigo.upper()
    
    if codigo_upper not in MONEDAS_OFICIALES:
        # Sugerir monedas similares
        similares = [k for k in MONEDAS_OFICIALES.keys() if codigo_upper.lower() in k.lower()]
        return {
            "error": f"Moneda '{codigo}' no encontrada",
            "sugerencias": similares[:5],
            "monedas_comunes": {
                "CRC": MONEDAS_OFICIALES["CRC"],
                "USD": MONEDAS_OFICIALES["USD"],
                "EUR": MONEDAS_OFICIALES["EUR"]
            }
        }
    
    return {
        "codigo": codigo_upper,
        "nombre": MONEDAS_OFICIALES[codigo_upper],
        "valida": True
    }

@router.post("/monedas/validar", summary="Validar código de moneda")
async def validar_moneda_endpoint(moneda: Dict[str, str]):
    """
    Validar código de moneda según ISO 4217
    
    Body:
    ```json
    {
        "codigo": "CRC"
    }
    ```
    """
    codigo = moneda.get("codigo", "").upper()
    
    es_valida, mensaje = validar_moneda(codigo)
    
    result = {
        "valida": es_valida,
        "mensaje": mensaje if not es_valida else "Código de moneda válido"
    }
    
    if es_valida:
        result["codigo"] = codigo
        result["nombre"] = MONEDAS_OFICIALES[codigo]
    
    return result

@router.get("/", summary="Información general de datos de referencia")
async def informacion_general():
    """
    Información general sobre los datos de referencia disponibles
    """
    return {
        "title": "Datos de Referencia Oficiales v4.4",
        "description": "Códigos oficiales del Ministerio de Hacienda de Costa Rica",
        "version": "4.4",
        "fuentes": {
            "ubicaciones": "Codificacionubicacion_V4.4.xlsx",
            "monedas": "Codigodemoneda_V4.4.pdf"
        },
        "estadisticas": {
            "total_provincias": len(UBICACIONES_CR),
            "total_monedas": len(MONEDAS_OFICIALES),
            "provincias": [
                {
                    "codigo": codigo,
                    "nombre": data["nombre"],
                    "cantones": len(data["cantones"])
                }
                for codigo, data in UBICACIONES_CR.items()
            ]
        },
        "endpoints": {
            "ubicaciones": "/referencias/ubicaciones",
            "monedas": "/referencias/monedas",
            "validar_ubicacion": "/referencias/ubicaciones/validar",
            "validar_moneda": "/referencias/monedas/validar"
        }
    }