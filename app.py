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
Kamu adalah Divisi Trend Personal Branding Edukasi di Mataram.

DATA LOKAL (Indonesia):
{lokal}

DATA GLOBAL:
{global_trend}

TUGAS:
1. Saring hanya trend yang relevan untuk edukasi/personal branding, BUKAN playlist musik umum.
2. WAJIB sebutkan minimal: sound Timur (Tabola Bale/Ambon Manise) kalau masih di FYP, format Swipe ALYPH, dan momen Hari Kesaktian Pancasila kalau masih 1-7 Okt.
3. Prediksi 2 trend global (Ramalama Walk / ATEEZ BAD / format hold it down) yang bakal masuk Indo.
4. 3 ide konten dengan struktur: Hook 3 detik, Format Video (15-30 detik), Sound yang dipakai, CTA komen.

Output harus Markdown Telegram, jangan pakai tabel yang lebar, pakai bullet list. Bahasa Indonesia gaul Mataram.
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
