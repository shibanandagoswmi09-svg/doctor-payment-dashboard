import streamlit as st
import pandas as pd
import plotly.express as px

# Page layout
st.set_page_config(page_title="Doctor Payment Analytics", layout="wide")

st.title("🏥 Smart Doctor Payment Dashboard")
st.markdown("### Upload your monthly Excel report to see the analysis.")

# File Uploader
uploaded_file = st.file_uploader("Upload Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step 1: Intelligent Header Detection
        # We read the file first to find where the actual table starts
        all_data = pd.read_excel(uploaded_file, header=None)
        
        header_row = 0
        for i, row in all_data.iterrows():
            # Checking for 'Doctor Name' to identify the header row
            if row.astype(str).str.contains('Doctor Name', case=False).any():
                header_row = i
                break
        
        # Reload with the correct header
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip() # Remove any accidental spaces

        # Step 2: Essential Columns Check
        # We look for columns even if the capitalization is different
        required = {'Doctor Name': None, 'Doc Share': None, 'Clinic Share': None, 'Net Amount': None}
        for col in df.columns:
            for req in required.keys():
                if col.lower() == req.lower():
                    required[req] = col

        if None in required.values():
            st.error(f"Required columns missing! Make sure your file has: Doctor Name, Doc Share, Clinic Share, and Net Amount.")
        else:
            # Step 3: Data Cleaning (Converting strings to numbers)
            for col in [required['Doc Share'], required['Clinic Share'], required['Net Amount']]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # --- DASHBOARD UI ---
            # Top Metrics
            total_rev = df[required['Net Amount']].sum()
            total_doc = df[required['Doc Share']].sum()
            total_clinic = df[required['Clinic Share']].sum()

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Net Revenue", f"₹{total_rev:,.2f}")
            with c2:
                st.metric("Total Doctor Payout", f"₹{total_doc:,.2f}", delta_color="normal")
            with c3:
                st.metric("Clinic's Total Earning", f"₹{total_clinic:,.2f}")

            st.divider()

            # Charts
            st.subheader("👨‍⚕️ Doctor-wise Payout & Clinic Share")
            doc_summary = df.groupby(required['Doctor Name']).agg({
                required['Doc Share']: 'sum',
                required['Clinic Share']: 'sum'
            }).reset_index()

            fig = px.bar(doc_summary, 
                         x=required['Doctor Name'], 
                         y=[required['Doc Share'], required['Clinic Share']],
                         barmode='group',
                         labels={'value': 'Amount (₹)', 'variable': 'Share Type'},
                         template="plotly_white")
            
            st.plotly_chart(fig, use_container_width=True)

            # Data Table
            with st.expander("View Full Summary Table"):
                st.dataframe(doc_summary.sort_values(by=required['Clinic Share'], ascending=False), use_container_width=True)

            # Download
            csv = doc_summary.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download This Report", data=csv, file_name="payment_summary.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error: Could not process the file. Detail: {e}")
else:
    st.info("👋 Please upload the Excel file from the sidebar or the box above to begin.")
