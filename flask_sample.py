from flask import Flask
from chatgpt_sample import chat_with_gpt

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/home/<user_message>")
def hello_home(user_message):
    chatgpt_response = chat_with_gpt(
        system_prompt="你是一個後端管理員，你現在正在客戶端被呼叫",
        user_message=user_message
    )
    return chatgpt_response

#if use "python xxx.py" to run this file
if __name__ == "__main__":
    app.run(debug=True)