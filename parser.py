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
    "6358885700",
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


# ================================================================
# ODYSSEY / TKT.GE MONITOR
# Отдельный блок, чтобы его было легко удалить позже.
# Следит за появлением среды 9 сентября на странице фильма.
# Уведомление отправляется ТОЛЬКО основному пользователю из Secret.
# ================================================================
ODYSSEY_URL = "https://tkt.ge/en/movies/441/the-odyssey"
ODYSSEY_STATE_FILE = "odyssey_wed_notified.txt"
ODYSSEY_TARGET_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def check_odyssey_wednesday():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(ODYSSEY_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Ищем именно дату 9 + Wed внутри одного календарного элемента.
        # Это не просто поиск слова "Wed", чтобы не поймать другие даты.
        wednesday_found = False

        for element in soup.find_all(True):
            text = " ".join(element.stripped_strings)
            if text == "9 Wed":
                wednesday_found = True
                break

        if not wednesday_found:
            print("Odyssey: среды 9 сентября пока нет.")
            return

        if os.path.exists(ODYSSEY_STATE_FILE):
            print("Odyssey: уведомление о среде 9 сентября уже отправлялось.")
            return

        message = "на фильм Одиссея на среду 9 сентября появились билеты"

        if not ODYSSEY_TARGET_CHAT_ID:
            print("Odyssey: TELEGRAM_CHAT_ID не задан, уведомление не отправлено.")
            return

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": ODYSSEY_TARGET_CHAT_ID,
            "text": message,
        }

        telegram_response = requests.post(url, json=payload, timeout=10)
        telegram_response.raise_for_status()

        with open(ODYSSEY_STATE_FILE, "w") as f:
            f.write("notified")

        print("Odyssey: уведомление отправлено основному пользователю.")

    except Exception as e:
        print(f"Odyssey: ошибка: {e}")


# ================================================================
# END ODYSSEY / TKT.GE MONITOR
# ================================================================


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
    check_odyssey_wednesday()
