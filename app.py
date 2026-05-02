import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from textblob import TextBlob

st.set_page_config(layout="wide", page_title="E-Commerce System")

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong credentials")

    st.stop()

# ---------------- TITLE ----------------
title = "🚀 E-Commerce Analytics System"
ph = st.empty()
for i in range(len(title)+1):
    ph.markdown(f"<h1 style='text-align:center;color:#FFD700'>{title[:i]}</h1>", unsafe_allow_html=True)
    time.sleep(0.02)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("processed_data/clean_orders.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date
df["hour"] = df["timestamp"].dt.hour

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Feedback"])

# ================= DASHBOARD =================
with tab1:

    # -------- FILTERS --------
    st.sidebar.title("Filters")

    products = st.sidebar.multiselect("Product", df["product"].unique(), df["product"].unique()[:10])
    categories = st.sidebar.multiselect("Category", df["category"].unique(), df["category"].unique())
    cities = st.sidebar.multiselect("City", df["city"].unique(), df["city"].unique())
    statuses = st.sidebar.multiselect("Status", df["status"].unique(), df["status"].unique())

    hours = st.sidebar.slider("Hour", 0, 23, (0, 23))
    date_range = st.sidebar.date_input("Date", [df["date"].min(), df["date"].max()])

    # -------- FILTER APPLY --------
    df_f = df[
        (df["product"].isin(products)) &
        (df["category"].isin(categories)) &
        (df["city"].isin(cities)) &
        (df["status"].isin(statuses)) &
        (df["hour"] >= hours[0]) &
        (df["hour"] <= hours[1]) &
        (df["date"] >= date_range[0]) &
        (df["date"] <= date_range[1])
    ]

    # -------- KPI --------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"₹{df_f['revenue'].sum():,}")
    col2.metric("Orders", len(df_f))
    col3.metric("Customers", df_f["customer_id"].nunique())
    col4.metric("Avg Order", f"₹{df_f['revenue'].mean():,.2f}")

    # -------- STATUS KPI --------
    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Placed", len(df_f[df_f["status"]=="Placed"]))
    col6.metric("Cancelled", len(df_f[df_f["status"]=="Cancelled"]))
    col7.metric("Scheduled", len(df_f[df_f["is_scheduled"]==True]))
    col8.metric("Delivered", len(df_f[df_f["status"]=="Delivered"]))

    # -------- PROFIT --------
    col9, col10 = st.columns(2)

    col9.metric("Total Profit", f"₹{df_f['profit'].sum():,.0f}")
    margin = (df_f['profit'].sum()/df_f['revenue'].sum())*100 if df_f['revenue'].sum()>0 else 0
    col10.metric("Profit %", f"{margin:.2f}%")

    # -------- CHARTS --------
    st.subheader("Revenue Trend")
    st.plotly_chart(px.line(df_f.groupby("date")["revenue"].sum().reset_index(), x="date", y="revenue"))

    st.subheader("Order Status")
    st.plotly_chart(px.pie(df_f, names="status"))

    st.subheader("Top Products")
    top = df_f.groupby("product")["revenue"].sum().nlargest(10).reset_index()
    st.plotly_chart(px.bar(top, x="product", y="revenue"))

# ================= FEEDBACK =================
with tab2:

    # LOAD FILE
    if os.path.exists("feedback.csv"):
        fb = pd.read_csv("feedback.csv")
    else:
        fb = pd.DataFrame(columns=["product","rating","review"])

    st.subheader("Give Feedback")

    with st.form("f"):
        p = st.selectbox("Product", df["product"].unique())
        r = st.slider("Rating", 1, 5)
        rev = st.text_area("Review")

        if st.form_submit_button("Submit"):
            new = pd.DataFrame([[p,r,rev]], columns=["product","rating","review"])
            new.to_csv("feedback.csv", mode="a", header=not os.path.exists("feedback.csv"), index=False)
            st.success("Saved!")

    # -------- SENTIMENT --------
    def senti(x):
        pol = TextBlob(str(x)).sentiment.polarity
        return "Positive" if pol>0 else "Negative" if pol<0 else "Neutral"

    if not fb.empty:
        fb["sentiment"] = fb["review"].apply(senti)

        st.subheader("Sentiment")
        st.plotly_chart(px.pie(fb, names="sentiment"))

        st.subheader("Ratings")
        st.plotly_chart(px.histogram(fb, x="rating"))

        st.dataframe(fb.tail(20))