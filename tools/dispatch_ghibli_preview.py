#!/usr/bin/env python3
import os
import httpx

token = "8976290222:AAGGiziDbhsKPbapeWLuSDBU7OCaDon0B9A"
chat_id = "8531839081"

photo_path = "production/scene2_ghibli_contact_sheet.jpg"
video_path = "production/scene2_ghibli_preview.mp4"

if os.path.exists(photo_path):
    with open(photo_path, "rb") as f:
        r1 = httpx.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={
                "chat_id": chat_id,
                "caption": "🎬 <b>Новая раскадровка: Атмосферный 2.5D стиль (Ghibli / 4K Supersampling)</b>\n• Настоящая ночная воздушная перспектива (индиго-фиолетовая глубина, луна, дымка)\n• Фактурный бетон стены с фасками и балками\n• Органические векторные силуэты персонажей (пальто на ветру, ботинки, помощь)\n• Золотой рассвет сквозь пролом",
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
                "caption": "🔥 <b>Новый ролик Сцены 2 (00:27–00:52): Чистый русский диктор + 2.5D Арт</b>\n⏱ 24.6 сек | 1080p 30fps | -16.0 LUFS\n🌐 Смотреть онлайн: https://signals-sacramento-enquiry-looks.trycloudflare.com/scene2_ghibli_preview.mp4",
                "parse_mode": "HTML"
            },
            files={"video": ("scene2_ghibli_preview.mp4", f, "video/mp4")},
            timeout=120
        )
        print("Video TG:", r2.status_code)
