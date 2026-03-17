import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["product_category_name_english"] = df["product_category_name_english"].fillna("uncategorized")
    df["customer_city"] = df["customer_city"].fillna("unknown")
    df["customer_state"] = df["customer_state"].fillna("unknown")
    return df


df = load_data()

st.title("E-Commerce Public Dataset Dashboard")
st.caption("Dashboard untuk menjawab Pertanyaan 1 dan Pertanyaan 2 secara langsung")

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("Filter Interaktif")

states = sorted(df["customer_state"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "Pilih State",
    options=states,
    default=states
)

year_options = [2018, 2017, 2016, "Semua Tahun"]
selected_year_q1 = st.sidebar.selectbox(
    "Tahun Analisis Q1 (default 2018)",
    options=year_options,
    index=0
)

min_unique_customers = st.sidebar.slider(
    "Minimum unique customers per kota (Q2)",
    min_value=10,
    max_value=100,
    value=30,
    step=5
)

top_n_cities = st.sidebar.slider(
    "Jumlah kota ditampilkan (Q2)",
    min_value=5,
    max_value=20,
    value=10
)

if not selected_states:
    st.warning("Pilih minimal 1 state.")
    st.stop()

# Base filter hanya state
base_df = df[df["customer_state"].isin(selected_states)].copy()
if base_df.empty:
    st.warning("Data kosong setelah filter state.")
    st.stop()

# Date range untuk Q1
if selected_year_q1 != "Semua Tahun":
    q1_date_base = base_df[base_df["order_purchase_timestamp"].dt.year == int(selected_year_q1)].copy()
else:
    q1_date_base = base_df.copy()

if q1_date_base.empty:
    st.warning("Tidak ada data pada kombinasi state dan tahun Q1.")
    st.stop()

min_date = q1_date_base["order_purchase_timestamp"].min().date()
max_date = q1_date_base["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.slider(
    "Rentang Tanggal (Q1)",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# =========================
# Q1 Data: state + year + date
# =========================
q1_df = q1_date_base[
    (q1_date_base["order_purchase_timestamp"].dt.date >= start_date) &
    (q1_date_base["order_purchase_timestamp"].dt.date <= end_date)
].copy()

if q1_df.empty:
    st.warning("Data Q1 kosong untuk kombinasi filter yang dipilih.")
    st.stop()

# KPI (berbasis Q1)
total_revenue = q1_df["revenue"].sum()
total_orders = q1_df["order_id"].nunique()
total_customers = q1_df["customer_unique_id"].nunique()

orders_per_customer = (
    q1_df.groupby("customer_unique_id", as_index=False)["order_id"]
    .nunique()
    .rename(columns={"order_id": "n_orders"})
)
repeat_customers = (orders_per_customer["n_orders"] > 1).sum()
repeat_rate_global = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue (Q1 Filter)", f"R$ {total_revenue:,.2f}")
k2.metric("Total Orders (Q1 Filter)", f"{total_orders:,}")
k3.metric("Unique Customers (Q1 Filter)", f"{total_customers:,}")
k4.metric("Global Repeat Rate (Q1 Filter)", f"{repeat_rate_global:.2f}%")

st.markdown("---")

# =========================
# Pertanyaan 1
# =========================
st.subheader("Pertanyaan 1")
st.write("Kategori produk apa yang menghasilkan revenue tertinggi pada tahun 2018, dan bagaimana trendnya per bulan?")

if selected_year_q1 == "Semua Tahun":
    st.info("Agar presisi untuk Q1, gunakan Tahun Analisis Q1 = 2018.")

cat_rev = (
    q1_df.groupby("product_category_name_english", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

if cat_rev.empty:
    st.warning("Data Q1 tidak tersedia.")
else:
    top_category = cat_rev.iloc[0]["product_category_name_english"]
    top_category_revenue = cat_rev.iloc[0]["revenue"]

    c1, c2 = st.columns(2)
    c1.metric("Kategori Revenue Tertinggi", str(top_category))
    c2.metric("Revenue Kategori Tertinggi", f"R$ {top_category_revenue:,.2f}")

    # Visual 1: Monthly Revenue Trend per Category
    default_categories = cat_rev.head(5)["product_category_name_english"].tolist()
    selected_categories = st.multiselect(
        "Pilih kategori untuk trend bulanan (Q1)",
        options=cat_rev["product_category_name_english"].tolist(),
        default=default_categories
    )

    if selected_categories:
        trend_df = q1_df[q1_df["product_category_name_english"].isin(selected_categories)].copy()
        trend_df["year_month"] = trend_df["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()

        monthly_cat = (
            trend_df.groupby(["year_month", "product_category_name_english"], as_index=False)["revenue"]
            .sum()
            .sort_values("year_month")
        )

        fig_q1_trend = px.line(
            monthly_cat,
            x="year_month",
            y="revenue",
            color="product_category_name_english",
            markers=True,
            title="Monthly Revenue Trend per Category"
        )
        fig_q1_trend.update_layout(
            xaxis_title="Bulan",
            yaxis_title="Revenue (R$)",
            legend_title="Category"
        )
        st.plotly_chart(fig_q1_trend, use_container_width=True)
    else:
        st.info("Pilih minimal 1 kategori untuk menampilkan trend bulanan.")

    # Visual 2: Top 10 Categories by Revenue
    top10_cat = cat_rev.head(10).sort_values("revenue")
    fig_top_cat = px.bar(
        top10_cat,
        x="revenue",
        y="product_category_name_english",
        orientation="h",
        title="Top 10 Categories by Revenue"
    )
    fig_top_cat.update_layout(
        xaxis_title="Revenue (R$)",
        yaxis_title="Category"
    )
    st.plotly_chart(fig_top_cat, use_container_width=True)

st.markdown("---")

# =========================
# Pertanyaan 2 (period fixed 2016-2018)
# =========================
st.subheader("Pertanyaan 2")
st.write("Kota mana yang memiliki repeat customer rate tertinggi selama periode 2016-2018 (dengan minimum 30 unique customers)?")
st.caption("Perhitungan Q2 selalu menggunakan data periode 2016-2018 agar konsisten dengan pertanyaan bisnis.")

q2_df = base_df[base_df["order_purchase_timestamp"].dt.year.between(2016, 2018)].copy()

if q2_df.empty:
    st.warning("Data Q2 kosong pada periode 2016-2018 untuk state terpilih.")
    st.stop()

# Order-level untuk hindari bias item-level
orders_city = q2_df[["order_id", "customer_unique_id", "customer_city"]].drop_duplicates()

cust_city_orders = (
    orders_city.groupby(["customer_city", "customer_unique_id"])["order_id"]
    .nunique()
    .reset_index(name="orders_per_customer")
)

city_summary = cust_city_orders.groupby("customer_city").agg(
    unique_customers=("customer_unique_id", "nunique"),
    repeat_customers=("orders_per_customer", lambda x: (x >= 2).sum()),
    avg_orders_per_customer=("orders_per_customer", "mean")
).reset_index()

city_total_orders = (
    orders_city.groupby("customer_city")["order_id"]
    .nunique()
    .reset_index(name="total_orders")
)

city_summary = city_summary.merge(city_total_orders, on="customer_city", how="left")
city_summary["repeat_rate"] = (
    city_summary["repeat_customers"] / city_summary["unique_customers"] * 100
).round(2)

city_filtered = city_summary[city_summary["unique_customers"] >= min_unique_customers].copy()
city_filtered = city_filtered.sort_values("repeat_rate", ascending=False)

if city_filtered.empty:
    st.warning("Tidak ada kota yang memenuhi minimum unique customers untuk Q2.")
else:
    best_city = city_filtered.iloc[0]

    q2m1, q2m2, q2m3 = st.columns(3)
    q2m1.metric("Kota Repeat Rate Tertinggi", str(best_city["customer_city"]))
    q2m2.metric("Repeat Rate Tertinggi", f"{best_city['repeat_rate']:.2f}%")
    q2m3.metric("Unique Customers (Kota Tertinggi)", f"{int(best_city['unique_customers']):,}")

    # Visual 3: Top Cities by Repeat Customer Rate
    top_repeat = city_filtered.head(top_n_cities).sort_values("repeat_rate")
    fig_repeat = px.bar(
        top_repeat,
        x="repeat_rate",
        y="customer_city",
        orientation="h",
        hover_data=["unique_customers", "repeat_customers", "avg_orders_per_customer", "total_orders"],
        title=f"Top {top_n_cities} Cities by Repeat Customer Rate (2016-2018)"
    )
    fig_repeat.update_layout(
        xaxis_title="Repeat Customer Rate (%)",
        yaxis_title="City"
    )
    st.plotly_chart(fig_repeat, use_container_width=True)

    with st.expander("Tabel ringkasan repeat rate per kota (Q2)"):
        st.dataframe(
            city_filtered[
                ["customer_city", "repeat_rate", "repeat_customers", "unique_customers", "avg_orders_per_customer", "total_orders"]
            ].reset_index(drop=True),
            use_container_width=True
        )