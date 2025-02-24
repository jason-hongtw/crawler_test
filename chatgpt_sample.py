from openai import OpenAI
from pprint import pprint
client = OpenAI()



def chat_with_gpt(
    user_message,
    system_prompt,
    completion_model="gpt-4o"):
    completion = client.chat.completions.create(
    model = completion_model,
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    )
    # pprint(completion)
    #print(completion.choices[0].message.content)
    return completion.choices[0].message.content

# 當這個檔案被執行時，以下的程式碼才會被執行,__name__是一個變數，當這個檔案被執行時，__name__會被設定為"__main__"
if __name__ == "__main__":
    chat_with_gpt(
        system_prompt = "你是一個飲料店店員，協助點餐",
        user_message ="我要一個珍珠奶茶"
    )