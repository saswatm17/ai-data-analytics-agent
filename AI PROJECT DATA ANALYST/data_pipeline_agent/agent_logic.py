from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "data/ecommerce.db"

def get_agent():
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        handle_parsing_errors=True,
    )
    return agent, db

def run_query(question: str):
    agent, db = get_agent()
    print(f"\n📋 DB Tables: {db.get_usable_table_names()}")
    result = agent.invoke({"input": question})
    return result["output"]

if __name__ == "__main__":
    answer = run_query("Show me top 5 customers by total revenue")
    print("\n🧠 Agent Answer:", answer)