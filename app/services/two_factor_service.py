import random
import string
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.security.two_factor_codes import TwoFactorCode

class TwoFactorService:

    @staticmethod
    def generate_2fa_code(db: Session, user_id: int, purpose: str = "login", ttl_minutes: int = 5):
        """Crea un código 2FA temporal y lo guarda en DB."""
        code = ''.join(random.choices(string.digits, k=6))  # 6 dígitos
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        temp_token = str(uuid4())

        db_code = TwoFactorCode(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        db.add(db_code)
        db.commit()
        db.refresh(db_code)

        # Aquí podrías enviar el código por SMS/email según tu proveedor
        print(f"[2FA] Código para usuario {user_id}: {code}")

        return {"temp_token": temp_token, "expires_at": expires_at, "code_id": db_code.id}
