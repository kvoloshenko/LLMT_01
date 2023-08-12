import re
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv
import tiktoken

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

TEMPERATURE = 1 # Температура модели
print(f'TEMPERATURE={TEMPERATURE}')

# Промптt
SYSTEM_DOC_URL = 'https://docs.google.com/document/d/14fKvev1HMdCe8StJGYuVnFwCIgxu0Pnu'
print(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')
# База знаний
KNOWLEDGE_BASE_URL = 'https://docs.google.com/document/d/1-JNOoO2og_WPUaAcBF7e10vL3JKuuv_e'
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

    num_tokens = num_tokens_from_messages(messages, LL_MODEL)
    print(f'num_tokens = {num_tokens}')

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



