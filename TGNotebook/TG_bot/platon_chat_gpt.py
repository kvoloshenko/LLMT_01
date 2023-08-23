import re
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, timezone
import tiktoken

# XML теги для лога
LOG_S = '<log>'
LOG_E = '</log>'
X_CDATA_S = '<![CDATA['
X_CDATA_E = ']]>'
PROMPT_S = '<prompt>' + X_CDATA_S
PROMPT_E = X_CDATA_E + '</prompt>'
KNOWLEDGE_DB_S = '<kdb>' + X_CDATA_S
KNOWLEDGE_DB_E = X_CDATA_E + '</kdb>'
MESSAGE_CONTENT_S = '<mc>' + X_CDATA_S
MESSAGE_CONTENT_E = X_CDATA_E + '</mc>'
NUM_TOKENS_S = '<num_tokens>'
NUM_TOKENS_E = '</num_tokens>'
CHUNK_NUM_S = '<chunk_num>'
CHUNK_NUM_E = '</chunk_num>'

# Get the current date and time
current_datetime = datetime.now(tz=timezone(timedelta(hours=3)))

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

logfilename = "Logs/" + formatted_datetime + "_tgbot_gpt.xml"
logging.getLogger("faiss").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, filename=logfilename,filemode="w")

load_dotenv()
# Загрузка значений из .env
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

logging.info(LOG_S)
LL_MODEL = os.environ.get("LL_MODEL") # модель
logging.info(f'LL_MODEL = {LL_MODEL}')
print(f'LL_MODEL = {LL_MODEL}')

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE")) # Количество токинов в  чанке
logging.info(f'CHUNK_SIZE={CHUNK_SIZE}')
print(f'CHUNK_SIZE={CHUNK_SIZE}')

NUMBER_RELEVANT_CHUNKS = int(os.environ.get("NUMBER_RELEVANT_CHUNKS"))   # Количество релевантных чанков
logging.info(f'NUMBER_RELEVANT_CHUNKS={NUMBER_RELEVANT_CHUNKS}')

TEMPERATURE = float(os.environ.get("TEMPERATURE")) # Температура модели
logging.info(f'TEMPERATURE={TEMPERATURE}')
print(f'TEMPERATURE={TEMPERATURE}')

SYSTEM_DOC_URL = os.environ.get("SYSTEM_DOC_URL") # промпт
logging.info(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')

KNOWLEDGE_BASE_URL = os.environ.get("KNOWLEDGE_BASE_URL") # база знаний
logging.info(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')


def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)
    # print (f'doc_id={doc_id}')
    text = ''

    try:
        # Download the document as plain text
        response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
        response.raise_for_status()
        if 'text/plain' in response.headers['Content-Type']:
            # print('Правильный доступ!')
            text = response.text
        else:
            raise ValueError('Invalid Google Docs URL')
            print('Нет доступа к документу анонимным пользователям')
            logging.error(f'!!! No access to the document by anonymous users !!!')

    except Exception as e:  # обработка ошибок requests.exceptions.HTTPError: 404 Client Error: Not Found for url
        print(f'!!! load_document_text error: {str(e)}')
        logging.error(f'!!! load_document_text error: {str(e)}')

    return text

# Инструкция для GPT, которая будет подаваться в system
system = load_document_text(SYSTEM_DOC_URL)  # Загрузка файла с Промтом
logging.info(f'{PROMPT_S}{system}{PROMPT_E}')

# База знаний, которая будет подаваться в LangChain
database = load_document_text(KNOWLEDGE_BASE_URL)  # Загрузка файла с Базой Знаний
logging.info(f'{KNOWLEDGE_DB_S}{database}{KNOWLEDGE_DB_E}')

source_chunks = []
splitter = CharacterTextSplitter(separator="\n", chunk_size=CHUNK_SIZE, chunk_overlap=0)

for chunk in splitter.split_text(database):
    source_chunks.append(Document(page_content=chunk, metadata={}))

chunk_num = len(source_chunks)
print(f'chunk_num={chunk_num}')
logging.info(f'{CHUNK_NUM_S}{chunk_num}{CHUNK_NUM_E}')

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

try:
    db = FAISS.from_documents(source_chunks, embeddings) # Создадим индексную базу из разделенных фрагментов текста
except Exception as e: # обработка ошибок openai.error.RateLimitError
    print(f'!!! External error: {str(e)}')
    logging.error(f'!!! External error: {str(e)}')

for chunk in source_chunks:  # Поиск слишком больших чанков
    if len(chunk.page_content) > CHUNK_SIZE:
        logging.warning(f'*** Слишком большой кусок! ***')
        logging.warning(f'chunk_len ={len(chunk.page_content)}')
        logging.warning(f'content ={chunk.page_content}')
        print(f'*** Слишком большой кусок! ***')
        print(f'chunk_len ={len(chunk.page_content)}')
        print(f'content ={chunk.page_content}')

def num_tokens_from_messages(messages, model):
    """Возвращает количество токенов, используемых списком сообщений."""
    try:
        encoding = tiktoken.encoding_for_model(model) # Пытаемся получить кодировку для выбранной модели
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # если не получается, используем кодировку "cl100k_base"
    if model == "gpt-3.5-turbo-0301" or "gpt-3.5-turbo-0613" or "gpt-3.5-turbo-16k" or "gpt-3.5-turbo":
        num_tokens = 0 # начальное значение счетчика токенов
        for message in messages: # Проходимся по каждому сообщению в списке сообщений
            num_tokens += 4  # каждое сообщение следует за <im_start>{role/name}\n{content}<im_end>\n, что равно 4 токенам
            for key, value in message.items(): # итерация по элементам сообщения (роль, имя, контент)
                num_tokens += len(encoding.encode(value)) # подсчет токенов в каждом элементе
                if key == "name":  # если присутствует имя, роль опускается
                    num_tokens += -1  # роль всегда требуется и всегда занимает 1 токен, так что мы вычитаем его, если имя присутствует
        num_tokens += 2  # каждый ответ начинается с <im_start>assistant, что добавляет еще 2 токена
        return num_tokens # возвращаем общее количество токенов
    else:
      # Если выбранная модель не поддерживается, генерируем исключение
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}. # вызываем ошибку, если функция не реализована для конкретной модели""")


def answer_index(system, topic, index_db, temp=TEMPERATURE):

    # Поиск релевантных отрезков из базы знаний
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)

    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n ===================== Отрывок документа №{i+1} =====================\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    logging.info(f'{MESSAGE_CONTENT_S}{message_content}{MESSAGE_CONTENT_E}')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Документ с информацией для ответа клиенту: {message_content}\n\n Вопрос клиента: \n{topic}"}
    ]

    num_tokens = num_tokens_from_messages(messages, LL_MODEL)
    logging.info(f'{NUM_TOKENS_S}{num_tokens}{NUM_TOKENS_E}')
    print(f'num_tokens = {num_tokens}')

    try:
        completion = openai.ChatCompletion.create(
            model=LL_MODEL,
            messages=messages,
            temperature=temp
        )
    except Exception as e:  # обработка ошибок openai.error.RateLimitError
        print(f'!!! External error: {str(e)}')
        logging.error(f'!!! External error: {str(e)}')

    answer = completion.choices[0].message.content

    return answer  # возвращает ответ


def answer_user_question(topic):
    ans = answer_index(system, topic, db)  # получите ответ модели
    return ans

def do_test(topic):
    ans = answer_user_question(topic)
    return ans

if __name__ == '__main__':
    topic = 'Привет! Ты кто?'
    print(f'topic={topic}')
    response = do_test(topic)
    print(f'response={response}')



