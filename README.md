# LLMT_01
Python: LLM tools

# LLMT_01
LangChain: The sourse idea is here https://youtu.be/aywZrzNaKjs 

Colab notebooks:
* LLMT_01_001_en.ipynb
* LLMT_01_001_ru.ipynb

# Creating Telegram Bots with ChatGPT:

## Integration of Telegram bot and ChatGPT

### Here is an example for an Anticafe type establishment:

![AtticExample_01.png](TGNotebook%2FDocs%2FAtticExample_01.png)

### How it works:

![](TGNotebook/Docs/IntegrationTG-botChatGPT_02_en.png)


Video explanation in Russian see here:  https://youtu.be/8rKedN9tiuo

Colab notebook:
TGNotebook\TG_Bot_vccTest01_ChatGPT_02_ru_pablic.ipynb
 
Modules:
TGNotebook\TG_bot\
* chat_gpt.py - Module for OPEN API support;
* openlesson2_tgbot.py - Source Echo Bot;
* openlesson2_tgbot_gpt_01.py - Modified Echo Bot for a simple ChatGTP request;
* openlesson2_tgbot_gpt_02.py - Modified Echo Bot for requesting a pre-trained ChatGPT;

### Structure of the .env file:
TOKEN = '???'   # TG bot token

API_KEY = '???' # Open AI API Key

SYSTEM_DOC_URL = '???'          # Prompt

KNOWLEDGE_BASE_URL = '????'     # Knowledge Base

VERBOSE = 1                     # Display technical information

TEMPERATURE = 1                 # Model temperature

NUMBER_RELEVANT_CHUNKS = 5      # Number of relevant chunks

CHUNK_SIZE = 1024               # Number of tokens in a chunk

LL_MODEL = "gpt-3.5-turbo-0613" # Model

TEXT_BEGINNING = ''             # Text at the beginning

TEXT_END = ''                   # Text at the end

### Links to openai documentation:

Chat Completions API: https://platform.openai.com/docs/guides/gpt/chat-completions-api

Chat completions response format: https://platform.openai.com/docs/guides/gpt/chat-completions-response-format