from langchain.llms import OpenAI
from langchain.docstore.document import Document
import requests
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
import pathlib
import subprocess
import tempfile
# import ipywidgets as widgets
import os
# import gspread
import re
import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger("langchain.text_splitter").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
from getpass import getpass

import openai
import tiktoken
from dotenv import load_dotenv
import pickle


#api_key = getpass('Введите ваш ключ API:')
# возьмем переменные окружения из .env
load_dotenv()
# загружаем значеняи из файла .env
ll_model = os.environ.get("LL_MODEL")
print(f'll_model={ll_model}')
api_key = os.environ.get("API_KEY")
verbose = os.environ.get("VERBOSE")
print(f'verbose={verbose}')
temperature = float(os.environ.get("TEMPERATURE"))
print(f'temperature={temperature}')
# separator = os.environ.get("CHARACTER_TEXT_SPLITTER_SEPARATOR")
# print(f'separator={separator}')

openai.api_key = api_key
def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    # функция для загрузки документа по ссылке из гугл док
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text

# serialization_20230729
# Function to check if a serialized search index exists
def check_search_index():
    if os.path.exists("search_index.pickle"):
        with open("search_index.pickle", "rb") as file:
            print('Восстановили Базу знаний из файла search_index.pickle')
            return pickle.load(file)
    else:
        print('Отсутствует сохраненный файл Базы знаний search_index.pickle')
        return None

# serialization_20230729
# Function to create and save a search index
def create_permanent_search_index(text: str) -> Chroma:
    # Check if a saved search index exists
    search_index = check_search_index()

    if search_index is None:
        # If no search index exists, create a new one
        search_index = create_embedding(text)

        # Save the search index
        with open("search_index.pickle", "wb") as file:
            pickle.dump(search_index, file)
    return search_index

def create_search_index(text: str) -> Chroma:
    return create_embedding(text)
    # return create_permanent_search_index(text) # serialization_20230729


def create_embedding(data):
    def num_tokens_from_string(string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    source_chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=1024, chunk_overlap=0)
    # Так не работает
    # splitter = CharacterTextSplitter(separator=separator, chunk_size=1024, chunk_overlap=0)

    for chunk in splitter.split_text(data):
        source_chunks.append(Document(page_content=chunk, metadata={}))

    # Создание индексов документа
    search_index = Chroma.from_documents(source_chunks, OpenAIEmbeddings(openai_api_key=api_key), )

    count_token = num_tokens_from_string(' '.join([x.page_content for x in source_chunks]), "cl100k_base")
    print('\n ===========================================: ')
    print('Количество токенов в документе :', count_token)
    print('ЦЕНА запроса:', 0.0001*(count_token/1000), ' $')

    return search_index

def answer(system, topic, temp = 1):
    messages = [
      {"role": "system", "content": system},
      {"role": "user", "content": topic}
      ]

    completion = openai.ChatCompletion.create(
      # model="gpt-3.5-gpt-3.5-turbo-0613",
      model = ll_model,
      messages=messages,
      temperature=temp
      )

    return completion.choices[0].message.content

# def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
def num_tokens_from_messages(messages, model=ll_model):
    """Возвращает количество токенов, используемых списком сообщений."""
    try:
        encoding = tiktoken.encoding_for_model(model) # Пытаемся получить кодировку для выбранной модели
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # если не получается, используем кодировку "cl100k_base"

    if model == "gpt-3.5-turbo-0301" or "gpt-3.5-turbo-0613" or "gpt-3.5-turbo-16k" or "gpt-3.5-turbo":
        num_tokens = 0 # начальное значение счетчика токенов
        for message in messages: # Проходимся по каждому сообщению в списке сообщений
            num_tokens += 4 # каждое сообщение следует за <im_start>{role/name}\n{content}<im_end>\n, что равно 4 токенам
            for key, value in message.items(): # итерация по элементам сообщения (роль, имя, контент)
                num_tokens += len(encoding.encode(value)) # подсчет токенов в каждом элементе
                if key == "name": # если присутствует имя, роль опускается
                    num_tokens += -1 # роль всегда требуется и всегда занимает 1 токен, так что мы вычитаем его, если имя присутствует
        num_tokens += 2 # каждый ответ начинается с <im_start>assistant, что добавляет еще 2 токена
        return num_tokens # возвращаем общее количество токенов
    else: # Если выбранная модель не поддерживается, генерируем исключение
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")


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


def answer_index(system, topic, search_index, temp=1, verbose = 0):

    # Selecting documents similar to the question
    # Поиск релевантных отрезков из базы знаний
    docs = search_index.similarity_search(topic, k=5)
    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)

    # messages = [
    #     {"role": "system", "content": system + f"{message_content}"},
    #     {"role": "user", "content": topic}
    # ]
    messages = [
        {"role": "system", "content": system},
        {"role": "user",
         "content": f"Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{topic}"}
    ]

    if verbose: print('\n ===========================================: ')
    if verbose: print(f"{num_tokens_from_messages(messages, ll_model)} tokens used for the question")

    completion = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo-0613",
        model=ll_model,
        messages=messages,
        temperature=temp
    )

    if verbose: print('\n ===========================================: ')
    if verbose: print(f'{completion["usage"]["total_tokens"]} total tokens used (question-answer).')
    if verbose: print('\n ===========================================: ')
    answer = insert_newlines(completion.choices[0].message.content)
    return answer

def answer_user_question(system_doc: str, knowledge_base_url: str, user_question: str) -> str:

    system_doc_text = load_document_text(system_doc)
    knowledge_base_text = load_document_text(knowledge_base_url)

    # Создаем индексы поиска
    knowledge_base_index = create_search_index(knowledge_base_text)

    # Добавляем явное разделение между историей диалога и текущим вопросом
    input_text = user_question

    # Извлечение наиболее похожих отрезков текста из базы знаний и получение ответа модели
    answer_text = answer_index(system_doc_text, input_text, knowledge_base_index, temp=temperature, verbose=verbose)

    return answer_text
# temperature=0.5
# verbose=1
