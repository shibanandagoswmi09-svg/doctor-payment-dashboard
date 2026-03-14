import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Doctor Payment Analytics", layout="wide")

st.title("🏥 Smart Doctor & Clinic Dashboard")
st.markdown("### Monthly Financial Summary (Fees, Discounts & Shares)")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step A: Header Detection
        all_data = pd.read_excel(uploaded_file, header=None)
        header_row = 0
        for i, row in all_data.iterrows():
            if row.astype(str).str.contains('Doctor Name', case=False).any():
                header_row = i
                break
        
        df = pd.read_excel(uploaded_file, header=header_row)
        df.columns = df.columns.str.strip()

        # Step B: Column Mapping
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
            st.error(f"Required columns missing: {', '.join(missing)}")
        else:
            # Step C: Data Cleaning
            for key in ['Fee', 'Discount', 'Net Amount', 'Doc Share', 'Clinic Share']:
                col_name = mapped_cols[key]
                df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0)

            # Step D: Aggregation (The report Boss asked for)
            doc_summary = df.groupby(mapped_cols['Doctor Name']).agg({
                mapped_cols['Fee']: 'sum',
                mapped_cols['Discount']: 'sum',
                mapped_cols['Net Amount']: 'sum',
                mapped_cols['Doc Share']: 'sum',
                mapped_cols['Clinic Share']: 'sum'
            }).reset_index()

            doc_summary.columns = ['Doctor Name', 'Total Fees', 'Total Discount', 'Net Revenue', 'Doctor Share', 'Clinic Share']

            # Step E: Sidebar Filter
            st.sidebar.header("Filter Report")
            search_doc = st.sidebar.selectbox("Select a Doctor", ["All"] + list(doc_summary['Doctor Name'].unique()))

            if search_doc != "All":
                final_display = doc_summary[doc_summary['Doctor Name'] == search_doc]
            else:
                final_display = doc_summary

            # Step F: UI Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross Fees", f"₹{final_display['Total Fees'].sum():,.2f}")
            c2.metric("Discounts", f"₹{final_display['Total Discount'].sum():,.2f}")
            c3.metric("Doc Payout", f"₹{final_display['Doctor Share'].sum():,.2f}")
            c4.metric("Clinic Net", f"₹{final_display['Clinic Share'].sum():,.2f}")

            st.divider()

            # Step G: Main Table & Chart
            st.subheader(f"📊 Report for: {search_doc}")
            st.dataframe(final_display.style.format(precision=2), use_container_width=True)

            fig = px.bar(final_display, x='Doctor Name', y=['Doctor Share', 'Clinic Share', 'Total Discount'],
                         title="Revenue Composition (Stacked)", barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

            # Download
            csv = final_display.to_csv(index=False).encode('utf-8')
            st.download_button("📩 Download Report", data=csv, file_name="Doctor_Report.csv")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.info("👋 Please upload the Excel file to generate the dashboard.")
