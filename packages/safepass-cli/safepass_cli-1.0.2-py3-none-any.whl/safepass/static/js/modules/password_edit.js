/**
 * Password Edit Module
 */

document.addEventListener('DOMContentLoaded', () => {
    const editCardForm = document.getElementById('editCardForm');
    const passwordInput = document.getElementById('password');
    const passwordStrengthBar = document.getElementById('passwordStrengthBar');
    const passwordStrengthText = document.getElementById('passwordStrengthText');

    // Password toggle handler - handled by inline function in template
    // Keeping this for backwards compatibility if needed
    const toggleButtons = document.querySelectorAll('.btn-toggle-password[data-target]');
    
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            const eyeOpen = this.querySelector('.icon-eye-open');
            const eyeClosed = this.querySelector('.icon-eye-closed');
            
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (eyeOpen) eyeOpen.style.display = 'none';
                    if (eyeClosed) eyeClosed.style.display = 'block';
                } else {
                    input.type = 'password';
                    if (eyeOpen) eyeOpen.style.display = 'block';
                    if (eyeClosed) eyeClosed.style.display = 'none';
                }
            }
        });
    });

    // Password strength check
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;

            if (!password) {
                passwordStrengthBar.style.width = '0%';
                passwordStrengthText.textContent = 'Şifre girin';
                passwordStrengthText.style.color = '#94a3b8';
                return;
            }

            let strength = 0;
            if (password.length >= 8) strength += 25;
            if (password.length >= 12) strength += 15;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 20;
            if (/\d/.test(password)) strength += 20;
            if (/[^a-zA-Z0-9]/.test(password)) strength += 20;

            passwordStrengthBar.style.width = strength + '%';

            if (strength < 40) {
                passwordStrengthBar.style.backgroundColor = '#ef4444';
                passwordStrengthText.textContent = 'Zayıf';
                passwordStrengthText.style.color = '#ef4444';
            } else if (strength < 70) {
                passwordStrengthBar.style.backgroundColor = '#f59e0b';
                passwordStrengthText.textContent = 'Orta';
                passwordStrengthText.style.color = '#f59e0b';
            } else {
                passwordStrengthBar.style.backgroundColor = '#10b981';
                passwordStrengthText.textContent = 'Güçlü';
                passwordStrengthText.style.color = '#10b981';
            }
        });

        // Trigger initial check
        passwordInput.dispatchEvent(new Event('input'));
    }

    // Form submit handler
    if (editCardForm) {
        editCardForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const cardId = document.getElementById('cardId').value;
            const formData = {
                app_name: document.getElementById('title').value.trim(),
                username: document.getElementById('username').value.trim(),
                password: document.getElementById('password').value,
                url: document.getElementById('url')?.value.trim() || '',
                notes: document.getElementById('notes')?.value.trim() || '',
                category: document.getElementById('category')?.value || 'Genel'
            };

            // Validation
            if (!formData.app_name) {
                window.showAlert('Başlık gereklidir', 'error');
                return;
            }

            if (!formData.password || formData.password.length < 8) {
                window.showAlert('Şifre en az 8 karakter olmalıdır', 'error');
                return;
            }

            try {
                const response = await fetch(`/api/passwords/${cardId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.getCookie('csrftoken')
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    window.showAlert('Değişiklikler başarıyla kaydedildi!', 'success');
                    setTimeout(() => {
                        window.location.href = '/passwords';
                    }, 1000);
                } else {
                    window.showAlert(data.error || 'Değişiklikler kaydedilemedi', 'error');
                }
            } catch (error) {
                console.error('Update error:', error);
                window.showAlert('Bir hata oluştu', 'error');
            }
        });
    }
});
