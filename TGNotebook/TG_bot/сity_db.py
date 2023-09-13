import codecs
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

DB_DIR_NAME = os.environ.get("DB_DIR_NAME") # каталог для db
print(f'DB_DIR_NAME = {DB_DIR_NAME}')


def load_text(file_path):
    # Открытие файла для чтения
    with codecs.open(file_path, "r", encoding="utf-8", errors="ignore") as input_file:
        # Чтение содержимого файла
        content = input_file.read()
    return content

def create_db(database, ba):
    db_file_name = DB_DIR_NAME + 'db_file_' + ba

    source_chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=CHUNK_SIZE, chunk_overlap=0)

    for chunk in splitter.split_text(database):
        source_chunks.append(Document(page_content=chunk, metadata={}))

    chunk_num = len(source_chunks)
    print(f'chunk_num={chunk_num}')

    # Инициализирум модель эмбеддингов
    embeddings = OpenAIEmbeddings()

    try:
        db = FAISS.from_documents(source_chunks, embeddings) # Создадим индексную базу из разделенных фрагментов текста
        db.save_local(db_file_name)
    except Exception as e: # обработка ошибок openai.error.RateLimitError
        print(f'!!! External error: {str(e)}')

    for chunk in source_chunks:  # Поиск слишком больших чанков
        if len(chunk.page_content) > CHUNK_SIZE:
            print(f'*** Слишком большой кусок! ***')
            print(f'chunk_len ={len(chunk.page_content)}')
            print(f'content ={chunk.page_content}')
    return db, db_file_name, chunk_num



if __name__ == '__main__':
    # База знаний, которая будет подаваться в LangChain
    database = load_text('C:/_Proj/LLMT_01/TGNotebook/TG_bot/CityBuilder/gradkod_02.txt')
    ba = 'CityBuilder'
    db_file_name = 'db/db_file_ars'
    if not os.path.exists(db_file_name):
        print("Каталог не существует - создаем новую Базу Знаний")
        db, db_file_name, chunk_num = create_db(database, ba)
        print(f'db_file_name={db_file_name}, chunk_num={chunk_num}')
