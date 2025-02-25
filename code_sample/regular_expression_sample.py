import re
import json


def extract_dict_from_string(input_string):
    # 定義正則表達式來匹配字典內容
    pattern = r"\{\s*'[^']*':\s*'[^']*'(?:,\s*'[^']*':\s*'[^']*')*\s*\}"
    match = re.search(pattern, input_string)

    if match:
        dict_string = match.group(0)
        # 將單引號替換為雙引號以便於 json.loads 解析
        dict_string = dict_string.replace("'", "\"")
        return json.loads(dict_string)
    else:
        return None


# 測試範例
# input_string = "這是一個包含字典的字串：{'出發站': '台北', '到達站': '高雄', '出發日期': '2025/02/25', '出發時辰': '10:00'}"
input_string = """
```python
{
    '出發站': '台北',
    '到達站': '台南',
    '出發日期': '2025/02/25',
    '出發時辰': '10:00'
}
```
"""

extracted_dict = extract_dict_from_string(input_string)
print(extracted_dict)
