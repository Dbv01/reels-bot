import telebot
import google.generativeai as genai
import time
import threading

# ========== НАСТРОЙКИ ==========
TELEGRAM_TOKEN = '8206655661:AAFXzCApESMUlhKi8jPVoKgAWqGBjRtqhOA'  # Вставь то, что дал BotFather
GEMINI_API_KEY = 'AIzaSyDOf7K84fhl87TNWGQg0iuHvVeLzw_8vX0'        # Вставь ключ из Google AI Studio
# ===============================

# Настраиваем Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Настраиваем Telegram бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Твой "золотой промпт" (можно менять под свою идею)
SYSTEM_PROMPT = """
Ты — ИИ-гений виральных Reels. Твоя цель — сделать контент на миллион просмотров.
На любую идею отвечай по схеме:
1. ХУК (заголовок)
2. Сценарий (реплики)
3. Трюк для удержания
Используй молодежный сленг, никаких вежливых вступлений.
"""

# Словарь для подсчета запросов пользователей (для "монетизации")
user_requests = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "👋 Привет! Я твой личный сценарист Reels.\n"
                 "Просто напиши тему (например: 'кофе', 'отношения', 'bmw'), и я выдам виральный сценарий!\n\n"
                 "🔥 Первые 3 запроса — бесплатно.\n"
                 "Для безлимата жми /buy")

# Обработчик команды /buy (имитация оплаты)
@bot.message_handler(commands=['buy'])
def buy(message):
    bot.reply_to(message, 
                 "💎 Полный доступ на 30 дней — 990₽\n\n"
                 "Переведи по СБП на номер +7 (999) 123-45-67 (Альфа-Банк, Иван И.)\n"
                 "После оплаты пришли скриншот @твой_ник_менеджера, и я активирую безлимит.")

# Основной обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_text = message.text
    
    # Проверка лимита (заглушка под будущую монетизацию)
    if user_id not in user_requests:
        user_requests[user_id] = 0
    
    if user_requests[user_id] >= 3:
        bot.reply_to(message, "❌ Лимит бесплатных запросов исчерпан.\nЧтобы продолжить, используй /buy")
        return
    
    # Отправляем статус "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Отправляем запрос в Gemini
        full_prompt = SYSTEM_PROMPT + "\n\nИдея пользователя: " + user_text
        response = model.generate_content(full_prompt)
        
        # Увеличиваем счетчик запросов пользователя
        user_requests[user_id] += 1
        requests_left = 3 - user_requests[user_id]
        
        # Отправляем ответ
        bot.reply_to(message, 
                     f"{response.text}\n\n---\n✅ Осталось бесплатных запросов: {requests_left}")
    
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}. Попробуй еще раз.")

# Запуск бота (с защитой от повторного запуска на Render)
if __name__ == '__main__':
    print("Бот запущен и ждет сообщения...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"Ошибка соединения: {e}. Переподключение через 5 секунд...")
            time.sleep(5)