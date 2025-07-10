import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="PhonePe Dashboard")

# Database connection
conn = sqlite3.connect("phonepe_full_data.db")

# Header
st.title("PhonePe Transaction Insights Dashboard")
st.markdown("An interactive visualization of transaction data across India using PhonePe Pulse.")

# Sidebar Filters
st.sidebar.header("Filter Data")
selected_state = st.sidebar.selectbox("Select State", ["All"] + list(
    pd.read_sql("SELECT DISTINCT state FROM aggregated_transaction", conn)['state']))
selected_year = st.sidebar.selectbox("Select Year", ["All"] + list(
    pd.read_sql("SELECT DISTINCT year FROM aggregated_transaction", conn)['year']))
selected_quarter = st.sidebar.selectbox("Select Quarter", ["All", "Q1", "Q2", "Q3", "Q4"])

# Query Building
query = "SELECT * FROM aggregated_transaction WHERE 1=1"
if selected_state != "All":
    query += f" AND state = '{selected_state}'"
if selected_year != "All":
    query += f" AND year = {selected_year}"
if selected_quarter != "All":
    quarter_map = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    query += f" AND quarter = {quarter_map[selected_quarter]}"
df = pd.read_sql(query, conn)

# KPIs
total_txn = df['amount'].sum()
total_count = df['count'].sum()
st.markdown("### Key Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Transaction Value (INR)", f"₹ {total_txn:,.0f}")
col2.metric("Total Transaction Count", f"{total_count:,}")

# Top States by Amount
st.markdown("### Top States by Total Transaction Amount")
df_state_amt = pd.read_sql("""
    SELECT state, SUM(amount) AS total_amount
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY total_amount DESC
    LIMIT 10
""", conn)
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_state_amt, x="total_amount", y="state", palette="Set2", ax=ax1)
ax1.set_title("Top 10 States by Transaction Amount")
st.pyplot(fig1)

# Top States by Count
st.markdown("### Top States by Transaction Count")
df_state_count = pd.read_sql("""
    SELECT state, SUM(count) AS total_count
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY total_count DESC
    LIMIT 10
""", conn)
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_state_count, x="total_count", y="state", palette="Set2", ax=ax2)
ax2.set_title("Top 10 States by Transaction Count")
st.pyplot(fig2)

# Year-wise Growth Trend
st.markdown("### Year-wise Growth in Transaction Value")
df_yearly = df.groupby('year')['amount'].sum().reset_index()
fig3, ax3 = plt.subplots(figsize=(8, 4))
sns.lineplot(data=df_yearly, x='year', y='amount', marker='o', color='green', ax=ax3)
ax3.set_title("Year-wise Transaction Growth")
st.pyplot(fig3)

# Transaction Type Breakdown
st.markdown("### Transaction Type Distribution")
df_types = df.groupby("transaction_type")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
fig4, ax4 = plt.subplots(figsize=(8, 5))
sns.barplot(data=df_types, x="amount", y="transaction_type", palette="Set2", ax=ax4)
ax4.set_title("Transaction Amount by Type")
st.pyplot(fig4)

# Average Transaction Size by State
st.markdown("### Top States by Average Transaction Size")
df_avg_txn = pd.read_sql("""
    SELECT state, SUM(amount)*1.0 / SUM(count) AS avg_txn_size
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY avg_txn_size DESC
    LIMIT 10
""", conn)
fig5, ax5 = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_avg_txn, x="avg_txn_size", y="state", palette="Set2", ax=ax5)
ax5.set_title("Average Transaction Size by State")
st.pyplot(fig5)

# -------------------- NEW SECTION: QUARTER-WISE TOTAL TRANSACTIONS --------------------
st.markdown("### Quarter-wise Transaction Volume")
df_quarter = pd.read_sql("""
    SELECT quarter, SUM(amount) AS total_amount
    FROM aggregated_transaction
    GROUP BY quarter
    ORDER BY quarter
""", conn)

fig7, ax7 = plt.subplots(figsize=(8, 4))
sns.barplot(data=df_quarter, x="quarter", y="total_amount", palette="Set2", ax=ax7)
ax7.set_title("Total Transaction Amount by Quarter")
st.pyplot(fig7)

# -------------------- NEW SECTION: HEATMAP OF TRANSACTIONS BY STATE AND YEAR --------------------
st.markdown("### Heatmap of Transaction Value by State and Year")
df_heat = pd.read_sql("""
    SELECT state, year, SUM(amount) AS amount
    FROM aggregated_transaction
    GROUP BY state, year
""", conn)

pivot_df = df_heat.pivot(index="state", columns="year", values="amount")
fig8, ax8 = plt.subplots(figsize=(12, 10))
sns.heatmap(pivot_df, cmap="YlGnBu", annot=True, fmt=".0f", linewidths=0.5, ax=ax8)
ax8.set_title("Heatmap: State vs Year - Transaction Amount")
st.pyplot(fig8)

# Raw Data
with st.expander("Show Filtered Raw Data"):
    st.dataframe(df)

# Footer
st.markdown("---")
st.markdown("Developed by Akash | Powered by Streamlit and PhonePe Pulse")
