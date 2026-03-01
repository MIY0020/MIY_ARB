# Инструкция по развертыванию Funding Rate Bot на хостинг

## Подготовка

### 1. Требования к серверу
- Ubuntu 20.04+ или аналогичная Linux система
- Python 3.8+
- Минимум 512MB RAM
- Стабильное интернет-соединение

### 2. Получение Telegram Bot Token
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

## Установка

### Способ 1: Автоматическая установка (рекомендуется)

1. **Загрузите файлы на сервер:**
```bash
# Скопируйте все файлы проекта в директорию на сервере
scp -r * user@your-server:/home/user/bot-trade/
```

2. **Запустите скрипт установки:**
```bash
ssh user@your-server
cd /home/user/bot-trade
chmod +x install.sh
./install.sh
```

3. **Настройте переменные окружения:**
```bash
cp env.example .env
nano .env
# Добавьте ваш TELEGRAM_TOKEN
```

4. **Запустите бота:**
```bash
sudo systemctl start funding-bot
sudo systemctl status funding-bot
```

### Способ 2: Ручная установка

1. **Подключитесь к серверу:**
```bash
ssh user@your-server
```

2. **Создайте директорию проекта:**
```bash
mkdir -p ~/bot-trade
cd ~/bot-trade
```

3. **Загрузите файлы проекта:**
```bash
# Скопируйте все файлы из локальной папки
```

4. **Установите Python зависимости:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Настройте переменные окружения:**
```bash
cp env.example .env
nano .env
# Добавьте:
# TELEGRAM_TOKEN=ваш_токен_от_botfather
# POLL_INTERVAL=5
# THRESHOLD_PCT=0.1
```

6. **Настройте systemd service:**
```bash
sudo cp funding-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable funding-bot.service
```

7. **Запустите бота:**
```bash
sudo systemctl start funding-bot
```

## Управление ботом

### Основные команды systemctl:

```bash
# Запуск бота
sudo systemctl start funding-bot

# Остановка бота
sudo systemctl stop funding-bot

# Перезапуск бота
sudo systemctl restart funding-bot

# Проверка статуса
sudo systemctl status funding-bot

# Просмотр логов
sudo journalctl -u funding-bot -f

# Отключить автозапуск
sudo systemctl disable funding-bot
```

### Альтернативный запуск (для тестирования):

```bash
cd ~/bot-trade
source venv/bin/activate
python bot.py
```

## Доступные боты

В проекте есть несколько вариантов ботов:

1. **bot.py** - Полнофункциональный Telegram бот с интерфейсом
2. **bybit_only.py** - Простой мониторинг только Bybit (консольный)
3. **funding_01_watch.py** - Мониторинг Binance и Bybit (консольный)

### Изменение запускаемого бота:

Отредактируйте файл `funding-bot.service`:
```bash
sudo nano /etc/systemd/system/funding-bot.service
```

Измените строку:
```
ExecStart=/home/ubuntu/bot-trade/venv/bin/python bot.py
```

На нужный файл, например:
```
ExecStart=/home/ubuntu/bot-trade/venv/bin/python bybit_only.py
```

Затем перезапустите:
```bash
sudo systemctl daemon-reload
sudo systemctl restart funding-bot
```

## Мониторинг и отладка

### Просмотр логов:
```bash
# Последние логи
sudo journalctl -u funding-bot -n 50

# Следить за логами в реальном времени
sudo journalctl -u funding-bot -f

# Логи за последний час
sudo journalctl -u funding-bot --since "1 hour ago"
```

### Проверка работы:
1. Отправьте `/start` боту в Telegram
2. Проверьте логи на наличие ошибок
3. Убедитесь, что бот отвечает на команды

## Обновление бота

1. **Остановите бота:**
```bash
sudo systemctl stop funding-bot
```

2. **Обновите файлы:**
```bash
# Загрузите новые файлы
```

3. **Обновите зависимости (если нужно):**
```bash
cd ~/bot-trade
source venv/bin/activate
pip install -r requirements.txt
```

4. **Запустите бота:**
```bash
sudo systemctl start funding-bot
```

## Решение проблем

### Бот не запускается:
1. Проверьте логи: `sudo journalctl -u funding-bot -n 20`
2. Убедитесь, что TELEGRAM_TOKEN корректный
3. Проверьте права доступа к файлам

### Бот не отвечает в Telegram:
1. Проверьте интернет-соединение
2. Убедитесь, что токен правильный
3. Проверьте, что бот не заблокирован

### Высокое потребление ресурсов:
1. Увеличьте POLL_INTERVAL в .env файле
2. Проверьте количество мониторируемых пар

## Безопасность

1. **Не публикуйте .env файл** - он содержит секретные данные
2. **Используйте firewall** для ограничения доступа
3. **Регулярно обновляйте** зависимости
4. **Мониторьте логи** на предмет подозрительной активности

## Поддержка

При возникновении проблем:
1. Проверьте логи бота
2. Убедитесь в корректности настроек
3. Проверьте доступность API бирж
4. Перезапустите бота при необходимости
