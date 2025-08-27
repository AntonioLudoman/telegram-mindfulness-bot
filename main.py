import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
from datetime import time
import os
import asyncio
import pytz
from flask import Flask
from threading import Thread

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем переменные окружения
TOKEN = os.environ.get('TOKEN')
YOUR_CHAT_ID = int(os.environ.get('YOUR_CHAT_ID'))

# Проверяем наличие обязательных переменных
if not TOKEN or not YOUR_CHAT_ID:
    logging.error("Не установлены обязательные переменные окружения: TOKEN и YOUR_CHAT_ID")
    exit(1)

# Контент
утренние_намерения = [
    "Сегодня я легко нахожу решения",
    "Я выбираю вариант с лёгкостью",
    "Мои мысли создают реальность"
]

цитаты = [
    "Познай себя — и ты познаешь Вселенную. — Гермес",
    "Снижай значимость — и реальность скользит. — Зеланд"
]

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Бот запущен!\n"
        "Каждое утро и вечер — напоминание.\n"
        "Приятного трансферинга!"
    )

async def send_morning(context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = (
            "🌅 *Утро*\n\n"
            f"🔹 Намерение: {random.choice(утренние_намерения)}\n\n"
            f"🔹 Цитата: {random.choice(цитаты)}"
        )
        await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=msg, parse_mode='Markdown')
        logging.info("Утреннее сообщение отправлено")
    except Exception as e:
        logging.error(f"Ошибка при отправке утреннего сообщения: {e}")

async def send_evening(context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = (
            "🌇 *Вечер*\n\n"
            "🔹 Что пришло без усилий?\n"
            "🔹 Где я был в реакции?\n"
            "🔹 Благодарность: 3 пункта"
        )
        await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=msg, parse_mode='Markdown')
        logging.info("Вечернее сообщение отправлено")
    except Exception as e:
        logging.error(f"Ошибка при отправке вечернего сообщения: {e}")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Тестовое сообщение отправлено!\n"
        "Если вы видите это сообщение, значит бот работает."
    )

# Создаем Flask приложение для поддержания активности
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

# Основная функция
async def main():
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    
    # Настраиваем планировщик заданий
    job_queue = application.job_queue
    
    # Устанавливаем московский часовой пояс
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Рассылка (время в МСК)
    job_queue.run_daily(send_morning, time(8, 0, 0, tzinfo=moscow_tz))   # 8:00 по МСК
    job_queue.run_daily(send_evening, time(23, 51, 0, tzinfo=moscow_tz))  # 23:00 по МСК
    
    # Запускаем бота в режиме polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logging.info("Бот запущен и работает")
    
    # Бесконечный цикл для поддержания работы бота
    while True:
        await asyncio.sleep(3600)

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    asyncio.run(main())
