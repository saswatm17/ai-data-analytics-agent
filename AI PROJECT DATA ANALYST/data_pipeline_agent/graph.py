from langgraph.graph import StateGraph, END
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from typing import TypedDict, Optional
import pandas as pd
import sqlite3
import re
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = "data/ecommerce.db"

class PipelineState(TypedDict):
    question: str
    sql_answer: str
    sql_query: str
    dataframe: Optional[object]
    chart: Optional[object]
    narrative: str
    error: Optional[str]

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

def get_small_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

def sql_agent_node(state: PipelineState) -> PipelineState:
    try:
        db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
        agent = create_sql_agent(
            llm=get_llm(),
            db=db,
            agent_type="openai-tools",
            verbose=False,
            handle_parsing_errors=True
        )
        result = agent.invoke({"input": state["question"]})
        return {**state, "sql_answer": result["output"]}
    except Exception as e:
        return {**state, "error": str(e), "sql_answer": "Could not process query."}

def extract_dataframe_node(state: PipelineState) -> PipelineState:
    try:
        llm = get_llm()
        prompt = f"""
Given this question: "{state['question']}"
Write ONLY a valid SQLite SQL query. No explanation. No markdown. No backticks. Just raw SQL starting with SELECT.
Tables:
- customers(customer_id, name, email, region, signup_date)
- products(product_id, name, category, price)
- sales(sale_id, customer_id, product_id, quantity, sale_date)
"""
        sql_response = llm.invoke(prompt).content.strip()
        sql = re.sub(r"```sql|```|`", "", sql_response).strip()
        sql = sql.split(";")[0].strip()

        print(f"🔍 Generated SQL: {sql}")

        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()

        print(f"✅ DataFrame shape: {df.shape}")
        return {**state, "dataframe": df, "sql_query": sql}
    except Exception as e:
        print(f"❌ DataFrame error: {e}")
        return {**state, "dataframe": None, "sql_query": "", "error": str(e)}

def visualization_node(state: PipelineState) -> PipelineState:
    from visualizer import generate_chart
    df = state.get("dataframe")
    if df is not None and not df.empty:
        try:
            chart = generate_chart(state["question"], df)
            return {**state, "chart": chart}
        except Exception as e:
            return {**state, "chart": None, "error": str(e)}
    return {**state, "chart": None}

def narrative_node(state: PipelineState) -> PipelineState:
    try:
        df = state.get("dataframe")
        if df is None or df.empty:
            return {**state, "narrative": "No data available for insights."}

        llm = get_small_llm()
        prompt = f"""
You are a senior data analyst presenting to a non-technical executive.

User Question: "{state['question']}"
Data Summary:
{df.to_string(index=False)}

Your task:
1. Write ONE headline finding (start with "Key Insight:")
2. Write ONE anomaly or surprising pattern (start with "Anomaly:")
3. Write ONE business recommendation (start with "Recommendation:")

Keep each point to 1-2 sentences. Be specific with numbers from the data.
"""
        response = llm.invoke(prompt)
        return {**state, "narrative": response.content.strip()}
    except Exception as e:
        return {**state, "narrative": "Could not generate narrative insights."}

def build_graph():
    graph = StateGraph(PipelineState)
    graph.add_node("sql_agent", sql_agent_node)
    graph.add_node("extract_df", extract_dataframe_node)
    graph.add_node("visualize", visualization_node)
    graph.add_node("narrative", narrative_node)

    graph.set_entry_point("sql_agent")
    graph.add_edge("sql_agent", "extract_df")
    graph.add_edge("extract_df", "visualize")
    graph.add_edge("visualize", "narrative")
    graph.add_edge("narrative", END)

    return graph.compile()