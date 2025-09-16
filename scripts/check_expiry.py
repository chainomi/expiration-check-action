# import yaml
# import os
# from datetime import datetime, date
# import requests

# FILE_PATH = "expirations.yaml"
# SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# def load_expirations(file_path):
#     with open(file_path, "r") as f:
#         data = yaml.safe_load(f)
#     return data["items"]

# def calculate_days_left(expiry_date):
#     if isinstance(expiry_date, date):  # already parsed as date
#         expiry = expiry_date
#     else:  # assume string like "2025-10-10"
#         expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()

#     today = datetime.today().date()
#     return (expiry - today).days

# def build_message(items):
#     lines = []
#     for item in items:
#         days_left = calculate_days_left(item["expiry"])
#         status = f"{item['name']}: {days_left} days left (expires {item['expiry']})"
#         if days_left <= 0:
#             status = f":warning: {item['name']} has expired on {item['expiry']}"
#         lines.append(status)
#     return "\n".join(lines)

# def send_to_slack(message):
#     if not SLACK_WEBHOOK_URL:
#         raise Exception("SLACK_WEBHOOK_URL not set")
#     payload = {"text": f"*Expiry Check Report*\n{message}"}
#     response = requests.post(SLACK_WEBHOOK_URL, json=payload)
#     response.raise_for_status()

# if __name__ == "__main__":
#     items = load_expirations(FILE_PATH)
#     message = build_message(items)
#     send_to_slack(message)

# import yaml
# import os
# from datetime import datetime, date
# import requests

# FILE_PATH = "expirations.yaml"
# SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

# def load_expirations(file_path):
#     with open(file_path, "r") as f:
#         data = yaml.safe_load(f)
#     return data["items"]

# def calculate_days_left(expiry_date):
#     if isinstance(expiry_date, date):  # already a date
#         expiry = expiry_date
#     else:  # parse string
#         expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
#     today = datetime.today().date()
#     return (expiry - today).days

# def build_message(items):
#     lines = []
#     for item in items:
#         days_left = calculate_days_left(item["expiry"])
#         repo = item.get("repo", "N/A")
#         if days_left <= 0:
#             status = f":warning: *{item['name']}* in <{repo}|repo> has expired on {item['expiry']}"
#         else:
#             status = f"*{item['name']}* in <{repo}|repo>: {days_left} days left (expires {item['expiry']})"
#         lines.append(status)
#     return "\n".join(lines)

# def send_to_slack(message):
#     if not SLACK_WEBHOOK_URL:
#         raise Exception("SLACK_WEBHOOK_URL not set")
#     payload = {"text": f"*Expiry Check Report*\n{message}"}
#     response = requests.post(SLACK_WEBHOOK_URL, json=payload)
#     response.raise_for_status()

# if __name__ == "__main__":
#     items = load_expirations(FILE_PATH)
#     message = build_message(items)
#     send_to_slack(message)

import yaml
import os
from datetime import datetime, date
import requests

FILE_PATH = "expirations.yaml"
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

def load_expirations(file_path):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return data["items"]

def calculate_days_left(expiry_date):
    if isinstance(expiry_date, date):  # already a date
        expiry = expiry_date
    else:  # parse string
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    today = datetime.today().date()
    return (expiry - today).days

def categorize_items(items):
    expired, soon, healthy = [], [], []
    for item in items:
        days_left = calculate_days_left(item["expiry"])
        repo = item.get("repo", "N/A")
        entry = {
            "name": item["name"],
            "expiry": item["expiry"],
            "days_left": days_left,
            "repo": repo
        }
        if days_left <= 0:
            expired.append(entry)
        elif days_left <= 30:
            soon.append(entry)
        else:
            healthy.append(entry)
    return expired, soon, healthy

def build_blocks(expired, soon, healthy):
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "⏳ Token Expiry Check Report"}
        },
        {"type": "divider"}
    ]

    def section(title, emoji, entries):
        if not entries:
            return
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{emoji} {title}*"}
        })
        for e in entries:
            if e["days_left"] <= 0:
                text = f":warning: *{e['name']}* expired on *{e['expiry']}*\nRepo: <{e['repo']}|link>"
            else:
                text = f"*{e['name']}* → {e['days_left']} days left (expires {e['expiry']})\nRepo: <{e['repo']}|link>"
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": text}
            })
        blocks.append({"type": "divider"})

    section("Expired", "🔴", expired)
    section("Expiring Soon (≤30 days)", "🟡", soon)
    section("Healthy (>30 days)", "🟢", healthy)

    return blocks

def send_to_slack(blocks):
    if not SLACK_WEBHOOK_URL:
        raise Exception("SLACK_WEBHOOK_URL not set")
    payload = {"blocks": blocks}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

if __name__ == "__main__":
    items = load_expirations(FILE_PATH)
    expired, soon, healthy = categorize_items(items)
    blocks = build_blocks(expired, soon, healthy)
    send_to_slack(blocks)
