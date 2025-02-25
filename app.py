from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import os
from datetime import date

# self defined function
from booking_info_extraction_flow import extract_dict_from_string
from chatgpt_sample import chat_with_gpt

app = Flask(__name__)

#os.getenv is used to get the environment variable
configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# User Data
# {
#     'user_id_a': {
#         'intent': '訂高鐵',
#         '出發站': '台北',
#         '到達站': '台南',
#         '出發日期': '2022/10/10',
#         '出發時辰': '10:00'
#     },
#     'user_id_b': {
#         'intent': '訂高鐵',
#         '到達站': '高雄',
#         '出發日期': '2022/11/11',
#     },
#     'user_id_c': {}
# }

user_data = {}

standard_format = {
    "出發站": "出發站名",
    "到達站": "到達站名",
    "出發日期": "YYYY/MM/DD",
    "出發時分": "H:S"
}

today = date.today().strftime("%Y/%m/%d")  # 取得今天日期

def update_user_data(user_id, **info_dict):
    if user_id not in user_data:
        user_data[user_id] = info_dict
    else:
        user_data[user_id].update(info_dict)

def get_user_data(user_id):
    return user_data.get(user_id, {})

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    user_data = get_user_data(user_id)
    necessary_slots = ['出發地', '到達站', '出發日期', '出發時分']

    #.get("") is used to get the value of the key, if the key does not exist, it will return the default value
    if user_data.get('intent',"") != '訂高鐵' and user_message == "訂高鐵":
        update_user_data(event.source.user_id, intent="訂高鐵") # 更新意圖為: 訂高鐵
        # 問第一個問題:"請輸入你的高鐵訂位資訊......"
        bot_response =  "請輸入你的高鐵訂位資訊，包含：出發站、到達站、出發日期、出發時分: "

    elif user_data.get('intent') == '訂高鐵': # 意圖判斷
        #上一輪的資訊狀態
        unfilled_slots = [
            key for key in necessary_slots if key not in user_data] # 未填寫的欄位

        #使用者訊息擷取
        system_prompt = f"""
        我想要從回話取得訂票資訊，包含：{"、".join(unfilled_slots)}。
        今天是 {today}，請把資料整理成python dictionary格式，例如：{standard_format}，
        不知道就填空字串，且回傳不包含其他內容。
        """

        booking_info = chat_with_gpt(user_message, system_prompt)
        booking_info = extract_dict_from_string(booking_info)
        update_user_data(user_id, **booking_info) # 更新使用者資訊

        # 判斷已填寫的資訊
        user_data = get_user_data(event.source.user_id) # 重新讀取一次新的使用者資訊
        filled_slots = [
            key for key in necessary_slots if key in user_data] # 已填寫的欄位
        unfilled_slots = [
            key for key in necessary_slots if key not in user_data] # 未填寫的欄位

        app.logger.info(f"已填寫欄位: {filled_slots}")
        app.logger.info(f"未填寫欄位: {unfilled_slots}")

        if len(unfilled_slots) == 0:
            # 依照訊息送出訂位，直到選車為止
            pass
        else:
            # 部分欄位已填寫
            # 詢問未填寫的欄位
            pass


    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    #  這邊是你要回覆給使用者的內容
                    TextMessage(text=chat_with_gpt(
                        system_prompt = "You are Elon Musk, answering questions as Elon Musk.",
                        user_message = event.message.text
                        )
                    )
                ]
            )
        )


if __name__ == "__main__":
    app.run()