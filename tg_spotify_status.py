import asyncio
import os
import time

from dotenv import load_dotenv
from telethon import TelegramClient, functions
import spotipy
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()


TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# Название локального файла-сессии Telegram
TELEGRAM_SESSION_NAME = "tg_session"

# Период опроса Spotify (секунды)
POLL_INTERVAL = 20


def get_spotify_client() -> spotipy.Spotify:
    """
    Создаёт клиент Spotify с правами на чтение текущего трека.
    При первом запуске откроет браузер для авторизации.
    """
    scope = "user-read-currently-playing"
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope,
        cache_path=".spotify_cache",
        open_browser=True,
        show_dialog=False,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def format_track_status(current_track: dict | None) -> str | None:
    """
    Преобразует ответ Spotify в строку для статуса Telegram.
    Если музыка не играет — возвращает None.
    """
    if not current_track:
        return None

    item = current_track.get("item")
    is_playing = current_track.get("is_playing", False)

    if not item or not is_playing:
        return None

    name = item.get("name")
    artists = item.get("artists") or []
    artists_names = ", ".join(a.get("name", "") for a in artists if a.get("name"))

    if not name:
        return None

    if artists_names:
        text = f"🎧 {artists_names} — {name}"
    else:
        text = f"🎧 {name}"

    # Ограничение Telegram на длину about ~70 символов
    return text[:70]


async def update_telegram_about(client: TelegramClient, text: str) -> None:
    """
    Меняет строку «О себе» в Telegram.
    """
    await client(functions.account.UpdateProfileRequest(about=text))


async def run():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        raise RuntimeError("Не заданы TELEGRAM_API_ID / TELEGRAM_API_HASH в .env")

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise RuntimeError("Не заданы SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET в .env")

    client = TelegramClient(TELEGRAM_SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

    # Первый запуск: попросит код подтверждения из Telegram
    await client.start()

    spotify = get_spotify_client()

    last_status: str | None = None

    print("Скрипт запущен. Нажмите Ctrl+C для остановки.")

    try:
        while True:
            try:
                current_track = spotify.current_user_playing_track()
                status_text = format_track_status(current_track)

                if status_text != last_status:
                    if status_text:
                        await update_telegram_about(client, status_text)
                        print(f"Обновлён статус: {status_text}")
                    else:
                        # Если ничего не играет — можете поменять текст по вкусу
                        default_about = "Не слушаю музыку"
                        await update_telegram_about(client, default_about)
                        print("Музыка не играет, установлен дефолтный статус.")

                    last_status = status_text

            except Exception as e:
                print(f"Ошибка при обновлении статуса: {e}")

            time.sleep(POLL_INTERVAL)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run())

