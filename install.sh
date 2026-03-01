#!/bin/bash

# Скрипт установки и запуска Funding Rate Bot
# Использование: ./install.sh

set -e

echo "🚀 Установка Funding Rate Bot..."

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Создаем директорию проекта
PROJECT_DIR="/home/ubuntu/bot-trade"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Копируем файлы проекта
echo "📋 Копирование файлов..."
# Здесь нужно скопировать все файлы проекта в $PROJECT_DIR

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "⚠️  Создайте файл .env на основе env.example"
    echo "   cp env.example .env"
    echo "   nano .env  # добавьте ваш TELEGRAM_TOKEN"
fi

# Устанавливаем systemd service
echo "⚙️  Настройка systemd service..."
sudo cp funding-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable funding-bot.service

echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Создайте файл .env: cp env.example .env"
echo "2. Добавьте ваш TELEGRAM_TOKEN в .env файл"
echo "3. Запустите бота: sudo systemctl start funding-bot"
echo "4. Проверьте статус: sudo systemctl status funding-bot"
echo "5. Просмотр логов: sudo journalctl -u funding-bot -f"
