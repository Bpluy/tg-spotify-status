## Telegram Spotify Status

Скрипт на Python, который раз в несколько секунд берёт текущий трек из Spotify и ставит его в поле «О себе» в Telegram.

### 1. Установка

```bash
pip install -r requirements.txt
```

Создайте файл `.env` рядом со скриптом, взяв за основу `.env.example`, и заполните:

- `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` — из `https://my.telegram.org` → *API development tools*.
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` — из Spotify Developer Dashboard.
- `SPOTIFY_REDIRECT_URI` — тот же, что указан в настройках Spotify‑приложения (по умолчанию `http://127.0.0.1:8888/callback`).

### 2. Запуск

```bash
python tg_spotify_status.py
```

При первом запуске:

- Скрипт откроет браузер для авторизации в Spotify.
- Telegram‑клиент попросит код подтверждения, который придёт в Telegram / по SMS.

После этого скрипт будет периодически:

- забирать текущий трек из Spotify;
- менять поле «О себе» в Telegram на `🎧 Исполнитель — Название трека`;
- если музыка не играет — ставить текст `Не слушаю музыку` (можно поменять в коде).

