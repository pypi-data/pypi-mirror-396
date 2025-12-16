"""Views for SafePass"""

import json
import time
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import User, PasswordCard
from .encryption import (
    generate_salt, hash_master_password, verify_master_password,
    derive_key_from_master_password, encrypt_data, decrypt_data
)
from .generator import generate_password, calculate_password_strength
from .analytics import get_dashboard_stats


def get_json_body(request):
    """Parse JSON body from request"""
    try:
        return json.loads(request.body.decode('utf-8'))
    except:
        return {}


def check_session_timeout(request):
    """Check if session has timed out"""
    last_activity = request.session.get('last_activity')
    if last_activity:
        elapsed = time.time() - last_activity
        timeout = getattr(settings, 'SESSION_TIMEOUT', 3600)
        if elapsed > timeout:
            request.session.flush()
            return True
    
    request.session['last_activity'] = time.time()
    return False


def get_session_user(request):
    """Get user from session"""
    if check_session_timeout(request):
        return None
    
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        user = User.objects.get(id=user_id)
        user.session_master_password = request.session.get('master_password', '')
        return user
    except User.DoesNotExist:
        return None


def require_auth(view_func):
    """Decorator to require authentication"""
    def wrapper(request, *args, **kwargs):
        user = get_session_user(request)
        if not user:
            return redirect('/auth/login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_page(request):
    """Render login page"""
    user = get_session_user(request)
    if user:
        return redirect('/dashboard')
    request.session.flush()
    return render(request, 'auth/login.html')


def register_page(request):
    """Render register page"""
    if get_session_user(request):
        return redirect('/dashboard')
    return render(request, 'auth/register.html')


@require_auth
def dashboard_page(request):
    """Render dashboard page"""
    user = get_session_user(request)
    cards = PasswordCard.objects.filter(user=user)
    stats = get_dashboard_stats(user, cards)
    recent_cards = cards.order_by('-created_at')[:5]
    
    encryption_key = bytes(user.encryption_key_encrypted)
    for card in recent_cards:
        try:
            card.password = decrypt_data(bytes(card.password_encrypted), encryption_key)
        except:
            card.password = ''
    
    context = {
        'user': user,
        'stats': stats,
        'recent_cards': recent_cards
    }
    return render(request, 'dashboard.html', context)


@require_auth
def passwords_page(request):
    """Render passwords list page"""
    user = get_session_user(request)
    cards = PasswordCard.objects.filter(user=user).order_by('-updated_at')
    
    encryption_key = bytes(user.encryption_key_encrypted)
    for card in cards:
        try:
            card.password = decrypt_data(bytes(card.password_encrypted), encryption_key)
        except:
            card.password = ''
    
    context = {
        'user': user,
        'cards': cards
    }
    return render(request, 'cards.html', context)


@require_auth
def generator_page(request):
    """Render password generator page"""
    user = get_session_user(request)
    context = {'user': user}
    return render(request, 'generator.html', context)


@require_auth
def password_add_page(request):
    """Render add password page"""
    user = get_session_user(request)
    context = {'user': user}
    return render(request, 'card_add.html', context)


@require_auth
def password_edit_page(request, password_id):
    """Render edit password page"""
    user = get_session_user(request)
    try:
        card = PasswordCard.objects.get(id=password_id, user=user)
        encryption_key = bytes(user.encryption_key_encrypted)
        
        try:
            decrypted_password = decrypt_data(bytes(card.password_encrypted), encryption_key)
        except:
            decrypted_password = ''
        
        context = {
            'user': user,
            'card': card,
            'decrypted_password': decrypted_password
        }
        return render(request, 'password_edit.html', context)
    except PasswordCard.DoesNotExist:
        return redirect('/passwords')


@require_auth
def profile_page(request):
    """Render profile page"""
    user = get_session_user(request)
    context = {'user': user}
    return render(request, 'profile.html', context)


@require_auth
def help_page(request):
    """Render help page"""
    user = get_session_user(request)
    context = {'user': user}
    return render(request, 'help.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """Register a new user"""
    data = get_json_body(request)
    username = data.get('username', '').strip()
    master_password = data.get('master_password', '')
    
    if not username or not master_password:
        return JsonResponse({'error': 'Kullanıcı adı ve ana şifre gerekli'}, status=400)
    
    if len(master_password) < 8:
        return JsonResponse({'error': 'Ana şifre en az 8 karakter olmalı'}, status=400)
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Bu kullanıcı adı zaten kullanılıyor'}, status=400)
    
    salt = generate_salt()
    master_hash = hash_master_password(master_password, salt)
    encryption_key = derive_key_from_master_password(master_password, salt)
    
    user = User.objects.create(
        username=username,
        master_password_hash=master_hash,
        encryption_key_encrypted=encryption_key,
        salt=salt
    )
    
    request.session['user_id'] = user.id
    request.session['master_password'] = master_password
    request.session['last_activity'] = time.time()
    
    return JsonResponse({
        'success': True,
        'message': 'Kayıt başarılı',
        'user': {'id': user.id, 'username': user.username}
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """Login user"""
    data = get_json_body(request)
    username = data.get('username', '').strip()
    master_password = data.get('master_password', '')
    
    if not username or not master_password:
        return JsonResponse({'error': 'Kullanıcı adı ve ana şifre gerekli'}, status=400)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Kullanıcı adı veya şifre hatalı'}, status=401)
    
    if not verify_master_password(master_password, bytes(user.salt), user.master_password_hash):
        return JsonResponse({'error': 'Kullanıcı adı veya şifre hatalı'}, status=401)
    
    request.session['user_id'] = user.id
    request.session['master_password'] = master_password
    request.session['last_activity'] = time.time()
    
    return JsonResponse({
        'success': True,
        'message': 'Giriş başarılı',
        'user': {'id': user.id, 'username': user.username}
    })


@csrf_exempt
@require_http_methods(["POST", "GET"])
def api_logout(request):
    """Logout user"""
    request.session.flush()
    if request.method == 'GET':
        return redirect('/auth/login')
    return JsonResponse({'success': True, 'message': 'Çıkış yapıldı'})


@csrf_exempt
@require_http_methods(["GET"])
def api_check_auth(request):
    """Check if user is authenticated"""
    user = get_session_user(request)
    if user:
        return JsonResponse({
            'authenticated': True,
            'user': {'id': user.id, 'username': user.username}
        })
    return JsonResponse({'authenticated': False})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_passwords(request):
    """List all passwords or create new password"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    if request.method == 'GET':
        cards = PasswordCard.objects.filter(user=user).order_by('-created_at')
        encryption_key = bytes(user.encryption_key_encrypted)
        
        cards_data = []
        for card in cards:
            try:
                password = decrypt_data(bytes(card.password_encrypted), encryption_key)
            except:
                password = ''
            
            cards_data.append({
                'id': card.id,
                'app_name': card.app_name,
                'username': card.username,
                'password': password,
                'url': card.url,
                'notes': card.notes,
                'category': card.category,
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            })
        
        return JsonResponse({'cards': cards_data})
    
    elif request.method == 'POST':
        data = get_json_body(request)
        app_name = data.get('app_name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        url = data.get('url', '').strip()
        notes = data.get('notes', '')
        category = data.get('category', '')
        
        if not app_name or not password:
            return JsonResponse({'error': 'Uygulama adı ve şifre gerekli'}, status=400)
        
        encryption_key = bytes(user.encryption_key_encrypted)
        password_encrypted = encrypt_data(password, encryption_key)
        
        card = PasswordCard.objects.create(
            user=user,
            app_name=app_name,
            username=username,
            password_encrypted=password_encrypted,
            url=url,
            notes=notes,
            category=category
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Şifre oluşturuldu',
            'card': {
                'id': card.id,
                'app_name': card.app_name,
                'username': card.username
            }
        })


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def api_password_detail(request, password_id):
    """Get or update a specific password"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    try:
        card = PasswordCard.objects.get(id=password_id, user=user)
    except PasswordCard.DoesNotExist:
        return JsonResponse({'error': 'Şifre bulunamadı'}, status=404)
    
    if request.method == 'GET':
        encryption_key = bytes(user.encryption_key_encrypted)
        try:
            password = decrypt_data(bytes(card.password_encrypted), encryption_key)
        except:
            password = ''
        
        return JsonResponse({
            'card': {
                'id': card.id,
                'app_name': card.app_name,
                'username': card.username,
                'password': password,
                'notes': card.notes,
                'category': card.category,
                'url': getattr(card, 'url', '')
            }
        })
    
    elif request.method == 'PUT':
        data = get_json_body(request)
        app_name = data.get('app_name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        url = data.get('url', '').strip()
        notes = data.get('notes', '')
        category = data.get('category', '')
        
        if not app_name or not password:
            return JsonResponse({'error': 'Uygulama adı ve şifre gerekli'}, status=400)
        
        card.app_name = app_name
        card.username = username
        card.url = url
        card.notes = notes
        card.category = category
        
        encryption_key = bytes(user.encryption_key_encrypted)
        card.password_encrypted = encrypt_data(password, encryption_key)
        
        card.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Şifre güncellendi',
            'card': {
                'id': card.id,
                'app_name': card.app_name,
                'username': card.username
            }
        })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_password_delete(request, password_id):
    """Delete a password"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    try:
        card = PasswordCard.objects.get(id=password_id, user=user)
        card.delete()
        return JsonResponse({'success': True, 'message': 'Şifre silindi'})
    except PasswordCard.DoesNotExist:
        return JsonResponse({'error': 'Şifre bulunamadı'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def api_generate_password(request):
    """Generate a random password"""
    data = get_json_body(request)
    length = data.get('length', 16)
    use_uppercase = data.get('uppercase', True)
    use_lowercase = data.get('lowercase', True)
    use_digits = data.get('numbers', True)
    use_symbols = data.get('symbols', True)
    exclude_similar = data.get('exclude_similar', False)
    
    password = generate_password(
        length=length,
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_similar=exclude_similar
    )
    
    strength = calculate_password_strength(password)
    
    return JsonResponse({
        'success': True,
        'password': password,
        'strength': strength
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    """Get dashboard statistics"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    cards = PasswordCard.objects.filter(user=user)
    stats = get_dashboard_stats(user, cards)
    return JsonResponse(stats)


@csrf_exempt
@require_http_methods(["GET"])
def api_export_data(request):
    """Export all user data as JSON"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    # Get master password from session
    master_password = request.session.get('master_password', '')
    if not master_password:
        return JsonResponse({'error': 'Oturum süresi dolmuş'}, status=401)
    
    # Derive encryption key from master password
    salt = bytes(user.salt)
    encryption_key = derive_key_from_master_password(master_password, salt)
    
    # Get all password cards
    cards = PasswordCard.objects.filter(user=user)
    
    # Build export data
    export_data = {
        'version': '1.0',
        'exported_at': datetime.now().isoformat(),
        'username': user.username,
        'passwords': []
    }
    
    for card in cards:
        try:
            # Decrypt password for export
            decrypted_password = decrypt_data(bytes(card.password_encrypted), encryption_key)
            
            export_data['passwords'].append({
                'app_name': card.app_name,
                'username': card.username,
                'password': decrypted_password,
                'url': card.url,
                'notes': card.notes,
                'category': card.category or '',
                'created_at': card.created_at.isoformat(),
                'updated_at': card.updated_at.isoformat()
            })
        except Exception:
            # Skip cards that fail to decrypt
            continue
    
    # Create response with JSON file
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json'
    )
    filename = f'safepass_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@csrf_exempt
@require_http_methods(["POST"])
def api_import_data(request):
    """Import data from JSON file"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    # Get master password from session
    master_password = request.session.get('master_password', '')
    if not master_password:
        return JsonResponse({'error': 'Oturum süresi dolmuş'}, status=401)
    
    # Derive encryption key from master password
    salt = bytes(user.salt)
    encryption_key = derive_key_from_master_password(master_password, salt)
    
    try:
        # Get uploaded file
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'Dosya yüklenmedi'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Read and parse JSON
        file_content = uploaded_file.read().decode('utf-8')
        import_data = json.loads(file_content)
        
        # Validate format
        if 'version' not in import_data or 'passwords' not in import_data:
            return JsonResponse({'error': 'Geçersiz dosya formatı'}, status=400)
        
        # Import passwords
        imported_count = 0
        skipped_count = 0
        
        for pwd_data in import_data['passwords']:
            try:
                # Check if this password already exists
                existing = PasswordCard.objects.filter(
                    user=user,
                    app_name=pwd_data.get('app_name', ''),
                    username=pwd_data.get('username', '')
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Encrypt password
                encrypted_password = encrypt_data(pwd_data['password'], encryption_key)
                
                # Create new card
                PasswordCard.objects.create(
                    user=user,
                    app_name=pwd_data.get('app_name', 'Bilinmeyen'),
                    username=pwd_data.get('username', ''),
                    password_encrypted=encrypted_password,
                    url=pwd_data.get('url', ''),
                    notes=pwd_data.get('notes', ''),
                    category=pwd_data.get('category', '')
                )
                imported_count += 1
                
            except Exception as e:
                skipped_count += 1
                continue
        
        return JsonResponse({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'message': f'{imported_count} şifre içe aktarıldı, {skipped_count} atlandı'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Geçersiz JSON formatı'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'İçe aktarma hatası: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_delete_account(request):
    """Delete user account and all associated data"""
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Oturum açmanız gerekiyor'}, status=401)
    
    try:
        data = get_json_body(request)
        master_password = data.get('master_password', '')
        
        if not master_password:
            return JsonResponse({'error': 'Ana şifre gerekli'}, status=400)
        
        if not verify_master_password(master_password, bytes(user.salt), user.master_password_hash):
            return JsonResponse({'error': 'Yanlış ana şifre'}, status=401)
        
        username = user.username
        user.delete()
        
        request.session.flush()
        
        return JsonResponse({
            'success': True,
            'message': f'{username} hesabı ve tüm verileri silindi'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Hesap silinirken hata: {str(e)}'}, status=500)

