import hashlib
import os
from bs4 import BeautifulSoup
import requests

URL = "https://gymbreeze.ge/eng"
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
STATE_FILE = "target_hash.txt"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram: сообщение отправлено успешно.")
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


def check_site():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Отслеживаем весь видимый текст страницы, а не отдельный блок.
        content = soup.get_text(" ", strip=True)
        current_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

        previous_hash = ""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                previous_hash = f.read().strip()

        if current_hash != previous_hash:
            print("Обнаружены изменения на сайте! Отправляем уведомление...")
            message = (
                "🔔 <b>На сайте GymBreeze обнаружены изменения!</b>\n\n"
                "Возможно, открылась регистрация на новый турнир.\n"
                f"🌐 <a href=\"{URL}\">Открыть GymBreeze</a>"
            )
            send_telegram_message(message)

            with open(STATE_FILE, "w") as f:
                f.write(current_hash)
        else:
            print("Изменений на сайте нет. Файл состояния не трогаем.")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_site()
