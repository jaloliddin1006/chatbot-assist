#!/usr/bin/env python3
"""
Production deployment script
"""
import os
import sys
import subprocess
import asyncio


def run_command(command, cwd=None):
    """Terminal buyruqni ishga tushirish"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {command}")
            return True, result.stdout
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False, str(e)


def check_requirements():
    """Kerakli dasturlarni tekshirish"""
    print("🔍 Kerakli dasturlar tekshirilmoqda...")
    
    requirements = [
        ("python3", "python --version"),
        ("pip", "pip --version"),
        ("git", "git --version"),
        ("postgresql", "psql --version"),
    ]
    
    all_good = True
    
    for name, command in requirements:
        success, output = run_command(command)
        if not success:
            print(f"❌ {name} o'rnatilmagan!")
            all_good = False
        else:
            version = output.strip().split('\n')[0]
            print(f"✅ {name}: {version}")
    
    return all_good


def setup_environment():
    """Virtual environment sozlash"""
    print("\n🛠️ Virtual environment sozlanmoqda...")
    
    # Virtual environment yaratish
    success, _ = run_command("python -m venv venv")
    if not success:
        return False
    
    # Pip ni yangilash
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    success, _ = run_command(f"{pip_path} install --upgrade pip")
    if not success:
        return False
    
    print("✅ Virtual environment tayyor")
    return True


def install_dependencies():
    """Kerakli kutubxonalarni o'rnatish"""
    print("\n📦 Kutubxonalar o'rnatilmoqda...")
    
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        pip_path = "venv/bin/pip"
    
    # Django dependencies
    print("Django dependencies...")
    success, _ = run_command(f"{pip_path} install -r src/requirements/prod.txt")
    if not success:
        return False
    
    # Bot dependencies  
    print("Bot dependencies...")
    success, _ = run_command(f"{pip_path} install -r bot/requirements/prod.txt")
    if not success:
        return False
    
    print("✅ Barcha kutubxonalar o'rnatildi")
    return True


def setup_database():
    """Database ni sozlash"""
    print("\n🗄️ Database sozlanmoqda...")
    
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Linux/Mac
        python_path = "venv/bin/python"
    
    # Migratsiyalar
    print("Migratsiyalar amalga oshirilmoqda...")
    success, _ = run_command(f"{python_path} manage.py makemigrations", cwd="src")
    if not success:
        return False
    
    success, _ = run_command(f"{python_path} manage.py migrate", cwd="src")
    if not success:
        return False
    
    # Statik fayllar
    success, _ = run_command(f"{python_path} manage.py collectstatic --noinput", cwd="src")
    if not success:
        print("⚠️ Collectstatic failed (not critical)")
    
    print("✅ Database tayyor")
    return True


def create_service_files():
    """Systemd service fayllarini yaratish (Linux)"""
    if os.name == 'nt':
        print("⚠️ Windows uchun service fayllari yaratilmaydi")
        return True
    
    print("\n🔧 Service fayllari yaratilmoqda...")
    
    project_dir = os.getcwd()
    
    # Django service
    django_service = f"""[Unit]
Description=Giveaway Bot Django
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={project_dir}/src
Environment=PATH={project_dir}/venv/bin
ExecStart={project_dir}/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
"""

    # Bot service
    bot_service = f"""[Unit]
Description=Giveaway Telegram Bot
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={project_dir}/bot
Environment=PATH={project_dir}/venv/bin
ExecStart={project_dir}/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
"""

    try:
        with open('/tmp/giveaway-django.service', 'w') as f:
            f.write(django_service)
        
        with open('/tmp/giveaway-bot.service', 'w') as f:
            f.write(bot_service)
        
        print("✅ Service fayllari yaratildi:")
        print("   /tmp/giveaway-django.service")
        print("   /tmp/giveaway-bot.service")
        print("\n💡 Systemctl bilan faollashtirish uchun:")
        print("   sudo cp /tmp/giveaway-*.service /etc/systemd/system/")
        print("   sudo systemctl daemon-reload")
        print("   sudo systemctl enable giveaway-django giveaway-bot")
        print("   sudo systemctl start giveaway-django giveaway-bot")
        
        return True
        
    except Exception as e:
        print(f"❌ Service fayllari yaratishda xato: {e}")
        return False


def create_nginx_config():
    """Nginx konfiguratsiyasini yaratish"""
    if os.name == 'nt':
        print("⚠️ Windows uchun nginx config yaratilmaydi")
        return True
    
    print("\n🌐 Nginx konfiguratsiyasi yaratilmoqda...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/static/files/;
    }

    location /media/ {
        alias /path/to/your/media/files/;
    }
}
"""

    try:
        with open('/tmp/giveaway-bot-nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        print("✅ Nginx config yaratildi: /tmp/giveaway-bot-nginx.conf")
        print("\n💡 Faollashtirish uchun:")
        print("   sudo cp /tmp/giveaway-bot-nginx.conf /etc/nginx/sites-available/")
        print("   sudo ln -s /etc/nginx/sites-available/giveaway-bot-nginx.conf /etc/nginx/sites-enabled/")
        print("   sudo nginx -t")
        print("   sudo systemctl restart nginx")
        
        return True
        
    except Exception as e:
        print(f"❌ Nginx config yaratishda xato: {e}")
        return False


def main():
    """Asosiy deployment funksiyasi"""
    print("🚀 Giveaway Bot deployment boshlandi...\n")
    
    steps = [
        ("Talablar tekshirish", check_requirements),
        ("Virtual environment sozlash", setup_environment),
        ("Kutubxonalar o'rnatish", install_dependencies),
        ("Database sozlash", setup_database),
        ("Service fayllari yaratish", create_service_files),
        ("Nginx config yaratish", create_nginx_config),
    ]
    
    completed = 0
    
    for step_name, step_func in steps:
        print(f"\n{'='*50}")
        print(f"QADAM: {step_name}")
        print('='*50)
        
        try:
            if step_func():
                completed += 1
                print(f"✅ {step_name} muvaffaqiyatli")
            else:
                print(f"❌ {step_name} xato")
                break
        except Exception as e:
            print(f"❌ {step_name} - Kutilmagan xato: {e}")
            break
    
    print(f"\n{'='*60}")
    print(f"DEPLOYMENT NATIJALARI: {completed}/{len(steps)} qadam bajarildi")
    print('='*60)
    
    if completed == len(steps):
        print("🎉 Deployment muvaffaqiyatli yakunlandi!")
        print("\n📋 Keyingi qadamlar:")
        print("1. .env faylini sozlang")
        print("2. Superuser yarating: python manage.py createsuperuser")
        print("3. Bot testini o'tkazing: python bot/test_setup.py")
        print("4. Production da ishga tushiring")
    else:
        print("❌ Deployment to'liq yakunlanmadi. Xatolarni tuzating.")
    
    return completed == len(steps)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
