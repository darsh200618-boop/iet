import streamlit as st

# Website Title
st.title("💼 Employee Payroll System")

st.write("Enter employee details below")

# Employee Inputs
employee_name = st.text_input("Employee Name")

hours_worked = st.number_input(
    "Hours Worked",
    min_value=0.0,
    step=1.0
)

hourly_rate = st.number_input(
    "Hourly Rate (₹)",
    min_value=0.0,
    step=10.0
)

# Button
if st.button("Calculate Salary"):

    gross_salary = hours_worked * hourly_rate

    tax = gross_salary * 0.10

    net_salary = gross_salary - tax

    st.success("Payroll Calculated Successfully!")

    st.subheader("Payroll Result")

    st.write(f"Employee Name: {employee_name}")
    st.write(f"Gross Salary: ₹{gross_salary:.2f}")
    st.write(f"Tax Deduction (10%): ₹{tax:.2f}")
    st.write(f"Net Salary: ₹{net_salary:.2f}")