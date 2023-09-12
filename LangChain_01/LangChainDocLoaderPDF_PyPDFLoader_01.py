import os
import openai
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader

# Loading values from .env file
load_dotenv()
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

# loader = PyPDFLoader("VectorDBAnalysis.pdf")
loader = PyPDFLoader("Jollibee-Dine-In-Menu.pdf")
pages = loader.load_and_split()

print(f'type={type(pages)}, pages={pages}')

