from pathlib import Path

# Ruta a las claves
PRIVATE_KEY_PATH = Path("keys/private.pem")
PUBLIC_KEY_PATH = Path("keys/public.pem")  # la pública actual
KID_CURRENT = "2025-11-23-v1"

# Carga de claves
with PRIVATE_KEY_PATH.open() as f:
    PRIVATE_KEY = f.read()

with PUBLIC_KEY_PATH.open() as f:
    PUBLIC_KEY = f.read()

# Diccionario de claves públicas (para rotación futura)
PUBLIC_KEYS = {
    KID_CURRENT: PUBLIC_KEY
}
