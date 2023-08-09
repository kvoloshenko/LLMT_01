import os
import openai
from dotenv import load_dotenv
import tiktoken
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader

CHUNK_SIZE = 1024                 # Количество токинов в  чанке

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
