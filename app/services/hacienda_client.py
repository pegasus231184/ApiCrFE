import httpx
import base64
from typing import Dict, Any, Optional
from app.core.config import settings
import asyncio

class HaciendaClient:
    def __init__(self):
        self.base_url = settings.hacienda_base_url
        self.token_url = settings.hacienda_token_url
        self.client_id = settings.hacienda_client_id
        self.client_secret = settings.hacienda_client_secret
        self.username = settings.hacienda_username
        self.password = settings.hacienda_password
        self.sandbox = settings.hacienda_sandbox
        self.access_token = None
        
        print(f"🌐 Hacienda Client initialized:")
        print(f"   Base URL: {self.base_url}")
        print(f"   Token URL: {self.token_url}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Username: {self.username}")
        print(f"   Sandbox: {self.sandbox}")
    
    async def obtener_token(self) -> str:
        """Obtener token de acceso OAuth2 para la API de Hacienda"""
        if not self.client_id:
            raise ValueError("Client ID es requerido")
        
        if not self.username or not self.password:
            raise ValueError("Username y Password son requeridos")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Para Hacienda SANDBOX se usa grant_type=password con username/password
        data = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'username': self.username,
            'password': self.password,
        }
        
        # Si hay client_secret, incluirlo
        if self.client_secret:
            data['client_secret'] = self.client_secret
        
        print(f"🔑 Obteniendo token de: {self.token_url}")
        print(f"   Grant type: password")
        print(f"   Client ID: {self.client_id}")
        print(f"   Username: {self.username}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    headers=headers,
                    data=data,
                    timeout=30.0
                )
                
                print(f"📡 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get('access_token')
                    print(f"✅ Token obtenido exitosamente")
                    return self.access_token
                else:
                    error_text = response.text
                    print(f"❌ Error obteniendo token: {response.status_code}")
                    print(f"   Response: {error_text}")
                    raise Exception(f"Error obteniendo token: {response.status_code} - {error_text}")
                    
            except httpx.TimeoutException:
                raise Exception("Timeout al obtener token de Hacienda")
            except Exception as e:
                print(f"❌ Excepción obteniendo token: {e}")
                raise
    
    async def enviar_documento(self, clave: str, xml_firmado: str) -> Dict[str, Any]:
        """Enviar documento electrónico a Hacienda"""
        if not self.access_token:
            await self.obtener_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Codificar XML en base64
        xml_base64 = base64.b64encode(xml_firmado.encode('utf-8')).decode('ascii')
        
        payload = {
            'clave': clave,
            'fecha': clave[3:13],  # Extraer fecha de la clave
            'emisor': {
                'tipoIdentificacion': clave[13:15],
                'numeroIdentificacion': clave[15:27]
            },
            'comprobanteXml': xml_base64
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/recepcion",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201, 202]:
                    return {
                        'clave': clave,
                        'estado': 'enviado',
                        'respuesta': response.json() if response.content else {},
                        'codigo_respuesta': response.status_code
                    }
                else:
                    return {
                        'clave': clave,
                        'estado': 'error',
                        'error': f"HTTP {response.status_code}: {response.text}",
                        'codigo_respuesta': response.status_code
                    }
                    
            except httpx.TimeoutException:
                return {
                    'clave': clave,
                    'estado': 'timeout',
                    'error': 'Timeout al enviar a Hacienda'
                }
            except Exception as e:
                return {
                    'clave': clave,
                    'estado': 'error',
                    'error': str(e)
                }
    
    async def consultar_estado(self, clave: str) -> Dict[str, Any]:
        """Consultar el estado de un documento en Hacienda"""
        if not self.access_token:
            await self.obtener_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/recepcion/{clave}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'clave': clave,
                        'ind-estado': data.get('ind-estado', 'desconocido'),
                        'fecha-procesamiento': data.get('fecha-procesamiento'),
                        'mensaje-hacienda': data.get('mensaje-hacienda'),
                        'respuesta-xml': data.get('respuesta-xml')
                    }
                elif response.status_code == 404:
                    return {
                        'clave': clave,
                        'ind-estado': 'no_encontrado',
                        'mensaje-hacienda': 'Documento no encontrado en Hacienda'
                    }
                else:
                    return {
                        'clave': clave,
                        'ind-estado': 'error_consulta',
                        'mensaje-hacienda': f"Error HTTP {response.status_code}: {response.text}"
                    }
                    
            except httpx.TimeoutException:
                return {
                    'clave': clave,
                    'ind-estado': 'timeout',
                    'mensaje-hacienda': 'Timeout al consultar estado'
                }
            except Exception as e:
                return {
                    'clave': clave,
                    'ind-estado': 'error_consulta',
                    'mensaje-hacienda': str(e)
                }
    
    async def reenviar_documento(self, clave: str) -> Dict[str, Any]:
        """Reenviar un documento a Hacienda (requiere el XML original)"""
        # En implementación real, buscaríamos el XML en la base de datos
        return {
            'clave': clave,
            'estado': 'reenviado',
            'mensaje': 'Documento marcado para reenvío'
        }
    
    async def consultar_masivo(self, claves: list) -> Dict[str, Any]:
        """Consultar el estado de múltiples documentos"""
        resultados = {}
        
        # Ejecutar consultas en paralelo (máximo 5 concurrentes)
        semaforo = asyncio.Semaphore(5)
        
        async def consultar_con_semaforo(clave):
            async with semaforo:
                return await self.consultar_estado(clave)
        
        tareas = [consultar_con_semaforo(clave) for clave in claves]
        respuestas = await asyncio.gather(*tareas, return_exceptions=True)
        
        for clave, respuesta in zip(claves, respuestas):
            if isinstance(respuesta, Exception):
                resultados[clave] = {
                    'ind-estado': 'error',
                    'mensaje-hacienda': str(respuesta)
                }
            else:
                resultados[clave] = respuesta
        
        return resultados
    
    async def obtener_consecutivo(self, tipo_documento: str = "01") -> str:
        """Obtener el próximo número consecutivo desde Hacienda"""
        if not self.access_token:
            await self.obtener_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Para sandbox, generar consecutivo válido localmente
        # En producción, esto debería llamar al endpoint real de Hacienda
        if self.sandbox:
            from datetime import datetime
            import secrets
            
            # Formato Costa Rica: 20 caracteres exactos 
            # Estructura: TTSSSSSSSSNNNNNNNNN
            # TT = Tipo documento (01) - 2 chars
            # SSSSSSSS = Terminal/Sucursal (00100001) - 8 chars  
            # NNNNNNNN = Consecutivo (01000001) - 8 chars
            # RRHH = Código seguridad (10) - 2 chars
            # Total: 2 + 8 + 8 + 2 = 20 caracteres
            
            contador = secrets.randbelow(99999999)  # Máximo 8 dígitos
            codigo_seguridad = secrets.randbelow(100)  # 2 dígitos
            
            consecutivo = f"{tipo_documento}00100001{contador:08d}{codigo_seguridad:02d}"
            
            print(f"🔢 Consecutivo generado para SANDBOX: {consecutivo} (longitud: {len(consecutivo)})")
            return consecutivo
        else:
            # Llamada real al API de Hacienda (para producción)
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{self.base_url}/consecutivos/{tipo_documento}",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('consecutivo')
                    else:
                        raise Exception(f"Error obteniendo consecutivo: {response.status_code}")
                        
                except httpx.TimeoutException:
                    raise Exception("Timeout al obtener consecutivo de Hacienda")
                except Exception as e:
                    raise Exception(f"Error al obtener consecutivo: {str(e)}")