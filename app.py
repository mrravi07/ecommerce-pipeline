import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from textblob import TextBlob

st.set_page_config(layout="wide", page_title="E-Commerce System")

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 18px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,215,0,0.3);
    text-align: center;
    transition: 0.4s ease;
}
.card:hover {
    transform: translateY(-10px) scale(1.05);
    box-shadow: 0px 10px 40px rgba(255,215,0,0.5);
}
.card h4 { color: #FFD700; }
.card h2 { color: white; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#020617,#0f172a);
}

div[data-baseweb="tag"] {
    background-color: #ff4b4b !important;
    border-radius: 10px !important;
}
div[data-baseweb="tag"]:hover {
    background-color: #FFD700 !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid")

    st.stop()

# ---------------- TITLE ----------------
title = "Scalable Real-Time E-Commerce Data Pipeline"
ph = st.empty()
for i in range(len(title)+1):
    ph.markdown(f"<h1 style='text-align:center;color:#FFD700'>{title[:i]}</h1>", unsafe_allow_html=True)
    time.sleep(0.02)

# ---------------- DATA ----------------
df = pd.read_csv("processed_data/clean_orders.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date
df["hour"] = df["timestamp"].dt.hour

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Feedback"])

# ================= DASHBOARD =================
with tab1:

    # ---------- SIDEBAR ----------
    st.sidebar.markdown("<h2 style='color:#FFD700'>⚡ Smart Filters</h2>", unsafe_allow_html=True)

    products = st.sidebar.multiselect("Product", df["product"].unique(), df["product"].unique()[:10])
    categories = st.sidebar.multiselect("Category", df["category"].unique(), df["category"].unique())
    cities = st.sidebar.multiselect("City", df["city"].unique(), df["city"].unique())
    statuses = st.sidebar.multiselect("Status", df["status"].unique(), df["status"].unique())

    hours = st.sidebar.slider("Hour", 0, 23, (0, 23))
    date_range = st.sidebar.date_input("Date", [df["date"].min(), df["date"].max()])

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

    # ---------- KPI CARDS ----------
    def card(t, v):
        return f"<div class='card'><h4>{t}</h4><h2>{v}</h2></div>"

    margin = (df_f['profit'].sum()/df_f['revenue'].sum()*100) if df_f['revenue'].sum()>0 else 0

    r1 = st.columns(5)
    r2 = st.columns(5)

    r1[0].markdown(card("Revenue", f"₹{df_f['revenue'].sum():,}"), True)
    r1[1].markdown(card("Orders", len(df_f)), True)
    r1[2].markdown(card("Customers", df_f["customer_id"].nunique()), True)
    r1[3].markdown(card("Avg Order", f"₹{df_f['revenue'].mean():,.0f}"), True)
    r1[4].markdown(card("Profit", f"₹{df_f['profit'].sum():,.2f}"), True)

    r2[0].markdown(card("Placed", len(df_f[df_f["status"]=="Placed"])), True)
    r2[1].markdown(card("Cancelled", len(df_f[df_f["status"]=="Cancelled"])), True)
    r2[2].markdown(card("Scheduled", len(df_f[df_f["is_scheduled"]==True])), True)
    r2[3].markdown(card("Delivered", len(df_f[df_f["status"]=="Delivered"])), True)
    r2[4].markdown(card("Profit %", f"{margin:.2f}%"), True)


# ---------- GRAPH STYLE FUNCTION ----------
def premium_fig(fig):
    fig.update_layout(
        template="plotly_dark",
        transition_duration=800,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(color="white"),
        paper_bgcolor="#0b0f1a",
        plot_bgcolor="#0b0f1a"
    )
    return fig


# ---------- GRAPHS ----------
st.markdown("## 📊 Advanced Business Insights")

# ROW 1
c1, c2 = st.columns(2)

fig1 = px.line(df_f.groupby("date")["revenue"].sum().reset_index(), x="date", y="revenue", title="Revenue Trend")
fig1.update_traces(mode="lines+markers", line=dict(width=3, color="#FFD700"))
c1.plotly_chart(premium_fig(fig1), use_container_width=True)

fig2 = px.line(df_f.groupby("date")["order_id"].count().reset_index(), x="date", y="order_id", title="Orders Trend")
fig2.update_traces(mode="lines+markers", line=dict(width=3, color="#00E5FF"))
c2.plotly_chart(premium_fig(fig2), use_container_width=True)


# ROW 2
c3, c4 = st.columns(2)

fig3 = px.bar(df_f.groupby("product")["revenue"].sum().nlargest(10).reset_index(),
              x="product", y="revenue", title="Top Products")
fig3.update_traces(marker_color="#FFD700")
c3.plotly_chart(premium_fig(fig3), use_container_width=True)

fig4 = px.pie(df_f, names="category", title="Category Share")
fig4.update_traces(textinfo="percent+label")
c4.plotly_chart(premium_fig(fig4), use_container_width=True)


# ROW 3
c5, c6 = st.columns(2)

fig5 = px.bar(df_f.groupby("city")["revenue"].sum().reset_index(),
              x="city", y="revenue", title="City Sales")
fig5.update_traces(marker_color="#00E5FF")
c5.plotly_chart(premium_fig(fig5), use_container_width=True)

fig6 = px.pie(df_f, names="status", title="Order Status")
c6.plotly_chart(premium_fig(fig6), use_container_width=True)


# ROW 4
c7, c8 = st.columns(2)

fig7 = px.line(df_f.groupby("date")["profit"].sum().reset_index(),
               x="date", y="profit", title="Profit Trend")
fig7.update_traces(mode="lines+markers", line=dict(width=3, color="#00FFAA"))
c7.plotly_chart(premium_fig(fig7), use_container_width=True)

fig8 = px.histogram(df_f, x="quantity", title="Quantity Distribution")
c8.plotly_chart(premium_fig(fig8), use_container_width=True)


# ROW 5
c9, c10 = st.columns(2)

fig9 = px.histogram(df_f, x="revenue", title="Revenue Distribution")
c9.plotly_chart(premium_fig(fig9), use_container_width=True)

fig10 = px.scatter(df_f, x="price", y="revenue", color="category", title="Price vs Revenue")
c10.plotly_chart(premium_fig(fig10), use_container_width=True)


# ROW 6
c11, c12 = st.columns(2)

fig11 = px.box(df_f, x="category", y="revenue", title="Revenue Spread")
c11.plotly_chart(premium_fig(fig11), use_container_width=True)

fig12 = px.violin(df_f, x="category", y="profit", title="Profit Distribution")
c12.plotly_chart(premium_fig(fig12), use_container_width=True)


# ROW 7
c13, c14 = st.columns(2)

fig13 = px.bar(df_f.groupby("hour")["revenue"].sum().reset_index(),
               x="hour", y="revenue", title="Hourly Sales")
c13.plotly_chart(premium_fig(fig13), use_container_width=True)

fig14 = px.bar(df_f.groupby("hour")["order_id"].count().reset_index(),
               x="hour", y="order_id", title="Orders by Hour")
c14.plotly_chart(premium_fig(fig14), use_container_width=True)


# ROW 8
c15, c16 = st.columns(2)

fig15 = px.bar(df_f.groupby("category")["profit"].sum().reset_index(),
               x="category", y="profit", title="Profit by Category")
c15.plotly_chart(premium_fig(fig15), use_container_width=True)

fig16 = px.bar(df_f.groupby("city")["profit"].sum().reset_index(),
               x="city", y="profit", title="Profit by City")
c16.plotly_chart(premium_fig(fig16), use_container_width=True)


# FINAL TABLE
st.dataframe(df_f.tail(100))


# ================= FEEDBACK =================
with tab2:

    st.markdown("## 💬 Customer Reviews")

    # 🔥 IMPORTANT CHANGE
    df_reviews = df.copy()   # orders.csv वाला data use

    if df_reviews.empty:
        st.info("No reviews available")
    else:

        # -------- PRODUCT SELECT --------
        product = st.selectbox("Select Product", sorted(df_reviews["product"].unique()))

        df_p = df_reviews[df_reviews["product"] == product]

        # -------- KPI --------
        avg_rating = df_p["rating"].mean()
        total_reviews = len(df_p)

        col1, col2 = st.columns(2)
        col1.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
        col2.metric("💬 Total Reviews", total_reviews)

        # -------- REVIEWS --------
        st.markdown("### 📝 Customer Reviews")

        for _, row in df_p.iterrows():
            stars = "⭐" * int(row["rating"])

            st.markdown(f"""
            <div style="
                padding:15px;
                margin-bottom:10px;
                border-radius:12px;
                background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,215,0,0.2);
            ">
                <h4 style='color:#FFD700'>{row["product"]}</h4>
                <p>{stars}</p>
                <p>{row["review"]}</p>
            </div>
            """, unsafe_allow_html=True)