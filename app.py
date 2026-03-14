import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Doctor Payment Analytics", layout="wide")

st.title("🏥 Smart Doctor & Clinic Dashboard")
st.markdown("### Comprehensive Financial Summary per Doctor")

uploaded_file = st.file_uploader("Upload Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step 1: Intelligent Header Detection
        all_data = pd.read_excel(uploaded_file, header=None)
        header_row = 0
        for i, row in all_data.iterrows():
            if row.astype(str).str.contains('Doctor Name', case=False).any():
                header_row = i
                break
        
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip()

        # Step 2: Essential Columns Check (Including Fees and Discount)
        # We define what we need and map them to what exists in the file
        cols_to_find = {
            'Doctor Name': ['Doctor Name', 'Doctor'],
            'Fee': ['Fee', 'Fees', 'Gross Amount'],
            'Discount': ['Discount', 'Disc'],
            'Net Amount': ['Net Amount', 'Net'],
            'Doc Share': ['Doc Share', 'Doctor Share'],
            'Clinic Share': ['Clinic Share', 'Hospital Share']
        }
        
        mapped_cols = {}
        for key, alternatives in cols_to_find.items():
            for col in df.columns:
                if col.lower() in [a.lower() for a in alternatives]:
                    mapped_cols[key] = col
                    break

        if len(mapped_cols) < len(cols_to_find):
            missing = set(cols_to_find.keys()) - set(mapped_cols.keys())
            st.error(f"Missing columns in Excel: {', '.join(missing)}")
        else:
            # Step 3: Data Cleaning
            numeric_cols = ['Fee', 'Discount', 'Net Amount', 'Doc Share', 'Clinic Share']
            for col_key in numeric_cols:
                actual_name = mapped_cols[col_key]
                df[actual_name] = pd.to_numeric(df[actual_name], errors='coerce').fillna(0)

            # --- CALCULATIONS ---
            # Grouping exactly as the Boss requested
            doc_summary = df.groupby(mapped_cols['Doctor Name']).agg({
                mapped_cols['Fee']: 'sum',
                mapped_cols['Discount']: 'sum',
                mapped_cols['Net Amount']: 'sum',
                mapped_cols['Doc Share']: 'sum',
                mapped_cols['Clinic Share']: 'sum'
            }).reset_index()

            # Renaming for a clean display
            doc_summary.columns = ['Doctor Name', 'Total Fees', 'Total Discount', 'Net Revenue', 'Doctor Share', 'Clinic Share']

            # --- UI DISPLAY ---
            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross Fees", f"₹{doc_summary['Total Fees'].sum():,.2f}")
            c2.metric("Total Discount", f"₹{doc_summary['Total Discount'].sum():,.2f}", delta=None, delta_color="inverse")
            c3.metric("Doctor Payout", f"₹{doc_summary['Doctor Share'].sum():,.2f}")
            c4.metric("Clinic Net", f"₹{doc_summary['Clinic Share'].sum():,.2f}")

            st.divider()

            # Main Detailed Table (What the Boss asked for)
            st.subheader("📋 Doctor Wise Summary Report")
            st.markdown("Detailed breakdown of Fees, Discounts, and Share distribution.")
            
            # Styling the table to highlight high revenue
            st.dataframe(doc_summary.style.format(precision=2).highlight_max(axis=0, subset=['Net Revenue'], color='#d4edda'), use_container_width=True)

            # Visual Chart
            st.subheader("📊 Financial Distribution Chart")
            fig = px.bar(doc_summary, 
                         x='Doctor Name', 
                         y=['Doctor Share', 'Clinic Share', 'Total Discount'],
                         title="Share vs Discount Breakdown",
                         barmode='stack') # Stacked shows the total 'Fee' composition better
            st.plotly_chart(fig, use_container_width=True)

            # Export
            csv = doc_summary.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Professional Summary", data=csv, file_name="Doctor_Wise_Report.csv", mime="text/csv")
            # Add this right after the file upload section in your app.py
if uploaded_file is not None:
    # ... (existing code to load df) ...
    
    # NEW SEARCH FILTER
    st.sidebar.header("Filter Options")
    all_doctors = ["All"] + list(doc_summary['Doctor Name'].unique())
    selected_doc = st.sidebar.selectbox("Select Doctor for Personal Summary", all_doctors)

    if selected_doc != "All":
        display_df = doc_summary[doc_summary['Doctor Name'] == selected_doc]
    else:
        display_df = doc_summary

    # Use 'display_df' for your table and metrics

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload the file to generate the Doctor Summary.")
