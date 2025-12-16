import bcrypt
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional

from supabase import create_client, Client


class LicenseError(Exception):
    pass


class InvalidCredentialsError(LicenseError):
    pass


class InvalidLicenseCodeError(LicenseError):
    pass


class SubscriptionExpiredError(LicenseError):
    pass


class SubscriptionInactiveError(LicenseError):
    pass


@dataclass
class LicenseInfo:
    email: str
    plan_type: str
    expires_at: datetime
    days_remaining: int
    is_valid: bool
    
    def __str__(self) -> str:
        status = "Válida" if self.is_valid else "Expirada"
        return (
            f"Email: {self.email}\n"
            f"Plano: {self.plan_type}\n"
            f"Expira em: {self.days_remaining} dias ({self.expires_at.strftime('%d/%m/%Y %H:%M')})\n"
            f"Status: {status}"
        )


class LicenseManager:
    
    @staticmethod
    def verify(
        email: str,
        user: str,
        password: str,
        license_code: str,
        supabase_url: str,
        supabase_key: str
    ) -> LicenseInfo:
        if not email or not isinstance(email, str) or '@' not in email:
            raise ValueError("Email inválido")
        
        if not user or not isinstance(user, str) or len(user.strip()) == 0:
            raise ValueError("User inválido")
        
        if not password or not isinstance(password, str) or len(password) < 3:
            raise ValueError("Senha inválida")
        
        if not license_code or not isinstance(license_code, str) or len(license_code.strip()) == 0:
            raise ValueError("Código de licença inválido")
        
        email = email.strip().lower()
        user = user.strip()
        license_code = license_code.strip()
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            
            response = supabase.table("users")\
                .select("*")\
                .eq("email", email)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                raise InvalidCredentialsError("Email, user ou senha incorretos")
            
            user_data = response.data[0]
            
            if user_data.get("user") != user:
                raise InvalidCredentialsError("Email, user ou senha incorretos")
            
            password_hash = user_data.get("password_hash")
            if not LicenseManager._verify_password(password, password_hash):
                raise InvalidCredentialsError("Email, user ou senha incorretos")
            
            if user_data.get("license_code") != license_code:
                raise InvalidLicenseCodeError(
                    f"Código de licença não pertence ao email {email}"
                )
            
            if not user_data.get("is_active", False):
                raise SubscriptionInactiveError("RENOVE SEU PLANO")
            
            expires_at_str = user_data.get("expires_at")
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            
            now = datetime.now(timezone.utc)
            is_valid = expires_at > now
            days_remaining = max(0, (expires_at - now).days)
            
            if not is_valid:
                raise SubscriptionExpiredError(
                    f"Assinatura expirada em {expires_at.strftime('%d/%m/%Y %H:%M')}"
                )
            
            return LicenseInfo(
                email=email,
                plan_type=user_data.get("plan_type", "UNKNOWN"),
                expires_at=expires_at,
                days_remaining=days_remaining,
                is_valid=is_valid
            )
            
        except (InvalidCredentialsError, InvalidLicenseCodeError, 
                SubscriptionExpiredError, SubscriptionInactiveError):
            raise
        except Exception as e:
            raise LicenseError(f"Erro ao verificar licença: {str(e)}") from e
    
    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False

