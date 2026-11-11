#!/usr/bin/env python3
import os
import httpx

token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

photo_path = "production/scene2_contact_sheet.jpg"
video_path = "production/scene2_redesign_preview.mp4"

if not token or not chat_id:\n    raise SystemExit("Telegram не настроен: используйте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")\n\nif os.path.exists(photo_path):
    with open(photo_path, "rb") as f:
        r1 = httpx.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={
                "chat_id": chat_id,
                "caption": "🎬 <b>Раскадровка пересобранной Сцены 2 (00:27–00:52)</b>\n• Жесткая опора грунта и физика падения плит\n• Анатомический риг персонажей (колени, плечи, помощь)\n• Рассветный контурный свет (Rim Light)",
                "parse_mode": "HTML"
            },
            files={"photo": ("contact_sheet.jpg", f, "image/jpeg")},
            timeout=60
        )
        print("Photo TG:", r1.status_code)

if os.path.exists(video_path):
    with open(video_path, "rb") as f:
        r2 = httpx.post(
            f"https://api.telegram.org/bot{token}/sendVideo",
            data={
                "chat_id": chat_id,
                "caption": "🔥 <b>Превью пересобранной Сцены 2 (00:27–00:52)</b>\n⏱ 25 сек | 1080p 30fps | Вариант диктора B (-16.4 LUFS)\n🌐 Онлайн: https://signals-sacramento-enquiry-looks.trycloudflare.com/scene2_preview.mp4",
                "parse_mode": "HTML"
            },
            files={"video": ("scene2_preview.mp4", f, "video/mp4")},
            timeout=120
        )
        print("Video TG:", r2.status_code)
