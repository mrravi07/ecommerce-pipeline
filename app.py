import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
from textblob import TextBlob
import random

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
    background: #1f2937;
    color: #e5e7eb;
    border-radius: 10px;
    border: 1px solid #374151;
    font-weight: 500;
    transition: 0.25s;
}

.stButton>button:hover {
    background: #374151;
    transform: translateY(-2px);
}

/* ---------- INPUT ---------- */
.stTextInput>div>div>input {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
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

/* ---------- TABS CONTAINER ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background: rgba(255,255,255,0.03);
    padding: 10px;
    border-radius: 14px;
    backdrop-filter: blur(12px);
}

/* ---------- TAB ---------- */
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 8px 18px;
    color: #aaa;
    transition: all 0.3s ease;
    font-weight: 500;
}

/* hover */
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.1);
    color: white;
}

/* active tab */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FFD700, #ffae00);
    color: black !important;
    font-weight: 600;
    box-shadow: 0px 5px 20px rgba(255,215,0,0.5);
    transform: scale(1.05);
}

/* remove default border */
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)




# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login")

    # ✅ form start
    with st.form("login_form"):

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

    # ✅ handle submit (Enter + Button both)
    if submit:
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")

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

# ---------- NAME GENERATOR ----------
first_names = [
    "Aarav","Vivaan","Aditya","Arjun","Reyansh","Ishaan","Kabir","Rohan","Yash","Krishna",
    "Ananya","Diya","Priya","Neha","Simran","Pooja","Sneha","Kiran","Meera","Ritika",
    "Rahul","Aman","Varun","Sahil","Nikhil","Akash","Deepak","Ritesh","Manish","Vikas",
    "Shreya","Kavya","Isha","Naina","Sanya","Tanvi","Muskan","Komal","Riya","Payal"
]

last_names = [
    "Sharma","Verma","Gupta","Singh","Yadav","Mishra","Tiwari","Pandey","Dubey","Chauhan",
    "Patel","Mehta","Jain","Agarwal","Bansal","Kumar","Das","Reddy","Iyer","Nair",
    "Khan","Ansari","Sheikh","Malik","Qureshi","Kapoor","Khanna","Arora","Gill","Sandhu",
    "Joshi","Thakur","Chopra","Saxena","Tripathi","Pillai","Menon","Kulkarni","Deshmukh","Ghosh"
]

def generate_names(n=600):
    return list(set(
        random.choice(first_names) + " " + random.choice(last_names)
        for _ in range(n)
    ))

# ================= TAB 2 =================

