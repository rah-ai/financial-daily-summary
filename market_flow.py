# crewai_app/flows/market_flow.py

import os
from crewai import Crew, Agent, Task
from crewai.llm import LLM

# Import all agent tools with clear names to avoid conflicts
from ..agents.search_agent import search_agent as search_tool
from ..agents.summary_agent import summary_agent as summary_tool
from ..agents.formatting_agent import formatting_agent as formatting_tool
from ..agents.translate_agent import translate_agent as translate_tool
from ..agents.send_agent import send_agent as send_tool

# ================================
# API Key Setup with Updated Model
# ================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def create_groq_llm():
    """Create a properly configured Groq LLM instance with updated model"""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is required but not found!")

    return LLM(
        model="groq/llama-3.3-70b-versatile",  # FIXED: Updated to supported model
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=4096
        # Removed unsupported parameters: top_p, top_k
    )

# ================================
# Flow Definition
# ================================
def run_market_flow():
    print("Starting Daily Market Summary Flow...")
    print("Using updated Groq model: llama-3.3-70b-versatile")

    try:
        # Create LLM instance
        llm = create_groq_llm()

        # Define Agents with proper tool assignment
        search_agent = Agent(
            role="News Researcher",
            goal="Find the latest financial news",
            backstory="Expert at scanning financial sources quickly.",
            llm=llm,
            tools=[search_tool],  # Fixed: Using renamed import
            verbose=True
        )

        summarizer_agent = Agent(
            role="Financial Analyst",
            goal="Summarize financial news into concise insights",
            backstory="Experienced at creating clear market reports.",
            llm=llm,
            tools=[summary_tool],  # Fixed: Using renamed import
            verbose=True
        )

        formatter_agent = Agent(
            role="Chart Specialist",
            goal="Attach financial charts and visualizations",
            backstory="Specialist in financial data presentation.",
            llm=llm,
            tools=[formatting_tool],  # Fixed: Using renamed import
            verbose=True
        )

        translator_agent = Agent(
            role="Translator",
            goal="Translate summaries into multiple languages",
            backstory="Fluent in multiple languages for global reach.",
            llm=llm,
            tools=[translate_tool],  # Fixed: Using renamed import
            verbose=True
        )

        sender_agent = Agent(
            role="Messenger",
            goal="Send the report to Telegram",
            backstory="Responsible for delivering the summary to users.",
            llm=llm,
            tools=[send_tool],  # Fixed: Using renamed import
            verbose=True
        )

        # Define Tasks with clearer descriptions
        search_task = Task(
            description="Search for the latest financial news headlines using the search_latest_financial_news tool. Focus on major indices, stock movements, and market trends.",
            agent=search_agent,
            expected_output="List of current financial news headlines and market updates"
        )

        summary_task = Task(
            description="Summarize the financial news into a concise report under 200 words using the summarize_financial_news tool. Include key market movements, trends, and important developments.",
            agent=summarizer_agent,
            expected_output="Clear and concise financial market summary",
            context=[search_task]
        )

        charts_task = Task(
            description="Generate chart URLs for the financial summary using the generate_financial_charts tool to provide visual representations of market data.",
            agent=formatter_agent,
            expected_output="List of chart image URLs for market visualization",
            context=[summary_task]
        )

        translate_task = Task(
            description="Translate the market summary into Hindi, Arabic, and Hebrew using the translate_summary tool to reach a global audience.",
            agent=translator_agent,
            expected_output="Dictionary containing translations in Hindi, Arabic, and Hebrew",
            context=[summary_task]
        )

        send_task = Task(
            description="Send the complete market report including summary, charts, and translations to Telegram using the send_to_telegram tool. Ensure all data is properly formatted.",
            agent=sender_agent,
            expected_output="Confirmation message of successful delivery to Telegram",
            context=[summary_task, charts_task, translate_task]
        )

        # Create and run crew
        crew = Crew(
            agents=[search_agent, summarizer_agent, formatter_agent, translator_agent, sender_agent],
            tasks=[search_task, summary_task, charts_task, translate_task, send_task],
            verbose=True,
            process="sequential"  # Ensure tasks run in order
        )

        print("Executing crew tasks...")
        result = crew.kickoff()
        print("Flow completed successfully!")
        return result

    except Exception as e:
        print(f"Flow failed with error: {e}")
        
        # Enhanced error handling with fallback notification
        try:
            error_data = {
                "summary": f"Daily market summary failed due to technical issue: {str(e)[:200]}",
                "charts": [],
                "translations": {
                    "Hindi": "दैनिक सारांश विफल हुआ",
                    "Arabic": "فشل الملخص اليومي", 
                    "Hebrew": "סיכום יומי נכשל"
                }
            }
            
            # Try to send error notification - Fixed: Using renamed import
            error_result = send_tool.run(error_data)
            print(f"Error notification sent: {error_result}")
            
        except Exception as send_error:
            print(f"Failed to send error notification: {send_error}")
        
        # Re-raise the original exception
        raise e


# ================================
# Alternative fallback function
# ================================
def run_market_flow_simple():
    """Simplified version that runs without CrewAI if there are issues"""
    print("Running simplified market flow...")
    
    try:
        # Direct tool execution with renamed imports
        print("Step 1: Searching for news...")
        news_data = search_tool.run("latest financial market news")
        
        print("Step 2: Summarizing...")
        summary_data = summary_tool.run(news_data)
        
        print("Step 3: Generating charts...")
        charts_data = formatting_tool.run(summary_data)
        
        print("Step 4: Translating...")
        translations_data = translate_tool.run(summary_data)
        
        print("Step 5: Sending to Telegram...")
        final_data = {
            "summary": summary_data,
            "charts": charts_data,
            "translations": translations_data
        }
        send_result = send_tool.run(final_data)
        
        print("Simplified flow completed successfully!")
        return send_result
        
    except Exception as e:
        print(f"Simplified flow also failed: {e}")
        return f"All flows failed: {e}"


# ================================
# Main execution with fallback
# ================================
def main():
    """Main function with fallback mechanisms"""
    try:
        return run_market_flow()
    except Exception as e:
        print(f"Primary flow failed: {e}")
        print("Attempting simplified fallback...")
        return run_market_flow_simple()


if __name__ == "__main__":
    main()