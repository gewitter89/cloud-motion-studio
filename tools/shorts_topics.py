"""
Registry of viral topics and scripts for Autonomous Shorts / Reels / TikTok Factory.
Format: 9:16 Vertical (1080x1920).
"""

SHORTS_TOPICS = {
    "voyager_golden_record": {
        "slug": "voyager_golden_record",
        "title": "ТАЙНА ЗОЛОТОГО ДИСКА",
        "headline_badge": "СЕКРЕТНЫЙ АРТЕФАКТ",
        "estimated_duration_sec": 36.0,
        "voice": "ru-RU-SvetlanaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "hashtags": ["#космос", "#наука", "#вояджер", "#тайнывселенной", "#факты", "#shorts", "#тикток"],
        "caption": (
            "🚀 На борту Вояджера летит золотой диск, который переживет всё человечество.\n\n"
            "На нем записаны звуки Земли, смех ребенка, музыка Баха и карта 14 пульсаров, "
            "ведущая прямо к нашей планете. Когда Солнце погаснет — этот диск останется "
            "единственным доказательством, что мы вообще существовали.\n\n"
            "Подпишись на канал, чтобы не пропустить тайны Вселенной! 🛸"
        ),
        "acts": [
            {
                "id": "hook",
                "text": "На борту Вояджера летит послание, которое переживет всё человечество.",
                "hero_mode": "voyager_flyby",
                "highlight_words": ["Вояджера", "человечество"],
                "sfx": "sub_bass_drop"
            },
            {
                "id": "record_macro",
                "text": "Это позолоченный фонографический диск. На нем записаны звуки Земли, шепот ветра, смех ребенка и музыка.",
                "hero_mode": "golden_record_macro",
                "highlight_words": ["золотой", "диск", "звуки", "Земли"],
                "sfx": "needle_crackle"
            },
            {
                "id": "pulsar_map",
                "text": "Но самое жуткое — карта четырнадцати пульсаров. Любая цивилизация вычислит точные координаты Земли.",
                "hero_mode": "pulsar_map_scan",
                "highlight_words": ["жуткое", "координаты", "Земли"],
                "sfx": "laser_ping"
            },
            {
                "id": "climax",
                "text": "Через миллиарды лет Солнце погаснет. Земля исчезнет. А этот диск останется вечным памятником людям.",
                "hero_mode": "pale_blue_dot_fade",
                "highlight_words": ["Солнце", "погаснет", "вечным", "памятником"],
                "sfx": "cinematic_swell"
            }
        ]
    }
}

def get_topic(slug="voyager_golden_record"):
    if slug not in SHORTS_TOPICS:
        raise ValueError(f"Topic '{slug}' not found. Available: {list(SHORTS_TOPICS.keys())}")
    return SHORTS_TOPICS[slug]

if __name__ == "__main__":
    t = get_topic()
    print(f"Loaded topic: {t['title']} ({len(t['acts'])} acts)")
    for act in t['acts']:
        print(f" - [{act['id']}]: {act['text']}")
