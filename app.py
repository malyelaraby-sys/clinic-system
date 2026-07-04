import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

from database.models import create_tables
from modules.patients import add_patient, get_all_patients
from modules.visits import add_visit, get_visits_by_patient
from modules.doctors import add_doctor, get_doctors
from modules.orders import add_order, get_orders_by_patient
from utils.tracker import log_event


def format_datetime(timestamp):
    if not timestamp:
        return ""

    try:
        dt = datetime.fromisoformat(str(timestamp))

        # Cairo time
        dt = dt + timedelta(hours=3)

        return dt.strftime("%d %b %Y, %I:%M %p")

    except Exception:
        return str(timestamp)


# Title
st.title("Clinic System MVP")

# Ensure database exists
create_tables()

# -------------------------
# 🔑 Doctor Management (IMPROVED)
# -------------------------

st.sidebar.header("Doctors")

new_doctor = st.sidebar.text_input("Add New Doctor").strip()

if st.sidebar.button("Add Doctor"):
    if new_doctor:
        doctor_list = get_doctors()

        if new_doctor not in doctor_list:
            add_doctor(new_doctor)
            st.sidebar.success("Doctor added ✅")
        else:
            st.sidebar.warning("Doctor already exists")
    else:
        st.sidebar.error("Enter doctor name")

doctor_list = get_doctors()

if not doctor_list:
    st.warning("No doctors found. Please add one first.")
    st.stop()

doctor_name = st.selectbox("Select Current Doctor", doctor_list)

# ✅ Better UI display
st.header(f"Doctor: {doctor_name}")

# -------------------------
# SIDEBAR → Add Patient
# -------------------------

st.sidebar.header("Add New Patient")

name = st.sidebar.text_input("Patient Name")

birth_date = st.sidebar.date_input(
    "Date of Birth",
    value=date(1990, 1, 1),
    min_value=date(1900, 1, 1),
    max_value=date.today(),
)

gender = st.sidebar.selectbox("Gender", ["Male", "Female"])

phone = st.sidebar.text_input("Phone Number")

national_id = st.sidebar.text_input("National ID")

address = st.sidebar.text_area("Address")

emergency_contact = st.sidebar.text_input("Emergency Contact")

allergies = st.sidebar.text_area("Allergies")

chronic_diseases = st.sidebar.text_area("Chronic Diseases")

if st.sidebar.button("Add Patient"):
    if name:
        add_patient(
            name,
            phone,
            gender,
            doctor_name,
            str(birth_date),
            national_id,
            address,
            emergency_contact,
            allergies,
            chronic_diseases,
        )

        log_event("ADD_PATIENT", name)
        st.sidebar.success("Added ✅")
    else:
        log_event("ERROR_ADD_PATIENT", "Missing name")
        st.sidebar.error("Name required ❌")

# -------------------------
# MAIN → Patients + Search
# -------------------------

st.subheader("Patients")

patients = get_all_patients(doctor_name)

search_type = st.selectbox("Search By", ["Patient ID", "Name", "Phone", "National ID"])

search_value = st.text_input("Search")

if patients:
    df = pd.DataFrame(
        patients,
        columns=[
            "ID",
            "Name",
            "Phone",
            "Gender",
            "Birth Date",
            "National ID",
            "Address",
            "Emergency Contact",
            "Allergies",
            "Chronic Diseases",
            "Created At",
        ],
    )

    def calculate_age(birth_date):
        if pd.isna(birth_date) or birth_date in ["", None]:
            return None

        birth_date = datetime.strptime(str(birth_date), "%Y-%m-%d").date()

        today = date.today()

        return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

    df["Age"] = df["Birth Date"].apply(calculate_age)
    if search_value:
        if search_type == "Patient ID":
            df = df[df["ID"].astype(str) == search_value]
        elif search_type == "Name":
            df = df[df["Name"].str.contains(search_value, case=False, na=False)]
        elif search_type == "Phone":
            df = df[
                df["Phone"].astype(str).str.contains(search_value, case=False, na=False)
            ]
        elif search_type == "National ID":
            df = df[
                df["National ID"]
                .astype(str)
                .str.contains(search_value, case=False, na=False)
            ]
        log_event("SEARCH_PATIENT", f"{search_type}: {search_value}")
    st.dataframe(df)

    patient_options = {
        f"{row['Name']} (ID {row['ID']})": row["ID"] for _, row in df.iterrows()
    }

    patient_keys = list(patient_options.keys())

    if patient_keys:

        selected_patient = st.selectbox(
            "Current Patient", patient_keys, key="current_patient"
        )

        current_patient_id = patient_options.get(selected_patient)

        if current_patient_id is None:
            st.warning("Select a patient")
            st.stop()

    else:
        st.warning("No matching patients")
        st.stop()

    current_patient = df[df["ID"] == current_patient_id].iloc[0]
    st.markdown("---")
    st.subheader("Patient Summary")

    st.write(f"**Name:** {current_patient['Name']}")

    st.write(f"**Age:** {current_patient['Age']}")
    st.write(f"**Gender:** {current_patient['Gender']}")

    st.write(f"**Phone:** {current_patient['Phone']}")

    st.write(f"**National ID:** {current_patient['National ID']}")

    st.write(f"**Allergies:** " f"{current_patient['Allergies'] or 'None'}")

    st.write(
        f"**Chronic Diseases:** " f"{current_patient['Chronic Diseases'] or 'None'}"
    )

    st.markdown("---")
