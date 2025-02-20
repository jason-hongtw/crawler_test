from openai import OpenAI
from pprint import pprint
client = OpenAI()



def chat_with_gpt(user_message, system_prompt):
    completion = client.chat.completions.create(
    model="gpt-4o-mini", # replace any model you want
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
    print(completion.choices[0].message.content)

if __name__ == "__main__":
    chat_with_gpt(
        system_prompt = "你是一個飲料店店員，協助點餐",
        user_message ="我要一個珍珠奶茶"
    )