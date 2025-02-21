from flask import Flask, render_template
from chatgpt_sample import chat_with_gpt
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test/<int:user_id>/")
def hello_user(user_id):
    # show the post with the given id, the id is an integer
    return f'<p>Hello USER-{escape(user_id)}, World!</p>'

@app.route("/path/<path:subpath>/")
def hello_path(subpath):
    # show the subpath after /path/
    return f'<p>Hello PATH-{escape(subpath)}, World!</p>'

@app.route("/home/<user_message>/")
def hello_home(user_message):
    chatgpt_response = chat_with_gpt(
        system_prompt="你是一個後端管理員，你現在正在客戶端被呼叫",
        user_message=user_message
    )
    return chatgpt_response

@app.route("/sample/")
def show_html_sample():
    return render_template(
            "sample.html",
            name="Chanel",
            numbers=[1, 2, 3, 4, 5],
            pairs=[('A', 1), ('B', 2), ('C', 3)],
            dict_data={'A': 1, 'B': 2, 'C': 3}
        )

#if use "python xxx.py" to run this file
if __name__ == "__main__":
    app.run(debug=True)