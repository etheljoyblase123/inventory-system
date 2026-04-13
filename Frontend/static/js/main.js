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
        'updateProfileForm': '/api/update-profile',
        'editProductForm': (form) => `/api/update-product/${form.querySelector('#edit-prod-id').value}`,
        'editUserForm': (form) => `/api/update-user/${form.querySelector('#edit-user-id').value}`
    };

    Object.entries(forms).forEach(([id, urlSpec]) => {
        const form = document.getElementById(id);
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                
                let url = typeof urlSpec === 'function' ? urlSpec(form) : urlSpec;
                
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
                        if (['createUserForm', 'addProductForm', 'updateProfileForm', 'editProductForm', 'editUserForm'].includes(id)) {
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

function editProduct(btn) {
    const product = JSON.parse(btn.getAttribute('data-product'));
    document.getElementById('edit-prod-id').value = product.id;
    document.getElementById('edit-prod-name').value = product.name;
    document.getElementById('edit-prod-sku').value = product.sku;
    document.getElementById('edit-prod-category').value = product.category;
    document.getElementById('edit-prod-price').value = product.price;
    document.getElementById('edit-prod-stock').value = product.stock;
    const imgInput = document.getElementById('edit-prod-image');
    imgInput.value = product.image_url || '';
    previewImage(imgInput, 'edit-image-preview');
    openModal('editProductModal');
}

function previewImage(input, previewId) {
    const previewBox = document.getElementById(previewId);
    const url = input.value.trim();
    
    if (url) {
        previewBox.innerHTML = `<img src="${url}" onerror="this.parentElement.innerHTML='<i data-lucide=\'image-off\'></i>'; lucide.createIcons();" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">`;
    } else {
        previewBox.innerHTML = '<i data-lucide="image"></i>';
        lucide.createIcons();
    }
}

async function deleteProduct(id) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    try {
        const response = await fetch(`/api/delete-product/${id}`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            showToast('Product deleted', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Connection failed', 'error');
    }
}

function editUser(btn) {
    const user = JSON.parse(btn.getAttribute('data-user'));
    document.getElementById('edit-user-id').value = user.id;
    document.getElementById('edit-user-name').value = user.name;
    document.getElementById('edit-user-email').value = user.email;
    document.getElementById('edit-user-role').value = user.role;
    openModal('editUserModal');
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
        const response = await fetch(`/api/delete-user/${id}`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            showToast('User deleted', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Connection failed', 'error');
    }
}

async function buyProduct(id) {
    const formData = new FormData();
    formData.append('product_id', id);
    try {
        const response = await fetch('/api/buy-product', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.success) {
            showToast('Purchase successful!', 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(result.error, 'error');
        }
    } catch (e) {
        showToast('Connection failed', 'error');
    }
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
        series: [{ name: 'Monthly Revenue ($)', data: data.monthly_revenue }],
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

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('active'), 10);
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.style.display = 'none', 300);
    }
}

// Cart Logic
// Cart Logic
function addToCart(productId) {
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/api/cart/add', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('Item added to cart!');
            const cartBadge = document.getElementById('cart-count');
            if (cartBadge) cartBadge.textContent = data.count;
        }
    });
}

function buyNow(productId) {
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/api/buy-product', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('Purchase successful! Order placed.');
            setTimeout(() => window.location.href = '/buyer/orders', 1000);
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    });
}

function openCart() {
    fetch('/api/cart/get')
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById('cart-items-list');
        if (data.items.length === 0) {
            container.innerHTML = '<div class="empty-cart-state"><p>Your cart is empty</p></div>';
        } else {
            container.innerHTML = data.items.map(item => `
                <div class="cart-item">
                    <img src="${item.image}" class="cart-item-img">
                    <div class="cart-item-info">
                        <h4>${item.name}</h4>
                        <p>Quantity: ${item.quantity}</p>
                    </div>
                    <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                </div>
            `).join('');
        }
        document.getElementById('cart-total-display').textContent = `$${data.total.toFixed(2)}`;
        openModal('cartModal');
    });
}

function processCheckout() {
    fetch('/api/cart/checkout', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('Order placed successfully!');
            closeModal('cartModal');
            document.getElementById('cart-count').textContent = '0';
            setTimeout(() => window.location.href = '/buyer/orders', 1500);
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    });
}

function filterGrid(query) {
    const cards = document.querySelectorAll('.product-card');
    const q = query.toLowerCase();
    cards.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        const sku = card.querySelector('.sku-text').textContent.toLowerCase();
        if (name.includes(q) || sku.includes(q)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Task Manager Internal Logic
async function refreshTasks() {
    const list = document.getElementById('modalTasksList');
    if (!list) return;
    
    const res = await fetch('/api/tasks/get');
    const data = await res.json();
    
    if (data.success && data.tasks.length > 0) {
        list.innerHTML = data.tasks.map(t => `
            <div class="task-item-modal ${t.status.toLowerCase()}">
                <div class="task-item-content">
                    <input type="checkbox" class="task-checkbox" ${t.status === 'Completed' ? 'checked' : ''} onchange="toggleTaskStatus(${t.id})">
                    <span class="task-text-val">${t.task}</span>
                </div>
                <div class="task-item-actions">
                    <span class="due-tag">${t.due}</span>
                    <button class="btn-icon-subtle delete" onclick="removeTask(${t.id})"><i data-lucide="trash-2"></i></button>
                </div>
            </div>
        `).join('');
        lucide.createIcons();
    } else {
        list.innerHTML = '<div class="empty-state">No tasks found. Add your first task above!</div>';
    }
}

async function addNewTask() {
    const input = document.getElementById('newTaskInput');
    const task = input.value.trim();
    if (!task) return;
    
    const formData = new FormData();
    formData.append('task', task);
    
    const res = await fetch('/api/tasks/add', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.success) {
        input.value = '';
        showToast('Task added successfully!');
        refreshTasks(); 
    }
}

async function toggleTaskStatus(id) {
    const res = await fetch(`/api/tasks/toggle/${id}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
        refreshTasks();
    }
}

async function removeTask(id) {
    if (!confirm('Delete this task?')) return;
    const res = await fetch(`/api/tasks/delete/${id}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
        showToast('Task removed');
        refreshTasks();
    }
}

// File Manager Logic
async function refreshFileManager() {
    const grid = document.getElementById('fileManagerGrid');
    if (!grid) return;
    
    grid.innerHTML = '<div class="loading-state">Syncing files...</div>';
    
    const res = await fetch('/api/file-manager/reports');
    const data = await res.json();
    
    if (data.success && data.reports.length > 0) {
        grid.innerHTML = data.reports.map(r => `
            <div class="file-card glass animated-card">
                <i data-lucide="file-text" class="file-icon-large"></i>
                <div class="file-info-block">
                    <span class="file-name">Summary_${r.date}.log</span>
                    <span class="file-details">${r.count} Orders • $${r.total.toFixed(2)}</span>
                </div>
                <button class="btn-download" onclick="showToast('Downloading summary for ${r.date}...')">
                    <i data-lucide="download"></i>
                </button>
            </div>
        `).join('');
        lucide.createIcons();
    } else {
        grid.innerHTML = '<div class="empty-state-files">No confirmed orders found to generate logs.</div>';
    }
}
