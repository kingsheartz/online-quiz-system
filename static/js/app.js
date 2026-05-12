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

  // Custom Modal Logic
  window.openModal = function(title, message, callback) {
    const modal = document.getElementById('deleteModal');
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalMessage').innerText = message;
    modal.classList.add('active');
    
    const confirmBtn = document.getElementById('confirmActionBtn');
    // Remove old listeners
    const newBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
    
    newBtn.addEventListener('click', () => {
      callback();
      closeModal();
    });
  };

  window.closeModal = function() {
    document.getElementById('deleteModal').classList.remove('active');
  };

  // Close modal on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Handle all delete button clicks using event delegation
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-delete-confirm');
    if (btn) {
      e.preventDefault();
      const form = btn.closest('form');
      const msg = btn.getAttribute('data-message') || 'Are you sure you want to delete this?';
      openModal('Delete Confirmation', msg, () => {
        form.submit();
      });
    }
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
