import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Doctor Payment Analytics", layout="wide")

st.title("🏥 Smart Doctor & Clinic Dashboard")
st.markdown("### Logic: 80% Payout (85% for Dr. Soumya Chatterjee) | 100% Reg Fees to Clinic")

uploaded_file = st.file_uploader("Upload Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step A: Header Detection
        all_data = pd.read_excel(uploaded_file, header=None)
        header_row = 0
        for i, row in all_data.iterrows():
            if row.astype(str).str.contains('Doctor|Pt. Name', case=False).any():
                header_row = i
                break
        
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip()

        # Step B: Column Mapping
        mapping_rules = {
            'Doctor Name': ['doctor', 'dr', 'doc'],
            'Gross Amount': ['fee', 'gross', 'billing', 'charge'],
            'Discount': ['discount', 'disc', 'dsc'],
            'Reg Fee': ['reg', 'registration']
        }
        
        mapped = {}
        for key, keywords in mapping_rules.items():
            for col in df.columns:
                if any(kw in col.lower() for kw in keywords):
                    mapped[key] = col
                    break

        # Step C: Apply Business Logic Calculations
        # Convert to numbers
        for key in ['Gross Amount', 'Discount', 'Reg Fee']:
            if key in mapped:
                df[mapped[key]] = pd.to_numeric(df[mapped[key]], errors='coerce').fillna(0)
            else:
                # If Reg Fee column is missing in Excel, assume 0
                df[key] = 0
                mapped[key] = key

        # Calculate Net (Gross - Discount)
        df['Net For Share'] = df[mapped['Gross Amount']] - df[mapped['Discount']]

        # Define custom percentages
        def calculate_doc_share(row):
            doc_name = str(row[mapped['Doctor Name']]).lower()
            percentage = 0.85 if 'soumya chatterje' in doc_name else 0.80
            return row['Net For Share'] * percentage

        df['Calculated Doc Share'] = df.apply(calculate_doc_share, axis=1)
        # Clinic gets the rest of the Net + 100% of Reg Fee
        df['Calculated Clinic Share'] = (df['Net For Share'] - df['Calculated Doc Share']) + df[mapped['Reg Fee']]

        # Step D: Aggregation for Report
        doc_summary = df.groupby(mapped['Doctor Name']).agg({
            mapped['Gross Amount']: 'sum',
            mapped['Discount']: 'sum',
            mapped['Reg Fee']: 'sum',
            'Calculated Doc Share': 'sum',
            'Calculated Clinic Share': 'sum'
        }).reset_index()

        doc_summary.columns = ['Doctor Name', 'Total Gross', 'Total Discount', 'Total Reg Fees', 'Doctor Payout', 'Clinic Earning']

        # Step E: UI Metrics
        st.sidebar.header("Filter Report")
        search_doc = st.sidebar.selectbox("Select a Doctor", ["All Doctors"] + list(doc_summary['Doctor Name'].unique()))
        
        final_display = doc_summary if search_doc == "All Doctors" else doc_summary[doc_summary['Doctor Name'] == search_doc]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Gross Revenue", f"₹{final_display['Total Gross'].sum():,.2f}")
        c2.metric("Total Discount", f"₹{final_display['Total Discount'].sum():,.2f}")
        c3.metric("Doctor Payout", f"₹{final_display['Doctor Payout'].sum():,.2f}")
        c4.metric("Clinic Net", f"₹{final_display['Clinic Earning'].sum():,.2f}")

        st.divider()

        # Step F: Table and Charts
        st.subheader(f"Detailed Summary: {search_doc}")
        st.dataframe(final_display.style.format(precision=2), use_container_width=True)

        fig = px.bar(final_display, x='Doctor Name', y=['Doctor Payout', 'Clinic Earning'],
                     title="Payout vs Clinic Earnings (Including Reg Fees)", barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        # Download
        csv = final_display.to_csv(index=False).encode('utf-8')
        st.download_button("📩 Download Professional Report", data=csv, file_name="Doctor_Calculated_Report.csv")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Upload the Excel file to calculate shares based on Clinic Rules.")
