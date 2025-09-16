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

def build_message(items):
    lines = []
    for item in items:
        days_left = calculate_days_left(item["expiry"])
        repo = item.get("repo", "N/A")
        if days_left <= 0:
            status = f":warning: *{item['name']}* in <{repo}|repo> has expired on {item['expiry']}"
        else:
            status = f"*{item['name']}* in <{repo}|repo>: {days_left} days left (expires {item['expiry']})"
        lines.append(status)
    return "\n".join(lines)

def send_to_slack(message):
    if not SLACK_WEBHOOK_URL:
        raise Exception("SLACK_WEBHOOK_URL not set")
    payload = {"text": f"*Expiry Check Report*\n{message}"}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()

if __name__ == "__main__":
    items = load_expirations(FILE_PATH)
    message = build_message(items)
    send_to_slack(message)
