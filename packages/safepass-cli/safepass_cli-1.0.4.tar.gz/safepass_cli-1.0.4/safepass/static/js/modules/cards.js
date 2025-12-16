/* SafePass - Cards Module */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Event delegation for card actions
    document.addEventListener('click', function(e) {
        // Find the actual button element (handle SVG clicks)
        const button = e.target.closest('button');
        
        if (button && button.classList.contains('btn-edit')) {
            const cardId = button.dataset.cardId;
            editCard(cardId);
        }
        
        if (button && button.classList.contains('btn-delete')) {
            const cardId = button.dataset.cardId;
            deleteCard(cardId);
        }
        
        if (button && button.classList.contains('btn-toggle-password')) {
            togglePassword(button);
        }
        
        if (button && button.classList.contains('btn-copy-password')) {
            const password = button.dataset.password;
            copyPassword(password);
        }
    });
});

function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const cards = document.querySelectorAll('.password-card');
    
    cards.forEach(card => {
        const appName = card.querySelector('.card-title').textContent.toLowerCase();
        const username = card.querySelector('.card-username')?.textContent.toLowerCase() || '';
        
        if (appName.includes(searchTerm) || username.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

function togglePassword(button) {
    const passwordField = button.closest('.password-field');
    const hidden = passwordField.querySelector('.password-hidden');
    const visible = passwordField.querySelector('.password-visible');
    
    if (hidden && visible) {
        if (hidden.style.display === 'none') {
            hidden.style.display = '';
            visible.style.display = 'none';
        } else {
            hidden.style.display = 'none';
            visible.style.display = '';
        }
    }
}

async function copyPassword(password) {
    try {
        await navigator.clipboard.writeText(password);
        showToast('Şifre kopyalandı!', 'success');
    } catch (error) {
        showToast('Kopyalama başarısız', 'error');
    }
}

async function deleteCard(cardId) {
    if (!confirm('Bu şifreyi silmek istediğinize emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/passwords/${cardId}/delete`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            document.querySelector(`[data-id="${cardId}"]`).remove();
            showToast('Şifre silindi', 'success');
        } else {
            showToast('Silme başarısız', 'error');
        }
    } catch (error) {
        showToast('Bir hata oluştu', 'error');
    }
}

function editCard(cardId) {
    window.location.href = `/passwords/${cardId}/edit`;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '2rem';
    toast.style.right = '2rem';
    toast.style.zIndex = '1000';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
