"""CLI entry point for SafePass"""

import sys
import os
import argparse
from pathlib import Path


def get_data_dir():
    """Get SafePass data directory"""
    home = Path.home()
    data_dir = home / ".safepass"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def init_database():
    """Initialize database and configuration"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safepass.settings')
    import django
    django.setup()
    
    from django.core.management import call_command
    
    print("🔧 SafePass veritabanı başlatılıyor...")
    call_command('migrate', '--run-syncdb', verbosity=0)
    print("✅ Veritabanı hazır!")
    print(f"📁 Veriler: {get_data_dir()}")


def start_server(port=8000):
    """Start the Django development server"""
    import subprocess
    from pathlib import Path
    import time
    
    pid_file = get_data_dir() / "safepass.pid"
    
    # Check if already running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text())
            if sys.platform == 'win32':
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                if str(pid) in result.stdout:
                    print(f"⚠️  SafePass zaten çalışıyor (PID: {pid})")
                    print(f"🌐 Tarayıcınızda açın: http://localhost:{port}")
                    return
        except:
            pass
    
    manage_py = Path(__file__).parent / 'manage.py'
    
    print(f"🚀 SafePass başlatılıyor...")
    print(f"🌐 Tarayıcınızda açın: http://localhost:{port}")
    print("⏹️  Durdurmak için: Ctrl+C veya 'safepass stop'\n")
    
    try:
        # Start process and get actual PID
        process = subprocess.Popen(
            [sys.executable, str(manage_py), 'runserver', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait a moment for Django to start and capture its PID
        time.sleep(2)
        
        # Get the actual runserver process PID
        if sys.platform == 'win32':
            # Find python process listening on the port
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    actual_pid = parts[-1]
                    pid_file.write_text(actual_pid)
                    break
        else:
            pid_file.write_text(str(process.pid))
        
        # Wait for process to finish
        process.wait()
    except KeyboardInterrupt:
        print("\n👋 SafePass kapatıldı.")
    finally:
        if pid_file.exists():
            pid_file.unlink()


def stop_server():
    """Stop the running SafePass server"""
    import signal
    
    pid_file = get_data_dir() / "safepass.pid"
    
    if not pid_file.exists():
        print("ℹ️  SafePass çalışmıyor.")
        sys.exit(0)
    
    try:
        pid = int(pid_file.read_text())
        
        # Check if process is actually running
        if sys.platform == 'win32':
            import subprocess
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                  capture_output=True, text=True)
            if str(pid) not in result.stdout:
                print("ℹ️  SafePass çalışmıyor.")
                pid_file.unlink()
                sys.exit(0)
        else:
            try:
                os.kill(pid, 0)  # Check if process exists
            except ProcessLookupError:
                print("ℹ️  SafePass çalışmıyor.")
                pid_file.unlink()
                sys.exit(0)
        
        # Kill the process
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            else:
                os.kill(pid, signal.SIGTERM)
            
            print("✅ SafePass durduruldu.")
        except ProcessLookupError:
            print("ℹ️  Süreç zaten sonlanmış.")
        
        pid_file.unlink()
    except Exception as e:
        print(f"❌ Durdurulurken hata: {e}")
        if pid_file.exists():
            pid_file.unlink()


def reset_data():
    """Reset all data (WARNING: deletes everything!)"""
    data_dir = get_data_dir()
    db_file = data_dir / "db.sqlite3"
    
    if db_file.exists():
        confirm = input("⚠️  UYARI: TÜM VERİLER SİLİNECEK! Devam etmek istiyor musunuz? (evet/hayır): ")
        if confirm.lower() in ['evet', 'yes', 'e', 'y']:
            db_file.unlink()
            print("✅ Tüm veriler silindi.")
            init_database()
        else:
            print("❌ İşlem iptal edildi.")
    else:
        print("ℹ️  Silinecek veri bulunamadı.")


def main():
    """Main CLI handler"""
    parser = argparse.ArgumentParser(
        description='SafePass - Offline Password Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Komutlar:
  init      Veritabanını başlat
  start     Web sunucusunu başlat (varsayılan port: 8000)
  stop      Çalışan sunucuyu durdur
  reset     Tüm verileri sil ve sıfırla (UYARI: geri alınamaz!)

Örnekler:
  safepass init
  safepass start
  safepass start --port 8080
  safepass stop
  safepass reset
        """
    )
    
    parser.add_argument('command', 
                       choices=['init', 'start', 'stop', 'reset'],
                       help='Çalıştırılacak komut')
    parser.add_argument('--port', 
                       type=int, 
                       default=8000,
                       help='Web sunucu portu (varsayılan: 8000)')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_database()
    elif args.command == 'start':
        # Auto-init if database doesn't exist
        db_file = get_data_dir() / "db.sqlite3"
        if not db_file.exists():
            init_database()
        start_server(args.port)
    elif args.command == 'stop':
        stop_server()
    elif args.command == 'reset':
        reset_data()


if __name__ == '__main__':
    main()
