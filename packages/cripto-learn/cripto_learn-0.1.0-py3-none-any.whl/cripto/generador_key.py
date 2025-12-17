# generador_key.py - Cryptographic Key and IV Generation Module

import os
import base64

# --- ALGORITHM PARAMETERS (Must match cifrador_core.py) ---
KEY_LENGTH = 32  # 256-bit Key (32 bytes)
BLOCK_SIZE = 8   # 64-bit Block for the Initialization Vector (IV)

def generar_componentes_criptograficos(output_file: str = "clave_secreta.txt"):
    """
    Generates a random Key (KEY) and Initialization Vector (IV) 
    and saves them Base64-encoded to a file.
    """
    
    # Generate cryptographically secure random bytes
    key = os.urandom(KEY_LENGTH)
    iv = os.urandom(BLOCK_SIZE)
    
    # Encode to Base64 for storing in a plaintext file
    key_b64 = base64.urlsafe_b64encode(key).decode('utf-8')
    iv_b64 = base64.urlsafe_b64encode(iv).decode('utf-8')
    
    # Save components to the output file
    with open(output_file, "w") as f:
        f.write(f"KEY:{key_b64}\n")
        f.write(f"IV:{iv_b64}\n")
    
    return output_file
    
if __name__ == "__main__":
    output_file = generar_componentes_criptograficos()
    print(f"Key and IV saved to '{output_file}'.")