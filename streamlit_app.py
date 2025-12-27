# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="Car Data Visualization Dashboard",
    page_icon="🚗",
    layout="wide"
)

# -------------------------------
# Title
# -------------------------------
st.title("🚗 Car Data Upload & Visualization Dashboard")
st.markdown("Upload your CSV file to automatically clean and visualize your data interactively.")

# -------------------------------
# File Upload Section
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded: `{uploaded_file.name}`")
    st.markdown(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")

    # -------------------------------
    # Preprocessing (Auto-clean)
    # -------------------------------
    processed_df = df.copy()

    # 1️⃣ Remove duplicate rows
    processed_df.drop_duplicates(inplace=True)

    # 2️⃣ Remove rows with missing (NaN) values
    processed_df.dropna(inplace=True)

    # 3️⃣ Remove invalid or extreme numeric values
    num_cols = processed_df.select_dtypes(include=["float64", "int64"]).columns
    for col in num_cols:
        processed_df = processed_df[processed_df[col].between(
            processed_df[col].quantile(0.01), processed_df[col].quantile(0.99)
        )]

    # -------------------------------
    # Right Sidebar Controls
    # -------------------------------
    with st.sidebar:
        st.title("🎛 Dashboard Controls")

        num_rows = st.slider(
            "Select number of rows to display:",
            min_value=5,
            max_value=len(processed_df),
            value=min(50, len(processed_df)),
            step=5,
        )

        chart_type = st.selectbox(
            "Select Chart Type:",
            ["Bar Chart", "Box Plot", "Scatter Plot", "Pie Chart"],
            index=0
        )

        show_data = st.checkbox("Show Data Tables", value=True)

    # -------------------------------
    # Show Data Tables
    # -------------------------------
    if show_data:
        st.subheader("📋 Original vs Preprocessed Data (First Rows)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧾 Original Data")
            st.dataframe(df.head(num_rows), use_container_width=True)
        with col2:
            st.markdown("### ⚙️ Preprocessed Data (Cleaned)")
            st.dataframe(processed_df.head(num_rows), use_container_width=True)

    st.divider()

    # -------------------------------
    # Visualization Section
    # -------------------------------
    st.header("📊 Interactive Visualization")

    numeric_cols = processed_df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    categorical_cols = processed_df.select_dtypes(include=["object", "category"]).columns.tolist()

    if chart_type in ["Bar Chart", "Box Plot", "Scatter Plot"]:
        colx, coly = st.columns(2)
        with colx:
            x_axis = st.selectbox("Select X-axis:", categorical_cols + numeric_cols, index=0)
        with coly:
            y_axis = st.selectbox("Select Y-axis:", numeric_cols, index=0)

    data = processed_df.head(num_rows)

    # -------------------------------
    # Chart Generation
    # -------------------------------
    if chart_type == "Bar Chart":
        st.subheader(f"📊 Bar Chart: {y_axis} by {x_axis}")
        fig = px.bar(
            data,
            x=x_axis,
            y=y_axis,
            color=x_axis,
            title=f"{y_axis} by {x_axis}",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot":
        st.subheader(f"📦 Box Plot: {y_axis} by {x_axis}")
        fig = px.box(
            data,
            x=x_axis,
            y=y_axis,
            color=x_axis,
            title=f"Distribution of {y_axis} by {x_axis}",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter Plot":
        st.subheader(f"📈 Scatter Plot: {x_axis} vs {y_axis}")
        color_col = st.selectbox("Color by:", options=processed_df.columns, index=0)
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color=color_col,
            hover_name=color_col,
            title=f"{y_axis} vs {x_axis} (colored by {color_col})",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie Chart":
        st.subheader("🥧 Pie Chart")
        col = st.selectbox("Select column for Pie Chart:", options=processed_df.columns, index=0)
        fig = px.pie(
            data,
            names=col,
            title=f"Distribution of {col}",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📤 Please upload a CSV file to begin preprocessing and visualization.")

# -------------------------------
# Footer
# -------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center; color:gray;'>"
    "Built with ❤️ using Streamlit & Plotly | Car Data Dashboard"
    "</p>",
    unsafe_allow_html=True,
)
