# -*- coding: utf-8 -*-
"""OpenLesson2 TGbot.ipynb.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-U9xvN4IwSmVQNNKz-bgN1yiyWJrK4L8

## update_context.py
"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import time
import os

# возьмем переменные окружения из .env
load_dotenv()

# загружаем токен бота
TOKEN = os.environ.get("TOKEN")


# функция команды /start
async def start(update, context):
  await update.message.reply_text('Привет! Это update_context бот.')


# функция для текстовых сообщений
async def text(update, context):

    # использование update
    print(update)
    print('-------------------')
    print(f'text: {update.message.text}')
    print(f'date: {update.message.date}')
    print(f'id message: {update.message.message_id}')
    print(f'name: {update.message.from_user.first_name}')
    print(f'user.id: {update.message.from_user.id}')
    print('-------------------')

    my_message = await update.message.reply_text(f'Получено текстовое сообщение: {update.message.text}')

    # использованеи context

    #time.sleep(5)
    # УДАЛЕНИЕ сообщений
    #                    update.message.chat_id - получаем сообщение и message_id получаем из переменной my_message
    #await context.bot.deleteMessage(chat_id=update.message.chat_id, message_id=my_message.message_id)

    # закрепление сообщений
    # await context.bot.pin_chat_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    # изменение описания бота
    # await context.bot.set_my_short_description("Этот бот очень умный, добрый и красивый")



def main():

    # точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен..!')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()


if __name__ == "__main__":
    main()