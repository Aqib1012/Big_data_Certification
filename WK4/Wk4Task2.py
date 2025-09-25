import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="📱 Google Play Store EDA", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Professional Look ---
st.markdown("""
<style>
/* Background & Font */
body {
    background-color: #0e1117;
    color: #ffffff;
}
h1, h2, h3, h4 {
    color: #4CAF50;
    font-weight: 700;
}
.sidebar .sidebar-content {
    background-color: #161a23;
}
div[data-testid="stMetricValue"] {
    font-size: 24px;
    color: #00FFB3;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("📱 Google Play Store Apps EDA Dashboard")
st.markdown("Explore, clean, and visualize Google Play Store data with a **professional, modern dashboard**.")

# --- Load Dataset ---
df = pd.read_csv("WK4/googleplaystore.csv")
df.columns = df.columns.str.strip()

# --- Data Cleaning ---
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['Installs'] = df['Installs'].str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')
df['Price'] = df['Price'].str.replace('$', '', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# --- Sidebar ---
st.sidebar.header("📊 Navigation Panel")
option = st.sidebar.radio(
    "Choose Analysis Section:",
    (
        "📂 Dataset Preview",
        "ℹ️ Info",
        "📊 Describe",
        "🚨 Missing Values",
        "📑 Duplicates",
        "📊 Value Counts",
        "🔢 Unique Values Count",
        "🧹 Data Cleaning",
        "📈 Visualizations",
        "📊 Stats & Insights"
    )
)

# --- Section Rendering ---
if option == "📂 Dataset Preview":
    st.subheader("🔍 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

elif option == "ℹ️ Info":
    st.subheader("📄 Dataset Info")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.code(buffer.getvalue(), language="text")

elif option == "📊 Describe":
    st.subheader("📊 Summary Statistics")
    st.dataframe(df.describe(include="all"), use_container_width=True)

elif option == "🚨 Missing Values":
    st.subheader("🚨 Missing Values per Column")
    st.bar_chart(df.isnull().sum())

elif option == "📑 Duplicates":
    st.subheader("📑 Duplicate Rows")
    st.metric("Duplicate Rows Found", df.duplicated().sum())

elif option == "📊 Value Counts":
    st.subheader("📊 Value Counts by Column")
    col = st.selectbox("Select Column", df.columns)
    st.dataframe(df[col].value_counts(), use_container_width=True)

elif option == "🔢 Unique Values Count":
    st.subheader("🔢 Unique Values Count")
    unique_counts = df.nunique().reset_index()
    unique_counts.columns = ["Column", "Unique Count"]
    st.dataframe(unique_counts, use_container_width=True)

elif option == "🧹 Data Cleaning":
    st.subheader("🧹 Data Cleaning Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Drop Duplicates"):
            df.drop_duplicates(inplace=True)
            st.success("✅ Duplicates removed successfully!")
    with col2:
        if st.button("🛠️ Fill Missing Values"):
            df['Rating'].fillna(df['Rating'].median(), inplace=True)
            df.fillna("Unknown", inplace=True)
            st.success("✅ Missing values filled successfully!")

    st.write("Preview After Cleaning:")
    st.dataframe(df.head(), use_container_width=True)

elif option == "📈 Visualizations":
    st.subheader("📊 Interactive Visualizations")
    chart_type = st.selectbox(
        "Select Chart",
        (
            "📦 Top 10 Categories by App Count",
            "🆓 Free vs Paid (Pie)",
            "⭐ Ratings Distribution (Histogram)",
            "🏆 Top 10 Categories by Average Rating",
            "📥 Installs by Category (Bar)",
            "📉 Reviews vs Rating (Scatter)"
        )
    )

    if chart_type == "📦 Top 10 Categories by App Count":
        top_cat = df['Category'].value_counts().nlargest(10)
        fig = px.bar(
            x=top_cat.index, y=top_cat.values,
            title="Top 10 Categories by App Count",
            labels={"x": "Category", "y": "App Count"},
            text=top_cat.values,
            color=top_cat.values,
            color_continuous_scale="mint"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "🆓 Free vs Paid (Pie)":
        free_paid = df['Type'].value_counts()
        fig = px.pie(values=free_paid.values, names=free_paid.index,
                     title="Free vs Paid Apps", hole=0.3,
                     color=free_paid.index,
                     color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "⭐ Ratings Distribution (Histogram)":
        fig = px.histogram(df, x="Rating", nbins=40, title="Ratings Distribution",
                           color_discrete_sequence=["#4CAF50"])
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "🏆 Top 10 Categories by Average Rating":
        avg_rating = df.groupby("Category")['Rating'].mean().sort_values(ascending=False).head(10)
        fig = px.bar(x=avg_rating.index, y=avg_rating.values,
                     title="Top 10 Categories by Average Rating",
                     color=avg_rating.values,
                     text=avg_rating.values.round(2),
                     color_continuous_scale="Greens")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "📥 Installs by Category (Bar)":
        installs = df.groupby("Category")['Installs'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=installs.index, y=installs.values,
                     title="Top 10 Categories by Total Installs",
                     color=installs.values,
                     text=installs.values,
                     color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "📉 Reviews vs Rating (Scatter)":
        scatter_df = df.dropna(subset=["Reviews", "Rating", "Installs"])
        scatter_df = scatter_df[scatter_df["Installs"] > 0]
        scatter_df = scatter_df[scatter_df["Reviews"] < scatter_df["Reviews"].quantile(0.99)]

        fig = px.scatter(
            scatter_df,
            x="Reviews", y="Rating",
            size="Installs",
            size_max=60,
            color="Category",
            title="Reviews vs Rating (Bubble Size = Installs)",
            hover_data=['App'],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

elif option == "📊 Stats & Insights":
    st.subheader("📈 Key Stats & Insights")
    stats = df.groupby("Category").agg({
        "Rating": "mean",
        "Installs": "sum",
        "App": "count"
    }).reset_index().sort_values("Installs", ascending=False)
    stats.rename(columns={"App": "App Count"}, inplace=True)
    st.dataframe(stats, use_container_width=True)

    st.subheader("💰 Free vs Paid: Average Rating")
    paid_free_stats = df.groupby("Type")["Rating"].mean().reset_index()
    fig = px.bar(paid_free_stats, x="Type", y="Rating",
                 title="Average Rating: Free vs Paid",
                 color="Rating", text_auto=True,
                 color_continuous_scale="greens")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Category vs Content Rating Crosstab")
    cross = pd.crosstab(df['Category'], df['Content Rating'])
    st.dataframe(cross, use_container_width=True)

    st.subheader("📆 Category + Type Aggregation")
    multi = df.groupby(["Category", "Type"]).agg({
        "Rating": "mean",
        "Installs": "sum"
    }).reset_index()
    st.dataframe(multi, use_container_width=True)
