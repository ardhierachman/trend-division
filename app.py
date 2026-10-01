import os
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def send_telegram(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text[:4000], "parse_mode": "Markdown"})

def search_serper(query):
    key = os.getenv("SERPER_API_KEY")
    try:
        r = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "gl": "id", "hl": "id", "num": 5},
            timeout=20
        )
        data = r.json()
        out = []
        for item in data.get("organic", [])[:5]:
            out.append(f"- {item.get('title')}: {item.get('snippet')}")
        return "\n".join(out)
    except Exception as e:
        return f"Search error {e}"

print("=== DIVISI TREND LIGHT MODE START ===")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# cek key kepotong apa enggak
print(f"GROQ KEY terdeteksi: {os.getenv('GROQ_API_KEY','')[0:10]}...")

lokal = search_serper("tiktok viral Indonesia hari ini Oktober 2026")
global_trend = search_serper("tiktok viral global today USA trends")

prompt = f"""
Kamu Divisi Trend. Data Lokal:\n{lokal}\n\nData Global:\n{global_trend}\n\nBuat laporan Telegram: Top 5 Trend Hari Ini, 2 Prediksi Global yang bakal masuk Indo, 3 Ide Konten (Hook, Format, Sound, CTA). Bahasa Indonesia.
"""

# DAFTAR MODEL YANG MASIH HIDUP DI GROQ 2026
MODELS = [
    "openai/gpt-oss-20b", # paling gratis & stabil sekarang
    "openai/gpt-oss-120b",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

laporan = None
for m in MODELS:
    try:
        print(f"Coba model: {m}")
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        laporan = resp.choices[0].message.content
        print(f"SUKSES pakai {m}")
        break
    except Exception as e:
        print(f"Gagal {m}: {e}")
        continue

if not laporan:
    laporan = "Gagal semua model Groq. Cek GROQ_API_KEY di console.groq.com - buat key baru."

print(laporan)
send_telegram(laporan)
print("=== SELESAI ===")
