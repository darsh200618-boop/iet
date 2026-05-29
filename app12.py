import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="HRMS Payroll",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("hrms.db", check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL;')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    emp_id TEXT,
    name TEXT,
    department TEXT,
    salary INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    emp_id TEXT,
    date TEXT,
    check_in TEXT,
    check_out TEXT,
    working_hours REAL
)
''')

conn.commit()

# =========================================================
# PROFESSIONAL UI
# =========================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #f5f7fb;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
    width: 240px !important;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.header {
    background: white;
    padding: 20px 30px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    margin-bottom: 25px;
}

.header-title {
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
}

.header-sub {
    color: #64748b;
    margin-top: 5px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.03);
}

.metric-label {
    color: #64748b;
    font-size: 14px;
    font-weight: 500;
}

.metric-number {
    font-size: 34px;
    font-weight: 700;
    color: #0f172a;
    margin-top: 10px;
}

.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🏢 HRMS Payroll")
st.sidebar.caption("Biometric Payroll System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Employees",
        "Attendance Upload",
        "Payroll"
    ]
)

# =========================================================
# FUNCTIONS
# =========================================================
def get_employees():
    return pd.read_sql_query("SELECT * FROM employees", conn)


def get_attendance():
    df = pd.read_sql_query("SELECT * FROM attendance", conn)

    if not df.empty:
        df['emp_id'] = df['emp_id'].astype(str).str.strip()
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    return df

# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":

    emp_df = get_employees()
    att_df = get_attendance()

    total_emp = len(emp_df)

    total_salary = 0
    if not emp_df.empty:
        total_salary = emp_df['salary'].sum()

    today_attendance = 0
    if not att_df.empty:
        today = datetime.now().strftime('%Y-%m-%d')
        att_df['date'] = pd.to_datetime(att_df['date']).dt.strftime('%Y-%m-%d')
        today_attendance = len(att_df[att_df['date'] == today])

    st.markdown("""
    <div class='header'>
        <div class='header-title'>Dashboard</div>
        <div class='header-sub'>Manage biometric payroll and employee attendance</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-label'>TOTAL EMPLOYEES</div>
            <div class='metric-number'>{total_emp}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-label'>TODAY ATTENDANCE</div>
            <div class='metric-number'>{today_attendance}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='card'>
            <div class='metric-label'>MONTHLY PAYROLL</div>
            <div class='metric-number'>₹ {int(total_salary):,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not emp_df.empty:
        dept_df = emp_df['department'].value_counts().reset_index()
        dept_df.columns = ['Department', 'Employees']

        fig = px.bar(
            dept_df,
            x='Department',
            y='Employees',
            text='Employees'
        )

        fig.update_layout(
            height=420,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=30, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Employees")
    st.dataframe(emp_df, use_container_width=True)

# =========================================================
# EMPLOYEE PAGE
# =========================================================
elif page == "Employees":

    st.markdown("""
    <div class='header'>
        <div class='header-title'>Employee Management</div>
        <div class='header-sub'>Add and manage employees</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            emp_id = st.text_input("Employee ID")
            emp_name = st.text_input("Employee Name")

        with col2:
            department = st.selectbox(
                "Department",
                ["IT", "HR", "Finance", "Operations", "Marketing"]
            )
            salary = st.number_input("Salary", min_value=0)

        if st.button("Add Employee"):

            cursor.execute('''
            INSERT INTO employees VALUES (?, ?, ?, ?)
            ''', (
                emp_id,
                emp_name,
                department,
                salary
            ))

            conn.commit()

            st.success("Employee added successfully")

    st.markdown("---")

    st.dataframe(get_employees(), use_container_width=True)

# =========================================================
# ATTENDANCE UPLOAD
# =========================================================
elif page == "Attendance Upload":

    st.markdown("""
    <div class='header'>
        <div class='header-title'>Attendance Upload</div>
        <div class='header-sub'>Upload biometric attendance excel file</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file:

        # =====================================================
        # READ FILE
        # =====================================================
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_excel(uploaded_file, header=None)

        # =====================================================
        # YOUR BIOMETRIC FORMAT
        # =====================================================
        # Column 0 = Employee ID
        # Column 1 = Date
        # Column 2 = Time

        df.columns = ['Employee ID', 'Date', 'Time']

        # CLEAN DATA
        df['Employee ID'] = df['Employee ID'].astype(str).str.strip()
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['Time'] = df['Time'].astype(str)

        st.success("Biometric file detected successfully")

        st.markdown("### Attendance Preview")
        st.dataframe(df.head(20), use_container_width=True)

        # =====================================================
        # PROCESS ATTENDANCE
        # =====================================================
        if st.button("Process Attendance"):

            grouped = df.groupby([
                'Employee ID',
                'Date'
            ])

            # CLEAR OLD ATTENDANCE BEFORE IMPORT
            cursor.execute('DELETE FROM attendance')
            conn.commit()

            for (emp_id, date), group in grouped:

                times = sorted(group['Time'].tolist())

                check_in = times[0]
                check_out = times[-1]

                try:
                    in_time = pd.to_datetime(check_in)
                    out_time = pd.to_datetime(check_out)

                    working_hours = (
                        out_time - in_time
                    ).seconds / 3600

                except:
                    working_hours = 0

                cursor.execute('''
                INSERT INTO attendance
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    emp_id,
                    date,
                    check_in,
                    check_out,
                    round(working_hours, 2)
                ))

            conn.commit()

            st.success("Attendance imported successfully")

# =========================================================
# PAYROLL PAGE
# =========================================================
elif page == "Payroll":

    st.markdown("""
    <div class='header'>
        <div class='header-title'>Payroll Reports</div>
        <div class='header-sub'>Employee salary calculations</div>
    </div>
    """, unsafe_allow_html=True)

    emp_df = get_employees()
    att_df = get_attendance()

    payroll_list = []

    for _, emp in emp_df.iterrows():

        att_df['emp_id'] = att_df['emp_id'].astype(str).str.strip()
        emp_id = str(emp['emp_id']).strip()

        emp_att = att_df[
            att_df['emp_id'] == emp_id
        ]

        days = len(emp_att)

        per_day = emp['salary'] / 30

        net_salary = round(days * per_day, 2)

        payroll_list.append({
            'Employee ID': emp['emp_id'],
            'Employee Name': emp['name'],
            'Department': emp['department'],
            'Present Days': days,
            'Net Salary': net_salary
        })

    payroll_df = pd.DataFrame(payroll_list)

    st.dataframe(payroll_df, use_container_width=True)

    if not payroll_df.empty:

        fig = px.bar(
            payroll_df,
            x='Employee Name',
            y='Net Salary',
            text='Net Salary'
        )

        fig.update_layout(
            height=450,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        csv = payroll_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label='Download Payroll Report',
            data=csv,
            file_name='payroll_report.csv',
            mime='text/csv'
        )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("HRMS Payroll System • Streamlit Professional UI")
