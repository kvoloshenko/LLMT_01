# https://www.sbert.net/examples/applications/retrieve_rerank/README.html#pre-trained-bi-encoders-retrieval
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer

load_dotenv()
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY
database = ''' Это заглушка на содержание Базы Знаний'''
source_chunks = []
splitter = CharacterTextSplitter(separator="\n", chunk_size=512, chunk_overlap=0)
for chunk in splitter.split_text(database):
    source_chunks.append(Document(page_content=chunk, metadata={}))
embeddings = OpenAIEmbeddings()

# https://www.sbert.net/docs/pretrained-models/msmarco-v3.html
model = SentenceTransformer('msmarco-MiniLM-L-6-v3')


db = FAISS.from_documents(source_chunks, embeddings)