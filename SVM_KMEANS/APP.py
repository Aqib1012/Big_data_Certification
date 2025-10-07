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

linear_data = pd.read_csv("linear.csv")
logistic_data = pd.read_csv("logistic.csv")

st.subheader("📈 Linear Dataset (for Regression)")
st.dataframe(linear_data)

st.subheader("🧩 Logistic Dataset (for Classification)")
st.dataframe(logistic_data)

# -------------------------------
# Step 2: SVM Regression
# -------------------------------
st.header("📈 Step 2: SVM Regression (Supervised)")

X = linear_data.iloc[:, :-1]
y = linear_data.iloc[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

svm_reg = svm.SVR(kernel='linear')
svm_reg.fit(X_train, y_train)
y_pred = svm_reg.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
st.success(f"✅ Mean Squared Error: {mse:.2f}")

# ---- FIXED REGRESSION PLOT ----
fig, ax = plt.subplots()
if X.shape[1] == 1:
    # Single feature → simple 2D scatter
    ax.scatter(X, y, color='blue', label='Actual')
    ax.plot(X, svm_reg.predict(X), color='red', label='SVM Line')
    ax.set_xlabel(X.columns[0])
    ax.set_ylabel(y.name)
else:
    # Multi-feature → show only first feature vs target for visualization
    ax.scatter(X.iloc[:, 0], y, color='blue', label='Actual')
    ax.scatter(X.iloc[:, 0], svm_reg.predict(X), color='red', label='Predicted')
    ax.set_xlabel(X.columns[0])
    ax.set_ylabel(y.name)
ax.set_title("SVM Regression Visualization")
ax.legend()
st.pyplot(fig)

# -------------------------------
# Step 3: SVM Classification
# -------------------------------
st.header("🧩 Step 3: SVM Classification (Supervised)")

X = logistic_data.iloc[:, :-1].copy()
y = logistic_data.iloc[:, -1].copy()

# Encode categorical columns
for col in X.columns:
    if X[col].dtype == 'object':
        X[col] = LabelEncoder().fit_transform(X[col])
if y.dtype == 'object':
    y = LabelEncoder().fit_transform(y)

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

svm_clf = svm.SVC(kernel='linear')
svm_clf.fit(X_train, y_train)
y_pred = svm_clf.predict(X_test)

acc = accuracy_score(y_test, y_pred)
st.success(f"✅ SVM Classification Accuracy: {acc*100:.2f}%")

# -------------------------------
# Step 4: K-Means Clustering
# -------------------------------
st.header("🎯 Step 4: K-Means Clustering (Unsupervised)")

cluster_data = linear_data.copy()
scaled_data = StandardScaler().fit_transform(cluster_data)

kmeans = KMeans(n_clusters=2, random_state=42)
kmeans.fit(scaled_data)
cluster_data["Cluster"] = kmeans.labels_

fig2, ax2 = plt.subplots()
ax2.scatter(cluster_data.iloc[:, 0], cluster_data.iloc[:, 1], c=cluster_data["Cluster"], cmap="rainbow")
ax2.set_title("K-Means Clustering Result")
st.pyplot(fig2)

st.success("🎉 Demonstration Complete — SVM Regression, Classification & K-Means Done!")
