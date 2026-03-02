#!/usr/bin/env python3
"""
Challenge file generator for CTF Practice Platform.
Run this script once to create all necessary challenge files.
"""

import os
import struct
import wave
import json
import zipfile
import io

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGES_DIR = os.path.join(BASE_DIR, '..', 'challenges')
os.makedirs(CHALLENGES_DIR, exist_ok=True)

# ─── Challenge 2: XOR Encrypted Image ────────────────────────────────────────
def generate_xor_challenge():
    """Create a 1×1 white PNG then XOR-encrypt it with key 0x5A."""
    # Minimal valid 1x1 white PNG (raw bytes)
    png_bytes = bytes([
        0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,  # PNG signature
        0x00,0x00,0x00,0x0D,                          # IHDR length
        0x49,0x48,0x44,0x52,                          # IHDR
        0x00,0x00,0x00,0x01,                          # width = 1
        0x00,0x00,0x00,0x01,                          # height = 1
        0x08,0x02,                                    # 8-bit, RGB
        0x00,0x00,0x00,
        0x90,0x77,0x53,0xDE,                          # CRC
        0x00,0x00,0x00,0x0C,                          # IDAT length
        0x49,0x44,0x41,0x54,                          # IDAT
        0x08,0xD7,0x63,0xF8,0xFF,0xFF,0x3F,0x00,
        0x05,0xFE,0x02,0xFE,
        0xDC,0xCC,0x59,0xE7,                          # CRC
        0x00,0x00,0x00,0x00,                          # IEND length
        0x49,0x45,0x4E,0x44,                          # IEND
        0xAE,0x42,0x60,0x82,                          # CRC
    ])

    XOR_KEY = 0x5A
    encrypted = bytes([b ^ XOR_KEY for b in png_bytes])

    out_path = os.path.join(CHALLENGES_DIR, 'encrypted.bin')
    with open(out_path, 'wb') as f:
        f.write(encrypted)
    print(f"[+] Challenge 2: encrypted.bin created ({len(encrypted)} bytes, key=0x5A)")

# ─── Challenge 3: Corrupted JPEG Header ──────────────────────────────────────
def generate_corrupted_header_challenge():
    """
    Create a JPEG with a corrupted magic bytes header.
    The first 2 bytes (FF D8) are replaced with 00 00.
    Students must restore the JPEG header to view the flag text.
    """
    from PIL import Image, ImageDraw, ImageFont
    import io

    img = Image.new('RGB', (400, 100), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    text = "flag{header_restored_success}"
    draw.text((20, 35), text, fill=(0, 255, 128))

    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    jpeg_bytes = bytearray(buf.getvalue())

    # Corrupt the JPEG signature (FF D8 → 00 00)
    jpeg_bytes[0] = 0x00
    jpeg_bytes[1] = 0x00

    out_path = os.path.join(CHALLENGES_DIR, 'flag.jpg')
    with open(out_path, 'wb') as f:
        f.write(jpeg_bytes)
    print(f"[+] Challenge 3: flag.jpg created (header corrupted)")

# ─── Challenge 4: WAV Steganography ──────────────────────────────────────────
def generate_wav_challenge():
    """Embed a ZIP file containing flag.txt at the end of a WAV file."""

    # Create ZIP in memory
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('flag.txt', 'flag{hidden_in_sound}\n')

    zip_bytes = zip_buf.getvalue()

    # Create a simple WAV (1 second, 44100 Hz, mono, silence)
    wav_buf = io.BytesIO()
    with wave.open(wav_buf, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        # 1 second of silence
        wf.writeframes(b'\x00\x00' * 44100)

    wav_bytes = wav_buf.getvalue()

    # Append ZIP after WAV data
    combined = wav_bytes + zip_bytes

    out_path = os.path.join(CHALLENGES_DIR, 'challenge.wav')
    with open(out_path, 'wb') as f:
        f.write(combined)
    print(f"[+] Challenge 4: challenge.wav created (ZIP appended, {len(zip_bytes)} bytes)")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=== CTF Challenge File Generator ===\n")
    generate_xor_challenge()
    generate_corrupted_header_challenge()
    generate_wav_challenge()
    print("\n[✓] All challenge files generated in:", os.path.abspath(CHALLENGES_DIR))
