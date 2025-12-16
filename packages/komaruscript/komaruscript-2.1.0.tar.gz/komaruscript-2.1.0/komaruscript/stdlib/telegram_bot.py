
try:
    import telebot
except ImportError:
    print("❌ Error: 'telebot' module not found. Please run 'komaru install pyTelegramBotAPI'")
    telebot = None

import threading
import time

class KomaruBot:
    def __init__(self, token):
        if telebot:
            self.bot = telebot.TeleBot(token)
        else:
            self.bot = None

    def добавить_обработчик(self, command, handler):
        if not self.bot: return
        
        if command == "start":
            @self.bot.message_handler(commands=['start'])
            def _handler(message):
                # Convert telebot message to dict for Komaru usage
                msg_dict = {
                    "chat": {"id": message.chat.id},
                    "text": message.text
                }
                handler(msg_dict)
        else:
            # Generic handler for text
            @self.bot.message_handler(func=lambda m: True)
            def _handler(message):
                 msg_dict = {
                    "chat": {"id": message.chat.id},
                    "text": message.text
                }
                 handler(msg_dict)

    def отправить_сообщение(self, chat_id, text):
        if not self.bot: return
        self.bot.send_message(chat_id, text)

    def отправить_фото(self, chat_id, photo_url, caption=None):
        if not self.bot: return
        try:
            self.bot.send_photo(chat_id, photo_url, caption=caption)
        except Exception as e:
            print(f"❌ Ошибка отправки фото: {e}")

def создать_бота(token):
    return KomaruBot(token)

def запустить_бота_в_фоне(bot_instance):
    if not bot_instance.bot: return
    print("🤖 Бот запущен...")
    # Run polling in main thread for now as it's easier, or thread if user really wants 'background'
    # The prompt usage implies it just starts running.
    # But function name says "background".
    
    t = threading.Thread(target=bot_instance.bot.infinity_polling)
    t.daemon = True
    t.start()

