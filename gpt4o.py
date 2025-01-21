import asyncio
import platform
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import g4f
import html

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BOT_TOKEN = "7783506104:AAE-eH3yGUFMu8Md76g01h4Uqred1yIs494"

bot = telebot.TeleBot(BOT_TOKEN)

chat_contexts = {}

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="🔄 Закінчити бесіду"))
    return keyboard

def split_long_message(message, chunk_size=4096):
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "👋 Привіт, я твій помічник GPT - 4 🤖.\n\n"
        "Задайте мені будь яке питання!💡\n"
        "Іноді відповідь може зайняти до 5 хвилин. 🕒😊\n\n"
        "Почнемо? 🎉",
        reply_markup=get_main_keyboard()
    )
    chat_contexts[chat_id] = [{"role": "system", "content": "Пожалуйста, используй обычные математические символы и знаки вместо HTML-форматирования. Например, используй *, /, ^, ≤, ≥, ≠, ∑, ∏, √ и другие символы напрямую."}]

@bot.message_handler(func=lambda msg: msg.text == "🔄 Закінчити бесіду")
def end_chat(message):
    chat_id = message.chat.id
    if chat_id in chat_contexts:
        chat_contexts.pop(chat_id)
    bot.send_message(chat_id, "Ну тіпа пока. 😊")
    chat_contexts[chat_id] = [{"role": "system", "content": "Будь ласка, використовуй звичайні математичні символи та знаки замість HTML-форматування. Наприклад, використовуй *, /, ^, ≤, ≥, ≠, ∑, ∏, √ и другие символы напрямую."}]

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text.strip()

    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = [{"role": "system", "content": "Будь ласка, ваідповідай чітко та нормально."}]
    
    chat_contexts[chat_id].append({"role": "user", "content": user_input})

    bot.send_chat_action(chat_id, "typing")

    prompt = f"Користувач запитав: '{user_input}'. Дай відповідь чітко та нормально."
    prompt += "\nІсторія розмов:\n" + "\n".join([item["content"] for item in chat_contexts[chat_id]])

    try:
        response = g4f.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )

        if isinstance(response, dict) and 'choices' in response:
            assistant_message = response['choices'][0]['message']['content']
        else:
            assistant_message = str(response)

    except Exception as e:
        assistant_message = f"Сталась помилка під час генерування відповіді.: {str(e)}"

    chat_contexts[chat_id].append({"role": "assistant", "content": assistant_message})

    decoded_response = html.unescape(assistant_message)
    split_messages = split_long_message(decoded_response)
    
    for msg in split_messages:
        bot.send_message(chat_id, msg)

if __name__ == '__main__':
    print("Бот запущений!")
    bot.infinity_polling()
