# CTF Challenge Solutions

Это руководство для проверки всех заданий платформы.

## Challenge 1: Magic Token (Web Security)

**Флаг:** `flag{magic_token_admin_access}`

**Решение:**
1. Войти в систему (любой пользователь)
2. Открыть DevTools → Application → Cookies
3. Найти cookie `role_token`
4. Декодировать Base64: `{"user": "student", "role": "guest"}`
5. Изменить на: `{"user": "student", "role": "admin"}`
6. Закодировать в Base64: `eyJ1c2VyIjogInN0dWRlbnQiLCAicm9sZSI6ICJhZG1pbiJ9`
7. Заменить cookie и перейти на `/admin`

**Проверка:**
```python
import base64, json
admin = base64.b64encode(json.dumps({'user': 'student', 'role': 'admin'}).encode()).decode()
print(admin)  # eyJ1c2VyIjogInN0dWRlbnQiLCAicm9sZSI6ICJhZG1pbiJ9
```

---

## Challenge 2: XOR Encrypted Image (Cryptography)

**Флаг:** `flag{xor_key_is_0x5A}`

**Решение:**
1. Скачать `encrypted.bin`
2. Использовать brute-force для поиска XOR ключа
3. PNG файлы начинаются с `89 50 4E 47`
4. Ключ: `0x5A`
5. Расшифровать и открыть PNG

**Проверка:**
```python
with open('encrypted.bin', 'rb') as f:
    data = f.read()

PNG_SIG = bytes([0x89, 0x50, 0x4E, 0x47])

for key in range(256):
    decrypted = bytes([b ^ key for b in data])
    if decrypted[:4] == PNG_SIG:
        print(f"Ключ: 0x{key:02X}")
        with open('result.png', 'wb') as out:
            out.write(decrypted)
        break
```

---

## Challenge 3: Corrupted Header (Forensics)

**Флаг:** `flag{header_restored_success}`

**Решение:**
1. Скачать `flag.jpg`
2. Открыть в hex editor
3. Первые байты: `00 00 FF E0` (испорчены)
4. Исправить на: `FF D8 FF E0` (JPEG signature)
5. Сохранить и открыть изображение

**Проверка:**
```python
with open('flag.jpg', 'rb') as f:
    data = bytearray(f.read())

# Исправить заголовок
data[0] = 0xFF
data[1] = 0xD8

with open('fixed.jpg', 'wb') as f:
    f.write(data)
```

---

## Challenge 4: Midnight Melody (Steganography)

**Флаг:** `flag{hidden_in_sound}`

**Решение:**
1. Скачать `challenge.wav`
2. Открыть в hex editor или использовать binwalk
3. Найти ZIP signature: `50 4B 03 04` (PK)
4. Извлечь ZIP архив из конца файла
5. Распаковать и прочитать `flag.txt`

**Проверка:**
```python
with open('challenge.wav', 'rb') as f:
    data = f.read()

# Найти ZIP
zip_offset = data.find(b'PK\x03\x04')
print(f"ZIP найден на позиции: {zip_offset}")

# Извлечь ZIP
with open('hidden.zip', 'wb') as f:
    f.write(data[zip_offset:])

# Распаковать
import zipfile
with zipfile.ZipFile('hidden.zip', 'r') as zf:
    flag = zf.read('flag.txt').decode()
    print(flag)
```

---

## Автоматическая проверка

Запустить тестовый скрипт:
```bash
python3 scripts/test_challenges.py
```

Этот скрипт проверит все задания и создаст расшифрованные файлы в папке `challenges/`.

---

## Флаги для быстрой проверки

1. Challenge 1: `flag{w5kz_c00k13_byp4ss_9f2a}`
2. Challenge 2: `flag{w5kz_xor_br3ak_7c1d}`
3. Challenge 3: `flag{w5kz_h3ad3r_f1x_4e8b}`
4. Challenge 4: `flag{w5kz_st3g0_w4v_2k9x}`
