# CTF Challenge Solutions

## Challenge 1: Magic Token (Web Security)

**Флаг:** `flag{w5kz_c00k13_byp4ss_9f2a}`

Токен закодирован через **Base85 + ROT13** (не Base64 — старый код не работает).

```python
import base64, json

def rot13(s):
    result = []
    for c in s:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)

# Декодировать
token = "COOKIE_МӘНІ"
rotated = json.loads(base64.b85decode(token).decode())
data = {rot13(k): rot13(v) for k, v in rotated.items()}
# {'user': '...', 'role': 'guest'}

# Изменить и закодировать обратно
data['role'] = 'admin'
new_rotated = {rot13(k): rot13(v) for k, v in data.items()}
new_token = base64.b85encode(json.dumps(new_rotated).encode()).decode()
print(new_token)  # вставить в cookie role_token
```

---

## Challenge 2: XOR Encrypted Image (Cryptography)

**Флаг:** `flag{w5kz_xor_br3ak_7c1d}`

```python
with open('encrypted.bin', 'rb') as f:
    data = f.read()

PNG_SIG = bytes([0x89, 0x50, 0x4E, 0x47])
for key in range(256):
    dec = bytes([b ^ key for b in data])
    if dec[:4] == PNG_SIG:
        with open(f'result.png', 'wb') as out:
            out.write(dec)
        print(f"key=0x{key:02X}")
        break
```

---

## Challenge 3: Corrupted Header (Forensics)

**Флаг:** `flag{w5kz_h3ad3r_f1x_4e8b}`

```python
with open('flag.jpg', 'rb') as f:
    data = bytearray(f.read())
data[0], data[1] = 0xFF, 0xD8
with open('fixed.jpg', 'wb') as f:
    f.write(data)
```

---

## Challenge 4: Midnight Melody (Steganography)

**Флаг:** `flag{w5kz_st3g0_w4v_2k9x}`

```python
import zipfile
with open('challenge.wav', 'rb') as f:
    data = f.read()
offset = data.find(b'PK\x03\x04')
with open('hidden.zip', 'wb') as f:
    f.write(data[offset:])
with zipfile.ZipFile('hidden.zip') as z:
    print(z.read('flag.txt').decode())
```

---

## Флаги

| # | Флаг |
|---|------|
| ch1 | `flag{w5kz_c00k13_byp4ss_9f2a}` |
| ch2 | `flag{w5kz_xor_br3ak_7c1d}` |
| ch3 | `flag{w5kz_h3ad3r_f1x_4e8b}` |
| ch4 | `flag{w5kz_st3g0_w4v_2k9x}` |
