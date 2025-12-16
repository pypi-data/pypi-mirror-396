/**
 * Password Generator Module
 * Handles password generation with customizable options
 */

/**
 * Generate new password based on selected options
 */
async function generateNewPassword() {
    const generatedPasswordInput = document.getElementById('generatedPassword');
    const strengthText = document.getElementById('strengthText');
    const strengthBar = document.getElementById('strengthBar');
    const passwordLengthSelect = document.getElementById('passwordLength');
    const includeUppercase = document.getElementById('includeUppercase');
    const includeLowercase = document.getElementById('includeLowercase');
    const includeNumbers = document.getElementById('includeNumbers');
    const includeSymbols = document.getElementById('includeSymbols');
    const length = parseInt(passwordLengthSelect.value);
    const options = {
        length: length,
        uppercase: includeUppercase.checked,
        lowercase: includeLowercase.checked,
        numbers: includeNumbers.checked,
        symbols: includeSymbols.checked
    };

    // Validate at least one option is selected
    if (!options.uppercase && !options.lowercase && !options.numbers && !options.symbols) {
        if (window.showAlert) window.showAlert('En az bir karakter tipi seçmelisiniz!', 'error');
        return;
    }

    try {
        const response = await fetch('/api/generate-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.getCookie ? window.getCookie('csrftoken') : ''
            },
            body: JSON.stringify(options)
        });

        const data = await response.json();

        if (data.success) {
            generatedPasswordInput.value = data.password;
            updateStrengthIndicator(data.strength);
        } else {
            if (window.showAlert) window.showAlert(data.error || 'Şifre üretilemedi', 'error');
        }
    } catch (error) {
        console.error('Generate password error:', error);
        if (window.showAlert) window.showAlert('Şifre üretilirken bir hata oluştu', 'error');
    }
}

/**
 * Copy generated password to clipboard
 */
function copyGeneratedPassword() {
    const generatedPasswordInput = document.getElementById('generatedPassword');
    const password = generatedPasswordInput.value;
    
    if (!password) {
        if (window.showAlert) window.showAlert('Önce bir şifre üretin!', 'error');
        return;
    }

    navigator.clipboard.writeText(password).then(() => {
        if (window.showAlert) window.showAlert('Şifre kopyalandı!', 'success');
    }).catch((error) => {
        console.error('Copy failed:', error);
        if (window.showAlert) window.showAlert('Kopyalama başarısız', 'error');
    });
}

/**
 * Update strength indicator
 */
function updateStrengthIndicator(strength) {
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    const score = strength.score;
    const percentage = (score / 100) * 100;
    
    strengthBar.style.width = percentage + '%';
    strengthText.textContent = strength.label;
    
    // Color coding
    strengthBar.className = 'strength-fill';
    if (score >= 80) {
        strengthBar.classList.add('strength-strong');
        strengthText.style.color = '#10b981';
    } else if (score >= 60) {
        strengthBar.classList.add('strength-good');
        strengthText.style.color = '#3b82f6';
    } else if (score >= 40) {
        strengthBar.classList.add('strength-medium');
        strengthText.style.color = '#f59e0b';
    } else {
        strengthBar.classList.add('strength-weak');
        strengthText.style.color = '#ef4444';
    }
}

// Make functions globally accessible
window.generateNewPassword = generateNewPassword;
window.copyGeneratedPassword = copyGeneratedPassword;

// Generate password on page load
document.addEventListener('DOMContentLoaded', () => {
    generateNewPassword();
});
