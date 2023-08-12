from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import uii_chat_gpt as chat_gpt

# Загружаем значеняи из файла .env
load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Функция команды /start
async def start(update, context):
  await update.message.reply_text('Hi! This is the update_context bot.')

# Функция для текстовых сообщений
async def text(update, context):
    # Использование update
    print('-------------------')
    print(f'update: {update}')
    print(f'date: {update.message.date}')
    print(f'id message: {update.message.message_id}')
    print(f'name: {update.message.from_user.first_name}')
    print(f'user.id: {update.message.from_user.id}')
    print(f'text: {update.message.text}')

    topic = update.message.text

    reply_text = chat_gpt.answer_user_question(topic)

    await update.message.reply_text(f'{reply_text}')
    print(f'reply_text: {reply_text}')
    print('-------------------')

def main():

    # Точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    print('Bot started!')
    # print(LOG_S)

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # Запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()

    print('Bot stopped!')


if __name__ == "__main__":
    main()