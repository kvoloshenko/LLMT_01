import os
import openai
from dotenv import load_dotenv
import tiktoken
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader

# Loading values from .env file
load_dotenv()
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

CHUNK_SIZE = 1024                 # Количество токинов в  чанке
NUMBER_RELEVANT_CHUNKS = 5        # Количество релевантных чанков

loader = TextLoader("Docs/База знаний УИИ.txt", encoding='utf8')
documents = loader.load()
text_splitter = CharacterTextSplitter(separator="\n", chunk_size=CHUNK_SIZE, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# всего получилось чанков:
print(f'len(docs)={len(docs)}')

# первый чанк
print(f'первый чанк = {docs[0]}')
page_content = docs[0].page_content
# длина первого чанка
print(f'длина первого чанка = {len(page_content)}')

print(f'metadata до = {docs[0].metadata}')
# Устанавливаем метаданные для первого чанка
docs[0].metadata["teg"] = "Описание УИИ"

# Так перезапишет
# docs[0].metadata = {"teg": "Описание УИИ"}

# выводим на печать обновленные метаданные чанка
print(f'metadata псле = {docs[0].metadata}')

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

# Создадим индексную базу из разделенных фрагментов текста
# https://python.langchain.com/docs/integrations/vectorstores/faiss
db = FAISS.from_documents(docs, embeddings)

# Поиск текста по схожести
# similarity_search
print('similarity_search')
query = "нужно ли знать математику?"
docs = db.similarity_search(query, k=NUMBER_RELEVANT_CHUNKS)

i=1
for item in docs:
    print(f'{i} item.page_content={item.page_content}\n\n')
    i += 1

# similarity_search_with_score
print('similarity_search_with_score')
docs_and_scores = db.similarity_search_with_score(query, k=NUMBER_RELEVANT_CHUNKS)

# print (type(docs_and_scores))
# print (docs_and_scores)
i=1
for doc in docs_and_scores:
    print(f'{i}')
    for item in doc:
        print (item)

    i += 1
    print(f'\n')

# Нужно проверять условие изменения файла Базы знаний.
# db.save_local("/content/drive/My Drive/faiss_index")
db.save_local("DB/faiss_index")
print('Db saved')

#Load file.
new_db = db.load_local('DB/faiss_index', embeddings)
print('Db loaded')

docs = new_db.similarity_search(query, k=NUMBER_RELEVANT_CHUNKS)

i=1
for item in docs:
    print(f'{i} item.page_content={item.page_content}\n\n')
    i += 1
