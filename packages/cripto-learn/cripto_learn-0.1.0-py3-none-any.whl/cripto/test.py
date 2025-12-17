import cripto
import os
import sqlite3
import shutil
import random
import string
import sys
import binascii

# --- Configuration and Test Constants ---
KEY_FILE = 'clave_maestra_test.txt'
DB_NAME = 'db_test_cripto.sqlite'
TEST_DIR = 'temp_test_data'
WRONG_KEY = b'0' * 32 

CLAVE = None
IV = None

def get_random_string(length=30):
    """Generates a random string for file and token content."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def setup_key():
    """Generates the key material if it doesn't exist and loads it."""
    global CLAVE, IV
    
    print("\n[SETUP] 🔑 Verifying and Loading Cryptographic Material...")
    if not os.path.exists(KEY_FILE):
        cripto.generar_componentes_criptograficos(KEY_FILE)
        print(f"        -> Master Key file generated: {KEY_FILE}")
    
    try:
        CLAVE, IV = cripto.cargar_componentes_clave(KEY_FILE)
        print(f"        -> Key loaded (256-bit): {len(CLAVE)} bytes")
        print(f"        -> IV loaded (64-bit):    {len(IV)} bytes")
    except Exception as e:
        print(f"ERROR FATAL: Failed to load key material. {e}")
        sys.exit(1)

