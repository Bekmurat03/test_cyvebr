# 🛡️ CTF Practice Platform – Module A

Студенттерге арналған ақпараттық қауіпсіздік практикалық оқу платформасы.

## 🚀 Жылдам іске қосу

### 1. Virtual environment жасап, тәуелділіктерді орнату

```bash
cd ctf_platform
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Challenge файлдарын генерациялау

```bash
python scripts/generate_challenges.py
```

### 3. Flask сервері іске қосу

```bash
python app.py
```

Браузерде: **http://localhost:5000**

---

### 🐳 Docker арқылы іске қосу

```bash
docker-compose up --build
```

Немесе тікелей:

```bash
docker build -t ctf-platform .
docker run -p 5000:5000 ctf-platform
```

---

## 🔐 Кіру деректері

| Логин   | Пароль   |
| ------- | -------- |
| ali     | 12345678 |
| aizat   | 12345678 |
| berik   | 12345678 |
| student | 12345678 |

---

## 🧩 Тапсырмалар

| #   | Атауы            | Санат         | Қиындық | Ұпай |
| --- | ---------------- | ------------- | ------- | ---- |
| 1   | Magic Token      | Web Security  | Оңай    | 15   |
| 2   | XORed Image      | Cryptography  | Орташа  | 15   |
| 3   | Corrupted Header | Forensics     | Орташа  | 15   |
| 4   | Midnight Melody  | Steganography | Қиын    | 15   |

**Максималды ұпай: 60**

---

## 🗂️ Жоба құрылымы

```
ctf_platform/
├── app.py                    # Flask backend
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── scripts/
│   └── generate_challenges.py  # Challenge файл генераторы
├── challenges/               # Генерацияланған файлдар
│   ├── encrypted.bin         # Challenge 2
│   ├── flag.jpg              # Challenge 3
│   └── challenge.wav         # Challenge 4
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── challenge1.html
    ├── challenge2.html
    ├── challenge3.html
    ├── challenge4.html
    ├── admin.html
    └── scoreboard.html
```

---

## ⚠️ Ескерту

Бұл платформа **тек оқу мақсатында** жасалған. Production ортасында пайдалануға арналмаған.
