import re
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv

# Загрузка значений из .env
load_dotenv()
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

TEMPERATURE = 0.5 # Температура модели
print(f'TEMPERATURE={TEMPERATURE}')

# Промптt
SYSTEM_DOC_URL = 'https://docs.google.com/document/d/1eW_hbYfvLM38n4X5nc6u9oEaV4wuPeio'
print(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')
# База знаний
KNOWLEDGE_BASE_URL = 'https://docs.google.com/document/d/1LgPsHoy3YA2wfnKRjW05a1_NztZVcdH7'
print(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')

def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Скачать документ в виде обычного текста
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text

# Инструкция для GPT, которая будет подаваться в system
system = load_document_text(SYSTEM_DOC_URL)  # Загрузка файла с Промтом

# База знаний, которая будет подаваться в LangChain
database = load_document_text(KNOWLEDGE_BASE_URL)  # Загрузка файла с Базой Знаний

source_chunks = []
splitter = CharacterTextSplitter(separator="\n", chunk_size=CHUNK_SIZE, chunk_overlap=0)

for chunk in splitter.split_text(database):
    source_chunks.append(Document(page_content=chunk, metadata={}))

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

# Создадим индексную базу из разделенных фрагментов текста
db = FAISS.from_documents(source_chunks, embeddings)

def answer_index(system, topic, index_db, temp=TEMPERATURE):

    # Поиск релевантных отрезков из базы знаний
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)

    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n ===================== Отрывок документа №{i+1} =====================\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    print(f'message_content={message_content}')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Документ с информацией для ответа клиенту:: {message_content}\n\n Customer Question: \n{topic}"}
    ]

    completion = openai.ChatCompletion.create(
        model=LL_MODEL,
        messages=messages,
        temperature=temp
    )

    answer = completion.choices[0].message.content

    return answer


def answer_user_question(topic):
    ans = answer_index(system, topic, db)  # Ответ модели
    return ans

def do_test(topic):
    ans = answer_user_question(topic)
    return ans

if __name__ == '__main__':
    print('---------------------------')
    topic = 'Привет, ты кто?'
    print(f'topic={topic}')
    response = do_test(topic)
    print('---------------------------')
    print(f'response={response}')



