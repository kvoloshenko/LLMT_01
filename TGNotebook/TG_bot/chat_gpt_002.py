import re
import requests
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv

load_dotenv()
# Загрузка значений из .env
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE")) # Количество токинов в  чанке
print(f'CHUNK_SIZE={CHUNK_SIZE}')

NUMBER_RELEVANT_CHUNKS = int(os.environ.get("NUMBER_RELEVANT_CHUNKS"))   # Количество релевантных чанков
print(f'NUMBER_RELEVANT_CHUNKS={NUMBER_RELEVANT_CHUNKS}')

VERBOSE = int(os.environ.get("VERBOSE")) # Выводить тех. инфу
print(f'VERBOSE={VERBOSE}')

TEMPERATURE = float(os.environ.get("TEMPERATURE")) # Температура модели
print(f'TEMPERATURE={TEMPERATURE}')

SYSTEM_DOC_URL = os.environ.get("SYSTEM_DOC_URL") # промпт
print (f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')

KNOWLEDGE_BASE_URL = os.environ.get("KNOWLEDGE_BASE_URL") # база знаний
print (f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')


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
if VERBOSE: print(f'\n ===========================================\nsystem={system}')

# База знаний, которая будет подаваться в LangChain
database = load_document_text(KNOWLEDGE_BASE_URL)  # Загрузка файла с Базой Знаний
if VERBOSE: print(f'\n ===========================================\ndatabase={database}\n ===========================================')

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

def answer_index(system, topic, search_index, temp=TEMPERATURE, verbose=VERBOSE):

    # Поиск релевантных отрезков из базы знаний
    docs = search_index.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)
    # print(f'type(docs)={type(docs)}')

    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n===================== Отрывок документа №{i+1} =====================\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{topic}"}
    ]
    # print(f'type(messages)={type(messages)}')

    if verbose: print(f'temperature={temp}')
    if verbose: print('\n ===========================================: ')

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temp
    )
    answer = insert_newlines(completion.choices[0].message.content)
    return answer  # возвращает ответ


def answer_user_question(topic):

    source_chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=1024, chunk_overlap=0)

    for chunk in splitter.split_text(database):
        source_chunks.append(Document(page_content=chunk, metadata={}))

    # Инициализирум модель эмбеддингов
    embeddings = OpenAIEmbeddings()

    # Создадим индексную базу из разделенных фрагментов текста
    db = FAISS.from_documents(source_chunks, embeddings)

    # print(f'type(source_chunks)={type(source_chunks)}')
    # print(f'type(embeddings)={type(embeddings)}')
    # print(f'type(db)={type(db)}')

    for c in source_chunks: # Поиск слишком больших чанков
        if len(c.page_content) > CHUNK_SIZE:
            print(f'chunk_len ={len(c.page_content)}')
            print(f'content ={c.page_content}')

    ans = answer_index(system, topic, db)  # получите ответ модели
    # print(f'type(ans)={type(ans)}')
    # print(ans)

    return ans

def do_test(topic):
    ans = answer_user_question(topic)
    return ans

if __name__ == '__main__':
    topic = 'Привет! Ты кто?'
    print(f'topic={topic}')
    response = do_test(topic)
    print(f'response={response}')



