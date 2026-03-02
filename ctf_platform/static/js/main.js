// ── Flag Submission ───────────────────────────────
function submitFlag(chId) {
    const input = document.getElementById('flag-input');
    const result = document.getElementById('flag-result');
    const flag = input.value.trim();

    if (!flag) {
        showResult(result, 'wrong', '⚠️ Flag бос болмауы керек!');
        return;
    }

    const formData = new FormData();
    formData.append('flag', flag);

    fetch(`/submit/${chId}`, { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            showResult(result, data.result, data.message);
            if (data.result === 'correct') {
                document.querySelector('.nav .score-badge') &&
                    (document.querySelector('.score-badge').innerHTML =
                        `${data.score}<span class="score-max">/60</span> pts`);
                // Animate card solved
                input.style.borderColor = 'var(--accent-green)';
                input.disabled = true;
                document.querySelector('.btn-submit-flag').disabled = true;
                setTimeout(() => window.location.reload(), 1800);
            }
        })
        .catch(() => showResult(result, 'wrong', '❌ Сервер қатесі. Қайтадан байқаңыз.'));
}

function showResult(el, type, msg) {
    el.className = `flag-result ${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    el.style.animation = 'none';
    void el.offsetWidth; // reflow
    el.style.animation = 'fadeInUp .3s ease';
}

// Enter key for flag submission
document.addEventListener('DOMContentLoaded', () => {
    const fi = document.getElementById('flag-input');
    if (fi) {
        fi.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                const btn = document.querySelector('.btn-submit-flag');
                btn && btn.click();
            }
        });
    }

    // Typing animation for terminal-style headers
    const typed = document.querySelectorAll('[data-typewriter]');
    typed.forEach(el => {
        const text = el.getAttribute('data-typewriter');
        el.textContent = '';
        let i = 0;
        const timer = setInterval(() => {
            el.textContent += text[i];
            i++;
            if (i >= text.length) clearInterval(timer);
        }, 45);
    });
});
