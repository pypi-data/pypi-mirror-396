/* SafePass - Main Application */

// Global utilities - Define before exports to ensure it's available
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.position = 'fixed';
    alert.style.top = '2rem';
    alert.style.right = '2rem';
    alert.style.zIndex = '1000';
    alert.style.maxWidth = '400px';
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// Make globally available
window.showAlert = showAlert;

// CSRF Token handling
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Make globally available
window.getCookie = getCookie;

// Add CSRF token to all fetch requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
    if (args[1] && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(args[1].method)) {
        args[1].headers = args[1].headers || {};
        args[1].headers['X-CSRFToken'] = getCookie('csrftoken');
    }
    return originalFetch.apply(this, args);
};

// Active navigation highlighting
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-menu a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Developer Info Modal
    const devBtn = document.getElementById('devInfoBtn');
    const devModal = document.getElementById('devModal');
    const closeBtn = document.getElementById('closeModal');
    
    if (devBtn && devModal) {
        devBtn.addEventListener('click', () => {
            devModal.classList.add('show');
        });
        
        closeBtn.addEventListener('click', () => {
            devModal.classList.remove('show');
        });
        
        devModal.addEventListener('click', (e) => {
            if (e.target === devModal) {
                devModal.classList.remove('show');
            }
        });
    }
});
