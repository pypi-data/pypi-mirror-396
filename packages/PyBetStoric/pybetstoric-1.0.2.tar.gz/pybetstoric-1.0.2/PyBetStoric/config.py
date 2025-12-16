import os
from typing import Optional

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


class ConfigError(Exception):
    pass


class SupabaseConfig:
    _url: Optional[str] = "https://vpjmqdrxgsdnhvhhjvzw.supabase.co"
    _key: Optional[str] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwam1xZHJ4Z3Nkbmh2aGhqdnp3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0NjcyMjEsImV4cCI6MjA4MTA0MzIyMX0.kV5D2V00EpjvaHydPVqMlR34QLhNNOkRRorJOAtAyF8"
    
    _initialized: bool = False
    
    @classmethod
    def _load_from_env(cls) -> None:
        if _DOTENV_AVAILABLE:
            load_dotenv()
        
        env_url = os.getenv("SUPABASE_URL")
        env_key = os.getenv("SUPABASE_ANON_KEY")
        
        if env_url and env_key:
            cls._url = env_url.strip()
            cls._key = env_key.strip()
            cls._initialized = True
            return
        
        if cls._url and cls._key and cls._url.strip() and cls._key.strip():
            cls._url = cls._url.strip()
            cls._key = cls._key.strip()
            cls._initialized = True
            return
        
        raise ConfigError(
            "Credenciais do Supabase não configuradas. "
            "Configure SUPABASE_URL e SUPABASE_ANON_KEY no arquivo .env "
            "ou entre em contato com o suporte."
        )
    
    @classmethod
    def get_url(cls) -> str:
        if not cls._initialized:
            cls._load_from_env()
        if not cls._url:
            raise ConfigError("URL do Supabase não configurada")
        return cls._url
    
    @classmethod
    def get_key(cls) -> str:
        if not cls._initialized:
            cls._load_from_env()
        if not cls._key:
            raise ConfigError("Chave do Supabase não configurada")
        return cls._key
    
    @classmethod
    def set_credentials(cls, url: str, key: str) -> None:
        if not url or not key:
            raise ConfigError("URL e chave são obrigatórias")
        cls._url = url
        cls._key = key
        cls._initialized = True
    
    @classmethod
    def reset(cls) -> None:
        cls._url = None
        cls._key = None
        cls._initialized = False

