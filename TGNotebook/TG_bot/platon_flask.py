from flask import Flask, request, json
import platon_chat_gpt as chat_gpt

app = Flask(__name__)
@app.route('/chat', methods=['POST'])
def chat():
    data = json.loads(request.data)
    # print(f'{type(data)} data={data}')
    topic = data['topic']
    ba = data['ba']
    # print(f'{type(topic)} data={topic}')
    reply_text, num_tokens, messages, completion = chat_gpt.chat_question(topic, ba)
    # data['reply_text'] = reply_text
    data['num_tokens'] = num_tokens
    data['messages'] = messages
    data['completion'] = completion

    return data

@app.route('/create_db', methods=['POST'])
def create_db():
    data = json.loads(request.data)
    knowledge_base_url = data['knowledge_base_url']
    ba = data['ba']
    db, db_file_name = chat_gpt.create_db(knowledge_base_url, ba)
    data['db_file_name'] = db_file_name
    return data

if __name__ == "__main__":
    app.run()