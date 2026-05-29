import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Payroll Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# PROFESSIONAL UI DESIGN
# =====================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #f4f7fb;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 5px;
}

.sub-title {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    border: 1px solid #e5e7eb;
}

.metric-card {
    background: white;
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.metric-title {
    color: #6b7280;
    font-size: 14px;
    font-weight: 500;
}

.metric-value {
    color: #111827;
    font-size: 34px;
    font-weight: 700;
    margin-top: 10px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #1d4ed8;
    color: white;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect("payroll.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    emp_id TEXT,
    name TEXT,
    department TEXT,
    designation TEXT,
    salary REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    emp_id TEXT,
    date TEXT,
    check_in TEXT,
    check_out TEXT,
    working_hours REAL,
    status TEXT
)
''')

conn.commit()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("💼 Payroll Pro")
st.sidebar.caption("Biometric Payroll Management")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "MENU",
    [
        "Dashboard",
        "Employees",
        "Attendance",
        "Payroll Reports"
    ]
)

# =====================================================
# FUNCTIONS
# =====================================================
def load_employees():
    return pd.read_sql_query("SELECT * FROM employees", conn)


def load_attendance():
    return pd.read_sql_query("SELECT * FROM attendance", conn)

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    employees_df = load_employees()
    attendance_df = load_attendance()

    total_employees = len(employees_df)

    total_salary = 0
    if not employees_df.empty:
        total_salary = employees_df['salary'].sum()

    present_today = 0

    if not attendance_df.empty:
        today = datetime.now().strftime("%Y-%m-%d")
        present_today = len(
            attendance_df[
                attendance_df['date'] == today
            ]
        )

    st.markdown("<div class='main-title'>Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Professional biometric payroll management system</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>TOTAL EMPLOYEES</div>
            <div class='metric-value'>{total_employees}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>PRESENT TODAY</div>
            <div class='metric-value'>{present_today}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>MONTHLY PAYROLL</div>
            <div class='metric-value'>₹ {int(total_salary):,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not employees_df.empty:

        dept = employees_df['department'].value_counts().reset_index()
        dept.columns = ['Department', 'Employees']

        fig = px.bar(
            dept,
            x='Department',
            y='Employees',
            text='Employees'
        )

        fig.update_layout(
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Employee Overview")
    st.dataframe(employees_df, use_container_width=True)

# =====================================================
# EMPLOYEES
# =====================================================
elif menu == "Employees":

    st.markdown("<div class='main-title'>Employees</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Manage employee information</div>", unsafe_allow_html=True)

    with st.container():

        with st.form("employee_form"):

            col1, col2 = st.columns(2)

            with col1:
                emp_id = st.text_input("Employee ID")
                name = st.text_input("Employee Name")
                department = st.selectbox(
                    "Department",
                    ["HR", "IT", "Finance", "Marketing", "Operations"]
                )

            with col2:
                designation = st.text_input("Designation")
                salary = st.number_input("Salary", min_value=0)

            submit = st.form_submit_button("Add Employee")

            if submit:
                cursor.execute('''
                INSERT INTO employees VALUES (?, ?, ?, ?, ?)
                ''', (
                    emp_id,
                    name,
                    department,
                    designation,
                    salary
                ))

                conn.commit()

                st.success("Employee added successfully")

    st.markdown("---")

    employees_df = load_employees()

    st.dataframe(employees_df, use_container_width=True)

# =====================================================
# ATTENDANCE
# =====================================================
elif menu == "Attendance":

    st.markdown("<div class='main-title'>Attendance Upload</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Upload biometric attendance excel sheet</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file:

        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.markdown("### Uploaded Attendance")
        st.dataframe(df, use_container_width=True)

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

                    status = "Present"

                    cursor.execute('''
                    INSERT INTO attendance VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        emp_id,
                        str(date),
                        str(check_in),
                        str(check_out),
                        working_hours,
                        status
                    ))

                conn.commit()

                st.success("Attendance processed successfully")

            except Exception as e:
                st.error(e)

# =====================================================
# PAYROLL REPORTS
# =====================================================
elif menu == "Payroll Reports":

    st.markdown("<div class='main-title'>Payroll Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Employee payroll summary and analytics</div>", unsafe_allow_html=True)

    employees_df = load_employees()
    attendance_df = load_attendance()

    payroll_data = []

    if not employees_df.empty:

        for _, emp in employees_df.iterrows():

            emp_attendance = attendance_df[
                attendance_df['emp_id'] == emp['emp_id']
            ]

            present_days = len(emp_attendance)

            per_day = emp['salary'] / 30

            net_salary = round(per_day * present_days, 2)

            payroll_data.append({
                'Employee ID': emp['emp_id'],
                'Name': emp['name'],
                'Department': emp['department'],
                'Present Days': present_days,
                'Net Salary': net_salary
            })

    payroll_df = pd.DataFrame(payroll_data)

    st.dataframe(payroll_df, use_container_width=True)

    if not payroll_df.empty:

        fig = px.bar(
            payroll_df,
            x='Name',
            y='Net Salary',
            text='Net Salary'
        )

        fig.update_layout(
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        csv = payroll_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            "Download Payroll Report",
            csv,
            file_name='payroll_report.csv',
            mime='text/csv'
        )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Payroll Pro • Professional HRMS & Biometric Payroll Software")
