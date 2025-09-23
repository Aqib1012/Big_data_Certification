import streamlit as st
import pandas as pd
import numpy as np

# Title
st.title("📊 My Mini Dashboard")

# Sidebar Slider
st.sidebar.header("Controls")
slider_value = st.sidebar.slider("Select Number of Rows", min_value=5, max_value=50, value=10)

# Generate Random Data
data = pd.DataFrame(
    np.random.randn(slider_value, 3),
    columns=['Feature A', 'Feature B', 'Feature C']
)

# Show Data
st.subheader(f"Showing {slider_value} Rows")
st.dataframe(data)

# Chart
st.subheader("Feature A vs Feature B")
st.line_chart(data[['Feature A', 'Feature B']])
