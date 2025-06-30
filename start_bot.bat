@echo off
REM Giveaway Bot ishga tushirish skripti (Windows)

echo 🚀 Giveaway Bot ishga tushmoqda...
echo.

REM Virtual environment faollashtirish
if exist "venv\Scripts\activate.bat" (
    echo 📦 Virtual environment faollashtirilmoqda...
    call venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment topilmadi!
    echo Iltimos avval deploy.py ni ishga tushiring.
    pause
    exit /b 1
)

REM Bot papkasiga o'tish
cd bot

REM Kerakli modullarni tekshirish
echo 🔍 Modullar tekshirilmoqda...
python -c "import sys; sys.path.append('.'); import data.config" 2>nul
if errorlevel 1 (
    echo ❌ Bot modullari yuklanmadi!
    echo .env fayli to'g'ri sozlanganini tekshiring.
    pause
    exit /b 1
)

REM Botni ishga tushirish
echo ✅ Bot ishga tushirilmoqda...
echo.
python main.py

REM Xato bo'lsa pause
if errorlevel 1 (
    echo.
    echo ❌ Bot xato bilan to'xtadi!
    pause
)

echo.
echo 👋 Bot yopildi
pause
