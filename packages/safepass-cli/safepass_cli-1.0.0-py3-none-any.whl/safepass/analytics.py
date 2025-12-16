"""Dashboard analytics utilities"""

from .generator import calculate_password_strength


def get_dashboard_stats(user, cards):
    """Calculate dashboard statistics"""
    
    total_cards = cards.count()
    
    if total_cards == 0:
        return {
            'total_cards': 0,
            'strong_count': 0,
            'medium_count': 0,
            'weak_count': 0,
            'weak_passwords': [],
            'duplicate_passwords': [],
            'duplicate_count': 0,
            'security_score': 100
        }
    
    # Decrypt passwords and analyze
    strong_passwords = []
    medium_passwords = []
    weak_passwords = []
    duplicate_passwords = []
    password_list = []
    
    from .encryption import decrypt_data
    
    # Use the encryption key directly (already derived from master password)
    encryption_key = bytes(user.encryption_key_encrypted)
    
    for card in cards:
        try:
            password = decrypt_data(bytes(card.password_encrypted), encryption_key)
            
            password_list.append({
                'card_id': card.id,
                'app_name': card.app_name,
                'password': password
            })
            
            # Check strength
            strength = calculate_password_strength(password)
            
            password_info = {
                'id': card.id,
                'app_name': card.app_name,
                'score': strength['score'],
                'label': strength['label']
            }
            
            if strength['strength'] == 'strong':
                strong_passwords.append(password_info)
            elif strength['strength'] == 'medium':
                medium_passwords.append(password_info)
            else:  # weak
                weak_passwords.append(password_info)
        except Exception as e:
            # If decryption fails, count as weak
            weak_passwords.append({
                'id': card.id,
                'app_name': card.app_name,
                'score': 0,
                'label': 'Hata'
            })
    
    # Find duplicates
    seen = {}
    for item in password_list:
        pwd = item['password']
        if pwd in seen:
            # Check if this password is already in duplicates list
            found = False
            for dup in duplicate_passwords:
                if dup['password'] == pwd:
                    if item['app_name'] not in dup['apps']:
                        dup['apps'].append(item['app_name'])
                    found = True
                    break
            
            if not found:
                duplicate_passwords.append({
                    'password': pwd,
                    'apps': [seen[pwd], item['app_name']]
                })
        else:
            seen[pwd] = item['app_name']
    
    # Calculate security score
    # Base: 100 points
    # -2 points for each weak password
    # -1 point for each medium password
    # -3 points for each duplicate password
    security_score = 100
    security_score -= len(weak_passwords) * 2
    security_score -= len(medium_passwords) * 1
    security_score -= len(duplicate_passwords) * 3
    security_score = max(0, min(100, security_score))
    
    result = {
        'total_cards': total_cards,
        'strong_count': len(strong_passwords),
        'medium_count': len(medium_passwords),
        'weak_count': len(weak_passwords),
        'weak_passwords': weak_passwords,
        'duplicate_passwords': duplicate_passwords,
        'duplicate_count': len(duplicate_passwords),
        'security_score': int(security_score)
    }
    
    return result
