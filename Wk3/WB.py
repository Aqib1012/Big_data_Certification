import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Clean Streamlit Page Setup
st.set_page_config(page_title="Titanic EDA", page_icon="🚢", layout="wide")

# 🎨 Use a nice Seaborn theme
sns.set_theme(style="whitegrid", palette="pastel")

# 🏷️ Title
st.title("🚢 Titanic Dataset Analysis")
st.markdown("---")

# 📂 Load Dataset
readfile = pd.read_csv("titanic_data.csv")

# 🔎 Dataset Preview
st.subheader("📋 Dataset Preview")
st.dataframe(readfile.head())

st.markdown("---")

# 👥 Count Men vs Women
st.subheader("👨‍🦱👩 Men vs Women Count")

fig, ax = plt.subplots(figsize=(6, 4))
sns.countplot(x="Sex", data=readfile, ax=ax)
ax.set_title("Number of Men and Women", fontsize=14, weight="bold")
ax.set_xlabel("Gender")
ax.set_ylabel("Count")
st.pyplot(fig)

# 🧮 Display numbers below graph
men_count = (readfile["Sex"] == "male").sum()
women_count = (readfile["Sex"] == "female").sum()
st.info(f"**Total Men:** {men_count} | **Total Women:** {women_count}")

st.markdown("---")

# 💰 Average Fare Comparison
st.subheader("💰 Average Fare: Men vs Women")

fig1, ax1 = plt.subplots(figsize=(6, 4))
sns.barplot(x="Sex", y="Fare", data=readfile, ax=ax1, ci=None)
ax1.set_title("Average Fare by Gender", fontsize=14, weight="bold")
ax1.set_xlabel("Gender")
ax1.set_ylabel("Average Fare")
st.pyplot(fig1)

# 🧮 Show numeric values
avg_men_fare = readfile[readfile["Sex"] == "male"]["Fare"].mean()
avg_women_fare = readfile[readfile["Sex"] == "female"]["Fare"].mean()
st.success(f"**Average Fare (Men):** ${avg_men_fare:.2f} | **Average Fare (Women):** ${avg_women_fare:.2f}")

# Show Survived Peoples Count
st.subheader("Survided Peoples")

fig2, ax2=plt.subplots()
sns.countplot(x="Survived",hue="Sex",data=readfile,ax=ax2)
ax2.set_title("Survived By Gender")
st.pyplot(fig2)


st.markdown("---")
st.caption("© 2025 | Developed by Aqib")
