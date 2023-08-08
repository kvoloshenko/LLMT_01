from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import time
import os
import uii_chat_gpt as chat_gpt
import logging

# XML теги для лога
LOG_S = '<log>'
LOG_E = '</log>'
X_CDATA_S = '<![CDATA['
X_CDATA_E = ']]>'
MESSAGE_TEXT_S = '<mt>' + X_CDATA_S
MESSAGE_TEXT_E = X_CDATA_E + '</mt>'
MESSAGE_DATE_S = '<md>'
MESSAGE_DATE_E = '</md>'
MESSAGE_ID_S = '<mi>'
MESSAGE_ID_E = '</mi>'
USER_NAME_S = '<un>'
USER_NAME_E = '</un>'
USER_ID_S = '<ui>'
USER_ID_E = '</ui>'
REPLY_TEXT_S = '<rt>' + X_CDATA_S
REPLY_TEXT_E = X_CDATA_E + '</rt>'

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

# возьмем переменные окружения из .env
load_dotenv()

# загружаем значеняи из файла .env
TOKEN = os.environ.get("TOKEN")

TEXT_BEGINNING = '*** Bot is talking to you: ***'
print(f'TEXT_BEGINNING = {TEXT_BEGINNING}')
TEXT_END = '*** Check the information with the manager! ***'
print (f'TEXT_END = {TEXT_END}')

QUESTION_FILTER = '@userTest01bot'

# функция команды /start
async def start(update, context):
  await update.message.reply_text('Привет! Это update_context бот.')

# функция для текстовых сообщений
async def text(update, context):
    # использование update
    logging.info(f'{MESSAGE_DATE_S}{update.message.date}{MESSAGE_DATE_E}')
    logging.info(f'{MESSAGE_ID_S}{update.message.message_id}{MESSAGE_ID_E}')
    logging.info(f'{USER_NAME_S}{update.message.from_user.first_name}{USER_NAME_E}')
    logging.info(f'{USER_ID_S}{update.message.from_user.id}{USER_ID_E}')
    logging.info(f'{MESSAGE_TEXT_S}{update.message.text}{MESSAGE_TEXT_E}')
    print('-------------------')
    print(f'update: {update}')
    print(f'date: {update.message.date}')
    print(f'id message: {update.message.message_id}')
    print(f'name: {update.message.from_user.first_name}')
    print(f'user.id: {update.message.from_user.id}')
    print(f'text: {update.message.text}')


    topic = update.message.text
    question_filter_len = len (QUESTION_FILTER)
    topic_first_n = topic[:question_filter_len]

    chat_type = update.message.chat.type

    if (QUESTION_FILTER == topic_first_n) or (chat_type == 'private'):
        reply_text = chat_gpt.answer_user_question(topic)
        response = TEXT_BEGINNING + '\n'
        response = response + reply_text + '\n' + TEXT_END

        my_message = await update.message.reply_text(f'{response}')
        logging.info(f'{REPLY_TEXT_S}{reply_text}{REPLY_TEXT_E}')
        print(f'reply_text: {reply_text}')
        print('-------------------')


def main():

    # точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен..!')
    # logging.info(LOG_S)

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()

    print('Бот остановлен..!')
    logging.info(LOG_E)



if __name__ == "__main__":
    main()