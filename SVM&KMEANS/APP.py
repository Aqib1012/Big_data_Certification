import streamlit as st
import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

st.set_page_config(page_title="🧠 SVM & K-Means Demonstration", layout="wide")
st.title("🧠 SVM & K-Means Demonstration")

# -------------------------------
# Step 1: Load Datasets
# -------------------------------
st.header("📂 Step 1: Load Datasets")

# Linear dataset (Regression)
st.subheader("📈 Linear Dataset (for Regression)")
linear_data = pd.DataFrame({
    "X": [1, 2, 3, 4, 5, 6, 7],
    "Y": [2, 4, 6, 8, 10, 12, 14]
})
st.dataframe(linear_data)

# Logistic dataset (Classification)
st.subheader("🧩 Logistic Dataset (for Classification)")
logistic_data = pd.DataFrame({
    "Weather": ["Sunny", "Rainy", "Overcast", "Sunny", "Rainy", "Overcast", "Sunny", "Rainy"],
    "Temperature": ["Hot", "Mild", "Cool", "Hot", "Mild", "Cool", "Hot", "Cool"],
    "Play": ["No", "Yes", "Yes", "No", "Yes", "Yes", "No", "Yes"]
})
st.dataframe(logistic_data)

# -------------------------------
# Step 2: SVM Regression
# -------------------------------
st.header("📈 Step 2: SVM Regression (Supervised)")

X = linear_data[["X"]]
y = linear_data["Y"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

svm_reg = svm.SVR(kernel='linear')
svm_reg.fit(X_train, y_train)
y_pred = svm_reg.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
st.success(f"✅ Mean Squared Error: {mse:.2f}")

# Plot regression
fig, ax = plt.subplots()
ax.scatter(X, y, color='blue', label='Actual')
ax.plot(X, svm_reg.predict(X), color='red', label='SVM Line')
ax.set_title("SVM Regression Result")
ax.legend()
st.pyplot(fig)

# -------------------------------
# Step 3: SVM Classification
# -------------------------------
st.header("🧩 Step 3: SVM Classification (Supervised)")

# Copy data to avoid pandas warnings
X = logistic_data[["Weather", "Temperature"]].copy()
y = logistic_data["Play"].copy()

# Encode all categorical data
encoders = {}
for col in X.columns:
    enc = LabelEncoder()
    X[col] = enc.fit_transform(X[col])
    encoders[col] = enc

y_enc = LabelEncoder().fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.3, random_state=42)

# Scale features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train SVM classifier
svm_clf = svm.SVC(kernel='linear')
svm_clf.fit(X_train, y_train)
y_pred = svm_clf.predict(X_test)

acc = accuracy_score(y_test, y_pred)
st.success(f"✅ SVM Classification Accuracy: {acc*100:.2f}%")

# -------------------------------
# Step 4: K-Means Clustering
# -------------------------------
st.header("🎯 Step 4: K-Means Clustering (Unsupervised)")

cluster_data = pd.DataFrame({
    "X": [1, 2, 3, 8, 9, 10],
    "Y": [1, 2, 3, 8, 9, 10]
})
st.dataframe(cluster_data)

kmeans = KMeans(n_clusters=2, random_state=42)
kmeans.fit(cluster_data)
cluster_data["Cluster"] = kmeans.labels_

fig2, ax2 = plt.subplots()
ax2.scatter(cluster_data["X"], cluster_data["Y"], c=cluster_data["Cluster"], cmap="rainbow")
ax2.set_title("K-Means Clustering Result")
st.pyplot(fig2)

st.success("🎉 Demonstration Complete — SVM Regression, Classification & K-Means Done!")
