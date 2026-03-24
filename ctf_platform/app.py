"""
CTF Practice Platform – Flask Backend
Module A + B | Оқу мақсатындағы платформа
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
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = bool(os.environ.get('RENDER', False))  # True on Render (HTTPS)

CHALLENGES_DIR = os.path.join(os.path.dirname(__file__), 'challenges')

# ─── Token encoding for Challenge 1 ──────────────────────────────────────────
# Simple Base64 encoded JSON — students must decode and change role to admin.

# ─── Users ─────────────────────────────────────────────────────────────────
USERS = {
    'ali':    '12345678',
    'aizat':  '12345678',
    'berik':  '12345678',
    'student': '12345678',
}

# ─── Flags & Points ────────────────────────────────────────────────────────
FLAGS = {
    'ch1': 'flag{w5kz_c00k13_byp4ss_9f2a}',
    'ch2': 'flag{w5kz_xor_br3ak_7c1d}',
    'ch3': 'flag{w5kz_h3ad3r_f1x_4e8b}',
    'ch4': 'flag{w5kz_st3g0_w4v_2k9x}',
    # Module B
    'ch_b1': 'flag{w5kz_rce_upl04d_3x9p}',
    'ch_b2': 'flag{w5kz_r00t_su1d_7f3k}',
}
POINTS_PER_CHALLENGE = 15

# ─── Module A metadata ────────────────────────────────────────────────────────
CHALLENGE_META = {
    'ch1': {
        'title': 'Magic Token',
        'category': 'Web Security',
        'icon': '🔑',
        'difficulty': 'Оңай',
        'difficulty_class': 'easy',
        'description': (
            'Біз жаңа әкімшілік (admin) панелін іске қостық. Оған кіру үшін admin құқығы қажет. '
            'Қазіргі уақытта жүйе сізге тек guest рұқсатын беріп тұр. '
            'Жүйені алдап, өзіңізді Admin ретінде таныстырыңыз және түды алыңыз.'
        ),
        'hint': '',
    },
    'ch2': {
        'title': 'XORed Image',
        'category': 'Cryptography',
        'icon': '🔒',
        'difficulty': 'Орташа',
        'difficulty_class': 'medium',
        'description': (
            'Біз қылмыскерлердің компьютерлік желісінен маңызды суретті қолға түсірдік. '
            'Бірақ файл ашылмай тұр. Барлаушылардың айтуынша бұл PNG сурет, '
            'XOR амалымен шифрланған, кілт небәрі 1 байт. Brute-force жасап суретті қалпына келтіріңіз.'
        ),
        'hint': '',
    },
    'ch3': {
        'title': 'Corrupted Header',
        'category': 'Forensics',
        'icon': '🔍',
        'difficulty': 'Орташа',
        'difficulty_class': 'medium',
        'description': (
            'Жүйелік әкімшілеріміз хакерлердің серверінен маңызды файлды ұстап қалды. '
            'Файлда жасырын flag бар, бірақ ашылмайды — хакерлер тақырыпшасын бүлдіріп кеткен. '
            'Файл құрылымын зерттеп, қалпына келтіріп, суреттегі түды табыңыз.'
        ),
        'hint': '',
    },
    'ch4': {
        'title': 'Midnight Melody',
        'category': 'Steganography',
        'icon': '🎵',
        'difficulty': 'Қиын',
        'difficulty_class': 'hard',
        'description': (
            'Киберқауіпсіздік бөліміміз күдікті серверден музыкалық файл тапты. '
            'Әуеннің өзінде ешнәрсе естілмейді, бірақ файлдың құрылымында артық нәрсе бар сияқты. '
            'Файлдың ішкі құрылымын тексеріп, жасырын файлды шығарып алыңыз.'
        ),
        'hint': '',
    },
}

# ─── Module B metadata ────────────────────────────────────────────────────────
CHALLENGE_META_B = {
    'ch_b1': {
        'title': 'Corporate File Server',
        'category': 'Web Exploitation',
        'icon': '🌐',
        'difficulty': 'Орташа',
        'difficulty_class': 'medium',
        'description': (
            'Барлаушылар бәсекелестің корпоративтік файл алмасу серверін тапты. '
            'Сайттағы осалдықты тауып, серверге файл жүктеңіз (RCE). '
            'www-data немесе user атынан серверге кіріңіз және /home/user/user.txt файлындағы жалаушаны табыңыз. '
            'Сілтеме: https://test-cyvebr.onrender.com/'
        ),
        'hint': '',
    },
    'ch_b2': {
        'title': 'Root Access',
        'category': 'Privilege Escalation',
        'icon': '👑',
        'difficulty': 'Қиын',
        'difficulty_class': 'hard',
        'description': (
            'Сіз сервердің ішіндесіз, бірақ құқығыңыз шектеулі. '
            'Жүйе әкімшісі (root) кейбір бағдарламаларды дұрыс баптамаған сияқты. '
            'SUID биттері бар файлдарды зерттеп, root құқығын иемденіп, /root/root.txt файлындағы жалаушаны табыңыз. '
            'Сілтеме: https://test-cyvebr.onrender.com/'
        ),
        'hint': '',
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
        challenges_b=CHALLENGE_META_B,
        solved=solved,
        score=get_score(),
        max_score=len(FLAGS) * POINTS_PER_CHALLENGE,
    )

# ─── Challenge Pages ─────────────────────────────────────────────────────────
@app.route('/challenge/<ch_id>')
@login_required
def challenge(ch_id):
    if ch_id in CHALLENGE_META:
        meta = CHALLENGE_META[ch_id]
        solved = session.get('solved', [])
        return render_template(
            f'challenge{ch_id[2:]}.html',
            ch_id=ch_id, meta=meta, solved=solved,
            score=get_score(), username=session['username'],
        )
    elif ch_id in CHALLENGE_META_B:
        meta = CHALLENGE_META_B[ch_id]
        solved = session.get('solved', [])
        return render_template(
            f'challenge_b{ch_id[4:]}.html',
            ch_id=ch_id, meta=meta, solved=solved,
            score=get_score(), username=session['username'],
        )
    return redirect(url_for('dashboard'))

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
    breakdown_a = []
    for ch_id, meta in CHALLENGE_META.items():
        breakdown_a.append({
            'ch_id': ch_id, 'title': meta['title'], 'category': meta['category'],
            'icon': meta['icon'], 'points': POINTS_PER_CHALLENGE if ch_id in solved else 0,
            'solved': ch_id in solved,
        })
    breakdown_b = []
    for ch_id, meta in CHALLENGE_META_B.items():
        breakdown_b.append({
            'ch_id': ch_id, 'title': meta['title'], 'category': meta['category'],
            'icon': meta['icon'], 'points': POINTS_PER_CHALLENGE if ch_id in solved else 0,
            'solved': ch_id in solved,
        })
    return render_template(
        'scoreboard.html',
        username=session['username'],
        breakdown_a=breakdown_a,
        breakdown_b=breakdown_b,
        score=get_score(),
        max_score=len(FLAGS) * POINTS_PER_CHALLENGE,
    )

# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
