import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR, SVC
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, mean_squared_error
import streamlit as st

st.title("🧠 SVM & K-Means Demonstration")

# ------------------ Load Datasets ------------------
st.header("📂 Step 1: Load Datasets")
linear_df = pd.read_csv("linear.csv")
logistic_df = pd.read_csv("logistic.csv")

st.subheader("Linear Dataset (for Regression)")
st.write(linear_df.head())

st.subheader("Logistic Dataset (for Classification)")
st.write(logistic_df.head())

# ------------------ SVM Regression ------------------
st.header("📈 Step 2: SVM Regression (Supervised)")

X_linear = linear_df.iloc[:, :-1]
y_linear = linear_df.iloc[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X_linear, y_linear, test_size=0.2, random_state=42)

svm_reg = SVR(kernel='linear')
svm_reg.fit(X_train, y_train)
y_pred_reg = svm_reg.predict(X_test)

mse = mean_squared_error(y_test, y_pred_reg)
st.write(f"✅ **Mean Squared Error:** {mse:.2f}")

fig, ax = plt.subplots()
ax.scatter(y_test, y_pred_reg)
ax.set_xlabel("Actual")
ax.set_ylabel("Predicted")
ax.set_title("SVM Regression Results")
st.pyplot(fig)

# ------------------ SVM Classification ------------------
st.header("🧩 Step 3: SVM Classification (Supervised)")

X_log = logistic_df.iloc[:, :-1]
y_log = logistic_df.iloc[:, -1]

X_train, X_test, y_train, y_test = train_test_split(X_log, y_log, test_size=0.2, random_state=42)

svm_clf = SVC(kernel='linear')
svm_clf.fit(X_train, y_train)
y_pred_clf = svm_clf.predict(X_test)

acc = accuracy_score(y_test, y_pred_clf)
st.write(f"✅ **Accuracy:** {acc*100:.2f}%")

fig, ax = plt.subplots()
sns.scatterplot(x=X_log.iloc[:, 0], y=X_log.iloc[:, 1], hue=y_log, ax=ax)
ax.set_title("SVM Classification (Original Data)")
st.pyplot(fig)

# ------------------ K-Means Clustering ------------------
st.header("🔵 Step 4: K-Means Clustering (Unsupervised)")

X_kmeans = X_log  # use logistic data (no labels needed)
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(X_kmeans)

logistic_df["Cluster"] = clusters

fig, ax = plt.subplots()
sns.scatterplot(x=X_log.iloc[:, 0], y=X_log.iloc[:, 1], hue=clusters, palette='viridis', ax=ax)
ax.set_title("K-Means Clustering Result")
st.pyplot(fig)

st.write("✅ K-Means completed! Cluster labels added to dataset:")
st.write(logistic_df.head())

st.success("🎉 All tasks (SVM Regression, Classification & K-Means) completed successfully!")
