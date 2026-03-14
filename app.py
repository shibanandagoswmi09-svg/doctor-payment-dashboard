import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Doctor Payment Dashboard", layout="wide")

st.title("🏥 Hospital & Doctor Payment Dashboard")
st.markdown("Apnar Excel (.xlsx) file-ti upload korun automatic report-er jonno.")

# File Uploader (Excel support added)
uploaded_file = st.file_uploader("Upload Doctor Payment Excel File", type=["xlsx"])

if uploaded_file is not None:
    # Excel file read korchi
    # header=1 karon apnar file-er prothom row-te totals thake, 2nd row theke main column shuru
    df = pd.read_excel(uploaded_file, header=1)
    
    # Column name clean kora
    df.columns = df.columns.str.strip()

    # Data analysis calculations
    # Sudhu numeric data niye kaaj korchi jate error na hoy
    total_net = df['Net Amount'].sum()
    total_doc = df['Doc Share'].sum()
    total_clinic = df['Clinic Share'].sum()

    # Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{total_net:,.2f}")
    col2.metric("Doctor's Total Share", f"₹{total_doc:,.2f}")
    col3.metric("Clinic's Total Share", f"₹{total_clinic:,.2f}")

    st.divider()

    # Doctor-wise Summary Table
    st.subheader("👨‍⚕️ Doctor-wise Payout Analysis")
    doc_summary = df.groupby('Doctor Name').agg({
        'Doc Share': 'sum',
        'Clinic Share': 'sum',
        'Net Amount': 'sum'
    }).reset_index()

    # Graphical View
    fig = px.bar(doc_summary, x='Doctor Name', y=['Doc Share', 'Clinic Share'],
                 title="Doctor vs Clinic Revenue Distribution",
                 barmode='group',
                 color_discrete_map={'Doc Share': '#1f77b4', 'Clinic Share': '#ff7f0e'})
    
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Table
    st.subheader("📋 Summary Data")
    st.dataframe(doc_summary.style.highlight_max(axis=0, subset=['Clinic Share']), use_container_width=True)

    # Export Option
    csv = doc_summary.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary Report", data=csv, file_name="Doctor_Payment_Summary.csv")

else:
    st.info("Oporer box-e Excel file-ti drag and drop korun.")
