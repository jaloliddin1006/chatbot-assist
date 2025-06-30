#!/bin/bash
# Giveaway Bot ishga tushirish skripti (Linux/Mac)

echo "🚀 Giveaway Bot ishga tushmoqda..."
echo

# Virtual environment faollashtirish
if [ -f "venv/bin/activate" ]; then
    echo "📦 Virtual environment faollashtirilmoqda..."
    source venv/bin/activate
else
    echo "❌ Virtual environment topilmadi!"
    echo "Iltimos avval deploy.py ni ishga tushiring."
    exit 1
fi

# Bot papkasiga o'tish
cd bot

# Kerakli modullarni tekshirish
echo "🔍 Modullar tekshirilmoqda..."
python -c "import sys; sys.path.append('.'); import data.config" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Bot modullari yuklanmadi!"
    echo ".env fayli to'g'ri sozlanganini tekshiring."
    exit 1
fi

# Botni ishga tushirish
echo "✅ Bot ishga tushirilmoqda..."
echo
python main.py

# Xato kodi tekshirish
if [ $? -ne 0 ]; then
    echo
    echo "❌ Bot xato bilan to'xtadi!"
    exit 1
fi

echo
echo "👋 Bot yopildi"
