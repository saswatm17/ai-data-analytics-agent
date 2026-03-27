import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

def detect_chart_type(question: str, df: pd.DataFrame) -> str:
    cols = list(df.columns)
    llm = get_llm()
    prompt = f"""
You are a data visualization expert.
User question: "{question}"
DataFrame columns: {cols}
Reply with ONLY one word: bar | line | pie | scatter | table
"""
    response = llm.invoke(prompt)
    return response.content.strip().lower()

def generate_chart(question: str, df: pd.DataFrame):
    if df is None or df.empty:
        return None

    try:
        chart_type = detect_chart_type(question, df)
        cols = list(df.columns)

        if chart_type == "bar" and len(cols) >= 2:
            fig = px.bar(df, x=cols[0], y=cols[1], title=question,
                        color=cols[0])
        elif chart_type == "line" and len(cols) >= 2:
            fig = px.line(df, x=cols[0], y=cols[1], title=question,
                         markers=True)
        elif chart_type == "pie" and len(cols) >= 2:
            fig = px.pie(df, names=cols[0], values=cols[1], title=question)
        elif chart_type == "scatter" and len(cols) >= 2:
            fig = px.scatter(df, x=cols[0], y=cols[1], title=question)
        else:
            fig = go.Figure(data=[go.Table(
                header=dict(values=cols,
                           fill_color='paleturquoise',
                           align='left'),
                cells=dict(values=[df[c] for c in cols],
                          fill_color='lavender',
                          align='left')
            )])
            fig.update_layout(title=question)

        return fig

    except Exception as e:
        print(f"⚠️ Chart error: {e}")
        return None