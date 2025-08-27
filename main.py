import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
import random
from datetime import time, datetime, timedelta
import os
import asyncio
import pytz

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === ЗАМЕНИТЕ ЭТИ ЗНАЧЕНИЯ ===
TOKEN = "8031227579:AAGic9Nz_Lc1YXt7oe-NjhZs5UgOCWT2Efg"  # ← Замените на свой токен!
YOUR_CHAT_ID = 5226029430  # ← Замените на ваш ID (узнать: @userinfobot)

# Контент
утренние_намерения = [
    "Сегодня я легко нахожу решения",
    "Я выбираю вариант с лёгкостью",
    "Мои мысли создают реальность"
]

цитаты = [
    "Познай себя — и ты познаешь Вселенную. — Гермес",
    "Снижай значимость — и реальность скользит. — Зеланд",
    "Я - часть разума, создающего этот мир. - Гермес",
    "Я снижаю значимость, не цепляюсь, доверяю потоку. - Зеланд",
]

# Обработчики
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

async def manual_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручная отправка утреннего сообщения"""
    await send_morning(context)
    await update.message.reply_text("Утреннее сообщение отправлено вручную")

async def manual_evening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручная отправка вечернего сообщения"""
    await send_evening(context)
    await update.message.reply_text("Вечернее сообщение отправлено вручную")

async def check_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка активных задач планировщика"""
    job_names = [job.name for job in context.application.job_queue.jobs()]
    await update.message.reply_text(f"Активные задачи: {', '.join(job_names) if job_names else 'Нет активных задач'}")

# Основная функция
async def main():
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    application.add_handler(CommandHandler("morning", manual_morning))
    application.add_handler(CommandHandler("evening", manual_evening))
    application.add_handler(CommandHandler("jobs", check_jobs))
    
    # Настраиваем планировщик заданий
    job_queue = application.job_queue
    
    # Устанавливаем московский часовой пояс
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Рассылка (время в МСК)
    job_queue.run_daily(send_morning, time(8, 0, 0, tzinfo=moscow_tz))   # 8:00 по МСК
    job_queue.run_daily(send_evening, time(23, 20, 0, tzinfo=moscow_tz))  # 23:00 по МСК
    
    # Альтернативный способ - отправка каждые 10 минут для тестирования
    # job_queue.run_repeating(send_morning, interval=600, first=10)
    
    # Запускаем бота в режиме polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Сохраняем ссылку на application для доступа извне
    global app_instance
    app_instance = application
    
    # Бесконечный цикл для поддержания работы бота
    while True:
        await asyncio.sleep(3600)

# Создаем простой HTTP-сервер для поддержания активности
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Бот работает! Последняя активность: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Запуск приложения
if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    asyncio.run(main())
