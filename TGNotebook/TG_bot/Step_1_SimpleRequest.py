import os
import openai
from dotenv import load_dotenv

# Loading values from .env file
load_dotenv()
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

# LLM: gpt-3.5-turbo-0613, gpt-3.5-turbo-0301, gpt-3.5-turbo-16k, gpt-3.5-turbo
LL_MODEL = "gpt-3.5-turbo-0613"
print(f'LL_MODEL = {LL_MODEL}')

# Interact with the OpenAI API
result = openai.ChatCompletion.create(
  model=LL_MODEL,
  messages=[
        {"role": "system", "content": "You are a diligent assistant."},
        {"role": "user", "content": "who won the f1 championship in 2021?"}
    ]
)

print(result)  # query result
message = result['choices'][0]['message']['content']
print(f'message={message}')