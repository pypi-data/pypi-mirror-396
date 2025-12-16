"""Password generator utilities"""

import secrets
import string


def calculate_password_strength(password: str) -> dict:
    """Calculate password strength score and feedback"""
    score = 0
    feedback = []
    
    # Length check
    length = len(password)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    elif length >= 8:
        score += 20
    else:
        feedback.append("Şifre çok kısa (minimum 8 karakter)")
    
    # Character variety
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    variety_count = sum([has_lower, has_upper, has_digit, has_symbol])
    score += variety_count * 15
    
    if not has_lower:
        feedback.append("Küçük harf ekleyin")
    if not has_upper:
        feedback.append("Büyük harf ekleyin")
    if not has_digit:
        feedback.append("Rakam ekleyin")
    if not has_symbol:
        feedback.append("Sembol ekleyin")
    
    # Determine strength level
    if score >= 80:
        strength = "strong"
        label = "Güçlü"
    elif score >= 50:
        strength = "medium"
        label = "Orta"
    else:
        strength = "weak"
        label = "Zayıf"
    
    return {
        "score": min(score, 100),
        "strength": strength,
        "label": label,
        "feedback": feedback
    }


def generate_password(length=16, use_uppercase=True, use_lowercase=True, 
                     use_digits=True, use_symbols=True, exclude_similar=False):
    """Generate a random password with specified options"""
    
    # Build character set
    chars = ""
    if use_lowercase:
        chars += string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation
    
    # Exclude similar characters if requested
    if exclude_similar:
        similar = "il1Lo0O"
        chars = "".join(c for c in chars if c not in similar)
    
    # Ensure at least one character set is selected
    if not chars:
        chars = string.ascii_letters + string.digits
    
    # Generate password
    password = "".join(secrets.choice(chars) for _ in range(length))
    
    return password
