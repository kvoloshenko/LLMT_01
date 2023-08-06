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
import datetime

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

# Get the current date and time
current_datetime = datetime.datetime.now()

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

# модель: gpt-3.5-turbo-0613, gpt-3.5-turbo-0301, gpt-3.5-turbo-16k, gpt-3.5-turbo
LL_MODEL = "gpt-3.5-turbo-0613"
print(f'LL_MODEL = {LL_MODEL}')

CHUNK_SIZE = 1024  # Количество токинов в  чанке
print(f'CHUNK_SIZE={CHUNK_SIZE}')

NUMBER_RELEVANT_CHUNKS = 5  # Количество релевантных чанков
print(f'NUMBER_RELEVANT_CHUNKS={NUMBER_RELEVANT_CHUNKS}')

TEMPERATURE = 1 # Температура модели
print(f'TEMPERATURE={TEMPERATURE}')


SYSTEM_DOC_URL = 'https://docs.google.com/document/d/1eG-WfEiwyJZIZPgi-GK7-Q9ueO1FNcgfvFjsAf99N6g'     # промпт
print(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')

KNOWLEDGE_BASE_URL = 'https://docs.google.com/document/d/1eVdtf7fpChQl7dKic-qI-BFjNtSGkAbQ' # база знаний
print(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')

def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text

# Инструкция для GPT, которая будет подаваться в system
system = load_document_text(SYSTEM_DOC_URL)  # Загрузка файла с Промтом
logging.info(f'{PROMPT_S}{system}{PROMPT_E}')

# База знаний, которая будет подаваться в LangChain
database = load_document_text(KNOWLEDGE_BASE_URL)  # Загрузка файла с Базой Знаний
logging.info(f'{KNOWLEDGE_DB_S}{database}{KNOWLEDGE_DB_E}')

source_chunks = []
splitter = CharacterTextSplitter(separator="\n", chunk_size=1024, chunk_overlap=0)

for chunk in splitter.split_text(database):
    source_chunks.append(Document(page_content=chunk, metadata={}))

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

# Создадим индексную базу из разделенных фрагментов текста
db = FAISS.from_documents(source_chunks, embeddings)

for chunk in source_chunks:  # Поиск слишком больших чанков
    if len(chunk.page_content) > CHUNK_SIZE:
        logging.warning(f'*** Слишком большой кусок! ***')
        logging.warning(f'chunk_len ={len(chunk.page_content)}')
        logging.warning(f'content ={chunk.page_content}')

# Функция, которая позволяет выводить ответ модели в удобочитаемом виде
def insert_newlines(text: str, max_len: int = 170) -> str:
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > max_len:
            lines.append(current_line)
            current_line = ""
        current_line += " " + word
    lines.append(current_line)
    return " ".join(lines)

def answer_index(system, topic, index_db, temp=TEMPERATURE):

    # Поиск релевантных отрезков из базы знаний
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)

    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n ===================== Отрывок документа №{i+1} =====================\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    logging.info(f'{MESSAGE_CONTENT_S}{message_content}{MESSAGE_CONTENT_E}')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Документ с информацией для ответа клиенту: {message_content}\n\n Вопрос клиента: \n{topic}"}
    ]

    completion = openai.ChatCompletion.create(
        model=LL_MODEL,
        messages=messages,
        temperature=temp
    )

    answer = insert_newlines(completion.choices[0].message.content)

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



