import requests


def sendMessage():
    url = "https://api.telegram.org/file/bot5447202255:AAG6Qu5Pb8ve76aAp0sCsQHIGassQWTMnJA/sendMessage"

    for i in range(2):
        data = {
            "chat_id": 779890968,
            "text": f"{i} - message",
            "parse_mode": "HTML",
        }
        requests.post(url, data=data)


if __name__ == '__main__':
    sendMessage()
