import os
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def send_telegram(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not token or not chat_id:
        print("BOT_TOKEN/CHAT_ID kosong")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # Telegram max 4000 char
    requests.post(url, json={"chat_id": chat_id, "text": text[:4000], "parse_mode": "Markdown"})

def search_serper(query):
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return "Serper key kosong"
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "gl": "id", "hl": "id", "num": 5},
            timeout=20
        )
        data = r.json()
        results = []
        for item in data.get("organic", [])[:5]:
            results.append(f"- {item.get('title')}: {item.get('snippet')}")
        return "\n".join(results)
    except Exception as e:
        return f"Search error: {e}"

# --- MAIN ---
print("=== DIVISI TREND LIGHT MODE START ===")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

lokal = search_serper("tiktok viral Indonesia hari ini Oktober 2026")
global_trend = search_serper("tiktok viral global today USA trends")

prompt = f"""
Kamu adalah Divisi Trend untuk Personal Branding Edukasi.

Data Lokal:
{lokal}

Data Global:
{global_trend}

Buat laporan Telegram (pakai Markdown rapi):
1. Top 5 Trend TikTok/Reels Hari Ini (Indonesia)
2. Prediksi 2 Trend Internasional yang akan masuk Indonesia + alasan kenapa cocok
3. 3 Ide Konten 3 Hari Ke Depan (Hook, Format Video, Sound/Ref, CTA)

Bahasa Indonesia santai, to-the-point.
"""

response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

laporan = response.choices[0].message.content
print(laporan)
send_telegram(laporan)
print("=== SELESAI, TELEGRAM TERKIRIM ===")
