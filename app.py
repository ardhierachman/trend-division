import os
import requests
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv

load_dotenv()

# --- LLM GROQ yang benar ---
groq_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# --- TOOLS ---
def send_telegram(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not token or not chat_id:
        print("BOT_TOKEN / CHAT_ID belum diisi")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text[:4000], "parse_mode": "Markdown"})

# --- 3 AGENT ---
scout_lokal = Agent(
    role='Trend Scout Indonesia',
    goal='Cari 5 trend TikTok & Reels viral Indonesia hari ini',
    backstory='Kamu ahli TikTok Creative Center Indonesia',
    tools=[SerperDevTool()],
    llm=groq_llm,
    verbose=True
)

scout_global = Agent(
    role='Trend Scout Internasional',
    goal='Cari 3 trend internasional yang belum masuk Indonesia',
    backstory='Kamu pantau TikTok US, Reels US, YouTube Shorts global',
    tools=[WebsiteSearchTool()],
    llm=groq_llm,
    verbose=True
)

strategist = Agent(
    role='Content Strategist Personal Branding Edukasi',
    goal='Prediksi trend dan bikin 3 ide konten',
    backstory='Kamu strategist niche personal branding / edukasi',
    llm=groq_llm,
    verbose=True
)

# --- TASK ---
task1 = Task(
    description='Riset trend lokal hari ini. Cari "tiktok viral indonesia hari ini". Hasil: list 5 trend dengan sound & hashtag.',
    agent=scout_lokal,
    expected_output='List 5 trend lokal'
)

task2 = Task(
    description='Riset trend internasional hari ini. Cari "tiktok viral global today". Hasil: list 3 trend.',
    agent=scout_global,
    expected_output='List 3 trend global'
)

task3 = Task(
    description='''
    Berdasarkan hasil 2 scout, buat laporan akhir untuk Telegram (Markdown):
    1. Ringkasan diskusi divisi
    2. Top 5 Trend Hari Ini
    3. Prediksi 2 trend internasional yang akan diadaptasi di Indonesia (kenapa cocok)
    4. Ide konten 3 hari ke depan untuk personal branding edukasi, format: Hook, Format Video, Sound/Ref, CTA
    ''',
    agent=strategist,
    expected_output='Laporan lengkap siap kirim Telegram'
)

crew = Crew(agents=[scout_lokal, scout_global, strategist], tasks=[task1, task2, task3])

if __name__ == "__main__":
    print("=== DIVISI TREND MULAI DISKUSI ===")
    result = crew.kickoff()
    print(result)
    send_telegram(str(result))
