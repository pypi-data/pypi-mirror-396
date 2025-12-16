/**
 * Profile Module
 * Handles profile settings and account management
 */

// Use global functions from app.js
const showAlert = window.showAlert;
const getCookie = window.getCookie;

// Load stats on page load
document.addEventListener('DOMContentLoaded', () => {
    loadProfileStats();
});

// Make functions globally accessible
window.openChangeMasterPassword = openChangeMasterPassword;
window.closeChangeMasterPassword = closeChangeMasterPassword;
window.exportData = exportData;
window.importData = importData;
window.deleteAccount = deleteAccount;

/**
 * Load profile statistics
 */
async function loadProfileStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        // API returns stats directly, not wrapped in success/stats
        document.getElementById('totalCards').textContent = data.total_cards || 0;
        document.getElementById('safeCards').textContent = data.strong_count || 0;
        document.getElementById('weakCards').textContent = data.weak_count || 0;
        
        // Calculate average strength
        const total = data.total_cards || 0;
        if (total > 0) {
            const avgScore = Math.round(data.security_score || 0);
            document.getElementById('avgStrength').textContent = avgScore + '%';
        } else {
            document.getElementById('avgStrength').textContent = '0%';
        }
    } catch (error) {
        console.error('Load stats error:', error);
    }
}

/**
 * Open change master password modal
 */
function openChangeMasterPassword() {
    const modal = document.getElementById('changeMasterPasswordModal');
    modal.style.display = 'flex';

    // Form submit handler
    const form = document.getElementById('changeMasterPasswordForm');
    form.onsubmit = async (e) => {
        e.preventDefault();

        const currentPassword = document.getElementById('currentMasterPassword').value;
        const newPassword = document.getElementById('newMasterPassword').value;
        const confirmPassword = document.getElementById('confirmMasterPassword').value;

        if (newPassword !== confirmPassword) {
            showAlert('Yeni şifreler eşleşmiyor!', 'error');
            return;
        }

        if (newPassword.length < 8) {
            showAlert('Şifre en az 8 karakter olmalıdır', 'error');
            return;
        }

        try {
            const response = await fetch('/api/auth/change-master-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (data.success) {
                showAlert('Master şifre değiştirildi!', 'success');
                closeChangeMasterPassword();
                form.reset();
            } else {
                showAlert(data.error || 'Şifre değiştirilemedi', 'error');
            }
        } catch (error) {
            console.error('Change password error:', error);
            showAlert('Bir hata oluştu', 'error');
        }
    };
}

/**
 * Close change master password modal
 */
function closeChangeMasterPassword() {
    const modal = document.getElementById('changeMasterPasswordModal');
    modal.style.display = 'none';
}

/**
 * Export data
 */
function exportData() {
    showAlert('Verileriniz indiriliyor...', 'info');
    window.location.href = '/api/export';
}

/**
 * Import data
 */
function importData() {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file type
        if (!file.name.endsWith('.json')) {
            showAlert('Lütfen JSON dosyası seçin', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/import', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(data.message, 'success');
                // Reload stats after import
                setTimeout(() => {
                    loadProfileStats();
                }, 1000);
            } else {
                showAlert(data.error || 'İçe aktarma başarısız', 'error');
            }
        } catch (error) {
            console.error('Import error:', error);
            showAlert('İçe aktarma sırasında bir hata oluştu', 'error');
        }
    };
    
    // Trigger file selection
    input.click();
}

/**
 * Delete account
 */
function deleteAccount() {
    const confirmed = confirm(
        'UYARI: Hesabınızı ve tüm verilerinizi kalıcı olarak silmek istediğinizden emin misiniz?\n\n' +
        'Bu işlem GERİ ALINAMAZ!\n\n' +
        'Devam etmek için "Tamam" düğmesine basın.'
    );

    if (!confirmed) return;

    const masterPassword = prompt('Şifrenizi girin:');
    if (!masterPassword) {
        showAlert('Şifre gerekli', 'error');
        return;
    }

    const doubleConfirm = prompt(
        'Son onay: Devam etmek için "SİL" yazın (büyük harflerle):'
    );

    if (doubleConfirm !== 'SİL') {
        showAlert('İşlem iptal edildi', 'info');
        return;
    }

    fetch('/api/profile/delete-account', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            master_password: masterPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/auth/login';
            }, 2000);
        } else {
            showAlert(data.error || 'Hesap silinirken hata oluştu', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Hesap silinirken hata oluştu', 'error');
    });
}

// Close modal on ESC key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeChangeMasterPassword();
    }
});

// Close modal on outside click
document.getElementById('changeMasterPasswordModal')?.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeChangeMasterPassword();
    }
});
