// ═══════════════════════════════════════════════════════
// QuizMaster — JavaScript Module
// ═══════════════════════════════════════════════════════

// ─── Theme Switcher ─────────────────────────────────────
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === theme);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Theme buttons
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.dataset.theme;
      setTheme(theme);
      window.location.href = '/set-theme/' + theme;
    });
  });

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // Auto-dismiss flash messages
  document.querySelectorAll('.flash').forEach(flash => {
    flash.addEventListener('click', () => flash.remove());
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(30px)';
      setTimeout(() => flash.remove(), 300);
    }, 4000);
  });

  // Confirm delete actions
  document.querySelectorAll('.confirm-delete').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Radio option selection visual feedback
  document.querySelectorAll('.form-check input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', () => {
      const name = radio.name;
      document.querySelectorAll(`.form-check input[name="${name}"]`).forEach(r => {
        r.closest('.form-check').classList.remove('selected');
      });
      radio.closest('.form-check').classList.add('selected');
    });
  });
});

// ─── Quiz Timer ─────────────────────────────────────────
function initQuizTimer(durationSeconds, formId) {
  let timeLeft = durationSeconds;
  const timerDisplay = document.getElementById('timer-display');
  const timerProgress = document.getElementById('timer-progress-bar');
  const form = document.getElementById(formId);
  if (!timerDisplay || !form) return;

  const interval = setInterval(() => {
    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    timerDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

    const pct = (timeLeft / durationSeconds) * 100;
    if (timerProgress) timerProgress.style.width = pct + '%';

    if (pct < 20) {
      timerDisplay.className = 'timer-display danger';
    } else if (pct < 40) {
      timerDisplay.className = 'timer-display warning';
    }

    if (timeLeft <= 0) {
      clearInterval(interval);
      alert('Time is up! Your quiz will be submitted automatically.');
      form.submit();
    }
    timeLeft--;
  }, 1000);
}
