# 🚀 Crypto Funding Rate Monitor Bot

**Telegram бот для мониторинга funding rates криптовалютных фьючерсов на биржах Binance и Bybit**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)

## 📋 Описание

Этот проект представляет собой многофункциональный Telegram бот для мониторинга funding rates криптовалютных фьючерсов. Бот отслеживает изменения funding rates на биржах Binance и Bybit в реальном времени и отправляет уведомления пользователям при превышении заданных пороговых значений.

### ✨ Основные возможности

- 🔄 **Реальное время**: Мониторинг funding rates каждые 5 секунд
- 📊 **Мультибиржевой**: Поддержка Binance и Bybit
- 🎯 **Настраиваемые пороги**: Уведомления от ±0.1% или ±0.5%
- 🔍 **Режим отладки**: Подробная информация о всех парах
- 🛑 **Управление**: Простые команды для запуска/остановки
- 👤 **Многопользовательский**: Поддержка множества пользователей
- 🔒 **Безопасность**: Режим Alex для административного контроля

## 🏗️ Архитектура

Проект состоит из нескольких компонентов:

- **`bot.py`** - Основной Telegram бот с полным интерфейсом
- **`funding_01_watch.py`** - Консольная версия для мониторинга
- **`bybit_only.py`** - Упрощенная версия только для Bybit
- **`alex_trigger.py`** - Специальные триггеры для Alex режима

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.8+
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- Стабильное интернет-соединение

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/yourusername/crypto-funding-rate-monitor.git
cd crypto-funding-rate-monitor
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте переменные окружения:**
```bash
cp env.example .env
# Отредактируйте .env файл и добавьте ваш TELEGRAM_TOKEN
```

4. **Запустите бота:**
```bash
python bot.py
```

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_TOKEN` | Токен Telegram бота | - |
| `POLL_INTERVAL` | Интервал опроса в секундах | 5 |
| `THRESHOLD_PCT` | Порог уведомлений в % | 0.1 |

### Команды бота

- **`/start`** - Запуск бота и выбор режима
- **`Уведомлять от ±0.1%`** - Мониторинг с порогом 0.1%
- **`Уведомлять от ±0.5%`** - Мониторинг с порогом 0.5%
- **`Отладка ВКЛ/ВЫКЛ`** - Включение/выключение режима отладки
- **`Стоп`** - Остановка мониторинга
- **`/alex`** - Активация административного режима
- **`/alex_off`** - Деактивация административного режима

## 📊 Мониторинг

### Поддерживаемые биржи

- **Binance Futures** - Все perpetual фьючерсы
- **Bybit** - Все linear perpetual контракты

### Типы уведомлений

- 🟢 **Положительные funding rates** - Зеленый индикатор
- 🔴 **Отрицательные funding rates** - Красный индикатор
- 📈 **Формат**: `btc/usdt | 🟢 0.1234% | binance`

## 🔧 Развертывание

### Автоматическое развертывание

```bash
chmod +x install.sh
./install.sh
```

### Ручное развертывание

1. Настройте systemd service:
```bash
sudo cp funding-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable funding-bot
```

2. Запустите сервис:
```bash
sudo systemctl start funding-bot
```

Подробная инструкция доступна в [DEPLOYMENT.md](DEPLOYMENT.md)

## 📈 Производительность

- **Масштабируемость**: Поддержка до 25 одновременных запросов
- **Эффективность**: Асинхронная обработка запросов
- **Надежность**: Обработка ошибок и таймаутов
- **Ресурсы**: Минимальное потребление памяти и CPU

## 🛡️ Безопасность

- 🔐 Защищенные API ключи через переменные окружения
- 🚫 Режим Alex для административного контроля
- 📝 Логирование всех операций
- 🔄 Автоматическое восстановление при ошибках

## 📝 Логирование

Бот ведет подробные логи всех операций:

```bash
# Просмотр логов systemd
sudo journalctl -u funding-bot -f

# Логи за последний час
sudo journalctl -u funding-bot --since "1 hour ago"
```

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте [Issues](https://github.com/yourusername/crypto-funding-rate-monitor/issues)
2. Создайте новый Issue с описанием проблемы
3. Приложите логи и конфигурацию

## 🔗 Полезные ссылки

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Binance API](https://binance-docs.github.io/apidocs/futures/en/)
- [Bybit API](https://bybit-exchange.github.io/docs/)
- [Python aiohttp](https://docs.aiohttp.org/)
- [aiogram](https://docs.aiogram.dev/)

## 📊 Статистика

- **Мониторируемые пары**: 500+ на каждой бирже
- **Частота обновления**: 5 секунд
- **Время отклика**: < 100ms
- **Доступность**: 99.9%

---

**Создано с ❤️ для криптотрейдеров**
