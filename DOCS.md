<div align=center>

# 📚 Документация Mafia Bot для Discord

[![Python Version](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![Discord API](https://img.shields.io/badge/Discord%20API-v10-blue)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Полное руководство по установке, настройке и управлению ботом для игры в Мафию

![Mafia Bot Logo](img/banner.png) <!-- Добавьте логотип -->

</div>

## 🛠 Установка и настройка

### ⚙️ Требования
- Python 3.12
- Discord сервер с правами администратора
- Доступ к [порталу разработчиков Discord](https://discord.com/developers/applications)

### 🔐 Настройка интентов
1. Перейдите на [портал разработчиков Discord](https://discord.com/developers/applications)
2. Выберите ваше приложение
3. В разделе "Bot" включите:
   - `PRESENCE INTENT`
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`

<img src="img/intents.png" width="70%">

### 🔗 Приглашение бота на сервер
1. В разделе **OAuth2** → **URL Generator** выберите:
   - `bot` — для добавления бота на сервер
   - `applications.commands` — для работы слеш-команд
2. В разделе **Bot Permissions** выберите **Администратор** — это даёт все необходимые права без лишних настроек
3. **Важно для `OWNER_ID`**: владелец бота (указанный в `.env`) должен авторизовать приложение и находиться на одном сервере с ботом, чтобы бот мог отправлять ему личные сообщения

### 🚀 Установка бота
```bash
# Клонирование репозитория
git clone https://github.com/paranoik1/MafiaBot.git
cd MafiaBot

# Установка зависимостей
pip install -r requirements.txt

# Создание конфигурационного файла
touch .env
nano .env  # Редактируем файл конфигурации
```

### 🔧 Конфигурация (.env)
```ini
BOT_TOKEN=your_bot_token_here
OWNER_ID=your_discord_id
YOOMONEY_TOKEN=your_yoomoney_token
YOOMONEY_RECEIVER=your_yoomoney_wallet
```

### ▶️ Запуск бота
```bash
python main.py
```

## 👨‍💻 Команды для разработчика

Требуют прав владельца бота (`OWNER_ID` из .env)

### 📊 Информация о состоянии (`.state`)
Показывает ключевую статистику бота:

```bash
Серверов: 42
Активных игр: 7
Аптайм: 2д 5ч 13м
```

### 💻 Выполнение кода (`.code`)
Позволяет выполнять Python код прямо в чате.

**Форматы:**
```python
.code print("Hello World")  # Однострочный код

.code
```python
for i in range(3):
    print(f"Многострочный код {i}")
```  # Многострочный код
```

**Безопасность:**
⚠️ Эта команда может выполнять ЛЮБОЙ Python код. Используйте с осторожностью!


### 📸 Скриншот
<img src="img/owner_commands.png">


## 🛡 Меры безопасности
1. Никому не передавайте ваш `BOT_TOKEN`
2. Ограничьте доступ к командам разработчика
3. Регулярно обновляйте зависимости
4. Используйте виртуальное окружение

## ❓ Поддержка
Если у вас возникли проблемы:
1. Создайте issue в [репозитории](https://github.com/paranoik1/MafiaBot/issues)

---

[⬆ Наверх](#) | [🏠 Главная страница](README.md)
