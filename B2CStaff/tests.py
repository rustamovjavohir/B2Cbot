import requests

img_url = "https://api.telegram.org/file/bot5418412192:AAGDKxap_t-_EH6E87VGlbMA4zPI8Q7VojM/photos/file_8.jpg"

response = requests.get(img_url)

print(response.content)
