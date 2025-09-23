import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

st.title("Wk 3 Test")
readfile=pd.read_csv("titanic_data.csv")

readfile['title']=readfile['Name'].apply(lambda y:re.search(r'([A-Z][a-z]+)\.', y).group(1)) ##.apply function()
readfile['title'].value_counts()


st.title("Graph 1")
readfile.loc[(~readfile['title'].isin(['Mr','Mrs','Miss','Master'])),'title'] = 'Rare Title'
fig1, ax1 = plt.subplots(figsize=(6, 4))
sns.countplot(x='title',hue="Survived",data=readfile)
st.pyplot(fig1)

st.title("Graph 2")
readfile['Fsize']=readfile['SibSp']+ readfile['Parch']+1
fig2, ax2 = plt.subplots(figsize=(6, 4))
sns.countplot(x='Fsize',hue="Survived",data=readfile)

st.pyplot(fig2)

st.title("graph 3")
temp = readfile.groupby('Fsize')['Survived'].value_counts(normalize=True).reset_index(name='Percentage')
fig3, ax3 = plt.subplots(figsize=(6, 4))
sns.barplot(x='Fsize',y='Percentage',data=temp)
st.pyplot(fig3)
