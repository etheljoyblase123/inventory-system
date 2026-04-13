document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initModals();
    initOthersTabs();
    initAccordions();
});

// --- Theme Toggle Logic ---
function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    
    const themeSwitch = document.getElementById('theme-toggle');
    if (themeSwitch) {
        themeSwitch.checked = theme === 'dark';
        themeSwitch.addEventListener('change', (e) => {
            const newTheme = e.target.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// --- Add to Cart Modal Logic ---
function initModals() {
    const modal = document.getElementById('cart-modal');
    const closeBtn = document.querySelector('.close-btn');
    const cancelBtn = document.querySelector('.btn-cancel');
    
    if (!modal) return;

    window.openCartModal = (productName, productId) => {
        document.getElementById('modal-product-name').textContent = productName;
        document.getElementById('modal-product-id').value = productId;
        document.getElementById('modal-product-qty').value = 1;
        modal.style.display = 'flex';
    };

    const closeModal = () => {
        modal.style.display = 'none';
    };

    if (closeBtn) closeBtn.onclick = closeModal;
    if (cancelBtn) cancelBtn.onclick = closeModal;
    
    window.onclick = (event) => {
        if (event.target == modal) closeModal();
    };
}

// --- Others Page Tab Switching ---
function initOthersTabs() {
    // This handles both the sidebar links and showing the correct content
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const sections = document.querySelectorAll('.content-section');
    
    if (sidebarLinks.length === 0) return;

    // Check if a tab is specified in the URL or set by backend
    const currentTab = window.location.pathname.split('/').pop();
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // If we want to stay on the same page without reload:
            /*
            e.preventDefault();
            const targetId = link.getAttribute('href').split('/').pop();
            
            // Update UI
            sidebarLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');
            
            // Update URL without reload
            history.pushState(null, '', link.getAttribute('href'));
            */
        });
    });
}

// --- FAQ Accordion Logic ---
function initAccordions() {
    const questions = document.querySelectorAll('.faq-question');
    
    questions.forEach(q => {
        q.addEventListener('click', () => {
            const answer = q.nextElementSibling;
            const icon = q.querySelector('i');
            
            const isOpen = answer.style.display === 'block';
            
            // Close all others
            document.querySelectorAll('.faq-answer').forEach(a => a.style.display = 'none');
            document.querySelectorAll('.faq-question i').forEach(i => i.style.transform = 'rotate(0)');
            
            if (!isOpen) {
                answer.style.display = 'block';
                if (icon) icon.style.transform = 'rotate(180deg)';
            }
        });
    });
}

// --- Cart Actions ---
function confirmAddToCart() {
    const name = document.getElementById('modal-product-name').textContent;
    const qty = document.getElementById('modal-product-qty').value;
    
    // In a real app, this would be an AJAX call
    alert(`Added ${qty} x ${name} to your cart!`);
    document.getElementById('cart-modal').style.display = 'none';
    
    // Update cart badge (visual only for now)
    const badge = document.querySelector('.badge');
    if (badge) {
        let current = parseInt(badge.textContent) || 0;
        badge.textContent = current + parseInt(qty);
    }
}

function placeOrder(name) {
    alert(`Successfully placed order for ${name}!`);
}
