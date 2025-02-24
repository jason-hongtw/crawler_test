from chatgpt_sample import chat_with_gpt
from datetime import date
import json

standard_format = {
    "出發站": "出發站名",
    "到達站": "到達站名",
    "出發日期": "YYYY/MM/DD",
    "出發時辰": "H:S"
}

today = date.today().strftime("%Y/%m/%d")  # 取得今天日期


def ask_booking_information():
    print("Ask booking information")

    user_response = input(
        "請輸入你的高鐵訂位資訊，包含：出發站、到達站、出發日期、出發時分: ")
    system_prompt = f"""
    我想要從回話取得訂票資訊，包含：出發站、到達站、出發日期、出發時分。
    今天是 {today}，請把資料整理成python dictionary格式，例如：{standard_format}，
    不知道就填空字串，且回傳不包含其他內容。
    """
    booking_info = chat_with_gpt(user_response, system_prompt)
    return json.loads(booking_info.replace("'", "\""))


def ask_missing_information(booking_info):  # Slot filling
    print("Ask missing information")
    missing_slots = [key for key, value in booking_info.items() if not value]
    if not missing_slots:
        print("All slots are filled")
        return booking_info
    else:
        user_response = input(
            f"請補充你的高鐵訂位資訊，包含：{', '.join(missing_slots)}: ")

        system_prompt = f"""
        我想要從回話取得訂票資訊，包含：{', '.join(missing_slots)}。
        並與 {booking_info} 合併，今天是 {today} 。
        請把資料整理成python dictionary格式，例如：{standard_format}，
        不知道就填空字串，且回傳不包含其他內容。
        """

        booking_info = chat_with_gpt(user_response, system_prompt)
        return json.loads(booking_info.replace("'", "\""))


def convert_date_to_thsr_format(booking_info):
    map_number_to_chinese_word = {
        "01": "一月", "02": "二月", "03": "三月", "04": "四月",
        "05": "五月", "06": "六月", "07": "七月", "08": "八月",
        "09": "九月", "10": "十月", "11": "十一月", "12": "十二月"
    }
    Year, Month, Day = booking_info['出發日期'].split('/')
    booking_info['出發日期'] = f"{map_number_to_chinese_word[Month]} {Day}, {Year}"
    print("格式轉換後......")
    print(booking_info)
    return booking_info


if __name__ == '__main__':
    # Step 1
    booking_info = ask_booking_information()

    # Step 2
    booking_info = ask_missing_information(booking_info)

    # Step 3：調整日期格式以便爬蟲使用, ex: '2025/02/25' -> '二月 25, 2025'
    booking_info = convert_date_to_thsr_format(booking_info)