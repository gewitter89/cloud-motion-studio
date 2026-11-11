# Tasks: Автономная фабрика Shorts/Reels/TikTok

## Dependency Graph
```
TSK-001 (Config & Topics) ──→ TSK-002 (Vertical Audio Pipeline) ──┐
                                                                 ├──→ TSK-004 (Master Mux & Audit) ──→ TSK-005 (VPS & Telegram)
TSK-003 (Vertical 9:16 Render Engine) ───────────────────────────┘
```

---

### [x] TSK-001: Создать реестр тем и контентных скриптов (`tools/shorts_topics.py`)
- **Requirement:** FR-1, FR-2
- **Deliverables:** Структура данных с текстом озвучки, разбивкой субтитров, хук-заголовком, безопасными зонами и хэштегами.
- **Acceptance:** Модуль импортируется, валидирует тайминги и содержит пилотный сценарий про Вояджер.

---

### [ ] TSK-002: Разработать вертикальный звуковой движок (`tools/shorts_audio_engine.py`)
- **Requirement:** FR-3
- **Deliverables:** Синтез речи Edge-TTS + процедурный суб-бас дроп + атмосферный дрон + EBU R128 (-14 LUFS) мастеринг.
- **Acceptance:** На выходе чистый WAV/MP3 файл с точной длительностью ~36с и нормализацией -14 LUFS.

---

### [ ] TSK-003: Разработать рендер-движок 9:16 (`tools/shorts_render_engine.py`)
- **Requirement:** FR-1, FR-2, FR-4
- **Deliverables:** Генератор кадров 1080×1920: анимированное звездное поле, центральный анимированный объект, кинетические плашки субтитров.
- **Acceptance:** Рендерит 30 FPS без задержек и артефактов через pipe в FFmpeg.

---

### [ ] TSK-004: Сборка и локальная валидация пилотного шортса (`pilot_shorts_36s.mp4`)
- **Requirement:** NFR-1, NFR-2
- **Deliverables:** Полный ролик с видео и звуком + контактный лист кадров аудита (1080x1920).
- **Acceptance:** Длина ~36 секунд, звук идеально синхронен с субтитрами, безопасные зоны соблюдены.

---

### [ ] TSK-005: Развертывание и автономный запуск на Cloud VPS + Telegram бот
- **Requirement:** FR-5, NFR-3
- **Deliverables:** Синхронизация кода на VPS `169.58.30.140`, генерация, размещение на CDN и доставка в `@prostov_shrink_bot`.
- **Acceptance:** Видео воспроизводится в Telegram и доступно по Cloudflare URL.
