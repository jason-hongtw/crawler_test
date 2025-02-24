# 啟用 Ngrok + webhook server 的流程

1. NGrok: 總機 (API Gateway 反向代理)
    * 申請帳號：可以使用Gmail or Github帳號申請
    * 下載Ngrok到任意方便處
    * 於Ngrok.exe處，CMD下加入憑證指令：
        > ./ngrok config add-authtoken <你的Ngrok憑證>

    * 啟用Ngrok，目標5000 port 
        > ./ngrok http 5000

    * 複製Forwarding URL

2. Flask App: 分機
    * > pip install flask line-bot-sdk
    * [範本使用Linebot SDK 範例程式碼](https://github.com/line/line-bot-sdk-python?tab=readme-ov-file#synopsis)
    * 運行Flask網頁應用程式
    * 後續可修改回應方式及對話流程

3. Line Server: 來賓
    * 移動到 Line Developer 後台，找到你的channel
    * 更改webhook server url 並測試，常見問題：
        * url or route 錯誤
        * access token or secret 填錯或變數名對不上
        * Ngrok or Flask 沒開好
        * 程式碼有其他語法錯誤
