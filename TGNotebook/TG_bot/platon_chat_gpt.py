import re
import requests
import os
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, timezone
import tiktoken
import chat_function_01 as cf

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
MESSAGES_S = '<messages>' + X_CDATA_S
MESSAGES_E = X_CDATA_E + '</messages>'
COMPLETION_S = '<completion>' + X_CDATA_S
COMPLETION_E = X_CDATA_E + '</completion>'


# Get the current date and time
current_datetime = datetime.now(tz=timezone(timedelta(hours=3)))

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

logfilename = "Logs/" + formatted_datetime + "_tgbot_gpt.xml"
csvfilename = "Logs/" + formatted_datetime + "_answers.csv"
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
print(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')
logging.info(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')

KNOWLEDGE_BASE_URL = os.environ.get("KNOWLEDGE_BASE_URL") # база знаний
print(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')
logging.info(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')

# Функции для работы с файлом
def write_to_file(file_data, file_name=csvfilename):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(file_data)

# Записывам в файл заголовок
write_to_file('question;answer')

def append_to_file(new_line, file_name=csvfilename):
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write('\n' + new_line)

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

# Функция создания индексной базы знаний
def create_index_db():
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

    return db

db = create_index_db()


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


# Запрос в ChatGPT с использованием функций
def answer_function(system, topic, index_db, temp=TEMPERATURE):

    # Поиск релевантных отрезков из базы знаний
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)

    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n#### Document excerpt №{i+1}####\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    logging.info(f'{MESSAGE_CONTENT_S}{message_content}{MESSAGE_CONTENT_E}')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Here is the document with information to respond to the client: {message_content}\n\n Here is the client's question: \n{topic}"}
    ]

    logging.info(f'{MESSAGES_S}{messages}{MESSAGES_E}')
    num_tokens = num_tokens_from_messages(messages, LL_MODEL)
    logging.info(f'{NUM_TOKENS_S}{num_tokens}{NUM_TOKENS_E}')
    print(f'num_tokens = {num_tokens}')

    try:
        completion = openai.ChatCompletion.create(
            model=LL_MODEL,
            messages=messages,
            temperature=temp,
            functions=cf.function_descriptions,   # Add function calling
            function_call="auto"                  # specify the function call
        )
    except Exception as e:  # обработка ошибок openai.error.RateLimitError
        print(f'!!! External error: {str(e)}')
        logging.error(f'!!! External error: {str(e)}')

    logging.info(f'{COMPLETION_S}{completion}{COMPLETION_E}')
    answer = completion.choices[0].message.content

    if completion.choices[0].finish_reason == "function_call":
        function_answer = completion.choices[0].message
        print(f'Сработала функция {function_answer.function_call.name} - нужно извлекать значения параметров функции')
        # Извлекаем параметры функции
        params = json.loads(function_answer.function_call.arguments)
        print(f'params={params}')
        # Используем вывод LLM для ручного вызова функции.
        function_name = 'cf.'+function_answer.function_call.name
        chosen_function = eval(function_name)
        functionResult = chosen_function(**params)
        print(functionResult)
        answer, completion = answer_2(system, topic, message_content, function_answer, functionResult)
    else:
        print(f'Функции не было')
        line_for_file = '"' + topic + '";"' + answer + '"'
        append_to_file(line_for_file)

    return answer, completion  # возвращает ответ

# Второй вызов ChatGPT для обработки результатов выполнения функции
def answer_2(system, topic, message_content, function_answer, functionResult, temp=TEMPERATURE):


    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Here is the document with information to respond to the client: {message_content}\n\n Here is the client's question: \n{topic}"},
        {"role": "function", "name": function_answer.function_call.name, "content": functionResult}
    ]

    completion = openai.ChatCompletion.create(
        model=LL_MODEL,
        messages=messages,
        temperature=temp,
        functions=cf.function_descriptions,   # Add function calling
        # function_call="auto"               # specify the function call
    )

    answer = completion.choices[0].message.content
    line_for_file = '"' + topic + '";"' + answer + '"'
    append_to_file(line_for_file)

    return answer, completion

def answer_user_question(topic):
    ans, completion = answer_function(system, topic, db)  # получите ответ модели

    return ans

def do_test(topic):
    ans = answer_user_question(topic)
    return ans

if __name__ == '__main__':
    # topic = 'Привет! Ты кто?'
    # topic = 'Нас 20 человек, мы студенты, хотим прийти на четыре часа, посчитайте, плиз, сколько будет стоить?'
    topic = 'Нас 20 человек, хотим прийти на четыре часа, посчитайте, плиз, сколько будет стоить?'
    print(f'topic={topic}')
    response = do_test(topic)
    print(f'response={response}')



