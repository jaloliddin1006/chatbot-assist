# 🎁 Telegram Giveaway Bot

Telegram orqali konkurslar o'tkazish uchun professional bot tizimi. Django ORM va aiogram 3.x asosida yaratilgan.

## 🚀 Xususiyatlar

### 👥 Foydalanuvchilar uchun:
- **Konkursda ishtirok** - Majburiy kanallarga obuna bo'lish orqali
- **Referral tizimi** - Do'stlarni taklif qilib ball to'plash 
- **Ixtiyoriy kanallar** - Qo'shimcha ball olish imkoniyati
- **Reyting ko'rish** - O'z o'rni va boshqa ishtirokchilar
- **Profil boshqaruvi** - Statistika va ball holati

### 👑 Adminlar uchun:
- **Konkurs boshqaruvi** - Django admin panel orqali
- **Foydalanuvchi statistikasi** - To'liq analitika
- **Ommaviy xabar** - Barcha foydalanuvchilarga xabar yuborish
- **G'oliblarni aniqlash** - Avtomatik reyting asosida
- **Ball boshqaruvi** - Qo'lda ball qo'shish/ayirish

## 🏗️ Tizim arxitekturasi

```
📁 giveawaybot/
├── 📁 src/                    # Django backend
│   ├── 📁 main/              # Asosiy Django app
│   │   ├── models.py         # Database modellari
│   │   ├── admin.py          # Admin panel
│   │   ├── views.py          # API endpointlar
│   │   └── services.py       # Business logika
│   └── 📁 core/              # Django sozlamalari
├── 📁 bot/                    # Telegram bot
│   ├── main.py               # Bot ishga tushirish
│   ├── loader.py             # Bot va DB loader
│   ├── models.py             # Tortoise ORM modellari
│   ├── services.py           # Async business logika
│   ├── 📁 handlers/          # Xabar ishlovchilari
│   ├── 📁 keyboards/         # Klaviatura yaratish
│   ├── 📁 middlewares/       # O'rta dasturlar
│   └── 📁 utils/             # Yordamchi funksiyalar
└── 📁 requirements/          # Kerakli kutubxonalar
```

## ⚙️ O'rnatish

### 1. Loyihani yuklab olish
```bash
git clone <repository-url>
cd giveawaybot
```

### 2. Python virtual environment yaratish
```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux/Mac  
source venv/bin/activate
```

### 3. Kerakli kutubxonalarni o'rnatish

**Django uchun:**
```bash
cd src
pip install -r requirements/base.txt
```

**Bot uchun:**
```bash
cd ../bot
pip install -r requirements/base.txt
```

### 4. PostgreSQL database yaratish
```sql
CREATE DATABASE giveaway_bot;
CREATE USER bot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE giveaway_bot TO bot_user;
```

### 5. Environment o'zgaruvchilarini sozlash
`.env` faylini yarating va quyidagi ma'lumotlarni kiriting:

```env
# Bot sozlamalari
BOT_TOKEN=1234567890:ABCdef1234567890ABCdef1234567890ABC
ADMIN_ID=123456789

# Database sozlamalari  
DB_USER=bot_user
DB_PASS=your_password
DB_NAME=giveaway_bot
DB_HOST=localhost
DB_PORT=5432

# Django sozlamalari
SECRET_KEY=your-secret-key
DEBUG=True
```

### 6. Django migratsiyalarini amalga oshirish
```bash
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Botni test qilish
```bash
cd ../bot
python test_setup.py
```

## 🏃‍♂️ Ishga tushirish

### Django serverni ishga tushirish:
```bash
cd src
python manage.py runserver
```

### Telegram botni ishga tushirish:
```bash
cd bot
python main.py
```

## 📋 Foydalanish

### 1. Admin panel orqali konkurs yaratish
1. Django admin panelga kiring: `http://localhost:8000/admin`
2. "Contests" bo'limiga o'ting
3. Yangi konkurs qo'shing:
   - Nomi, tavsifi, sovg'a
   - Majburiy va ixtiyoriy kanallar
   - Ball tizimlari
   - Muddat va g'oliblar soni

### 2. Bot orqali foydalanish
- `/start` - Botni ishga tushirish
- `/contests` - Faol konkurslar ro'yxati  
- `/help` - Yordam
- `/admin` - Admin panel (faqat adminlar uchun)

### 3. Konkursda ishtirok etish jarayani
1. Foydalanuvchi `/start` buyrug'ini bosadi
2. Majburiy kanallarga obuna bo'ladi
3. Obunani tasdiqlaydi
4. Avtomatik ravishda konkursga qo'shiladi
5. Referral orqali do'stlarini taklif qiladi
6. Ixtiyoriy kanallarga obuna bo'lib qo'shimcha ball oladi

## 🗃️ Database modellari

### Asosiy modellar:
- **TelegramUser** - Foydalanuvchi ma'lumotlari
- **Channel** - Telegram kanallari
- **Contest** - Konkurs ma'lumotlari
- **ContestParticipant** - Konkursda ishtirokchilar
- **ChannelSubscription** - Kanal obunalari
- **Referral** - Referral aloqalar
- **ContestWinner** - G'oliblar

## 🔧 Texnologiyalar

- **Backend:** Django 4.2+ ORM
- **Bot:** aiogram 3.x (async)
- **Database:** PostgreSQL + Tortoise ORM
- **Cache:** Redis (ixtiyoriy)
- **Environment:** python-dotenv

## 📊 Ball tizimi

- **Boshlang'ich ball:** Konkursga qo'shilganda
- **Referral balli:** Har bir taklif qilingan do'st uchun
- **Ixtiyoriy kanal balli:** Qo'shimcha kanallarga obuna uchun
- **Bonus ball:** Admin tomonidan qo'lda qo'shiladi

## 🔐 Xavfsizlik

- Admin huquqlari ID orqali tekshiriladi
- Barcha database so'rovlari himoyalangan
- Rate limiting middleware orqali spam himoyasi
- Input validation barcha joyda qo'llaniladi

## 🐛 Xatoliklarni tuzatish

### Test skriptini ishlatish:
```bash
cd bot
python test_setup.py
```

### Loglarni ko'rish:
- Django: `src/logs/` papkasi
- Bot: Console output

### Umumiy xatolar:
1. **Import Error** - Virtual environmentni aktivlashtiring
2. **Database Error** - PostgreSQL ishlaganini tekshiring
3. **Bot Token Error** - `.env` faylini tekshiring
4. **Permission Error** - Admin ID ni to'g'ri kiritganingizni tekshiring

## 📈 Monitoring

### Admin panel statistikalar:
- Jami foydalanuvchilar soni
- Faol konkurslar
- Kunlik yangi foydalanuvchilar
- Eng faol ishtirokchilar

### Bot buyruqlari (adminlar uchun):
- `/admin stats` - Tezkor statistika
- `/admin broadcast` - Ommaviy xabar yuborish
- `/admin winners` - G'oliblarni ko'rish

## 🤝 Hissa qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. Commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📜 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 📞 Aloqa

Savollar yoki takliflar uchun: [your-email@example.com]

---

**⚡ Eslatma:** Bot production muhitda ishlatishdan oldin barcha test skriptlarni ishlatib, xavfsizlik sozlamalarini tekshiring!
