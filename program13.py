import streamlit as st
import pandas as pd
st.set_page_config(page_title="Advanced HR Dashboard", layout="wide")
st.title("💼 Advanced HR Dashboard (Plotly)")

@st.cache_data
def load_data(path="hr_data.csv"):
    try:
        df = pd.read_csv(path, parse_dates=["JoinDate"])
        return df
    except Exception as e:
        st.error(f"Could not load CSV: {e}")
        return pd.DataFrame()

data = load_data()

if data.empty:
    uploaded = st.file_uploader("Upload HR CSV file (EmployeeID,Name,Department,Salary,Age,JoinDate,Attrition)", type=["csv"])
    if uploaded:
        data = pd.read_csv(uploaded, parse_dates=["JoinDate"])

if not data.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    departments = sorted(data["Department"].dropna().unique().tolist())
    selected_departments = st.sidebar.multiselect("Department", options=departments, default=departments)

    min_age, max_age = int(data["Age"].min()), int(data["Age"].max())
    age_range = st.sidebar.slider("Age range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

    salary_min, salary_max = int(data["Salary"].min()), int(data["Salary"].max())
    salary_range = st.sidebar.slider("Salary range", min_value=salary_min, max_value=salary_max, value=(salary_min, salary_max))

    attrition_options = ["All"] + sorted(data["Attrition"].dropna().unique().tolist())
    selected_attrition = st.sidebar.selectbox("Attrition", options=attrition_options, index=0)

    # Apply filters
    filtered = data.copy()
    filtered = filtered[filtered["Department"].isin(selected_departments)]
    filtered = filtered[(filtered["Age"] >= age_range[0]) & (filtered["Age"] <= age_range[1])]
    filtered = filtered[(filtered["Salary"] >= salary_range[0]) & (filtered["Salary"] <= salary_range[1])]
    if selected_attrition != "All":
        filtered = filtered[filtered["Attrition"] == selected_attrition]

    # Top KPI cards
    col1, col2, col3, col4 = st.columns([1.2,1.2,1.2,1.2])
    col1.metric("Total Employees", len(filtered))
    col2.metric("Average Salary", f"{int(filtered['Salary'].mean()) if not filtered.empty else 0}")
    col3.metric("Median Age", int(filtered['Age'].median()) if not filtered.empty else 0)
    attr_rate = round(100 * (filtered['Attrition'] == 'Yes').mean(), 1) if not filtered.empty else 0
    col4.metric("Attrition Rate", f"{attr_rate}%")

    # Layout: charts and table
    with st.expander("Charts", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Employees by Department")
            dept_counts = filtered["Department"].value_counts().rename_axis("Department").reset_index(name="Count")
            if not dept_counts.empty:
                fig_dept = px.bar(dept_counts, x="Department", y="Count", title="Employees by Department", labels={"Count":"Employees"})
                st.plotly_chart(fig_dept, use_container_width=True)
            else:
                st.info("No data for selected filters.")

            st.subheader("Salary Distribution")
            if not filtered.empty:
                fig_salary = px.histogram(filtered, x="Salary", nbins=20, title="Salary Distribution", labels={"Salary":"Salary"})
                st.plotly_chart(fig_salary, use_container_width=True)
            else:
                st.info("No data for selected filters.")

        with c2:
            st.subheader("Age vs Salary")
            if not filtered.empty:
                fig_scatter = px.scatter(filtered, x="Age", y="Salary", color="Department", hover_data=["Name","EmployeeID"], title="Age vs Salary")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No data for selected filters.")

            st.subheader("Attrition by Department")
            if not filtered.empty:
                attr_dept = filtered.groupby(["Department","Attrition"]).size().reset_index(name="Count")
                fig_attr = px.bar(attr_dept, x="Department", y="Count", color="Attrition", barmode="group", title="Attrition by Department")
                st.plotly_chart(fig_attr, use_container_width=True)

    st.markdown("---")
    st.subheader("Employee Table")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)

    st.markdown("### Export filtered data")
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV of filtered data", data=csv, file_name="filtered_hr_data.csv", mime="text/csv")
else:
    st.info("No data loaded. Upload a CSV or add 'hr_data.csv' to the repo.")