def create_test_files():
    """Creates the test directory structure with fresh files."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(os.path.join(TEST_DIR, 'sub_dir'), exist_ok=True)
    
    content_a = "Secret Content A: " + get_random_string()
    content_b = "Secret Content B: " + get_random_string()
    
    with open(os.path.join(TEST_DIR, 'file_a.txt'), 'w') as f:
        f.write(content_a)
    with open(os.path.join(TEST_DIR, 'sub_dir', 'file_b.txt'), 'w') as f:
        f.write(content_b)
        
    print(f"[FILES]  -> Test directory created at: {TEST_DIR}")
    
    return {
        os.path.join(TEST_DIR, 'file_a.txt'): content_a,
        os.path.join(TEST_DIR, 'sub_dir', 'file_b.txt'): content_b
    }

# --- Auxiliary File I/O Functions ---

def cifrar_archivo(input_path, output_path, key, iv):
    """Reads file data, encrypts it using cripto.cifrar_cbc(), and writes the ciphertext."""
    with open(input_path, 'rb') as f:
        data = f.read()
    ciphertext = cripto.cifrar_cbc(data, key, iv)
    with open(output_path, 'wb') as f:
        f.write(ciphertext)

def descifrar_archivo(input_path, output_path, key, iv):
    """Reads ciphertext, decrypts it using cripto.descifrar_cbc(), and writes the plaintext."""
    with open(input_path, 'rb') as f:
        data = f.read()
    plaintext = cripto.descifrar_cbc(data, key, iv)
    with open(output_path, 'wb') as f:
        f.write(plaintext)

# --- Core Tests ---

def test_core_functionality():
    """Tests the basic string encryption/decryption (cifrar_cbc and descifrar_cbc)."""
    print("\n=======================================================")
    print("🚀 TEST 1: CORE CIPHER FUNCTIONALITY (String/Bytes)")
    print("=======================================================")
    
    original_data = "This is the most critical secret."
    data_bytes = original_data.encode('utf-8')
    
    print(f"   [INFO] Original Data: '{original_data}' ({len(data_bytes)} bytes)")
    
    ciphertext = cripto.cifrar_cbc(data_bytes, CLAVE, IV)
    
    print(f"   [CIPHER] Ciphertext (Hex): {binascii.hexlify(ciphertext[:16]).decode()}... ({len(ciphertext)} bytes)")
    
    decrypted_bytes = cripto.descifrar_cbc(ciphertext, CLAVE, IV)
    decrypted_data = decrypted_bytes.decode('utf-8')
    
    print(f"   [DECIPHER] Decrypted Data: '{decrypted_data}'")
    
    success = (decrypted_data == original_data)
    assert success
    print(f"   [RESULT] ✅ PASS: Decrypted data matches original.")

def test_failure_handling():
    """Tests if decryption fails gracefully when the wrong key is used."""
    print("\n=======================================================")
    print("🚀 TEST 2: FAILURE HANDLING (Wrong Key Decryption)")
    print("=======================================================")

    original_data = "Testing error handling."
    data_bytes = original_data.encode('utf-8')
    
    ciphertext = cripto.cifrar_cbc(data_bytes, CLAVE, IV)
    print(f"   [INFO] Data encrypted with CORRECT Key (CLAVE).")
    
    try:
        print(f"   [ATTEMPT] Attempting decryption using WRONG_KEY (32 bytes of '0')...")
        cripto.descifrar_cbc(ciphertext, WRONG_KEY, IV) 
        
        assert False, "Decryption succeeded with the wrong key! (CRITICAL FAILURE)"
        
    except ValueError as e:
        print(f"   [RESULT] ✅ PASS: Decryption failed as expected, raising: {type(e).__name__} - {e}")
    except Exception as e:
        print(f"   [RESULT] ❌ FAIL: Unexpected error raised: {type(e).__name__} - {e}")
        assert False

def test_db_encryption():
    """Tests encryption/decryption within an SQLite column."""
    print("\n=======================================================")
    print("🚀 TEST 3: DATABASE COLUMN ENCRYPTION/DECRYPTION")
    print("=======================================================")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS tokens')
    c.execute('CREATE TABLE tokens (id INTEGER PRIMARY KEY, service TEXT, secret_token BLOB NOT NULL)')
    print(f"   [DB] Database '{DB_NAME}' initialized.")
    
    service_name = "API_Gateway"
    token_plano = "tk_prod_" + get_random_string(10)
    
    token_bytes = token_plano.encode('utf-8')
    token_cifrado = cripto.cifrar_cbc(token_bytes, CLAVE, IV)
    
    c.execute("INSERT INTO tokens (service, secret_token) VALUES (?, ?)", 
              (service_name, token_cifrado))
    conn.commit()
    print(f"   [ACTION] Inserted token for '{service_name}' (Encrypted BLOB).")
    
    c.execute("SELECT secret_token FROM tokens WHERE service = ?", (service_name,))
    token_cifrado_db = c.fetchone()[0]
    token_descifrado_bytes = cripto.descifrar_cbc(token_cifrado_db, CLAVE, IV)
    token_descifrado_plano = token_descifrado_bytes.decode('utf-8')
    
    success = (token_descifrado_plano == token_plano)
    assert success
    print(f"   [RESULT] ✅ PASS: DB token decrypted to '{token_descifrado_plano}'.")
    conn.close()

def test_file_encryption():
    """Tests the encryption and decryption of a single file."""
    print("\n=======================================================")
    print("🚀 TEST 4: SINGLE FILE ENCRYPTION/DECRYPTION")
    print("=======================================================")
    
    initial_contents = create_test_files()
    input_file = os.path.join(TEST_DIR, 'file_a.txt')
    encrypted_file = os.path.join(TEST_DIR, 'file_a.enc')
    decrypted_file = os.path.join(TEST_DIR, 'file_a.dec.txt')
    original_content = initial_contents[input_file]
    
    cifrar_archivo(input_file, encrypted_file, CLAVE, IV)
    os.remove(input_file)
    print(f"   [ACTION] Encrypting '{input_file}' to '{encrypted_file}'.")
    
    descifrar_archivo(encrypted_file, decrypted_file, CLAVE, IV)
    print(f"   [ACTION] Decrypting '{encrypted_file}' to '{decrypted_file}'.")

    with open(decrypted_file, 'r') as f:
        recovered_content = f.read()
    
    success = (recovered_content == original_content)
    assert success
    print(f"   [RESULT] ✅ PASS: Recovered file content is identical to original.")
    
    shutil.rmtree(TEST_DIR)

def test_directory_encryption():
    """Tests the recursive encryption and decryption of an entire directory."""
    print("\n=======================================================")
    print("🚀 TEST 5: RECURSIVE DIRECTORY ENCRYPTION/DECRYPTION")
    print("=======================================================")
    
    original_contents = create_test_files()
    
    print("   [STEP 1] Starting Recursive Directory ENCRYPTION...")
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.endswith('.txt'):
                input_path = os.path.join(root, file)
                output_path = input_path + '.enc'
                cifrar_archivo(input_path, output_path, CLAVE, IV)
                os.remove(input_path) 
                print(f"   [ENCRYPTED] -> {file} -> {os.path.basename(output_path)}")
    
    print("\n   [STEP 2] Starting Recursive Directory DECRYPTION...")
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.endswith('.enc'):
                input_path = os.path.join(root, file)
                output_path = input_path.replace('.enc', '.recuperado.txt') 
                descifrar_archivo(input_path, output_path, CLAVE, IV)
                os.remove(input_path) 
                print(f"   [DECRYPTED] -> {file} -> {os.path.basename(output_path)}")

    print("\n   [STEP 3] Verifying recovered contents...")
    all_recovered_ok = True
    for original_path, original_content in original_contents.items():
        recovered_file = original_path.replace('.txt', '.txt.recuperado.txt')
        
        with open(recovered_file, 'r') as f:
            recovered_content = f.read()
        
        if recovered_content != original_content:
            print(f"   [ERROR] Content mismatch detected in {os.path.basename(original_path)}")
            all_recovered_ok = False
            break
            
    assert all_recovered_ok
    print(f"   [RESULT] ✅ PASS: All directory files verified successfully.")

def cleanup():
    """Cleans up all created test artifacts."""
    print("\n=======================================================")
    print("🧹 FINAL CLEANUP")
    print("=======================================================")
    
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
        print(f"   -> Test directory removed: {TEST_DIR}")
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"   -> Test database removed: {DB_NAME}")
    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
        print(f"   -> Master key file removed: {KEY_FILE}")

# --- PROGRAM EXECUTION ---
if __name__ == "__main__":
    
    try:
        setup_key()
        
        test_core_functionality()
        test_failure_handling()
        test_db_encryption()
        test_file_encryption()
        test_directory_encryption()
        
        print("\n\n#######################################################")
        print("🎉 🎉 ALL 'CRIPTO' LIBRARY TESTS PASSED SUCCESSFULLY! 🎉 🎉")
        print("#######################################################")
        
    except AssertionError as e:
        print("\n\n❌ ❌ ASSERTION FAILURE! A verification step failed.")
        print(f"Error details: {e}")
    except Exception as e:
        print(f"\n\n❌ ❌ AN UNEXPECTED ERROR OCCURRED: {type(e).__name__}: {e}")
    finally:
        cleanup()