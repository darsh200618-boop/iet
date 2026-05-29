import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import hashlib

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Smart Payroll HRMS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }

    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .css-1d391kg {
        background-color: #111827;
    }

    h1, h2, h3 {
        color: #111827;
    }

    .salary-card {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }

    .attendance-card {
        background: linear-gradient(135deg, #059669, #10b981);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }

    .danger-card {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        padding: 20px;
        border-radius: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE
# ============================================================
DB_NAME = "payroll_system.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE,
        name TEXT,
        department TEXT,
        designation TEXT,
        salary REAL,
        joining_date TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        date TEXT,
        check_in TEXT,
        check_out TEXT,
        working_hours REAL,
        status TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT,
        month TEXT,
        basic_salary REAL,
        overtime REAL,
        deductions REAL,
        net_salary REAL
    )
    ''')

    conn.commit()

create_tables()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("💼 Smart Payroll HRMS")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Employees",
        "Attendance Upload",
        "Payroll",
        "Reports"
    ]
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_employee(emp_id, name, dept, designation, salary, joining_date):
    cursor.execute('''
    INSERT OR IGNORE INTO employees
    (emp_id, name, department, designation, salary, joining_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (emp_id, name, dept, designation, salary, joining_date))
    conn.commit()


def get_employees():
    return pd.read_sql_query("SELECT * FROM employees", conn)


def get_attendance():
    return pd.read_sql_query("SELECT * FROM attendance", conn)


def calculate_payroll(emp_id, month):
    employee = pd.read_sql_query(
        f"SELECT * FROM employees WHERE emp_id='{emp_id}'", conn
    )

    attendance = pd.read_sql_query(
        f"SELECT * FROM attendance WHERE emp_id='{emp_id}'",
        conn
    )

    if employee.empty:
        return None

    basic_salary = employee.iloc[0]['salary']

    present_days = len(attendance[attendance['status'] == 'Present'])

    per_day_salary = basic_salary / 30

    earned_salary = per_day_salary * present_days

    overtime = max(0, present_days - 26) * 500

    deductions = max(0, 30 - present_days) * 200

    net_salary = earned_salary + overtime - deductions

    return {
        'basic_salary': basic_salary,
        'present_days': present_days,
        'overtime': overtime,
        'deductions': deductions,
        'net_salary': round(net_salary, 2)
    }

# ============================================================
# DASHBOARD
# ============================================================
if menu == "Dashboard":

    st.title("📊 Payroll Dashboard")

    employees_df = get_employees()
    attendance_df = get_attendance()

    total_employees = len(employees_df)

    present_today = 0
    if not attendance_df.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        present_today = len(
            attendance_df[
                attendance_df['date'] == today
            ]
        )

    total_salary = 0
    if not employees_df.empty:
        total_salary = employees_df['salary'].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='salary-card'>
            <h3>Total Employees</h3>
            <h1>{total_employees}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='attendance-card'>
            <h3>Present Today</h3>
            <h1>{present_today}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='danger-card'>
            <h3>Monthly Payroll</h3>
            <h1>₹ {int(total_salary):,}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if not employees_df.empty:
        dept_chart = employees_df['department'].value_counts().reset_index()
        dept_chart.columns = ['Department', 'Employees']

        fig = px.pie(
            dept_chart,
            names='Department',
            values='Employees',
            title='Department Distribution'
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Recent Employees")
    st.dataframe(employees_df, use_container_width=True)

# ============================================================
# EMPLOYEES
# ============================================================
elif menu == "Employees":

    st.title("👨‍💼 Employee Management")

    with st.form("employee_form"):

        col1, col2 = st.columns(2)

        with col1:
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Employee Name")
            department = st.selectbox(
                "Department",
                [
                    "HR",
                    "IT",
                    "Finance",
                    "Marketing",
                    "Operations"
                ]
            )

        with col2:
            designation = st.text_input("Designation")
            salary = st.number_input("Monthly Salary", min_value=0)
            joining_date = st.date_input("Joining Date")

        submit = st.form_submit_button("Add Employee")

        if submit:
            add_employee(
                emp_id,
                name,
                department,
                designation,
                salary,
                str(joining_date)
            )

            st.success("Employee Added Successfully")

    st.markdown("---")

    st.subheader("Employee Records")

    employee_df = get_employees()

    st.dataframe(employee_df, use_container_width=True)

# ============================================================
# ATTENDANCE
# ============================================================
elif menu == "Attendance Upload":

    st.title("📥 Biometric Attendance Upload")

    uploaded_file = st.file_uploader(
        "Upload Biometric Excel File",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file:

        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        st.info("Expected Columns: Employee ID, Date, Check In, Check Out")

        if st.button("Process Attendance"):

            try:
                for _, row in df.iterrows():

                    emp_id = row['Employee ID']
                    date = row['Date']
                    check_in = row['Check In']
                    check_out = row['Check Out']

                    try:
                        in_time = pd.to_datetime(check_in)
                        out_time = pd.to_datetime(check_out)

                        working_hours = (
                            out_time - in_time
                        ).seconds / 3600

                    except:
                        working_hours = 0

                    status = "Present" if working_hours >= 4 else "Half Day"

                    cursor.execute('''
                    INSERT INTO attendance
                    (emp_id, date, check_in, check_out, working_hours, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        emp_id,
                        str(date),
                        str(check_in),
                        str(check_out),
                        working_hours,
                        status
                    ))

                conn.commit()

                st.success("Attendance Processed Successfully")

            except Exception as e:
                st.error(f"Error: {e}")

# ============================================================
# PAYROLL
# ============================================================
elif menu == "Payroll":

    st.title("💰 Payroll Processing")

    employees = get_employees()

    if employees.empty:
        st.warning("No employees found")

    else:

        emp_id = st.selectbox(
            "Select Employee",
            employees['emp_id']
        )

        month = st.selectbox(
            "Select Month",
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December"
            ]
        )

        if st.button("Generate Payroll"):

            payroll = calculate_payroll(emp_id, month)

            if payroll:

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Basic Salary",
                        f"₹ {payroll['basic_salary']:,.0f}"
                    )

                    st.metric(
                        "Present Days",
                        payroll['present_days']
                    )

                with col2:
                    st.metric(
                        "Overtime",
                        f"₹ {payroll['overtime']:,.0f}"
                    )

                    st.metric(
                        "Deductions",
                        f"₹ {payroll['deductions']:,.0f}"
                    )

                st.markdown("---")

                st.success(
                    f"Net Salary: ₹ {payroll['net_salary']:,.2f}"
                )

                if st.button("Save Payroll"):

                    cursor.execute('''
                    INSERT INTO payroll
                    (emp_id, month, basic_salary, overtime, deductions, net_salary)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        emp_id,
                        month,
                        payroll['basic_salary'],
                        payroll['overtime'],
                        payroll['deductions'],
                        payroll['net_salary']
                    ))

                    conn.commit()

                    st.success("Payroll Saved")

# ============================================================
# REPORTS
# ============================================================
elif menu == "Reports":

    st.title("📑 Reports & Analytics")

    payroll_df = pd.read_sql_query(
        "SELECT * FROM payroll",
        conn
    )

    attendance_df = get_attendance()

    tab1, tab2 = st.tabs([
        "Payroll Reports",
        "Attendance Reports"
    ])

    with tab1:

        st.subheader("Payroll History")

        st.dataframe(payroll_df, use_container_width=True)

        if not payroll_df.empty:

            fig = px.bar(
                payroll_df,
                x='emp_id',
                y='net_salary',
                title='Employee Salary Distribution'
            )

            st.plotly_chart(fig, use_container_width=True)

            csv = payroll_df.to_csv(index=False).encode('utf-8')

            st.download_button(
                "Download Payroll Report",
                csv,
                file_name='payroll_report.csv',
                mime='text/csv'
            )

    with tab2:

        st.subheader("Attendance Records")

        st.dataframe(attendance_df, use_container_width=True)

        if not attendance_df.empty:

            fig2 = px.histogram(
                attendance_df,
                x='status',
                title='Attendance Status Overview'
            )

            st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("Smart Payroll HRMS • Professional Biometric Payroll System • Streamlit Edition")
