#!/usr/bin/env python3
"""
Development setup script - tez sozlash uchun
"""
import os
import sys
import subprocess


def create_env_file():
    """Environment fayli yaratish"""
    if os.path.exists('.env'):
        print("⚠️ .env fayli allaqachon mavjud")
        return True
    
    print("📝 .env fayli yaratilmoqda...")
    
    env_content = """# Bot sozlamalari
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_ID=YOUR_ADMIN_ID_HERE

# Database sozlamalari
DB_USER=postgres
DB_PASS=your_password
DB_NAME=giveaway_bot
DB_HOST=localhost
DB_PORT=5432

# Django sozlamalari
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional
REDIS_URL=redis://localhost:6379/0
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env fayli yaratildi")
        print("⚠️ BOT_TOKEN va ADMIN_ID ni o'rnating!")
        return True
    except Exception as e:
        print(f"❌ .env fayli yaratishda xato: {e}")
        return False


def run_command(command, cwd=None):
    """Terminal buyruqni ishlatish"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def setup_dev_environment():
    """Development muhitini sozlash"""
    print("🛠️ Development muhiti sozlanmoqda...\n")
    
    steps = [
        ("Environment fayli yaratish", create_env_file),
    ]
    
    for step_name, step_func in steps:
        print(f"📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} xato")
            return False
        print()
    
    print("📋 Keyingi qadamlar:")
    print("1. .env faylida BOT_TOKEN va ADMIN_ID ni o'rnating")
    print("2. PostgreSQL database yarating")
    print("3. Virtual environment yaratib, dependencies o'rnating:")
    print("   python -m venv venv")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
        print("   pip install -r src\\requirements\\base.txt")
        print("   pip install -r bot\\requirements\\base.txt")
    else:
        print("   source venv/bin/activate")
        print("   pip install -r src/requirements/base.txt")
        print("   pip install -r bot/requirements/base.txt")
    print("4. Django migratsiyalarini bajaring:")
    print("   cd src && python manage.py migrate")
    print("5. Superuser yarating:")
    print("   python manage.py createsuperuser")
    print("6. Bot testini o'tkazing:")
    print("   cd ../bot && python test_setup.py")
    print("7. Bot va Django ni ishga tushiring:")
    if os.name == 'nt':
        print("   start_bot.bat")
    else:
        print("   ./start_bot.sh")
    
    return True


def main():
    print("🚀 Giveaway Bot - Development Setup\n")
    
    if setup_dev_environment():
        print("✅ Development setup tugallandi!")
    else:
        print("❌ Setup da xato bo'ldi!")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
