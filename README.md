# Bot Factory with ChatGPT

## Предварительные действия:

1. Получить Open AI API_KEY

## Как это работает:
Данная реализация предназначена для создания инфраструктуры предоставления услуги chat-bot для клиентов платформы. Каждый клиент имеет один или более billing accounts (ba). У каждого ba свой экземпляр Базы знаний.

Рассматриваются следующие сценарии:

### 1. POST create_db(knowledge_base_url, ba)
где:
* ba - значение билиннг аккаунта, для которого выполняются действия
* knowledge_base_url - url к файлу с Базой знаний для концертного ba 

#### Описание сценария: 
Создать для ba свою векторную Базу Знаний на основании подготовленного файла. Сохранить векторную базу в файл.

![IntegrationTG-botChatGPT_04_ru_create_db.png](TGNotebook%2FDocs%2FIntegrationTG-botChatGPT_04_ru_create_db.png)


### 2. POST chat(topic, ba)
где:
* ba - значение билиннг аккаунта, для которого выполняются действия
* topic - текст вопроса от пользователя

#### Описание сценария: 
Получить запрос от ba, загрузить из файла векторную Базу Знаний. Найти релевантные чанки. Отправить данные в языковую модель ChatGPT, получить ответ от языковой модели.

![IntegrationTG-botChatGPT_04_ru_chat.png](TGNotebook%2FDocs%2FIntegrationTG-botChatGPT_04_ru_chat.png)

### Видео (3 минуты)
https://youtu.be/piCCkb1zIyw?si=EM-8EfVgZk1vnXNs

### Теория

#### Видео (8 минут) 
https://youtu.be/NkjkqsLCweQ

#### Презентация: 
https://docs.google.com/presentation/d/1bo9T6LvS1CXjmT60hfaM4pRDcblufdAG/edit?usp=sharing&ouid=104673724125492337414&rtpof=true&sd=true



### Структура файла .env
TOKEN = '???'   # TG bot token

API_KEY = '???' # Open AI API Key

SYSTEM_DOC_URL = '???'          # Prompt

KNOWLEDGE_BASE_URL = '????'     # Knowledge Base

DB_DIR_NAME = "db/"             # db dir name

TEMPERATURE = 1                 # Model temperature

NUMBER_RELEVANT_CHUNKS = 5      # Number of relevant chunks

CHUNK_SIZE = 1024               # Number of tokens in a chunk

LL_MODEL = "gpt-3.5-turbo-0613" # Model

TEXT_BEGINNING = ''             # Text at the beginning

TEXT_END = ''                   # Text at the end


### Token Limit in GPT-3.5
see https://www.scriptbyai.com/token-limit-openai-chatgpt/ 

| Model| Max Tokens    |
| :-----: | :---: | 
| gpt-3.5-turbo| 4086 | 
| gpt-3.5-turbo-0613| 4086 |
| gpt-3.5-turbo-16k| 16384 |

### Links to openai documentation:

Chat Completions API: https://platform.openai.com/docs/guides/gpt/chat-completions-api

Chat completions response format: https://platform.openai.com/docs/guides/gpt/chat-completions-response-format