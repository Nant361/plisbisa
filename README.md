# Telegram Scraper Bot

Bot Telegram untuk pencarian data mahasiswa melalui PDDikti API.

## Struktur Proyek

- `main.py` - File utama untuk menjalankan bot
- `telegram_bot.py` - Implementasi bot Telegram utama
- `admin_bot.py` - Bot admin untuk mengelola pengguna
- `pddikti_api.py` - Implementasi API PDDikti
- `requirements.txt` - Dependensi Python
- `allowed_users.json` - Daftar pengguna yang diizinkan
- `user_logs.json` - Log aktivitas pengguna

## Deployment di Koyeb

### Persiapan

1. Buat akun di [Koyeb](https://app.koyeb.com)
2. Install [Koyeb CLI](https://www.koyeb.com/docs/cli/installation)
3. Login ke Koyeb CLI:
   ```
   koyeb login
   ```

### Deployment

1. Pastikan Anda memiliki file-file berikut:
   - Procfile
   - runtime.txt
   - koyeb.yaml
   - requirements.txt

2. Konfigurasi environment variables di Koyeb:
   - TELEGRAM_BOT_TOKEN
   - ADMIN_BOT_TOKEN
   - ADMIN_CHAT_ID
   - ADMIN_ID

3. Deploy aplikasi dengan CLI:
   ```
   koyeb app init telegram-scraper-bot --docker . --port 8080
   ```

   Atau deploy langsung dari GitHub dengan Koyeb UI:
   - Connect GitHub repository
   - Pilih buildpack sebagai builder
   - Tambahkan environment variables yang diperlukan
   - Deploy

### Monitoring

Pantau log aplikasi di dashboard Koyeb atau gunakan CLI:
```
koyeb service logs telegram-scraper-bot
```

## Penanganan Error

Bot ini dirancang dengan penanganan error yang baik:

1. Semua operasi dibungkus dalam try-except
2. Error logging tersedia di log sistem
3. Bot akan secara otomatis melakukan restart jika terjadi crash (dikelola oleh Koyeb)

## Perhatian Khusus

- Pastikan file `allowed_users.json` dan `user_logs.json` sudah ada di repository dan memiliki format yang benar
- Kredensial PDDikti tersimpan di `pddikti_api.py`, pastikan tidak berubah saat deployment 