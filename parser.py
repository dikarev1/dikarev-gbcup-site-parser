import hashlib
import os
from bs4 import BeautifulSoup
import requests

URL = "https://gymbreeze.ge/eng"
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Основной получатель хранится в GitHub Secret.
# Дополнительных получателей можно добавлять прямо сюда.
CHAT_IDS = [
    os.environ.get("TELEGRAM_CHAT_ID"),
    # "123456789",
    # "987654321",
]

STATE_FILE = "target_hash.txt"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    all_sent = True

    for chat_id in CHAT_IDS:
        if not chat_id:
            continue

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"Telegram: сообщение отправлено пользователю {chat_id}.")
        except Exception as e:
            print(f"Ошибка отправки пользователю {chat_id}: {e}")
            all_sent = False

    return all_sent


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

            if send_telegram_message(message):
                with open(STATE_FILE, "w") as f:
                    f.write(current_hash)
                print("Hash обновлён после успешной отправки всем получателям.")
            else:
                print("Hash не обновляем, чтобы повторить уведомление на следующем запуске.")
        else:
            print("Изменений на сайте нет. Файл состояния не трогаем.")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    check_site()
