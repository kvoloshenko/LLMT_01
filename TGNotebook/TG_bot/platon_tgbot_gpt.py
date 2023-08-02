from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import time
import os
import platon_chat_gpt as chat_gpt
import logging

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

# возьмем переменные окружения из .env
load_dotenv()

# загружаем значеняи из файла .env
TOKEN = os.environ.get("TOKEN")

TEXT_BEGINNING = os.environ.get("TEXT_BEGINNING")
logging.info(f'TEXT_BEGINNING = {TEXT_BEGINNING}')

TEXT_END = os.environ.get("TEXT_END")
logging.info (f'TEXT_END = {TEXT_END}')

# функция команды /start
async def start(update, context):
  await update.message.reply_text('Привет! Это update_context бот.')

# функция для текстовых сообщений
async def text(update, context):
    # использование update
    # print(update)
    logging.info('-------------------')
    logging.info(f'text: {update.message.text}')
    logging.info(f'date: {update.message.date}')
    logging.info(f'id message: {update.message.message_id}')
    logging.info(f'name: {update.message.from_user.first_name}')
    logging.info(f'user.id: {update.message.from_user.id}')
    print('-------------------')
    print(f'text: {update.message.text}')
    print(f'date: {update.message.date}')
    print(f'id message: {update.message.message_id}')
    print(f'name: {update.message.from_user.first_name}')
    print(f'user.id: {update.message.from_user.id}')

    topic = update.message.text
    response = TEXT_BEGINNING + '\n'
    response = response + chat_gpt.answer_user_question(topic) + '\n' + TEXT_END

    my_message = await update.message.reply_text(f'{response}')
    logging.info(f'answer: {response}')
    logging.info('-------------------')
    print(f'answer: {response}')
    print('-------------------')

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
    logging.info("Bot started..!")

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()



if __name__ == "__main__":
    main()