#!/usr/bin/env bash
# run_cloud_vps_voyager.sh
# Autonomous detached render script for Cloud VPS (169.58.30.140).
# Runs independently of local machine power.

set -e

WORK_DIR="/opt/cloud-motion-studio"
LOG_FILE="/var/log/voyager_render.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=========================================================="
echo "STARTING AUTONOMOUS VOYAGER 120s RENDER: $(date)"
echo "=========================================================="

if [ ! -d "$WORK_DIR" ]; then
    git clone https://github.com/gewitter89/cloud-motion-studio.git "$WORK_DIR"
fi

cd "$WORK_DIR"
git fetch origin main
git reset --hard origin/main

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install edge-tts numpy pillow opencv-python-headless requests

echo "1. Generating Master Audio & Soundscape..."
python tools/generate_voyager_audio.py

echo "2. Rendering 120s Film (3600 frames)..."
python tools/render_voyager_120s_film.py

echo "3. Publishing to Cyberdeck CDN..."
mkdir -p /opt/cyberdeck/public/
cp production/voyager_film/voyager_120s_cinematic_master.mp4 /opt/cyberdeck/public/voyager_120s_cinematic_master.mp4
cp production/voyager_film/voyager_120s_audit_sheet.jpg /opt/cyberdeck/public/voyager_120s_audit_sheet.jpg

echo "4. Notifying Telegram..."
python -c "
import requests, os
bot_token = '8976290222:AAGGiziDbhsKPbapeWLuSDBU7OCaDon0B9A'
chat_id = '8531839081'
vpath = '/opt/cyberdeck/public/voyager_120s_cinematic_master.mp4'
sheet_path = '/opt/cyberdeck/public/voyager_120s_audit_sheet.jpg'
caption = (
    '🚀 [CLOUD VPS DAEMON] ДВУХМИНУТНЫЙ КИНЕМАТОГРАФИЧНЫЙ ФИЛЬМ ГОТОВ!\n\n'
    '🎬 VOYAGER: Последний крик человечества во тьме (120s @ 30 FPS)\n'
    '🌐 CDN Ссылка: https://signals-sacramento-enquiry-looks.trycloudflare.com/voyager_120s_cinematic_master.mp4\n'
    '📊 Раскадровка: https://signals-sacramento-enquiry-looks.trycloudflare.com/voyager_120s_audit_sheet.jpg'
)
if os.path.exists(sheet_path):
    with open(sheet_path, 'rb') as f:
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendPhoto', data={'chat_id': chat_id, 'caption': caption}, files={'photo': f})
if os.path.exists(vpath) and os.path.getsize(vpath) < 50 * 1024 * 1024:
    with open(vpath, 'rb') as vf:
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendVideo', data={'chat_id': chat_id}, files={'video': ('voyager_film.mp4', vf, 'video/mp4')})
"

echo "=========================================================="
echo "VOYAGER RENDER COMPLETED SUCCESSFULLY: $(date)"
echo "=========================================================="
