# main.py
from dotenv import load_dotenv
load_dotenv()

from crewai_app.flows.market_flow import run_market_flow

if __name__ == "__main__":
    print("🚀 Starting Financial Daily Summary pipeline...")
    run_market_flow()
    print("✅ Finished successfully!")

