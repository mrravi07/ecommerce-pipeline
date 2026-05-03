import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from textblob import TextBlob

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=60000)

st.set_page_config(layout="wide", page_title="E-Commerce System")

st.markdown("""
<h4 style='color:#00ff88'>
🟢 Live Data Pipeline Running
</h4>
""", unsafe_allow_html=True)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* ---------- BACKGROUND ---------- */
html, body, [class*="css"]  {
    background: linear-gradient(135deg, #0b0f1a, #05070d);
    color: white;
}

/* ---------- GLASS CARD ---------- */
.card {
    padding: 22px;
    border-radius: 20px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}

/* glow effect */
.card::before {
    content: "";
    position: absolute;
    width: 120%;
    height: 120%;
    background: radial-gradient(circle, rgba(255,215,0,0.25), transparent);
    top: -50%;
    left: -50%;
    opacity: 0;
    transition: 0.5s;
}

.card:hover::before {
    opacity: 1;
}

/* hover animation */
.card:hover {
    transform: translateY(-12px) scale(1.04);
    box-shadow: 0px 20px 60px rgba(255,215,0,0.25);
}

.card h4 {
    color: #FFD700;
    font-weight: 600;
}

.card h2 {
    color: white;
    font-weight: 700;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#020617,#0f172a);
}

/* ---------- BUTTONS ---------- */
.stButton>button {
    background: linear-gradient(135deg, #FFD700, #ffae00);
    color: black;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 10px 30px rgba(255,215,0,0.5);
}

/* ---------- INPUT ---------- */
.stTextInput>div>div>input {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    color: white;
}

/* ---------- TAGS ---------- */
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
st.markdown(f"""
<h1 style="
text-align:center;
font-size:48px;
background: linear-gradient(90deg,#FFD700,#ffffff);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
">
Scalable AI E-Commerce Platform
</h1>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
# ---------------- DATA ----------------
df = pd.read_csv("processed_data/clean_orders.csv")

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 🔥 remove future data
from datetime import datetime
df = df[df["timestamp"] <= datetime.now()]

# 🔥 latest time (correct)
latest_time = df["timestamp"].max()

# show in UI
st.markdown(
    f"<p style='color:#FFD700'>🕒 Last Updated: {latest_time.strftime('%d %b %Y, %I:%M %p')}</p>",
    unsafe_allow_html=True
)

# extra columns
df["date"] = df["timestamp"].dt.date
df["hour"] = df["timestamp"].dt.hour

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Feedback", "🤖 Chatbot"])


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
    st.markdown("""
    <h2 style='color:#FFD700;margin-top:20px'>
    📊 Business Overview
    </h2>
    """, unsafe_allow_html=True)

    def card(t, v):
        return f"""
        <div class='card'>
            <h4>{t}</h4>
            <h2>{v}</h2>
        </div>
        """

    margin = (df_f['profit'].sum()/df_f['revenue'].sum()*100) if df_f['revenue'].sum()>0 else 0

    r1 = st.columns(5, gap="large")
    r2 = st.columns(5, gap="large")

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

    # ---------- AI Recommendation ----------
    st.markdown("## 🧠 AI Recommendations")

    if not df_f.empty:
        top_product = df_f.groupby("product")["revenue"].sum().idxmax()
        top_city = df_f.groupby("city")["revenue"].sum().idxmax()
        top_category = df_f.groupby("category")["revenue"].sum().idxmax()
        low_product = df_f.groupby("product")["revenue"].sum().idxmin()

        st.info(f"🔥 Focus more on **{top_product}**")
        st.info(f"📍 Best city: **{top_city}**")
        st.info(f"🛒 Category: **{top_category}**")
        st.warning(f"⚠️ Improve: **{low_product}**")

    # ---------- Alert ----------
    if df_f["revenue"].sum() > 1000000:
        st.warning("🔥 High Sales Alert!")

    # ---------- Graph Style ----------
    # ---------- Graph Style ----------
    def premium_fig(fig):

        fig.update_layout(
            template="plotly_dark",
            transition_duration=800,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(color="white"),
            paper_bgcolor="#05070d",
            plot_bgcolor="#05070d"
        )

        # 👉 Safe styling (no crash)
        if fig.data:
            t = fig.data[0].type

            if t == "scatter":   # line graphs
                fig.update_traces(mode="lines+markers",
                                line=dict(width=3),
                                marker=dict(size=6))

            elif t == "bar":
                fig.update_traces(marker=dict(opacity=0.85))

        return fig


    # ---------- Graphs ----------
    st.markdown("""
    <h2 style='color:#FFD700;margin-top:30px'>
    📊 Advanced Business Insights
    </h2>
    """, unsafe_allow_html=True)


    # ===== ROW 1 =====
    c1, c2 = st.columns(2)

    fig1 = px.line(df_f.groupby("date")["revenue"].sum().reset_index(),
                x="date", y="revenue", title="Revenue Trend")

    fig2 = px.line(df_f.groupby("date")["order_id"].count().reset_index(),
                x="date", y="order_id", title="Orders Trend")

    c1.plotly_chart(premium_fig(fig1), use_container_width=True)
    c2.plotly_chart(premium_fig(fig2), use_container_width=True)


    # ===== ROW 2 =====
    c3, c4 = st.columns(2)

    fig3 = px.bar(df_f.groupby("product")["revenue"].sum().nlargest(10).reset_index(),
                x="product", y="revenue", title="Top Products")

    fig4 = px.pie(df_f, names="category", title="Category Share")

    c3.plotly_chart(premium_fig(fig3), use_container_width=True)
    c4.plotly_chart(premium_fig(fig4), use_container_width=True)


    # ===== ROW 3 =====
    c5, c6 = st.columns(2)

    fig5 = px.bar(df_f.groupby("city")["revenue"].sum().reset_index(),
                x="city", y="revenue", title="City Sales")

    fig6 = px.pie(df_f, names="status", title="Order Status")

    c5.plotly_chart(premium_fig(fig5), use_container_width=True)
    c6.plotly_chart(premium_fig(fig6), use_container_width=True)


    # ===== ROW 4 =====
    c7, c8 = st.columns(2)

    fig7 = px.line(df_f.groupby("date")["profit"].sum().reset_index(),
                x="date", y="profit", title="Profit Trend")

    fig8 = px.histogram(df_f, x="quantity", title="Quantity Distribution")

    c7.plotly_chart(premium_fig(fig7), use_container_width=True)
    c8.plotly_chart(premium_fig(fig8), use_container_width=True)


    # ===== ROW 5 =====
    c9, c10 = st.columns(2)

    fig9 = px.histogram(df_f, x="revenue", title="Revenue Distribution")

    fig10 = px.scatter(df_f, x="price", y="revenue",
                    color="category", title="Price vs Revenue")

    c9.plotly_chart(premium_fig(fig9), use_container_width=True)
    c10.plotly_chart(premium_fig(fig10), use_container_width=True)


    # ===== ROW 6 =====
    c11, c12 = st.columns(2)

    fig11 = px.box(df_f, x="category", y="revenue", title="Revenue Spread")

    fig12 = px.violin(df_f, x="category", y="profit", title="Profit Distribution")

    c11.plotly_chart(premium_fig(fig11), use_container_width=True)
    c12.plotly_chart(premium_fig(fig12), use_container_width=True)


    # ===== ROW 7 =====
    c13, c14 = st.columns(2)

    fig13 = px.bar(df_f.groupby("hour")["revenue"].sum().reset_index(),
                x="hour", y="revenue", title="Hourly Sales")

    fig14 = px.bar(df_f.groupby("hour")["order_id"].count().reset_index(),
                x="hour", y="order_id", title="Orders by Hour")

    c13.plotly_chart(premium_fig(fig13), use_container_width=True)
    c14.plotly_chart(premium_fig(fig14), use_container_width=True)


    # ===== ROW 8 =====
    c15, c16 = st.columns(2)

    fig15 = px.bar(df_f.groupby("category")["profit"].sum().reset_index(),
                x="category", y="profit", title="Profit by Category")

    fig16 = px.bar(df_f.groupby("city")["profit"].sum().reset_index(),
                x="city", y="profit", title="Profit by City")

    c15.plotly_chart(premium_fig(fig15), use_container_width=True)
    c16.plotly_chart(premium_fig(fig16), use_container_width=True)


    # ---------- Forecast ----------
    from statsmodels.tsa.arima.model import ARIMA

    st.markdown("## 📈 Sales Forecast")

    try:
        df_trend = df_f.groupby("date")["revenue"].sum().reset_index()

        if len(df_trend) > 10:
            model = ARIMA(df_trend["revenue"], order=(2,1,2)).fit()
            forecast = model.forecast(steps=7)

            future_dates = pd.date_range(df_trend["date"].max(), periods=7)

            fig_f = px.line(df_trend, x="date", y="revenue")
            fig_f.add_scatter(x=future_dates, y=forecast)

            st.plotly_chart(fig_f, use_container_width=True)
        else:
            st.warning("Not enough data")

    except:
        st.error("Forecast error")

    # ---------- TABLE ----------
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

# ================= CHATBOT =================
with tab3:

    st.markdown("## 🤖 Smart Business Assistant")

    # -------- SESSION --------
    if "chat" not in st.session_state:
        st.session_state.chat = []

    # -------- INTENT --------
    def parse_intent(q):
        q = q.lower()

        if "revenue" in q or "sales" in q: return "revenue"
        if "order" in q: return "orders"
        if "profit" in q or "margin" in q: return "profit"
        if "trend" in q or "graph" in q: return "trend"
        if "city" in q: return "city"
        if "category" in q: return "category"
        if "top" in q or "best" in q: return "top_product"
        if "low" in q or "worst" in q: return "low_product"
        if "recommend" in q or "suggest" in q: return "recommend"
        if "forecast" in q or "future" in q: return "forecast"

        return "unknown"

    # -------- ANSWERS --------
    def answer_intent(intent, df):

        if intent == "revenue":
            total = df['revenue'].sum()
            avg = df['revenue'].mean()
            return f"💰 Revenue: ₹{total:,}\n🧾 Avg Order: ₹{avg:,.0f}"

        if intent == "orders":
            return f"📦 Orders: {len(df)}"

        if intent == "profit":
            profit = df['profit'].sum()
            margin = (profit/df['revenue'].sum()*100) if df['revenue'].sum()>0 else 0
            return f"📈 Profit: ₹{profit:,.0f} | Margin: {margin:.2f}%"

        if intent == "top_product":
            top = df.groupby("product")["revenue"].sum().idxmax()
            val = df.groupby("product")["revenue"].sum().max()
            return f"🔥 Top Product: {top}\n💰 Sales: ₹{val:,}"

        if intent == "low_product":
            low = df.groupby("product")["revenue"].sum().idxmin()
            return f"⚠️ Low Product: {low}"

        if intent == "city":
            city = df.groupby("city")["revenue"].sum().idxmax()
            return f"📍 Best City: {city}"

        if intent == "category":
            cat = df.groupby("category")["revenue"].sum().idxmax()
            return f"🛒 Best Category: {cat}"

        if intent == "recommend":
            top = df.groupby("product")["revenue"].sum().idxmax()
            low = df.groupby("product")["revenue"].sum().idxmin()
            city = df.groupby("city")["revenue"].sum().idxmax()

            return f"""
🎯 Recommendation:
• Focus on {top}
• Improve {low}
• Expand in {city}
"""

        if intent == "trend":
            return "📊 Showing revenue trend..."

        if intent == "forecast":
            return "📈 Showing future sales prediction..."

        return "🤖 Try: revenue, orders, profit, trend, city, category, top product"

    # -------- GRAPH --------
    def show_graph(intent, df):

        if intent == "trend":
            fig = px.line(df.groupby("date")["revenue"].sum().reset_index(),
                          x="date", y="revenue")
            st.plotly_chart(fig, use_container_width=True)

        elif intent == "city":
            fig = px.bar(df.groupby("city")["revenue"].sum().reset_index(),
                         x="city", y="revenue")
            st.plotly_chart(fig, use_container_width=True)

        elif intent == "category":
            fig = px.pie(df, names="category")
            st.plotly_chart(fig, use_container_width=True)

        elif intent == "forecast":
            try:
                from statsmodels.tsa.arima.model import ARIMA
                df_trend = df.groupby("date")["revenue"].sum().reset_index()

                if len(df_trend) > 10:
                    model = ARIMA(df_trend["revenue"], order=(2,1,2)).fit()
                    forecast = model.forecast(steps=7)

                    future_dates = pd.date_range(df_trend["date"].max(), periods=7)

                    fig = px.line(df_trend, x="date", y="revenue")
                    fig.add_scatter(x=future_dates, y=forecast)

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Not enough data")
            except:
                st.warning("Forecast not available")

    # -------- MAIN --------
    def get_response(q, df):
        intent = parse_intent(q)
        return answer_intent(intent, df), intent

    # -------- QUICK --------
    st.markdown("### ⚡ Quick Actions")

    b1, b2, b3, b4 = st.columns(4)

    if b1.button("💰 Revenue"):
        st.session_state.chat.append(("Revenue", get_response("revenue", df_f)[0]))

    if b2.button("📊 Trend"):
        st.session_state.chat.append(("Trend", "📊 Showing trend..."))
        show_graph("trend", df_f)

    if b3.button("🔥 Top Product"):
        st.session_state.chat.append(("Top Product", get_response("top product", df_f)[0]))

    if b4.button("🎯 Recommend"):
        st.session_state.chat.append(("Recommendation", get_response("recommend", df_f)[0]))

    # -------- INPUT --------
    user_q = st.text_input("💬 Ask anything...", key="chat_input")

    col1, col2 = st.columns([4,1])
    with col1:
        ask = st.button("🚀 Ask")
    with col2:
        clear = st.button("🧹 Clear")

    if ask and user_q:
        ans, intent = get_response(user_q, df_f)
        st.session_state.chat.append((user_q, ans))

        if intent in ["trend", "city", "category", "forecast"]:
            show_graph(intent, df_f)

    if clear:
        st.session_state.chat = []

    # -------- DISPLAY --------
    st.markdown("### 🧠 Conversation")

    for q, a in st.session_state.chat[::-1]:
        st.markdown(f"🧑 **You:** {q}")
        st.markdown(f"🤖 **Bot:** {a}")