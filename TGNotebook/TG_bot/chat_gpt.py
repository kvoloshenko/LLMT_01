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

#api_key = getpass('Введите ваш ключ API:')
# возьмем переменные окружения из .env
load_dotenv()
# загружаем значеняи из файла .env
api_key = os.environ.get("API_KEY")
verbose = os.environ.get("VERBOSE")
print(f'verbose={verbose}')
temperature = float(os.environ.get("TEMPERATURE"))
print(f'temperature={temperature}')

openai.api_key = api_key
def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text

def create_search_index(text: str) -> Chroma:
    return create_embedding(text)


def create_embedding(data):
    def num_tokens_from_string(string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    source_chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=1024, chunk_overlap=0)

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
      model="gpt-3.5-gpt-3.5-turbo-0613",
      messages=messages,
      temperature=temp
      )

    return completion.choices[0].message.content

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0613":
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":

                    num_tokens += -1
        num_tokens += 2
        return num_tokens
    else:
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
    docs = search_index.similarity_search(topic, k=5)
    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)

    messages = [
        {"role": "system", "content": system + f"{message_content}"},
        {"role": "user", "content": topic}
    ]

    if verbose: print('\n ===========================================: ')
    if verbose: print(f"{num_tokens_from_messages(messages, 'gpt-3.5-turbo-0613')} tokens used for the question")

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
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