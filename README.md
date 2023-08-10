# Creating Telegram Bots with ChatGPT:

## Integration of Telegram bot and ChatGPT

### Step 1: Simple Request
Step_1_SimpleRequest.py

![ChatCompletionsAPI_01.png](TGNotebook%2FDocs%2FChatCompletionsAPI_01.png)

See: https://platform.openai.com/docs/guides/gpt/chat-completions-api

### Step 2: Knowledge base
Step_2_KnowledgeBase.py
#### Here is an example for an Anticafe type establishment:

![AtticExample_01.png](TGNotebook%2FDocs%2FAtticExample_01.png)

### Step 3: TG bot and all together
Step_3_TgBot.py

#### How it works:
![](TGNotebook/Docs/IntegrationTG-botChatGPT_03_en.png)




### Structure of the .env file:
TOKEN = '???'   # TG bot token

API_KEY = '???' # Open AI API Key

### Links to openai documentation:

Chat Completions API: https://platform.openai.com/docs/guides/gpt/chat-completions-api

Chat completions response format: https://platform.openai.com/docs/guides/gpt/chat-completions-response-format

### Links to FAISS documentation:

https://python.langchain.com/docs/integrations/vectorstores/faiss

https://faiss.ai/

### Links to LangChain documentation:

https://python.langchain.com/docs/get_started/introduction.html



### Token Limit in GPT-3.5
see https://www.scriptbyai.com/token-limit-openai-chatgpt/ 

| Model| Max Tokens    |
| :-----: | :---: | 
| gpt-3.5-turbo| 4086 | 
| gpt-3.5-turbo-0613| 4086 |
| gpt-3.5-turbo-16k| 16384 |