#!/usr/bin/env python3
"""Validate Agent Control video jobs. No rendering or network access."""
import json
import sys
from pathlib import Path

SCHEMA = "agent-control-video-job/v1"
ENGINES = {"film": "Cloud Motion Studio", "short": "Viralna Studio AI"}

def inspect(job):
    errors, warnings = [], []
    if not isinstance(job, dict):
        return ["Root must be a JSON object"], []
    if job.get("schema") != SCHEMA:
        errors.append("Unsupported schema")
    kind = job.get("kind")
    if kind not in ENGINES:
        errors.append("Unknown job kind")
    try:
        duration = int(job["duration_seconds"])
    except (KeyError, TypeError, ValueError):
        duration = 0
    if kind == "film" and not 120 <= duration <= 240:
        errors.append("Film duration must be 120..240 seconds")
    if kind == "short" and not 15 <= duration <= 180:
        errors.append("Short duration must be 15..180 seconds")
    if kind in ENGINES:
        if job.get("engine") != ENGINES[kind]:
            errors.append("Engine and kind do not match")
        if job.get("aspect_ratio") != ("16:9" if kind == "film" else "9:16"):
            errors.append("Aspect ratio does not match")
    if job.get("execution_status") != "not_submitted":
        errors.append("Cannot claim submitted/executed by an offline export")
    voice = job.get("script")
    storyboard = job.get("storyboard")
    if not isinstance(voice, str) or not isinstance(storyboard, str):
        errors.append("Script and storyboard must be strings")
    else:
        words = len(voice.split())
        if duration and words < int(duration / 60 * 95):
            warnings.append("Narration is probably too short for the requested duration")
        target = (duration + (3 if kind == "short" else 7)) // (4 if kind == "short" else 8)
        if len([line for line in storyboard.splitlines() if line.strip()]) < target:
            warnings.append(f"Too few separate shots; target at least {target}")
    if not isinstance(job.get("qa"), dict) or not job["qa"].get("motion_required"):
        warnings.append("Motion quality gate is missing")
    return errors, warnings

def main(argv):
    if len(argv) < 2:
        print("Usage: python tools/agent_control_job_check.py video-job.json")
        return 2
    path = Path(argv[1])
    if path.stat().st_size > 5000000:
        print("JSON is too large")
        return 2
    job = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = inspect(job)
    print(json.dumps({"ready_for_human_review": not errors, "errors": errors,
                      "warnings": warnings, "video_rendered": False},
                     ensure_ascii=False, indent=2))
    return 2 if errors else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
