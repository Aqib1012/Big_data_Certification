import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="🏏 Cricket Data EDA Dashboard", layout="wide")
st.title("🏏 Cricket Data EDA Dashboard")

# --- Read CSV ---
df = pd.read_csv("WK4/ODI_Match_info.csv")  # apna correct path rakho

# --- Sidebar Options ---
st.sidebar.header("📊 EDA & Analysis")
option = st.sidebar.radio(
    "Select what to view:",
    (
        "Dataset Preview",
        "Info",
        "Describe",
        "Missing Values",
        "Duplicates",
        "Value Counts",
        "Unique Values Count",
        "Visualizations",
        "Stats & Insights"
    )
)

# --- Display According to Selection ---
if option == "Dataset Preview":
    st.subheader("🔍 Dataset Preview (Top 10 Rows By Using head())")
    st.dataframe(df.head(10))

elif option == "Info":
    st.subheader("ℹ️ Dataset Info By Using info()")
    buffer = io.StringIO()
    df.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)

elif option == "Describe":
    st.subheader("📊 Summary Statistics By Using describe()")
    st.dataframe(df.describe(include="all"))

elif option == "Missing Values":
    st.subheader("🚨 Missing Values per Column By Using isnull().sum()")
    st.dataframe(df.isnull().sum())

elif option == "Duplicates":
    st.subheader("📑 Duplicate Rows Count By Using duplicated().sum()")
    st.write(f"Total Duplicates: {df.duplicated().sum()}")

elif option == "Value Counts":
    st.subheader("📊 Value Counts By Using value_counts()")
    col = st.selectbox("Select Column", df.columns)
    st.dataframe(df[col].value_counts())

elif option == "Unique Values Count":
    st.subheader("🔢 Number of Unique Values By Using nunique().reset_index()")
    unique_counts = df.nunique().reset_index()
    unique_counts.columns = ["Column", "Unique Count"]
    st.dataframe(unique_counts)

elif option == "Visualizations":
    st.subheader("📊 Visualizations")
    chart_type = st.selectbox(
        "Choose Chart",
        ("Toss Winners (Bar)", "Toss Decision (Pie)", "Matches Per Season (Bar)")
    )

    if chart_type == "Toss Winners (Bar)":
        toss_counts = df["toss_winner"].value_counts().reset_index()
        toss_counts.columns = ["Team", "Toss Wins"]
        toss_counts = toss_counts.sort_values("Toss Wins", ascending=False)
        fig = px.bar(toss_counts, x="Team", y="Toss Wins", title="Toss Wins by Team")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Toss Decision (Pie)":
        decision_counts = df["toss_decision"].value_counts().reset_index()
        decision_counts.columns = ["Decision", "Count"]
        fig = px.pie(decision_counts, names="Decision", values="Count", title="Toss Decision Distribution")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Matches Per Season (Bar)":
        season_counts = df["season"].value_counts().reset_index()
        season_counts.columns = ["Season", "Matches"]
        season_counts = season_counts.sort_values("Season")
        fig = px.bar(season_counts, x="Season", y="Matches", title="Matches Per Season")
        st.plotly_chart(fig, use_container_width=True)

elif option == "Stats & Insights":
    st.subheader("📈 Toss Win % by Team")
    toss_win_total = df.groupby("toss_winner").size().reset_index(name="Toss Wins")
    match_played_total = pd.concat([df["team1"], df["team2"]]).value_counts().reset_index()
    match_played_total.columns = ["Team", "Matches Played"]

    toss_stats = pd.merge(toss_win_total, match_played_total, left_on="toss_winner", right_on="Team", how="right")
    toss_stats["Toss Win %"] = (toss_stats["Toss Wins"].fillna(0) / toss_stats["Matches Played"]) * 100

    st.dataframe(toss_stats[["Team", "Toss Wins", "Matches Played", "Toss Win %"]])

    fig = px.bar(
        toss_stats.sort_values("Toss Win %", ascending=False),
        x="Team", y="Toss Win %",
        title="Toss Win % by Team"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏆 Toss Decision Impact on Match Result")
    toss_outcome = df.groupby(["toss_decision", "winner"]).size().reset_index(name="Matches")
    fig2 = px.bar(
        toss_outcome,
        x="toss_decision",
        y="Matches",
        color="winner",
        title="Toss Decision vs Match Winners",
        barmode="stack"
    )
    st.plotly_chart(fig2, use_container_width=True)
