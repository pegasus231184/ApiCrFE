from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "API Facturación Electrónica CR"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://user:password@localhost/facturacion_cr"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Ministerio de Hacienda API
    hacienda_base_url: str = "https://api-sandbox.comprobanteselectronicos.go.cr"
    hacienda_token_url: str = "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token"
    hacienda_client_id: str = "api-stag"
    hacienda_client_secret: Optional[str] = ""
    hacienda_username: Optional[str] = None
    hacienda_password: Optional[str] = None
    hacienda_sandbox: bool = True
    
    # Certificado Digital
    certificate_path: Optional[str] = None
    certificate_password: Optional[str] = None
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()