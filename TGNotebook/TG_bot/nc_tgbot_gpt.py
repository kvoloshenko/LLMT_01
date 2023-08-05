from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import nc_chat_gpt as chat_gpt

# Loading values from .env file
load_dotenv()
TOKEN = os.environ.get("TOKEN")

TEXT_BEGINNING = '*** Bot is talking to you: ***'
print(f'TEXT_BEGINNING = {TEXT_BEGINNING}')
TEXT_END = '*** Check the information with the manager! ***'
print (f'TEXT_END = {TEXT_END}')

QUESTION_FILTER = '@userVccTest01bot'

# command function /start
async def start(update, context):
  await update.message.reply_text('Hi! This is the update_context bot.')

# Function for text messages
async def text(update, context):
    # Use update
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
        print(f'reply_text: {reply_text}')
        print('-------------------')

def main():

    # Application entry point
    application = Application.builder().token(TOKEN).build()
    print('Bot started!')
    # print(LOG_S)

    # Add handler for the command /start
    application.add_handler(CommandHandler("start", start))

    # Add a text message handler
    application.add_handler(MessageHandler(filters.TEXT, text))

    # Launching the application (to stop you need to press Ctrl-C)
    application.run_polling()

    print('Bot stopped!')


if __name__ == "__main__":
    main()