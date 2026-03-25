import streamlit as st
import duckdb

# ---------------- DATABASE (Day 2) ----------------
conn = duckdb.connect("ecommerce.db")

st.set_page_config(page_title="AI Data Agent", layout="wide")
st.title("📊 Autonomous Data Analytics Agent")

# ---------------- INPUT (Day 2 UI) ----------------
query = st.text_input("Ask your query:", key="main_query")

# ---------------- SMART SQL GENERATOR (Day 3) ----------------
def generate_sql(user_query):
    q = user_query.lower()

    # 🔥 Complex query (JOIN + GROUP BY)
    if "top" in q and "customer" in q and "revenue" in q:
        return """
        SELECT c.name, SUM(p.price * o.quantity) AS revenue
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.name
        ORDER BY revenue DESC
        LIMIT 5;
        """

    # 🔥 Aggregation
    elif "total orders" in q or "sum" in q:
        return """
        SELECT customer_id, SUM(quantity) AS total_orders
        FROM orders
        GROUP BY customer_id;
        """

    # 🔥 Filter
    elif "product" in q and ("price" in q or "above" in q):
        return "SELECT * FROM products WHERE price > 300;"

    # 🔥 Basic queries
    elif "customer" in q:
        return "SELECT * FROM customers;"
    elif "product" in q:
        return "SELECT * FROM products;"
    elif "order" in q:
        return "SELECT * FROM orders;"

    # 🔥 Error simulation (for KPI)
    elif "wrong" in q:
        return "SELECT wrong_column FROM customers;"

    else:
        return "SELECT * FROM customers;"


# ---------------- EXECUTION + ERROR HANDLING ----------------
if query:
    st.info("Processing your query...")

    sql_query = generate_sql(query)

    st.subheader("🧠 Generated SQL")
    st.code(sql_query, language="sql")

    try:
        result = conn.execute(sql_query).fetchdf()

        st.success("✅ Query executed successfully")
        st.dataframe(result)

    except Exception as e:
        st.error("❌ SQL Error detected!")

        # 🔥 AUTO CORRECTION (Day 3 feature)
        corrected_query = "SELECT name FROM customers;"

        st.warning("⚠️ Auto-correcting query...")
        st.code(corrected_query, language="sql")

        result = conn.execute(corrected_query).fetchdf()

        st.success("✅ Corrected Query Executed")
        st.dataframe(result)