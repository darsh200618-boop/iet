import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Biometric Payroll System", layout="wide")

st.title("🏢 Supermarket Biometric Payroll System")

# Upload biometric attendance file
uploaded_file = st.file_uploader(
    "Upload Monthly Attendance Excel",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    st.subheader("Attendance Data")
    st.dataframe(df)

    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'])

    # Convert In/Out times
    df['In Time'] = pd.to_datetime(df['In Time'], errors='coerce')
    df['Out Time'] = pd.to_datetime(df['Out Time'], errors='coerce')

    # Calculate working hours
    df['Working Hours'] = (
        df['Out Time'] - df['In Time']
    ).dt.total_seconds() / 3600

    # Attendance rules
    df['Present'] = df['Working Hours'].apply(
        lambda x: 1 if x >= 4 else 0
    )

    # Overtime calculation
    df['Overtime Hours'] = df['Working Hours'].apply(
        lambda x: max(0, x - 8)
    )

    # Employee payroll summary
    payroll = df.groupby(
        ['Employee ID', 'Name']
    ).agg({
        'Present': 'sum',
        'Overtime Hours': 'sum'
    }).reset_index()

    # Salary settings
    DAILY_SALARY = 800
    OT_RATE = 100

    # Payroll calculation
    payroll['Basic Salary'] = payroll['Present'] * DAILY_SALARY
    payroll['OT Pay'] = payroll['Overtime Hours'] * OT_RATE

    payroll['Net Salary'] = (
        payroll['Basic Salary'] +
        payroll['OT Pay']
    )

    st.subheader("Payroll Summary")
    st.dataframe(payroll)

    # Dashboard Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Employees",
        len(payroll)
    )

    col2.metric(
        "Total Salary",
        f"₹ {payroll['Net Salary'].sum():,.0f}"
    )

    col3.metric(
        "Total OT Hours",
        round(payroll['Overtime Hours'].sum(), 2)
    )

    # Download payroll report
    output_file = "payroll_report.xlsx"

    payroll.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            "⬇ Download Payroll Report",
            f,
            file_name="payroll_report.xlsx"
        )
