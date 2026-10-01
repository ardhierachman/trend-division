import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, WebsiteSearchTool
from pytrends.request import TrendReq
import requests
from dotenv import load_dotenv

load_dotenv()

# --- TOOLS GRATISAN ---
def get_google_trends():
    pytrends = TrendReq(hl='id-ID', tz=480)
    trending = pytrends.trending_searches(pn='indonesia')
    return trending.head(5).to_string()

def send_telegram(text):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    print("Terkirim ke Telegram!")

# --- 3 AGENT DIVISI ---
scout_lokal = Agent(
    role='Trend Scout Indonesia',
    goal='Cari 5 trend TikTok & Reels yang lagi viral di Indonesia hari ini',
    backstory='Kamu ahli TikTok Creative Center Indonesia, tau sound, hashtag, dan format yang naik.',
    tools=[SerperDevTool()],
    llm='groq/llama-3.1-8b-instant'
)

scout_global = Agent(
    role='Trend Scout Internasional',
    goal='Cari 3 trend internasional yang belum masuk Indonesia',
    backstory='Kamu pantau TikTok US, Reels US, YouTube Shorts global.',
    tools=[WebsiteSearchTool()],
    llm='groq/llama-3.1-8b-instant'
)

strategist = Agent(
    role='Content Strategist Personal Branding Edukasi',
    goal='Prediksi trend global yang akan masuk Indonesia dan bikin 3 ide konten edukasi',
    backstory='Kamu strategist untuk niche personal branding/edukasi. Kamu jago ubah trend joget jadi konten value.',
    llm='groq/llama-3.1-8b-instant'
)

# --- TASK (JADWAL KERJA) ---
task1 = Task(description='Riset trend lokal hari ini. Gunakan tool search untuk "tiktok viral indonesia hari ini" dan Google Trends. Hasil: list 5 trend.', agent=scout_lokal)
task2 = Task(description='Riset trend internasional. Cari "tiktok viral global today". Hasil: list 3 trend.', agent=scout_global)
task3 = Task(
    description='''
    Berdasarkan hasil 2 scout, buat laporan akhir:
    1. Ringkasan diskusi (seolah 3 agent ngobrol)
    2. Top 5 Trend Hari Ini
    3. Prediksi 2 trend internasional yang akan diadaptasi di Indonesia (jelaskan kenapa cocok)
    4. Ide konten 3 hari ke depan untuk personal branding edukasi, minimal 1 per hari dengan format: Hook, Format Video, Sound/Ref, CTA
    Format untuk Telegram Markdown.
    ''',
    agent=strategist
)

crew = Crew(agents=[scout_lokal, scout_global, strategist], tasks=[task1, task2, task3])

if __name__ == "__main__":
    result = crew.kickoff()
    send_telegram(str(result))