with tab2:

    st.markdown("## 💬 Customer Reviews Dashboard")

    df_reviews = df.copy()

    if df_reviews.empty:
        st.info("No reviews available")
    else:

        # -------- PRODUCT SELECT --------
        product = st.selectbox("Select Product", sorted(df_reviews["product"].unique()))
        df_p = df_reviews[df_reviews["product"] == product].copy()

        # -------- CUSTOMER NAME (FIXED) --------
        names = generate_names(600)
       # ---------- UNIQUE NAMES ----------
        names = generate_names(2000)  # ज्यादा names generate करो

        df_p["customer_name"] = random.sample(
            names * (len(df_p)//len(names) + 1),  # repeat list safely
            len(df_p)
        )

        # -------- PRODUCT-WISE REVIEW COUNT --------
        if "review_counts" not in st.session_state:
            st.session_state.review_counts = {}

        if product not in st.session_state.review_counts:
            st.session_state.review_counts[product] = random.randint(150, 900)

        review_count = st.session_state.review_counts[product]

        # -------- SAMPLING --------
        df_p = df_p.sample(n=review_count, replace=True)

        # ---------- REALISTIC RATING DISTRIBUTION ----------
        weights = [0.1, 0.15, 0.2, 0.3, 0.25]  # 1⭐ → 5⭐

        df_p["rating"] = random.choices(
            [1,2,3,4,5],
            weights=weights,
            k=len(df_p)
        )

        # -------- KPI --------
        avg_rating = df_p["rating"].mean()
        total_reviews = len(df_p)

        col1, col2, col3 = st.columns(3)
        col1.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
        col2.metric("💬 Reviews", total_reviews)
        col3.metric("👍 Positive %", f"{(df_p['rating']>=4).mean()*100:.0f}%")

        # ===============================
        # 📊 GRAPH
        # ===============================
        st.markdown("### 📊 Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.bar_chart(df_p["rating"].value_counts().sort_index())

        with col2:
            df_p["sentiment"] = df_p["rating"].apply(
                lambda r: "Positive" if r >= 4 else "Neutral" if r == 3 else "Negative"
            )
            st.bar_chart(df_p["sentiment"].value_counts())

        # ===============================
        # 🔎 FILTER
        # ===============================
        st.markdown("### 🔎 Filter Reviews")

        col1, col2 = st.columns(2)

        with col1:
            rating_filter = st.selectbox("Filter by Rating", ["All", "4⭐+", "3⭐", "Below 3"])

        with col2:
            search_text = st.text_input("Search keyword")

        df_filtered = df_p.copy()

        if rating_filter == "4⭐+":
            df_filtered = df_filtered[df_filtered["rating"] >= 4]
        elif rating_filter == "3⭐":
            df_filtered = df_filtered[df_filtered["rating"] == 3]
        elif rating_filter == "Below 3":
            df_filtered = df_filtered[df_filtered["rating"] < 3]

        if search_text:
            df_filtered = df_filtered[df_filtered["review"].str.contains(search_text, case=False, na=False)]

        # fallback if too few
        if len(df_filtered) < 20:
            st.warning("Too few reviews after filter — showing more data")
            df_filtered = df_p

        # ===============================
        # 🤖 SUMMARY
        # ===============================
        st.markdown("### 🤖 Quick Summary")

        top_positive = df_filtered[df_filtered["rating"] >= 4]["review"].drop_duplicates().head(3)
        top_negative = df_filtered[df_filtered["rating"] < 3]["review"].drop_duplicates().head(3)

        st.info(f"""
👍 What customers like:
- {"\n- ".join(top_positive)}

⚠️ Issues:
- {"\n- ".join(top_negative)}
""")

        # ===============================
        # 📝 REVIEWS
        st.markdown("### 📝 Reviews")

        # ---------- SCROLLABLE CONTAINER ----------
        st.markdown("""
        <div style="max-height:500px; overflow-y:auto; padding-right:10px;">
        """, unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():

            stars = "⭐" * int(row["rating"])

            # color based on rating
            if row["rating"] >= 4:
                color = "#22c55e"
            elif row["rating"] == 3:
                color = "#f59e0b"
            else:
                color = "#ef4444"

            st.markdown(f"""
            <div style="
                background:#111827;
                padding:12px;
                margin-bottom:10px;
                border-radius:10px;
                border-left:4px solid {color};
            ">
                <b style="color:#60a5fa;">{row['customer_name']}</b>
                <span style="float:right; color:#facc15;">{stars}</span>
                <br>
                <span style="color:#e5e7eb; font-size:14px;">
                    {row['review']}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ================= CHATBOT =================

with tab3:
    # chatbot code

# ================== PART 1 : CORE SETUP ==================

    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import random
    import re
    import time
    from difflib import get_close_matches


    # ================== INTENT MAP (ADVANCED) ==================

    INTENT_MAP = {
    "revenue": ["revenue","sales","sale","income","earning","turnover"],
    "orders": ["orders","order count","total order"],
    "profit": ["profit","margin","loss"],
    "trend": ["trend","graph","growth","increase","decrease"],
    "city": ["city","location"],
    "category": ["category","type"],
    "top_product": ["top product","best product","bestseller","most selling"],
    "low_product": ["low product","worst product","least selling"],
    "top_n_product": ["top 5","top products","top items"],
    "bottom_n_product": ["bottom 5","lowest products"],
    "compare_city": ["compare cities","sales across cities"],
    "hour_analysis": ["hour","peak hour","best time"],
    "recommend": ["recommend","suggest","strategy"],
    "forecast": ["forecast","future","prediction"]
    }

    ALL_KEYS = [k for v in INTENT_MAP.values() for k in v]


    # ================== 2000+ TYPE QUESTIONS SUPPORT ==================

    QUESTION_MAP = {
    "total revenue": ["revenue"],
    "average order value": ["revenue"],
    "profit details": ["profit"],
    "profit margin": ["profit"],
    "total orders": ["orders"],
    "top product": ["top_product"],
    "worst product": ["low_product"],
    "top 5 products": ["top_n_product"],
    "bottom 5 products": ["bottom_n_product"],
    "highest sales city": ["city"],
    "compare sales across cities": ["compare_city"],
    "best category": ["category"],
    "lowest category": ["category"],
    "sales trend": ["trend"],
    "profit trend": ["trend","profit"],
    "future sales": ["forecast"],
    "prediction": ["forecast"],
    "recommendation": ["recommend"],
    "business advice": ["recommend"],
    "highest sales hour": ["hour_analysis"]
    }


    # ================== QUERY SPLIT ==================

    def split_query(q):
        return [p.strip() for p in re.split(r"and|aur|,|\?|&", q.lower()) if p.strip()]


    # ================== INTENT DETECTION (SMART) ==================

    def detect_intents(q):
        ql = q.lower().strip()

        # 1. Direct match
        for key, val in QUESTION_MAP.items():
            if key in ql:
                return val

        intents = set()

        # 2. Keyword match
        for intent, keys in INTENT_MAP.items():
            for k in keys:
                if k in ql:
                    intents.add(intent)

        # 3. Fuzzy match (spelling mistake)
        if not intents:
            for word in ql.split():
                match = get_close_matches(word, ALL_KEYS, n=1, cutoff=0.7)
                if match:
                    for intent, keys in INTENT_MAP.items():
                        if match[0] in keys:
                            intents.add(intent)

        return list(intents) if intents else ["unknown"]


    # ================== PART 2 : ANSWER ENGINE ==================

    def get_answer(intents, df, user_q=""):

        out = []

        # ---------- SAFE CALCULATIONS ----------
        total_revenue = df["revenue"].sum()
        total_orders = len(df)
        total_profit = df["profit"].sum()

        avg_order = (total_revenue / total_orders) if total_orders else 0
        margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        for i in intents:

            # ---------- REVENUE ----------
            if i == "revenue":
                out.append(f"""
    💰 Revenue Insights
    • Total Revenue: ₹{total_revenue:,.0f}
    • Avg Order Value: ₹{avg_order:,.0f}
    • Revenue per Day: ₹{df.groupby("date")["revenue"].sum().mean():,.0f}
    """)

            # ---------- ORDERS ----------
            elif i == "orders":
                peak_hour = df.groupby("hour").size().idxmax() if not df.empty else 0

                out.append(f"""
    📦 Order Analysis
    • Total Orders: {total_orders}
    • Avg Orders/Day: {df.groupby("date").size().mean():.0f}
    • Peak Hour: {peak_hour}
    """)

            # ---------- PROFIT ----------
            elif i == "profit":
                out.append(f"""
    📈 Profit Analysis
    • Total Profit: ₹{total_profit:,.0f}
    • Profit Margin: {margin:.2f}%
    • Profit per Order: ₹{(total_profit/total_orders if total_orders else 0):,.0f}
    """)

            # ---------- TOP PRODUCT ----------
            elif i == "top_product":
                grp = df.groupby("product")["revenue"].sum()
                if not grp.empty:
                    p = grp.idxmax()
                    val = grp.max()
                    out.append(f"""
    🔥 Top Product
    • {p}
    • Revenue: ₹{val:,.0f}
    """)

            # ---------- LOW PRODUCT ----------
            elif i == "low_product":
                grp = df.groupby("product")["revenue"].sum()
                if not grp.empty:
                    p = grp.idxmin()
                    val = grp.min()
                    out.append(f"""
    ⚠️ Weak Product
    • {p}
    • Revenue: ₹{val:,.0f}
    """)

            # ---------- TOP 5 PRODUCTS ----------
            elif i == "top_n_product":
                grp = df.groupby("product")["revenue"].sum().nlargest(5)
                if not grp.empty:
                    text = "\n".join([f"• {k} → ₹{v:,.0f}" for k, v in grp.items()])
                    out.append(f"""
    🔥 Top 5 Products
    {text}
    """)

            # ---------- BOTTOM 5 PRODUCTS ----------
            elif i == "bottom_n_product":
                grp = df.groupby("product")["revenue"].sum().nsmallest(5)
                if not grp.empty:
                    text = "\n".join([f"• {k} → ₹{v:,.0f}" for k, v in grp.items()])
                    out.append(f"""
    ⚠️ Bottom 5 Products
    {text}
    """)

            # ---------- CITY ----------
            elif i == "city":
                grp = df.groupby("city")["revenue"].sum()
                if not grp.empty:
                    c = grp.idxmax()
                    val = grp.max()
                    out.append(f"""
    📍 Top City
    • {c}
    • Revenue: ₹{val:,.0f}
    """)

            # ---------- CITY COMPARISON ----------
            elif i == "compare_city":
                grp = df.groupby("city")["revenue"].sum()
                if not grp.empty:
                    text = "\n".join([f"• {k} → ₹{v:,.0f}" for k, v in grp.items()])
                    out.append(f"""
    🏙️ City Comparison
    {text}
    """)

            # ---------- CATEGORY ----------
            elif i == "category":
                grp = df.groupby("category")["revenue"].sum()
                if not grp.empty:
                    cat = grp.idxmax()
                    out.append(f"""
    🛒 Best Category
    • {cat}
    """)

            # ---------- HOUR ANALYSIS ----------
            elif i == "hour_analysis":
                if not df.empty:
                    hour = df.groupby("hour")["revenue"].sum().idxmax()
                    out.append(f"""
    ⏰ Best Sales Hour
    • {hour}
    """)

            # ---------- TREND ----------
            elif i == "trend":
                out.append("""
    📊 Trend Analysis
    Sales trend is shown below.
    Look for spikes 📈 and drops 📉
    """)

            # ---------- FORECAST ----------
            elif i == "forecast":
                out.append("""
    📈 Forecast
    Future prediction is based on past trends.
    """)

            # ---------- RECOMMEND ----------
            elif i == "recommend":
                grp_p = df.groupby("product")["revenue"].sum()
                grp_c = df.groupby("city")["revenue"].sum()

                if not grp_p.empty and not grp_c.empty:
                    top = grp_p.idxmax()
                    low = grp_p.idxmin()
                    city = grp_c.idxmax()

                    out.append(f"""
    🎯 Business Strategy
    • Focus on: {top}
    • Improve: {low}
    • Expand in: {city}
    """)

        # ---------- FALLBACK ----------
        if not out:
            return "🤖 Try asking about revenue, profit, product, city, or trend."

        # ---------- CLEAN OUTPUT ----------
        clean_text = "\n".join(out)
        clean_text = re.sub(r"<.*?>", "", clean_text)

        return clean_text.strip()



    # ================== PART 3 : GRAPH ENGINE ==================

    def show_graph(intent, df):

        # ---------- SAFETY ----------
        if df.empty:
            st.warning("No data available")
            return

        # ---------- TREND GRAPH ----------
        if intent == "trend":

            df_trend = df.groupby("date")["revenue"].sum().reset_index()

            fig = px.line(
                df_trend,
                x="date",
                y="revenue",
                title="📊 Revenue Trend"
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Revenue"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ---------- CITY GRAPH ----------
        elif intent == "city":

            df_city = df.groupby("city")["revenue"].sum().reset_index()

            fig = px.bar(
                df_city,
                x="city",
                y="revenue",
                title="🏙️ City Sales"
            )

            fig.update_layout(template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)

        # ---------- CATEGORY GRAPH ----------
        elif intent == "category":

            fig = px.pie(
                df,
                names="category",
                title="🛒 Category Share"
            )

            fig.update_layout(template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)

        # ---------- FORECAST GRAPH ----------
        elif intent == "forecast":

            try:
                from statsmodels.tsa.arima.model import ARIMA

                df_trend = df.groupby("date")["revenue"].sum().reset_index()

                if len(df_trend) > 10:

                    model = ARIMA(df_trend["revenue"], order=(2,1,2)).fit()
                    forecast = model.forecast(steps=7)

                    future_dates = pd.date_range(
                        start=df_trend["date"].max(),
                        periods=7
                    )

                    fig = px.line(
                        df_trend,
                        x="date",
                        y="revenue",
                        title="📈 Sales Forecast"
                    )

                    fig.add_scatter(
                        x=future_dates,
                        y=forecast,
                        mode="lines",
                        name="Forecast"
                    )

                    fig.update_layout(template="plotly_dark")

                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning("Not enough data for forecast")

            except Exception as e:
                st.error("Forecast error")




    # ================== PART 4 : PROCESS ENGINE ==================

    def process_query(q, df):

        # ---------- EMPTY CHECK ----------
        if not q or not q.strip():
            return

        # ---------- MULTI QUERY SPLIT ----------
        queries = split_query(q)

        all_intents = []

        for single_q in queries:
            detected = detect_intents(single_q)
            all_intents.extend(detected)

        # ---------- REMOVE DUPLICATE ----------
        all_intents = list(set(all_intents))

        # ---------- GET ANSWER ----------
        ans = get_answer(all_intents, df, q)

        # ---------- INIT CHAT ----------
        if "chat" not in st.session_state:
            st.session_state.chat = []

        # ---------- SAVE CHAT ----------
        st.session_state.chat.append((q, ans))

        # ---------- INPUT RESET FLAG ----------
        if "clear_input" not in st.session_state:
            st.session_state.clear_input = False

        st.session_state.clear_input = True

        # ---------- GRAPH AUTO ----------
    
        st.session_state.last_graphs = all_intents



    # ================== PART 5 : SESSION + INPUT CONTROL ==================


        # ADD THIS (PART 5 के top में)
    if "clicked_q" not in st.session_state:
        st.session_state.clicked_q = None

    if "last_graphs" not in st.session_state:
        st.session_state.last_graphs = []

    # ---------- INIT SESSION ----------
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False


    # ---------- INPUT UI ----------
    st.markdown("### 💬 Ask AI")

    col1, col2, col3 = st.columns([6,1,1])

    with col1:

        # safe value reset system
        default_value = ""

        if not st.session_state.clear_input:
            default_value = st.session_state.get("chat_input_main", "")

        user_q = st.text_input(
            "",
            value=default_value,
            placeholder="Ask anything about your business...",
            key="chat_input_main"
        )

    with col2:
        ask = st.button("🚀", use_container_width=True)

    with col3:
        clear = st.button("🧹", use_container_width=True)


    # ---------- RESET FLAG ----------
    st.session_state.clear_input = False


    # ---------- HANDLE INPUT ----------
    if (ask or user_q) and user_q.strip():
        process_query(user_q, df_f)


    # ---------- CLEAR CHAT ----------
    if clear:
        st.session_state.chat = []
        st.rerun()



   # ================== PART 6 : FINAL STABLE SUGGESTIONS ==================

    st.markdown("#### 💡 Suggestions")

    # ---------- GLOBAL LIST ----------
    all_suggestions = [
        "What is total revenue?",
        "Show profit details",
        "How many orders are there?",
        "What is the profit margin?",
        "Which product is top selling?",
        "Which product is performing worst?",
        "Which city has highest sales?",
        "Which category performs best?",
        "Show sales trend",
        "Predict future sales",
        "What is average order value?",
        "Which city should we expand in?",
        "Which category gives highest profit?",
        "Which product needs improvement?",
        "Compare sales across cities",
        "Which hour has highest sales?",
        "Show profit trend",
        "Which category has lowest sales?",
        "Top 5 products by revenue",
        "Bottom 5 products by revenue",
        "Which city has lowest performance?",
        "Show order distribution",
        "What is revenue growth?",
        "Which product has highest margin?",
        "Show category wise revenue",
        "Which product is trending now?",
        "Which segment is growing fast?",
        "Give business recommendations",
        "Revenue and profit summary",
        "Sales trend and forecast"
    ]

    # ---------- INIT ----------
    if "suggestions" not in st.session_state:
        shuffled = all_suggestions.copy()
        random.shuffle(shuffled)
        st.session_state.suggestions = shuffled[:4]

    if "clicked_q" not in st.session_state:
        st.session_state.clicked_q = None


    # ---------- DISPLAY ----------
    cols = st.columns(4)

    for i, q in enumerate(st.session_state.suggestions):

        if cols[i].button(q, key=f"sug_{i}_{q}"):

            # store only
            st.session_state.clicked_q = q


    # ---------- PROCESS AFTER CLICK ----------
    if st.session_state.clicked_q:

        process_query(st.session_state.clicked_q, df_f)

        # new shuffle
        shuffled = all_suggestions.copy()
        random.shuffle(shuffled)
        st.session_state.suggestions = shuffled[:4]

        st.session_state.clicked_q = None



    # ================== PART 7 : CHAT DISPLAY ==================

    st.markdown("### 🧠 Conversation")

    # ---------- CHAT CONTAINER ----------
    st.markdown("""
    <div style='
        max-width:700px;
        margin:auto;
        max-height:420px;
        overflow-y:auto;
        padding:10px;
        border-radius:12px;
        background:rgba(255,255,255,0.02);
        border:1px solid rgba(255,255,255,0.05);
    '>
    """, unsafe_allow_html=True)


    # ---------- MESSAGES ----------
    for q, a in st.session_state.chat[::-1]:

        # USER MESSAGE (RIGHT)
        st.markdown(f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            margin:6px 0;
        ">
            <div style="
                background:#2563eb;
                color:white;
                padding:8px 12px;
                border-radius:10px;
                max-width:70%;
                font-size:14px;
            ">
            {q}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # BOT MESSAGE (LEFT)
        st.markdown(f"""
        <div style="
            display:flex;
            justify-content:flex-start;
            margin:6px 0;
        ">
            <div style="
                background:#111827;
                color:#e5e7eb;
                padding:8px 12px;
                border-radius:10px;
                max-width:70%;
                font-size:14px;
                border-left:3px solid #3b82f6;
            ">
            {a}
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ---------- CLOSE CONTAINER ----------
    st.markdown("</div>", unsafe_allow_html=True)



    # ================= GRAPH DISPLAY (PERSISTENT) =================

if "last_graphs" in st.session_state:

    for intent in st.session_state.last_graphs:
        show_graph(intent, df_f)


    # ================== PART 8 : FINAL POLISH ==================

    # ---------- TYPING ANIMATION ----------
    def typing_effect(text):
        placeholder = st.empty()
        typed = ""

        for ch in text:
            typed += ch
            placeholder.markdown(f"🤖 {typed}")
            time.sleep(0.002)

        return placeholder


    # ---------- ENHANCED PROCESS (OPTIONAL EFFECT) ----------
    def process_query_with_effect(q, df):

        if not q.strip():
            return

        queries = split_query(q)
        all_intents = []

        for part in queries:
            all_intents.extend(detect_intents(part))

        all_intents = list(set(all_intents))

        ans = get_answer(all_intents, df, q)

        if "chat" not in st.session_state:
            st.session_state.chat = []

        # typing animation
        typing_effect(ans)

        # save chat
        st.session_state.chat.append((q, ans))

        # reset input
        st.session_state.clear_input = True

        # graphs
        for intent in all_intents:
            show_graph(intent, df)


    # ---------- OPTIONAL SWITCH (use animation or normal) ----------
    USE_TYPING_EFFECT = False

    if USE_TYPING_EFFECT:

        # override process function
        def process_query(q, df):
            process_query_with_effect(q, df)