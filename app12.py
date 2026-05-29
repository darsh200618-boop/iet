import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Biometric Payroll", layout="wide")

st.title("🏢 Supermarket Biometric Payroll System")

# Upload Excel file
uploaded_file = st.file_uploader(
    "Upload Biometric Excel File",
    type=["xlsx"]
)

if uploaded_file:

    # Read excel without header
    df = pd.read_excel(uploaded_file, header=None)

    # Rename columns
    df.columns = ["Employee ID", "Date", "Time"]

    st.subheader("Raw Biometric Data")
    st.dataframe(df.head(20))

    # Combine Date + Time
    df["Punch Datetime"] = pd.to_datetime(
        df["Date"].astype(str) + " " + df["Time"].astype(str)
    )

    # Sort data
    df = df.sort_values(
        by=["Employee ID", "Date", "Punch Datetime"]
    )

    # First IN time
    first_punch = df.groupby(
        ["Employee ID", "Date"]
    )["Punch Datetime"].first().reset_index()

    first_punch.rename(
        columns={"Punch Datetime": "In Time"},
        inplace=True
    )

    # Last OUT time
    last_punch = df.groupby(
        ["Employee ID", "Date"]
    )["Punch Datetime"].last().reset_index()

    last_punch.rename(
        columns={"Punch Datetime": "Out Time"},
        inplace=True
    )

    # Merge IN and OUT
    attendance = pd.merge(
        first_punch,
        last_punch,
        on=["Employee ID", "Date"]
    )

    # Working hours
    attendance["Working Hours"] = (
        attendance["Out Time"] - attendance["In Time"]
    ).dt.total_seconds() / 3600

    # Present / Absent
    attendance["Present"] = attendance[
        "Working Hours"
    ].apply(lambda x: 1 if x >= 4 else 0)

    # Overtime
    attendance["Overtime Hours"] = attendance[
        "Working Hours"
    ].apply(lambda x: max(0, x - 8))

    st.subheader("Processed Attendance")
    st.dataframe(attendance)

    # Salary settings
    DAILY_SALARY = st.number_input(
        "Daily Salary",
        value=800
    )

    OT_RATE = st.number_input(
        "Overtime Rate Per Hour",
        value=100
    )

    # Payroll summary
    payroll = attendance.groupby(
        "Employee ID"
    ).agg({
        "Present": "sum",
        "Overtime Hours": "sum"
    }).reset_index()

    # Salary calculations
    payroll["Basic Salary"] = (
        payroll["Present"] * DAILY_SALARY
    )

    payroll["OT Pay"] = (
        payroll["Overtime Hours"] * OT_RATE
    )

    payroll["Net Salary"] = (
        payroll["Basic Salary"] +
        payroll["OT Pay"]
    )

    st.subheader("💰 Payroll Summary")
    st.dataframe(payroll)

    # Dashboard
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Employees",
        payroll.shape[0]
    )

    col2.metric(
        "Total Salary",
        f"₹ {payroll['Net Salary'].sum():,.0f}"
    )

    col3.metric(
        "Total OT Hours",
        round(
            payroll["Overtime Hours"].sum(),
            2
        )
    )

    # Download payroll report
    payroll_file = "payroll_report.xlsx"

    payroll.to_excel(
        payroll_file,
        index=False
    )

    with open(payroll_file, "rb") as f:

        st.download_button(
            label="⬇ Download Payroll Report",
            data=f,
            file_name="payroll_report.xlsx"
        )