else:
    st.write("No patients yet")

# -------------------------
# MAIN → Add Visit
# -------------------------

with st.expander("Add Visit", expanded=True):

    if patients:
        if current_patient_id:

            st.write(f"Current Patient: {current_patient['Name']}")
            with st.form("visit_form"):

                chief_complaint = st.text_input(
                    "Chief Complaint", key="visit_chief_complaint"
                )

                history_present_illness = st.text_area(
                    "History of Present Illness", key="visit_hpi"
                )

                examination = st.text_area("Examination", key="visit_examination")

                assessment = st.text_input("Diagnosis", key="visit_diagnosis")

                plan = st.text_area("Plan", key="visit_plan")

                submitted = st.form_submit_button("Add Visit")

                if submitted:
                    patient_id = current_patient_id

                    if chief_complaint.strip() and assessment.strip():
                        add_visit(
                            patient_id=patient_id,
                            doctor_name=doctor_name,
                            chief_complaint=chief_complaint,
                            history_present_illness=history_present_illness,
                            examination=examination,
                            assessment=assessment,
                            plan=plan,
                        )
                        log_event("ADD_VISIT", current_patient["Name"])
                        st.success("Visit added ✅")

                    else:
                        log_event("ERROR_ADD_VISIT", current_patient["Name"])
                        st.error("Chief Complaint and Diagnosis are required ❌")
        else:
            st.write("Select a patient")
    else:
        st.write("Add a patient first")

# -------------------------
# MAIN → Visit History (FINAL VERSION)
# -------------------------

with st.expander("Visit History"):

    if patients:
        st.write(f"Current Patient: {current_patient['Name']}")

        patient_id = current_patient_id

        visits = get_visits_by_patient(patient_id, doctor_name)

        log_event("VIEW_HISTORY", current_patient["Name"])

        if visits:
            for visit in visits:
                if len(visit) == 6:
                    visit_id, pid, date, complaint, diagnosis, notes = visit

                    chief_complaint = ""
                    history_present_illness = ""
                    examination = ""
                    assessment = ""
                    plan = ""
                else:
                    (
                        visit_id,
                        pid,
                        date,
                        complaint,
                        diagnosis,
                        notes,
                        chief_complaint,
                        history_present_illness,
                        examination,
                        assessment,
                        plan,
                    ) = visit

                with st.expander(f"Visit on {format_datetime(date)}"):
                    # New structured visit
                    if chief_complaint:
                        st.markdown(f"**Chief Complaint:** {chief_complaint}")

                        st.markdown("**History of Present Illness:**")
                        st.text(
                            history_present_illness
                            if history_present_illness
                            else "Not documented"
                        )

                        st.markdown("**Examination:**")
                        st.text(examination if examination else "Not documented")

                        st.markdown(f"**Diagnosis:** {assessment}")

                        st.markdown("**Plan:**")
                        st.text(plan if plan else "Not documented")

                    # Legacy visit
                    else:
                        st.markdown(f"**Complaint:** {complaint}")

                        st.markdown(f"**Diagnosis:** {diagnosis}")

                        st.markdown("**Notes:**")

                        st.text(notes if notes else "No notes")
        else:
            st.write("No visits found")
# -------------------------
# MAIN → Orders
# -------------------------

with st.expander("Orders"):

    if patients:

        st.write(f"Current Patient: {current_patient['Name']}")
        with st.form("order_form"):
            order_type = st.selectbox(
                "Order Type", ["Laboratory", "Imaging", "Procedure", "Referral"]
            )

            order_text = st.text_area("Order Details")

            submitted_order = st.form_submit_button("Add Order")

            if submitted_order:

                if order_text.strip():

                    patient_id = current_patient_id

                    add_order(
                        visit_id=None,
                        patient_id=patient_id,
                        doctor_name=doctor_name,
                        order_type=order_type,
                        order_text=order_text,
                    )

                    st.success("Order added ✅")

                else:
                    st.error("Order details required ❌")
# -------------------------
# MAIN → Order History
# -------------------------

with st.expander("Order History"):

    if patients:

        st.write(f"Current Patient: {current_patient['Name']}")

        patient_id = current_patient_id

        orders = get_orders_by_patient(patient_id, doctor_name)

        if orders:

            for order in orders:

                with st.expander(
                    f"{order['order_type']} - "
                    f"{format_datetime(order['created_at'])}"
                ):

                    st.markdown(f"**Type:** {order['order_type']}")

                    st.markdown("**Details:**")

                    st.text(order.get("order_text", "No details"))

        else:
            st.write("No orders found")
