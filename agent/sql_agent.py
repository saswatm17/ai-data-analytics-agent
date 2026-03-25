import streamlit as st
import duckdb
import os

# Try importing Gemini (optional)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCkQPCpfl9IPhcsA_gV9aljSYYUXO5I-VA"
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    USE_LLM = True
except:
    USE_LLM = False

# DB connection
conn = duckdb.connect("ecommerce.db")

st.set_page_config(page_title="Data Analytics Agent")
st.title("📊 Autonomous Data Analytics Agent")

query = st.text_input("Ask your query:", key="main_query")

if query:
    query_lower = query.lower()

    sql_query = None

    # 🔥 TRY LLM FIRST
    if USE_LLM:
        try:
            prompt = f"""
            Convert natural language to SQL.

            Tables:
            customers(customer_id, name, city)
            products(product_id, product_name, price)
            orders(order_id, customer_id, product_id, quantity)

            Query: {query}

            Only return SQL query.
            """

            response = llm.invoke(prompt)
            sql_query = response.content.strip()

            st.success("🤖 AI Generated SQL")

        except:
            st.warning("⚠️ AI unavailable, using fallback logic")

    # 🔥 FALLBACK (ALWAYS WORKS)
    if not sql_query:
        if "customer" in query_lower:
            sql_query = "SELECT * FROM customers"
        elif "product" in query_lower:
            sql_query = "SELECT * FROM products"
        elif "order" in query_lower:
            sql_query = "SELECT * FROM orders"
        else:
            sql_query = "SELECT * FROM customers"

        st.info("🧠 Using fallback logic")

    try:
        st.subheader("🧾 SQL Query")
        st.code(sql_query, language="sql")

        result = conn.execute(sql_query).fetchdf()

        st.success("✅ Query executed")
        st.dataframe(result)

    except Exception as e:
        st.error(f"Error executing query: {e}")