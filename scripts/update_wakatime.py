#!/usr/bin/env python3
"""
Fetch WakaTime stats from public API and inject into README.
No secrets required — uses https://wakatime.com/api/v1/users/{username}/stats/last_7_days
"""

import requests
import re
from pathlib import Path

WAKATIME_USERNAME = "musiliandrew"
WAKATIME_API_URL = f"https://wakatime.com/api/v1/users/{WAKATIME_USERNAME}/stats/last_7_days"
README_PATH = Path("README.md")

# Markers for injection
START_MARKER = "<!--START_SECTION:waka-->"
END_MARKER = "<!--END_SECTION:waka-->"


def fetch_wakatime_stats():
    """Fetch last 7 days stats from public WakaTime API."""
    try:
        response = requests.get(WAKATIME_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️  Failed to fetch WakaTime stats: {e}")
        return None


def format_stats(data):
    """Format WakaTime stats as a readable terminal breakdown."""
    if not data:
        return "No stats available yet."

    lines = []
    lines.append("")
    lines.append("```text")

    # Top languages
    if "languages" in data and data["languages"]:
        lines.append("Language breakdown (last 7 days):")
        lines.append("")
        total_seconds = sum(lang.get("total_seconds", 0) for lang in data["languages"])
        for lang in data["languages"][:8]:  # Top 8
            name = lang.get("name", "Unknown")
            seconds = lang.get("total_seconds", 0)
            percent = (seconds / total_seconds * 100) if total_seconds > 0 else 0
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            lines.append(f"{name:<15} {percent:>5.1f}%  {time_str:>8}")
        lines.append("")

    # Total time
    total_time = data.get("total_seconds", 0)
    total_hours = int(total_time // 3600)
    total_minutes = int((total_time % 3600) // 60)
    if total_hours > 0 or total_minutes > 0:
        lines.append(f"Total:           {total_hours}h {total_minutes}m")
    else:
        lines.append("Total:           < 1 minute")

    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def update_readme(content):
    """Inject formatted stats into README between markers."""
    pattern = f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}"
    replacement = f"{START_MARKER}\n{content}\n{END_MARKER}"

    # If markers don't exist, warn but don't fail
    if START_MARKER not in README_PATH.read_text():
        print(f"⚠️  Markers not found in README.md. Add these lines where you want WakaTime stats:")
        print(f"  {START_MARKER}")
        print(f"  {END_MARKER}")
        return False

    updated = re.sub(pattern, replacement, README_PATH.read_text(), flags=re.DOTALL)
    README_PATH.write_text(updated)
    print("✅ README.md updated with WakaTime stats")
    return True


def main():
    stats = fetch_wakatime_stats()
    content = format_stats(stats)
    update_readme(content)


if __name__ == "__main__":
    main()
