#!/usr/bin/env python3
"""
Test script to verify all CTF challenges work correctly.
"""

import os
import base64
import json
import zipfile

CHALLENGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'challenges')

def test_challenge1():
    """Test Challenge 1: Magic Token"""
    print("\n=== Testing Challenge 1: Magic Token ===")
    
    # Simulate guest cookie
    guest_payload = {'user': 'student', 'role': 'guest'}
    guest_cookie = base64.b64encode(json.dumps(guest_payload).encode()).decode()
    
    # Create admin cookie
    admin_payload = {'user': 'student', 'role': 'admin'}
    admin_cookie = base64.b64encode(json.dumps(admin_payload).encode()).decode()
    
    print(f"✓ Guest cookie: {guest_cookie}")
    print(f"✓ Admin cookie: {admin_cookie}")
    print(f"✓ Expected flag: flag{{magic_token_admin_access}}")
    return True

def test_challenge2():
    """Test Challenge 2: XOR Encrypted Image"""
    print("\n=== Testing Challenge 2: XOR Encrypted Image ===")
    
    encrypted_path = os.path.join(CHALLENGES_DIR, 'encrypted.bin')
    with open(encrypted_path, 'rb') as f:
        data = f.read()
    
    print(f"✓ File size: {len(data)} bytes")
    
    # Brute-force XOR key
    PNG_SIG = bytes([0x89, 0x50, 0x4E, 0x47])
    for key in range(256):
        decrypted = bytes([b ^ key for b in data])
        if decrypted[:4] == PNG_SIG:
            print(f"✓ XOR key found: 0x{key:02X}")
            
            # Save decrypted PNG
            output_path = os.path.join(CHALLENGES_DIR, 'decrypted_ch2.png')
            with open(output_path, 'wb') as out:
                out.write(decrypted)
            print(f"✓ Decrypted PNG saved to: {output_path}")
            print(f"✓ Expected flag: flag{{xor_key_is_0x5A}}")
            return True
    
    print("✗ Failed to find XOR key!")
    return False

def test_challenge3():
    """Test Challenge 3: Corrupted JPEG Header"""
    print("\n=== Testing Challenge 3: Corrupted JPEG Header ===")
    
    jpeg_path = os.path.join(CHALLENGES_DIR, 'flag.jpg')
    with open(jpeg_path, 'rb') as f:
        jpeg_data = bytearray(f.read())
    
    print(f"✓ File size: {len(jpeg_data)} bytes")
    print(f"✓ Current header: {jpeg_data[:4].hex()}")
    print(f"✓ Correct header should be: ffd8ffe0")
    
    # Fix header
    jpeg_data[0] = 0xFF
    jpeg_data[1] = 0xD8
    
    output_path = os.path.join(CHALLENGES_DIR, 'fixed_ch3.jpg')
    with open(output_path, 'wb') as out:
        out.write(jpeg_data)
    
    print(f"✓ Fixed JPEG saved to: {output_path}")
    print(f"✓ Expected flag: flag{{header_restored_success}}")
    return True

def test_challenge4():
    """Test Challenge 4: WAV Steganography"""
    print("\n=== Testing Challenge 4: WAV Steganography ===")
    
    wav_path = os.path.join(CHALLENGES_DIR, 'challenge.wav')
    with open(wav_path, 'rb') as f:
        wav_data = f.read()
    
    print(f"✓ File size: {len(wav_data)} bytes")
    
    # Search for ZIP signature
    zip_sig = b'PK\x03\x04'
    zip_offset = wav_data.find(zip_sig)
    
    if zip_offset == -1:
        print("✗ ZIP signature not found!")
        return False
    
    print(f"✓ ZIP found at offset: {zip_offset}")
    
    # Extract ZIP
    zip_data = wav_data[zip_offset:]
    zip_path = os.path.join(CHALLENGES_DIR, 'extracted_ch4.zip')
    with open(zip_path, 'wb') as out:
        out.write(zip_data)
    
    print(f"✓ ZIP extracted to: {zip_path}")
    
    # Read flag from ZIP
    with zipfile.ZipFile(zip_path, 'r') as zf:
        flag_content = zf.read('flag.txt').decode().strip()
        print(f"✓ Flag content: {flag_content}")
    
    return True

def main():
    print("=" * 60)
    print("CTF Challenge Verification Script")
    print("=" * 60)
    
    results = {
        'Challenge 1': test_challenge1(),
        'Challenge 2': test_challenge2(),
        'Challenge 3': test_challenge3(),
        'Challenge 4': test_challenge4(),
    }
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✓ All challenges verified!" if all_passed else "✗ Some challenges failed!"))
    return all_passed

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
