import os


import openai
from dotenv import load_dotenv
from langchain.document_loaders import UnstructuredPDFLoader

# Loading values from .env file
load_dotenv()
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

# loader = UnstructuredPDFLoader("Jollibee-Dine-In-Menu.pdf")
loader = UnstructuredPDFLoader("VectorDBAnalysis.pdf")

data = loader.load()

print(f'type={type(data)}, data={data}')