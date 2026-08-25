/**
 * AI Event Registration — Main frontend utilities
 */

const API = {
  async get(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },
};

/* ── Toast notifications ───────────────────────────────────────────────────── */

function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.textContent = message;
  toast.setAttribute('role', 'alert');
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = '0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ── Animated counters ─────────────────────────────────────────────────────── */

function animateCounter(element, target, suffix = '', duration = 2000) {
  const start = performance.now();
  const isDecimal = !Number.isInteger(target);

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;

    if (isDecimal) {
      element.textContent = current.toFixed(1) + suffix;
    } else {
      element.textContent = Math.floor(current).toLocaleString() + suffix;
    }

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

async function loadStats() {
  const statElements = document.querySelectorAll('[data-stat]');
  if (!statElements.length) return;

  try {
    const result = await API.get('/api/stats');
    if (!result.success) return;

    const data = result.data;
    statElements.forEach((el) => {
      const key = el.dataset.stat;
      const suffix = el.dataset.suffix || '';
      const value = data[key];
      if (value !== undefined) {
        animateCounter(el, value, suffix);
      }
    });
  } catch (err) {
    console.warn('Failed to load stats:', err);
    statElements.forEach((el) => {
      el.textContent = '—';
    });
  }
}

/* ── Workflow step animation ─────────────────────────────────────────────────── */

function initWorkflowAnimation() {
  const steps = document.querySelectorAll('.workflow-step');
  if (!steps.length) return;

  let currentStep = 0;
  const totalSteps = steps.length;
  const stepDuration = 2000;

  function activateStep(index) {
    steps.forEach((step, i) => {
      step.classList.remove('workflow-step--active', 'workflow-step--completed');
      if (i < index) {
        step.classList.add('workflow-step--completed');
      } else if (i === index) {
        step.classList.add('workflow-step--active');
      }
    });

    const connectors = document.querySelectorAll('.workflow-connector');
    connectors.forEach((conn, i) => {
      conn.classList.toggle('workflow-connector--active', i < index);
    });
  }

  activateStep(0);

  setInterval(() => {
    currentStep = (currentStep + 1) % totalSteps;
    activateStep(currentStep);
  }, stepDuration);
}

/* ── Particle background ───────────────────────────────────────────────────── */

function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let animationId;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function createParticles() {
    const count = Math.min(Math.floor(window.innerWidth / 15), 80);
    particles = [];
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1.5 + 0.5,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.5 + 0.1,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 212, 255, ${p.opacity})`;
      ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 212, 255, ${0.08 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    animationId = requestAnimationFrame(draw);
  }

  resize();
  createParticles();
  draw();

  window.addEventListener('resize', () => {
    resize();
    createParticles();
  });

  return () => cancelAnimationFrame(animationId);
}

/* ── Mobile navigation ─────────────────────────────────────────────────────── */

function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const mobile = document.getElementById('navMobile');
  if (!toggle || !mobile) return;

  toggle.addEventListener('click', () => {
    const isOpen = mobile.hasAttribute('hidden');
    if (isOpen) {
      mobile.removeAttribute('hidden');
      toggle.setAttribute('aria-expanded', 'true');
    } else {
      mobile.setAttribute('hidden', '');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

/* ── Init ────────────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('page-enter');
  initParticles();
  initMobileNav();
  initWorkflowAnimation();
  loadStats();
  initAuthForms();
  updateNavForAuth();
});

/* ── Auth Logic ──────────────────────────────────────────────────────────────── */

function initAuthForms() {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      const data = new URLSearchParams(formData);
      const btn = document.getElementById('loginBtn');
      
      try {
        btn.disabled = true;
        btn.innerHTML = '<span>Loading...</span>';
        const res = await window.api.post('/auth/login', data, true);
        window.api.token = res.access_token;
        window.location.href = '/dashboard';
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Log In</span>';
      }
    });
  }

  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(signupForm);
      const data = Object.fromEntries(formData.entries());
      const btn = document.getElementById('signupBtn');
      
      try {
        btn.disabled = true;
        btn.innerHTML = '<span>Loading...</span>';
        await window.api.post('/auth/register', data);
        showToast('Account created! Please log in.', 'success');
        setTimeout(() => window.location.href = '/login', 1500);
      } catch (err) {
        showToast(err.message, 'error');
        btn.disabled = false;
        btn.innerHTML = '<span>Create Account</span>';
      }
    });
  }
}

async function updateNavForAuth() {
  if (window.api && window.api.token) {
    try {
      const user = await window.api.get('/auth/me');
      const navLinks = document.querySelector('.nav__links');
      const mobileNav = document.querySelector('.nav__mobile');
      
      const loggedInHtml = `
        <a href="/events" class="nav__link">Events</a>
        <a href="/dashboard" class="nav__link">Dashboard</a>
        ${user.role === 'ADMIN' || user.role === 'STAFF' ? '<a href="/admin" class="nav__link">Admin</a>' : ''}
        <button class="nav__link nav__link--cta" onclick="window.api.clearAuth(); window.location.href='/'">Logout</button>
      `;
      
      if(navLinks) navLinks.innerHTML = loggedInHtml;
      if(mobileNav) mobileNav.innerHTML = loggedInHtml;
    } catch (e) {
      // Token invalid
      window.api.clearAuth();
    }
  }
}

// Export for other modules
window.EventAI = { API, showToast, animateCounter };
