# 📰 Financial Daily Summary Automation

This project automates the process of generating **daily financial summaries** using **CrewAI agents**, enhanced with **Groq LLM**, and delivers the results directly to Telegram.

---

## 🚀 Features
- **News Researcher Agent** → Scrapes and finds the latest financial news.  
- **Financial Analyst Agent** → Summarizes the news into clear insights.  
- **Chart Specialist Agent** → Generates financial charts & visualizations.  
- **Translator Agent** → Translates summaries into Hindi, Arabic, and Hebrew.  
- **Messenger Agent** → Sends final reports, charts, and translations to Telegram.  

---

## ⚙️ Tech Stack
- **Python 3.11**  
- **CrewAI** (multi-agent orchestration)  
- **LiteLLM** with **Groq API** (`llama-3.1-70b-versatile`)  
- **Telegram Bot API**  
- **dotenv** for environment variables  

---

## 📂 Project Structure
          financial-daily-summary/
│── crewai_app/
│ ├── agents/ # Individual agent logic
│ ├── flows/ # Orchestrator flow
│ ├── tools/ # Tools & utilities
│ └── config.py # API keys and LLM configs
│── main.py # Entry point
│── requirements.txt # Dependencies
│── .env # API keys (not in repo)

---

## 🔑 Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/financial-daily-summary.git
   cd financial-daily-summary

2. Create a virtual environment:
   ```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


