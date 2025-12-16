/* SafePass - Auth Module */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        
        // Info modal functionality
        const infoBtn = document.getElementById('info-btn');
        const infoModal = document.getElementById('info-modal');
        const closeModal = document.getElementById('close-modal');
        
        if (infoBtn && infoModal && closeModal) {
            infoBtn.addEventListener('click', function() {
                infoModal.classList.add('show');
            });
            
            closeModal.addEventListener('click', function() {
                infoModal.classList.remove('show');
            });
            
            // Close on outside click
            infoModal.addEventListener('click', function(e) {
                if (e.target === infoModal) {
                    infoModal.classList.remove('show');
                }
            });
            
            // Close on ESC key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && infoModal.classList.contains('show')) {
                    infoModal.classList.remove('show');
                }
            });
        }
        
        // Real-time password match validation
        const passwordInput = document.getElementById('master-password');
        const confirmInput = document.getElementById('master-password-confirm');
        const matchHint = document.getElementById('password-match-hint');
        
        if (passwordInput && confirmInput && matchHint) {
            confirmInput.addEventListener('input', function() {
                const password = passwordInput.value;
                const confirm = confirmInput.value;
                
                if (confirm.length === 0) {
                    matchHint.textContent = '';
                    matchHint.className = 'form-hint password-match-hint';
                    confirmInput.style.borderColor = '';
                } else if (password === confirm) {
                    matchHint.textContent = '✓ Şifreler eşleşiyor';
                    matchHint.className = 'form-hint password-match-hint match-success';
                    confirmInput.style.borderColor = 'var(--success)';
                } else {
                    matchHint.textContent = '✗ Şifreler eşleşmiyor';
                    matchHint.className = 'form-hint password-match-hint match-error';
                    confirmInput.style.borderColor = 'var(--danger)';
                }
            });
            
            // Also check when password changes
            passwordInput.addEventListener('input', function() {
                if (confirmInput.value.length > 0) {
                    confirmInput.dispatchEvent(new Event('input'));
                }
            });
        }
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const masterPassword = document.getElementById('master-password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                master_password: masterPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            showAlert(data.error || 'Giriş başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bir hata oluştu', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const masterPassword = document.getElementById('master-password').value;
    const masterPasswordConfirm = document.getElementById('master-password-confirm').value;
    const checkbox = document.querySelector('input[type="checkbox"]');
    
    // Check if checkbox is checked
    if (!checkbox.checked) {
        showAlert('Devam etmek için şartları kabul etmelisiniz', 'error');
        return;
    }
    
    if (masterPassword !== masterPasswordConfirm) {
        showAlert('Şifreler eşleşmiyor!', 'error');
        return;
    }
    
    if (masterPassword.length < 8) {
        showAlert('Ana şifre en az 8 karakter olmalı', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                master_password: masterPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Kayıt başarılı! Giriş yapılıyor...', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showAlert(data.error || 'Kayıt başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bir hata oluştu', 'error');
    }
}

function showAlert(message, type = 'info') {
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} mt-3`;
    alert.textContent = message;
    
    const form = document.querySelector('form');
    form.parentNode.insertBefore(alert, form.nextSibling);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
