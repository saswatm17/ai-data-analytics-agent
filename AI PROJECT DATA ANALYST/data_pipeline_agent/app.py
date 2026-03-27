import streamlit as st
from database import init_db
from graph import build_graph
from fpdf import FPDF
import tempfile
import os

init_db()
pipeline = build_graph()

st.set_page_config(
    page_title="📊 Analyst Copilot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stChatMessage { border-radius: 12px; }
    .insight-box {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border-left: 4px solid #4fc3f7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    .sql-box {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        color: #4fc3f7;
    }
    .metric-card {
        background: #1e2a3a;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("## 📊 Analyst Copilot")
st.caption("🤖 AI-powered data analytics — ask questions in plain English, get instant insights")

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.markdown("### 💡 Sample Questions")

    samples = [
        "Show me top 5 customers by total revenue",
        "Which product category has the highest sales?",
        "Show monthly sales trend in 2024",
        "Which region has the most customers?",
        "Top 3 most sold products",
        "What is average order value by region?",
        "Which month had highest sales in 2024?",
    ]
    for s in samples:
        if st.button(s, use_container_width=True):
            st.session_state["query"] = s

    st.divider()
    st.markdown("### ⚙️ Settings")
    show_sql = st.toggle("Show SQL Query", value=False)
    show_data = st.toggle("Show Raw Data", value=True)

    st.divider()
    st.markdown("### 🔒 Security")
    st.success("✅ Read-Only Connection")
    st.caption("Agent cannot run DROP, DELETE or INSERT commands")

# --- PDF Export ---
def export_pdf(question, answer, narrative, sql_query):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Analyst Copilot - Report", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Question:", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, question)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Answer:", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, answer)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "AI Narrative Insights:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_narrative = narrative.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, clean_narrative)
    pdf.ln(3)

    if sql_query:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "SQL Query Used:", ln=True)
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(0, 7, sql_query)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("narrative"):
            st.markdown(f'<div class="insight-box">{msg["narrative"]}</div>',
                       unsafe_allow_html=True)
        if msg.get("sql") and show_sql:
            st.markdown("**🔍 SQL Query Used:**")
            st.code(msg["sql"], language="sql")
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True)

# --- Input ---
query = st.chat_input("💬 Ask your data question...")
if "query" in st.session_state:
    query = st.session_state.pop("query")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyzing your data..."):
            try:
                result = pipeline.invoke({
                    "question": query,
                    "sql_answer": "",
                    "sql_query": "",
                    "dataframe": None,
                    "chart": None,
                    "narrative": "",
                    "error": None
                })

                answer = result.get("sql_answer", "No answer returned.")
                chart = result.get("chart", None)
                df = result.get("dataframe", None)
                narrative = result.get("narrative", "")
                sql_query = result.get("sql_query", "")
                error = result.get("error", None)

                if error:
                    st.warning(f"⚠️ Note: {error}")

                st.markdown(answer)

                # Narrative Insights
                if narrative:
                    st.markdown(f'<div class="insight-box">{narrative}</div>',
                               unsafe_allow_html=True)

                # SQL Toggle
                if show_sql and sql_query:
                    st.markdown("**🔍 SQL Query Used:**")
                    st.code(sql_query, language="sql")

                # Raw Data
                if show_data and df is not None and not df.empty:
                    with st.expander("📋 View Raw Data"):
                        st.dataframe(df, use_container_width=True)

                # Chart
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

                # PDF Export
                if answer and narrative:
                    pdf_path = export_pdf(query, answer, narrative, sql_query)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📄 Export Report as PDF",
                            data=f,
                            file_name="analyst_report.pdf",
                            mime="application/pdf"
                        )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "chart": chart,
                    "narrative": narrative,
                    "sql": sql_query
                })

            except Exception as e:
                st.error(f"Pipeline error: {e}")