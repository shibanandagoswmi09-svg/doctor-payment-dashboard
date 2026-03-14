import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Doctor Payment Analytics", layout="wide")

st.title("🏥 Smart Doctor & Clinic Dashboard")
st.markdown("### Comprehensive Financial Summary (Fees, Discounts & Shares)")

uploaded_file = st.file_uploader("Upload Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step A: Intelligent Header Detection
        all_data = pd.read_excel(uploaded_file, header=None)
        header_row = 0
        for i, row in all_data.iterrows():
            # Check if row has 'Doctor' or 'Pt. Name' to identify header
            if row.astype(str).str.contains('Doctor|Pt. Name', case=False).any():
                header_row = i
                break
        
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip()

        # Step B: Super Flexible Column Mapping (Keyword Logic)
        # Ekhane amra common keywords diye column khujbo
        mapping_rules = {
            'Doctor Name': ['doctor', 'dr', 'doc'],
            'Fee': ['fee', 'gross', 'billing', 'charge'],
            'Discount': ['discount', 'disc', 'dsc', 'rebate'],
            'Net Amount': ['net', 'total', 'payable'],
            'Doc Share': ['doc share', 'doctor share', 'dr share', 'payout'],
            'Clinic Share': ['clinic share', 'hospital share', 'hosp share', 'profit']
        }
        
        mapped_cols = {}
        for final_key, keywords in mapping_rules.items():
            for col in df.columns:
                # Jodi column namer moddhe keyword-er kono ekta thake
                if any(kw in col.lower() for kw in keywords):
                    mapped_cols[final_key] = col
                    break

        # Validation check
        if len(mapped_cols) < 6:
            missing = set(mapping_rules.keys()) - set(mapped_cols.keys())
            st.warning(f"Note: Some columns might be missing: {', '.join(missing)}. Please check column headers.")
        
        # Step C: Data Cleaning & Numeric Conversion
        numeric_keys = ['Fee', 'Discount', 'Net Amount', 'Doc Share', 'Clinic Share']
        for key in numeric_cols_to_clean := [k for k in numeric_keys if k in mapped_cols]:
            col_name = mapped_cols[key]
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0)

        # Step D: Aggregation (The final report)
        if 'Doctor Name' in mapped_cols:
            doc_summary = df.groupby(mapped_cols['Doctor Name']).agg({
                mapped_cols.get('Fee', df.columns[0]): 'sum',
                mapped_cols.get('Discount', df.columns[0]): 'sum',
                mapped_cols.get('Net Amount', df.columns[0]): 'sum',
                mapped_cols.get('Doc Share', df.columns[0]): 'sum',
                mapped_cols.get('Clinic Share', df.columns[0]): 'sum'
            }).reset_index()

            doc_summary.columns = ['Doctor Name', 'Total Fees', 'Total Discount', 'Net Revenue', 'Doctor Share', 'Clinic Share']

            # Step E: Sidebar Filter
            st.sidebar.header("Search & Filter")
            search_doc = st.sidebar.selectbox("Select a Doctor", ["All Doctors"] + list(doc_summary['Doctor Name'].unique()))

            if search_doc != "All Doctors":
                final_display = doc_summary[doc_summary['Doctor Name'] == search_doc]
            else:
                final_display = doc_summary

            # Step F: Dashboard UI
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross Fees", f"₹{final_display['Total Fees'].sum():,.2f}")
            c2.metric("Discounts", f"₹{final_display['Total Discount'].sum():,.2f}")
            c3.metric("Doc Payout", f"₹{final_display['Doctor Share'].sum():,.2f}")
            c4.metric("Clinic Net", f"₹{final_display['Clinic Share'].sum():,.2f}")

            st.divider()

            st.subheader(f"📊 Detailed Breakdown: {search_doc}")
            st.dataframe(final_display.style.format(precision=2), use_container_width=True)

            # Interactive Stacked Chart
            fig = px.bar(final_display, x='Doctor Name', y=['Doctor Share', 'Clinic Share', 'Total Discount'],
                         title="Financial Distribution (Doctor Share + Clinic Share + Discount)",
                         labels={'value': 'Amount (₹)', 'variable': 'Type'},
                         barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

            # Export button
            csv = final_display.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Professional Report", data=csv, file_name="Doctor_Summary_Report.csv")
        else:
            st.error("Could not identify 'Doctor Name' column. Please check your Excel headers.")

    except Exception as e:
        st.error(f"Something went wrong while processing: {e}")
else:
    st.info("👋 Ready to process. Please upload the monthly Excel file.")
