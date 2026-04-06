document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initTheme();
    setupFormHandlers();
    setupInteractiveElements();
    
    // Page specific initializations
    if (document.getElementById('main-performance-chart')) initDashboardCharts();
    if (document.querySelector('.analytics-grid')) initAnalyticsCharts();
    
    // Update time/date
    updateDateTime();
    setInterval(updateDateTime, 60000);
});

function updateDateTime() {
    const now = new Date();
    const dateEl = document.getElementById('current-date');
    const timeEl = document.getElementById('current-time');
    
    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function initTheme() {
    const savedTheme = localStorage.getItem('admin-theme') || 'default';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    const root = document.documentElement;
    const themes = {
        'default': { primary: '#3b82f6', gradient: 'linear-gradient(135deg, #3b82f6, #06b6d4)' },
        'purple': { primary: '#8b5cf6', gradient: 'linear-gradient(135deg, #8b5cf6, #ec4899)' },
        'emerald': { primary: '#10b981', gradient: 'linear-gradient(135deg, #10b981, #3b82f6)' },
        'amber': { primary: '#f59e0b', gradient: 'linear-gradient(135deg, #f59e0b, #ef4444)' }
    };
    
    const colors = themes[theme] || themes['default'];
    root.style.setProperty('--primary-blue', colors.primary);
    
    // Update all elements with blue-gradient class dynamically
    document.querySelectorAll('.blue-gradient').forEach(el => {
        el.style.background = colors.gradient;
    });
}

function changeTheme(theme) {
    applyTheme(theme);
    localStorage.setItem('admin-theme', theme);
    showToast(`Theme switched to ${theme}!`, 'success');
}

function setupInteractiveElements() {
    // Stat Cards - show detail toast
    document.querySelectorAll('.stat-card.interactive').forEach(card => {
        card.addEventListener('click', () => {
            const title = card.querySelector('.stat-title').textContent;
            const value = card.querySelector('.stat-value').textContent;
            showToast(`Detail View: ${title} (${value})`, 'success');
        });
    });

    // Handle all generic buttons/icons that don't have specific roles
    document.querySelectorAll('button:not([onclick]):not([type="submit"]), .icon-action, .btn-icon, .menu-item:not([onclick])').forEach(btn => {
        if (btn.tagName === 'A' || btn.closest('form')) return;
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const label = btn.innerText.trim() || btn.querySelector('span')?.innerText || 'Action';
            showToast(`${label} feature is coming soon!`, 'success');
        });
    });

    // Chat items
    document.querySelectorAll('.chat-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const name = item.querySelector('.chat-name').textContent;
            document.querySelector('.chat-active-header .name').textContent = name;
            showToast(`Switched chat to ${name}`, 'success');
        });
    });
}

// Form Handlers
function setupFormHandlers() {
    const forms = {
        'createUserForm': '/api/create-user',
        'supportForm': '/api/submit-support',
        'maintenanceForm': '/api/schedule-maintenance',
        'reportGenForm': '/api/generate-report',
        'addProductForm': '/api/add-product',
        'updateProfileForm': '/api/update-profile'
    };

    Object.entries(forms).forEach(([id, url]) => {
        const form = document.getElementById(id);
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                
                try {
                    submitBtn.textContent = 'Processing...';
                    submitBtn.disabled = true;
                    
                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        showToast('Action successful!', 'success');
                        const modal = form.closest('.modal-overlay');
                        if (modal) {
                            closeModal(modal.id);
                        }
                        form.reset();
                        if (id === 'createUserForm' || id === 'addProductForm' || id === 'updateProfileForm') {
                             setTimeout(() => window.location.reload(), 1000);
                        }
                    } else {
                        showToast(result.error || 'Something went wrong', 'error');
                    }
                } catch (err) {
                    showToast('Server connection failed', 'error');
                } finally {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }
            });
        }
    });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast glass ${type}`;
    toast.innerHTML = `
        <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => toast.classList.add('active'), 10);
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Chart Initializations
async function initDashboardCharts() {
    const response = await fetch('/api/stats');
    const data = await response.json();
    
    // Sparklines 
    const sparkOptions = {
        chart: { type: 'area', height: 40, sparkline: { enabled: true } },
        stroke: { curve: 'smooth', width: 2 },
        colors: ['#3b82f6'],
        fill: { type: 'gradient', gradient: { opacityFrom: 0.3, opacityTo: 0 } },
        series: [{ data: [30, 40, 35, 50, 49, 60, 70] }],
        tooltip: { enabled: false }
    };
    
    ['users-spark-chart', 'revenue-spark-chart', 'sessions-spark-chart'].forEach(id => {
        if (document.getElementById(id)) new ApexCharts(document.getElementById(id), sparkOptions).render();
    });

    const mainOptions = {
        chart: { type: 'area', height: 300, toolbar: { show: false }, background: 'transparent' },
        theme: { mode: 'dark' },
        series: [{ name: 'Current Period', data: data.monthly_users }],
        colors: ['#8b5cf6'],
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.45, opacityTo: 0.05 } },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 3 },
        grid: { borderColor: 'rgba(255,255,255,0.05)', strokeDashArray: 4 },
        xaxis: { categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], axisBorder: { show: false } }
    };
    if (document.getElementById('main-performance-chart')) {
        new ApexCharts(document.getElementById('main-performance-chart'), mainOptions).render();
    }
}

function initAnalyticsCharts() {
    // Basic placeholder for analytics charts
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.style.display = 'none', 300);
    }
}
