import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
STAFF_USER_ID = os.getenv("STAFF_USER_ID")  # 👈←運営LINEアカウントのuserId

def translate_text(text, target_lang="ja"):
    prompt = f"Translate the following text into {target_lang}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def push_to_staff(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=body)

@app.route("/webhook", methods=['POST'])
def webhook():
    payload = request.json
    events = payload.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"]
            translated = translate_text(user_text, target_lang="ja")

            # 運営に送信（翻訳通知）
            push_to_staff(STAFF_USER_ID, f"📩 翻訳通知：\n原文: {user_text}\n翻訳: {translated}")

    return "OK"