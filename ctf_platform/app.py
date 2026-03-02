"""
CTF Practice Platform – Flask Backend
Module A | Оқу мақсатындағы платформа
"""

import os
import json
import base64
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, send_from_directory, make_response, jsonify
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ctf_super_secret_key_2024')

CHALLENGES_DIR = os.path.join(os.path.dirname(__file__), 'challenges')

# ─── Users ─────────────────────────────────────────────────────────────────
USERS = {
    'ali':    '12345678',
    'aizat':  '12345678',
    'berik':  '12345678',
    'student': '12345678',
}

# ─── Flags & Points ────────────────────────────────────────────────────────
FLAGS = {
    'ch1': 'flag{magic_token_admin_access}',
    'ch2': 'flag{xor_key_is_0x5A}',
    'ch3': 'flag{header_restored_success}',
    'ch4': 'flag{hidden_in_sound}',
}
POINTS_PER_CHALLENGE = 15

CHALLENGE_META = {
    'ch1': {
        'title': 'Magic Token',
        'category': 'Web Security',
        'icon': '🔑',
        'difficulty': 'Оңай',
        'difficulty_class': 'easy',
        'description': (
            'Сервер сессия мәліметтерін cookie ішінде Base64 кодталған JSON '
            'түрінде сақтайды. role мәні guest болып тұр. '
            'Cookie-ді өзгертіп role=admin жасасаң /admin бетінде flag табасың.'
        ),
        'hint': 'Браузер DevTools → Application → Cookies → role_token дегенді тауып өзгерт.',
    },
    'ch2': {
        'title': 'XORed Image',
        'category': 'Cryptography',
        'icon': '🔒',
        'difficulty': 'Орташа',
        'difficulty_class': 'medium',
        'description': (
            'encrypted.bin файлы жүктеле алады. Ол PNG суреті 1 байттық XOR '
            'кілтімен шифрланған. Кілт 0x00–0xFF арасында. Brute-force жасап '
            'дұрыс кілтті тап да суретті қалпына келтір.'
        ),
        'hint': 'Дұрыс шифрсызданған PNG файлы 0x89 0x50 0x4E 0x47 байттарынан басталады.',
    },
    'ch3': {
        'title': 'Corrupted Header',
        'category': 'Forensics',
        'icon': '🔍',
        'difficulty': 'Орташа',
        'difficulty_class': 'medium',
        'description': (
            'flag.jpg файлының алғашқы байттары бүлінген. JPEG сигнатурасын '
            'қалпына келтіріп суретті ашсаң flag табасың.'
        ),
        'hint': 'JPEG файлдары FF D8 FF E0 байттарынан басталуы керек. Hex editor қолдан.',
    },
    'ch4': {
        'title': 'Midnight Melody',
        'category': 'Steganography',
        'icon': '🎵',
        'difficulty': 'Қиын',
        'difficulty_class': 'hard',
        'description': (
            'challenge.wav аудио файлының ішінде ZIP мұрағаты жасырылған. '
            'Файлды мұқият талдап ZIP-ті тауып оның ішіндегі flag.txt-ті оқы.'
        ),
        'hint': 'WAV файлының соңына бинарлық зерттеу жаса. ZIP сигнатурасы: 50 4B 03 04.',
    },
}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_score():
    solved = session.get('solved', [])
    return len(solved) * POINTS_PER_CHALLENGE

# ─── Auth ─────────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        if username in USERS and USERS[username] == password:
            session.clear()
            session['username'] = username
            session['solved'] = []

            # Set challenge-1 role cookie (guest by default)
            resp = make_response(redirect(url_for('dashboard')))
            payload = base64.b64encode(
                json.dumps({'user': username, 'role': 'guest'}).encode()
            ).decode()
            resp.set_cookie('role_token', payload, httponly=False)  # intentionally not httponly
            return resp
        else:
            error = 'Логин немесе пароль қате!'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('role_token')
    return resp

# ─── Dashboard ────────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    solved = session.get('solved', [])
    return render_template(
        'dashboard.html',
        username=session['username'],
        challenges=CHALLENGE_META,
        solved=solved,
        score=get_score(),
        max_score=len(FLAGS) * POINTS_PER_CHALLENGE,
    )

# ─── Challenge Pages ─────────────────────────────────────────────────────────
@app.route('/challenge/<ch_id>')
@login_required
def challenge(ch_id):
    if ch_id not in CHALLENGE_META:
        return redirect(url_for('dashboard'))
    meta = CHALLENGE_META[ch_id]
    solved = session.get('solved', [])
    return render_template(
        f'challenge{ch_id[2:]}.html',
        ch_id=ch_id,
        meta=meta,
        solved=solved,
        score=get_score(),
        username=session['username'],
    )

# ─── Flag Submit ──────────────────────────────────────────────────────────────
@app.route('/submit/<ch_id>', methods=['POST'])
@login_required
def submit_flag(ch_id):
    if ch_id not in FLAGS:
        return jsonify({'result': 'error', 'message': 'Тапсырма табылмады'})

    flag = request.form.get('flag', '').strip()
    solved = session.get('solved', [])

    if ch_id in solved:
        return jsonify({'result': 'already', 'message': 'Бұл тапсырманы бұрын шештіңіз!'})

    if flag == FLAGS[ch_id]:
        solved.append(ch_id)
        session['solved'] = solved
        new_score = get_score()
        return jsonify({
            'result': 'correct',
            'message': '✅ Дұрыс! Flag қабылданды.',
            'score': new_score,
        })
    else:
        return jsonify({'result': 'wrong', 'message': '❌ Қате Flag. Тағы байқап көр!'})

# ─── Challenge 1: Admin Page ──────────────────────────────────────────────────
@app.route('/admin')
@login_required
def admin():
    cookie_val = request.cookies.get('role_token', '')
    flag = None
    error = None

    if cookie_val:
        try:
            decoded = json.loads(base64.b64decode(cookie_val).decode())
            if decoded.get('role') == 'admin':
                flag = FLAGS['ch1']
            else:
                error = f'Рұқсат жоқ. Сіздің рөліңіз: {decoded.get("role", "?")}'
        except Exception:
            error = 'Cookie форматы қате!'
    else:
        error = 'role_token cookie табылмады!'

    return render_template(
        'admin.html',
        flag=flag,
        error=error,
        score=get_score(),
        username=session['username'],
    )

# ─── Static Challenge Files ───────────────────────────────────────────────────
@app.route('/files/<filename>')
@login_required
def serve_challenge_file(filename):
    allowed = {'encrypted.bin', 'flag.jpg', 'challenge.wav'}
    if filename not in allowed:
        return 'Not Found', 404
    return send_from_directory(CHALLENGES_DIR, filename, as_attachment=True)

# ─── Scoreboard ───────────────────────────────────────────────────────────────
@app.route('/scoreboard')
@login_required
def scoreboard():
    solved = session.get('solved', [])
    breakdown = []
    for ch_id, meta in CHALLENGE_META.items():
        breakdown.append({
            'ch_id': ch_id,
            'title': meta['title'],
            'category': meta['category'],
            'icon': meta['icon'],
            'points': POINTS_PER_CHALLENGE if ch_id in solved else 0,
            'solved': ch_id in solved,
        })
    return render_template(
        'scoreboard.html',
        username=session['username'],
        breakdown=breakdown,
        score=get_score(),
        max_score=len(FLAGS) * POINTS_PER_CHALLENGE,
    )

# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
