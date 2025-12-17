# cifrador_core.py - Core Cryptography Module (Feistel, CBC, and Padding)

import base64
import sys

# --- CRYPTOGRAPHIC PARAMETERS ---
BLOCK_SIZE = 8
FEISTEL_ROUNDS = 8

# --- UTILITIES ---

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """Performs a byte-by-byte XOR operation."""
    if len(a) != len(b):
        raise ValueError("Block lengths do not match for XOR.")
    return bytes(b1 ^ b2 for b1, b2 in zip(a, b))

def funcion_f_simplificada(r_i: bytes, k_i: bytes) -> bytes:
    """Feistel Round Function F (Simplified)."""
    r_i_rotated = r_i[1:] + r_i[:1]
    return xor_bytes(r_i_rotated, k_i[:len(r_i_rotated)]) 

def get_subkeys(key: bytes, num_rondas: int) -> list:
    """Generates simplified subkeys by slicing the master key."""
    half_block = BLOCK_SIZE // 2
    subkeys = []
    for i in range(num_rondas):
        start_index = (i * half_block) % (len(key) - half_block + 1)
        subkeys.append(key[start_index : start_index + half_block])
    return subkeys

# --- PADDING ---

def pkcs7_padding(data: bytes, block_size: int) -> bytes:
    """Implements the PKCS#7 padding scheme."""
    padding_len = block_size - (len(data) % block_size)
    padding = bytes([padding_len]) * padding_len
    return data + padding

def pkcs7_unpadding(data: bytes) -> bytes:
    """Removes PKCS#7 padding."""
    if not data: raise ValueError("Empty data.")
    padding_len = data[-1]
    if padding_len < 1 or padding_len > BLOCK_SIZE:
        raise ValueError("Unpadding error: Invalid padding length.")
    
    if all(data[-i] == padding_len for i in range(1, padding_len + 1)):
        return data[:-padding_len]
    else:
        raise ValueError("Unpadding error: Corrupt padding bytes.")

# --- FEISTEL CORE (Internal Functions) ---

def _cifrar_bloque_feistel(bloque_entrada: bytes, clave: bytes) -> bytes:
    """Encrypts one block using the Feistel Network."""
    half_size = BLOCK_SIZE // 2
    L = bloque_entrada[:half_size]
    R = bloque_entrada[half_size:]
    subkeys = get_subkeys(clave, FEISTEL_ROUNDS)
    for K_i in subkeys:
        L_next = R
        F_output = funcion_f_simplificada(R, K_i)
        R_next = xor_bytes(L, F_output)
        L, R = L_next, R_next
    return R + L

def _descifrar_bloque_feistel(bloque_cifrado: bytes, clave: bytes) -> bytes:
    """Decrypts one block using the Feistel Network."""
    half_size = BLOCK_SIZE // 2
    R = bloque_cifrado[:half_size]
    L = bloque_cifrado[half_size:]
    subkeys = get_subkeys(clave, FEISTEL_ROUNDS)
    subkeys.reverse()
    for K_i in subkeys:
        F_output = funcion_f_simplificada(L, K_i)
        L_prev = xor_bytes(R, F_output)
        R_prev = L
        L, R = L_prev, R_prev
    return L + R

# --- PUBLIC CBC FUNCTIONS ---

def cifrar_cbc(datos: bytes, clave: bytes, iv: bytes) -> bytes:
    """Encrypts data using CBC mode with Feistel."""
    datos_con_padding = pkcs7_padding(datos, BLOCK_SIZE)
    texto_cifrado = b''
    previous_ciphertext_block = iv
    
    for i in range(0, len(datos_con_padding), BLOCK_SIZE):
        bloque_p = datos_con_padding[i:i + BLOCK_SIZE]
        bloque_xor = xor_bytes(bloque_p, previous_ciphertext_block)
        bloque_c = _cifrar_bloque_feistel(bloque_xor, clave)
        texto_cifrado += bloque_c
        previous_ciphertext_block = bloque_c
        
    return texto_cifrado

def descifrar_cbc(datos_cifrados: bytes, clave: bytes, iv: bytes) -> bytes:
    """Decrypts data using CBC mode with Feistel."""
    if len(datos_cifrados) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext size is incorrect.")
        
    texto_descifrado_con_padding = b''
    previous_ciphertext_block = iv
    
    for i in range(0, len(datos_cifrados), BLOCK_SIZE):
        bloque_c = datos_cifrados[i:i + BLOCK_SIZE]
        bloque_descifrado = _descifrar_bloque_feistel(bloque_c, clave)
        bloque_p = xor_bytes(bloque_descifrado, previous_ciphertext_block)
        
        texto_descifrado_con_padding += bloque_p
        previous_ciphertext_block = bloque_c
        
    return pkcs7_unpadding(texto_descifrado_con_padding)

def cargar_componentes_clave(archivo_clave):
    """Loads and decodes the KEY and IV from the specified file."""
    try:
        with open(archivo_clave, "r") as f:
            lines = f.readlines()
            key_b64 = lines[0].strip().split(":")[1]
            iv_b64 = lines[1].strip().split(":")[1]
            
            KEY = base64.urlsafe_b64decode(key_b64)
            IV = base64.urlsafe_b64decode(iv_b64)
            return KEY, IV
            
    except Exception as e:
        raise IOError(f"Error loading key/IV. Check the format of '{archivo_clave}': {e}")