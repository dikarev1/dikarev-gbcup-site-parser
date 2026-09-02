import hashlib
import os
from bs4 import BeautifulSoup
import requests

URL = "https://gymbreeze.ge/eng"  # Сайт GymBreeze[cite: 1]
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = "target_hash.txt"

def send_telegram_message(text):
  print(
      "DEBUG TOKEN:", TOKEN
  )  # Выведет токен в лог (или None, если он не подхватился)
  print("DEBUG CHAT_ID:", CHAT_ID)

  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text}
  try:
    response = requests.post(url, json=payload, timeout=10)
    print("Финальный URL:", url)
    print("Ответ Telegram:", response.text)
  except Exception as e:
    print(f"Ошибка отправки: {e}")

def check_site():
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # 🎯 УКАЗЫВАЕМ ТОЧЕЧНЫЙ БЛОК ДЛЯ ОТСЛЕЖИВАНИЯ
    # Пример: ищем блок, где находятся групповые занятия и турниры
    # (замените селектор на актуальный для вашей страницы класс или тег)
    target_element = soup.find(
        "div", class_="schedule-section"
    )  # замените под себя

    if not target_element:
      # Запасной вариант, если класс не найден, берем весь body,
      # но лучше всегда опираться на конкретный контейнер
      target_element = soup.body

    # Извлекаем текст только из этого блока и очищаем от лишних пробелов
    content = target_element.get_text(strip=True)

    # Считаем хэш целевого контента
    current_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

    # Сверяем с прошлым состоянием
    previous_hash = ""
    if os.path.exists(STATE_FILE):
      with open(STATE_FILE, "r") as f:
        previous_hash = f.read().strip()

    if current_hash != previous_hash:
      send_telegram_message(
          "🔔 На сайте обновился целевой раздел (расписание/турниры)!"
      )
      # Сохраняем новый хэш
      with open(STATE_FILE, "w") as f:
        f.write(current_hash)

  except Exception as e:
    print(f"Ошибка: {e}")


if __name__ == "__main__":
  check_site()
