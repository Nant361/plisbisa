#!/bin/bash

# Script untuk deployment ke Koyeb dengan file .env yang sudah ada

echo "Memulai deployment ke Koyeb..."

# Cek apakah Koyeb CLI terinstall
if ! command -v koyeb &> /dev/null; then
    echo "Koyeb CLI tidak terinstall. Silakan install terlebih dahulu."
    echo "Lihat https://www.koyeb.com/docs/cli/installation untuk petunjuk instalasi."
    exit 1
fi

# Cek apakah user sudah login
echo "Memeriksa status login Koyeb..."
if ! koyeb whoami &> /dev/null; then
    echo "Anda belum login ke Koyeb. Silakan login terlebih dahulu."
    koyeb login
fi

# Cek apakah file .env ada
if [ ! -f .env ]; then
    echo "File .env tidak ditemukan. Pastikan file sudah ada."
    exit 1
fi

# Baca file .env
echo "Membaca file .env..."
source .env

# Validasi environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$ADMIN_BOT_TOKEN" ] || [ -z "$ADMIN_CHAT_ID" ] || [ -z "$ADMIN_ID" ]; then
    echo "Ada variabel yang diperlukan tidak ditemukan di file .env"
    echo "Pastikan file .env berisi: TELEGRAM_BOT_TOKEN, ADMIN_BOT_TOKEN, ADMIN_CHAT_ID, ADMIN_ID"
    exit 1
fi

# Deploy aplikasi ke Koyeb
echo "Menginisialisasi aplikasi di Koyeb..."
koyeb app init telegram-scraper-bot --docker . --port 8080

# Tunggu sampai service tersedia
echo "Menunggu service tersedia..."
sleep 10

# Tambahkan environment variables
echo "Menambahkan environment variables..."
koyeb service env create telegram-scraper-bot --service telegram-scraper-bot \
  --env TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  --env ADMIN_BOT_TOKEN="$ADMIN_BOT_TOKEN" \
  --env ADMIN_CHAT_ID="$ADMIN_CHAT_ID" \
  --env ADMIN_ID="$ADMIN_ID"

echo "Deployment selesai! Silakan cek status aplikasi di dashboard Koyeb."
echo "Untuk melihat log, gunakan: koyeb service logs telegram-scraper-bot" 