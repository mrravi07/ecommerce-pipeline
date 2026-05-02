import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Pro Dashboard")

# Load data
url = "https://raw.githubusercontent.com/mrravi07/ecommerce-pipeline/main/processed_data/clean_orders.csv"
df = pd.read_csv(url, low_memory=False)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# ---------------- FILTERS ----------------
st.sidebar.title("🔍 Filters")

products = st.sidebar.multiselect("Product", df["product"].unique(), df["product"].unique())
cities = st.sidebar.multiselect("City", df["city"].unique(), df["city"].unique())

date_range = st.sidebar.date_input("Date Range", [df["date"].min(), df["date"].max()])

df = df[(df["product"].isin(products)) & (df["city"].isin(cities))]

# ---------------- TITLE ----------------
st.title("🚀 Pro E-Commerce Analytics Dashboard")

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"₹{int(df['revenue'].sum())}")
col2.metric("Orders", len(df))
col3.metric("Customers", df["customer_id"].nunique())
col4.metric("Avg Order", round(df["revenue"].mean(), 2))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Max Revenue", df["revenue"].max())
col6.metric("Min Revenue", df["revenue"].min())
col7.metric("Total Qty", df["quantity"].sum())
col8.metric("Unique Products", df["product"].nunique())

# ---------------- GRAPHS ----------------

st.subheader("📈 Revenue Trend")
st.plotly_chart(px.line(df.groupby("date")["revenue"].sum().reset_index(), x="date", y="revenue"), use_container_width=True)

st.subheader("📊 Orders Trend")
st.plotly_chart(px.line(df.groupby("date")["order_id"].count().reset_index(), x="date", y="order_id"), use_container_width=True)

st.subheader("🛒 Product Revenue")
st.plotly_chart(px.bar(df.groupby("product")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False).head(20),
                       x="product", y="revenue"), use_container_width=True)

st.subheader("🥧 Category Share")
st.plotly_chart(px.pie(df, names="category", values="revenue"), use_container_width=True)

st.subheader("📍 City Sales")
st.plotly_chart(px.bar(df.groupby("city")["revenue"].sum().reset_index(), x="city", y="revenue"), use_container_width=True)

st.subheader("📊 Quantity Distribution")
st.plotly_chart(px.histogram(df, x="quantity"), use_container_width=True)

st.subheader("🔥 Top 10 Products")
top = df.groupby("product")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
st.plotly_chart(px.bar(top, x="product", y="revenue"), use_container_width=True)

st.subheader("📉 Revenue Distribution")
st.plotly_chart(px.histogram(df, x="revenue"), use_container_width=True)

st.subheader("📊 Scatter Analysis")
st.plotly_chart(px.scatter(df, x="price", y="revenue", color="category"), use_container_width=True)

st.subheader("📅 Orders per City")
st.plotly_chart(px.line(df.groupby(["date", "city"])["order_id"].count().reset_index(),
                        x="date", y="order_id", color="city"), use_container_width=True)

st.subheader("📄 Data Table")
st.dataframe(df.tail(100))