import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["product_category_name_english"] = df["product_category_name_english"].fillna("uncategorized")
    return df


df = load_data()

st.title("E-Commerce Public Dataset Dashboard")
st.caption("Analisis performa revenue, kategori produk, dan loyalitas pelanggan")

# Sidebar filters
st.sidebar.header("Filter")

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.slider(
    "Rentang tanggal",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

states = sorted(df["customer_state"].dropna().unique().tolist())
select_all_states = st.sidebar.checkbox("Pilih semua state", value=True)

if select_all_states:
    selected_states = states
else:
    selected_states = st.sidebar.multiselect(
        "Pilih state",
        options=states,
        default=[]
    )

filtered = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["customer_state"].isin(selected_states))
].copy()

if filtered.empty:
    st.warning("Data kosong untuk filter yang dipilih. Coba perluas rentang tanggal atau pilih state lain.")
    st.stop()
    
# KPI metrics
total_revenue = filtered["revenue"].sum()
total_orders = filtered["order_id"].nunique()
total_customers = filtered["customer_unique_id"].nunique()

orders_per_customer = (
    filtered.groupby("customer_unique_id", as_index=False)["order_id"]
    .nunique()
    .rename(columns={"order_id": "n_orders"})
)
repeat_customers = (orders_per_customer["n_orders"] > 1).sum()
repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Unique Customers", f"{total_customers:,}")
col4.metric("Repeat Customer Rate", f"{repeat_rate:.2f}%")

st.markdown("---")

# Monthly revenue trend (FIX)
monthly_rev = (
    filtered.assign(
        year_month=filtered["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )
    .groupby("year_month", as_index=False)["revenue"]
    .sum()
    .sort_values("year_month")
)

fig_monthly = px.line(
    monthly_rev,
    x="year_month",
    y="revenue",
    markers=True,
    title="Monthly Revenue Trend"
)
fig_monthly.update_layout(xaxis_title="Year-Month", yaxis_title="Revenue (R$)")
st.plotly_chart(fig_monthly, use_container_width=True)

# Top categories and top cities
col_left, col_right = st.columns(2)

top_categories = (
    filtered.groupby("product_category_name_english", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(10)
)

fig_cat = px.bar(
    top_categories.sort_values("revenue"),
    x="revenue",
    y="product_category_name_english",
    orientation="h",
    title="Top 10 Product Categories by Revenue"
)
fig_cat.update_layout(xaxis_title="Revenue (R$)", yaxis_title="Category")
col_left.plotly_chart(fig_cat, use_container_width=True)

top_cities = (
    filtered.groupby("customer_city", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_unique_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
    .head(10)
)

fig_city = px.bar(
    top_cities.sort_values("revenue"),
    x="revenue",
    y="customer_city",
    orientation="h",
    title="Top 10 Cities by Revenue"
)
fig_city.update_layout(xaxis_title="Revenue (R$)", yaxis_title="City")
col_right.plotly_chart(fig_city, use_container_width=True)

# Optional raw data
with st.expander("Lihat data terfilter"):
    st.dataframe(filtered.head(200), use_container_width=True)