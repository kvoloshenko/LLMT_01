from dotenv import load_dotenv
import os
import platon_chat_gpt as chat_gpt
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

KNOWLEDGE_BASE_URL = os.environ.get("KNOWLEDGE_BASE_URL") # база знаний
print(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')

def main():

    topic = 'Привет! Ты кто?'
    print(f'topic={topic}')
    logging.info(f'{MESSAGE_TEXT_S}{topic}{MESSAGE_TEXT_E}')
    ba = '0001'
    db, db_file_name = chat_gpt.create_db(KNOWLEDGE_BASE_URL, '0001')
    reply_text, num_tokens, messages, completion = chat_gpt.chat_question(topic, ba)
    print(f'reply_text={reply_text}')
    logging.info(f'{REPLY_TEXT_S}{reply_text}{REPLY_TEXT_E}')

if __name__ == "__main__":
    main()