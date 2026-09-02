import os
import requests

print("--- НАЧАЛО ДЕБАГА ---")
token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Тип token: {type(token)}")
print(f"Значение token (длина): {len(token) if token else 0}")
print(f"Значение token (первые 4 символа): {token[:4] if token else 'ПУСТО'}")
print(f"CHAT_ID присутствует: {bool(chat_id)}")

if token and chat_id:
  url = f"https://api.telegram.org/bot{token}/getMe"
  res = requests.get(url)
  print(f"Ответ от getMe: {res.text}")
else:
  print("КРИТИЧЕСКАЯ ОШИБКА: Переменные окружения не дошли до Python!")
print("--- КОНЕЦ ДЕБАГА ---")
