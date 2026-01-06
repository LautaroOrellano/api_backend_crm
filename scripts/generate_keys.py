import os
from pathlib import Path

# Try to import cryptography, if not installed, warn user
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:
    print("Error: 'cryptography' library is required. Install it using:")
    print("pip install cryptography")
    exit(1)

def generate_keys():
    # Define keys directory
    base_dir = Path(__file__).resolve().parent.parent # Go up one level from scripts/
    keys_dir = base_dir / "keys"
    
    # Create directory if not exists
    if not keys_dir.exists():
        print(f"Creating directory: {keys_dir}")
        keys_dir.mkdir(parents=True, exist_ok=True)
    
    private_key_path = keys_dir / "private.pem"
    public_key_path = keys_dir / "public.pem"

    if private_key_path.exists() and public_key_path.exists():
        print("✅ Keys already exist. Skipping generation.")
        return

    print("🔑 Generating new RSA keys...")

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Write private key
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write public key
    public_key = private_key.public_key()
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print(f"✅ Keys generated successfully in '{keys_dir}'")
    print("⚠️  KEEP 'private.pem' SECRET! Do not commit it to git.")

if __name__ == "__main__":
    generate_keys()
