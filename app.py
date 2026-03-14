import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard-er setup
st.set_page_config(page_title="Doctor Payment Report", layout="wide")

st.title("📊 Doctor & Clinic Payment Dashboard")
st.markdown("Upload korun apnar payment CSV file-ti automatic report-er jonno.")

# File Uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Data load kora (apnar file-er prothom row skip kora hocche)
    df = pd.read_csv(uploaded_file, skiprows=1)
    df.columns = df.columns.str.strip() # Column name clean kora

    # Analysis Calculations
    total_net = df['Net Amount'].sum()
    total_doc = df['Doc Share'].sum()
    total_clinic = df['Clinic Share'].sum()

    # 1. Main Highlights (Boro font-e dekhabe)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{total_net:,.2f}")
    col2.metric("Total Doctor Payout", f"₹{total_doc:,.2f}")
    col3.metric("Total Clinic Earning", f"₹{total_clinic:,.2f}")

    st.divider()

    # 2. Doctor-wise Analysis
    st.subheader("👨‍⚕️ Doctor-wise Payment Breakdown")
    doc_summary = df.groupby('Doctor Name').agg({
        'Doc Share': 'sum',
        'Clinic Share': 'sum',
        'Net Amount': 'sum'
    }).reset_index()

    # Chart toiri
    fig = px.bar(doc_summary, x='Doctor Name', y=['Doc Share', 'Clinic Share'],
                 title="Doctor vs Clinic Share",
                 barmode='group',
                 labels={'value': 'Amount (₹)', 'variable': 'Category'})
    st.plotly_chart(fig, use_container_width=True)

    # 3. Data Table
    st.subheader("📋 Detailed Summary Table")
    st.dataframe(doc_summary, use_container_width=True)

    # 4. Download Option for Boss
    csv = doc_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Summary as CSV",
        data=csv,
        file_name='doctor_payment_summary.csv',
        mime='text/csv',
    )
else:
    st.info("Side-bar ba upore file upload korun.")
