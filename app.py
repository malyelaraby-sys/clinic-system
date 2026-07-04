import streamlit as st
import pandas as pd
from datetime import date, datetime

from database.models import create_tables
from modules.patients import add_patient, get_all_patients
from modules.visits import add_visit, get_visits_by_patient
from modules.doctors import add_doctor, get_doctors
from utils.tracker import log_event

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
    max_value=date.today()
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
    chronic_diseases
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

search_type = st.selectbox(
    "Search By",
    ["Patient ID", "Name", "Phone", "National ID"]
)

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
            "Created At"
        ]
    )
    def calculate_age(birth_date):
        if pd.isna(birth_date) or birth_date in ["", None]:
            return None

        birth_date = datetime.strptime(
            str(birth_date),
            "%Y-%m-%d"
        ).date()

        today = date.today()

        return (
            today.year
            - birth_date.year
            - (
                (today.month, today.day)
                < (birth_date.month, birth_date.day)
            )
        )

    df["Age"] = df["Birth Date"].apply(calculate_age)
    if search_value:
        if search_type == "Patient ID":
            df = df[
                df["ID"].astype(str) == search_value
            ]
        elif search_type == "Name":
            df = df[
                df["Name"].str.contains(
                    search_value,
                    case=False,
                    na=False
                )
            ]
        elif search_type == "Phone":
            df = df[
                df["Phone"].astype(str).str.contains(
                    search_value,
                    case=False,
                    na=False
                )
            ]
        elif search_type == "National ID":
            df = df[
                df["National ID"].astype(str).str.contains(
                    search_value,
                    case=False,
                    na=False
                )
            ]
        log_event(
            "SEARCH_PATIENT",
            f"{search_type}: {search_value}"
        )
    st.dataframe(df)
else:
    st.write("No patients yet")

# -------------------------
# MAIN → Add Visit
# -------------------------

st.subheader("Add Visit")

if patients:
    if search_value:
        patient_dict = {
            f"{row['Name']} (ID {row['ID']})": row["ID"]
            for _, row in df.iterrows()
        }
    else:
        patient_dict = {
            f"{p[1]} (ID {p[0]})": p[0]
            for p in patients
        }

    if patient_dict:
        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_dict.keys()),
            key="visit_patient"
        )

        chief_complaint = st.text_input("Chief Complaint")

        history_present_illness = st.text_area(
            "History of Present Illness"
        )

        examination = st.text_area(
            "Examination"
        )

        assessment = st.text_input("Diagnosis")

        plan = st.text_area(
            "Plan"
        )

        if st.button("Add Visit"):
            patient_id = patient_dict[selected_patient]

            if chief_complaint.strip() and assessment.strip():
                add_visit(
                    patient_id=patient_id,
                    doctor_name=doctor_name,
                    chief_complaint=chief_complaint,
                    history_present_illness=history_present_illness,
                    examination=examination,
                    assessment=assessment,
                    plan=plan
               )
                log_event("ADD_VISIT", selected_patient)
                st.success("Visit added ✅")
            else:
                log_event("ERROR_ADD_VISIT", selected_patient)
                st.error(
                    "Chief Complaint and Diagnosis are required ❌"
            )
    else:
        st.write("No matching patient")
else:
    st.write("Add a patient first")

# -------------------------
# MAIN → Visit History (FINAL VERSION)
# -------------------------

st.subheader("Visit History")

if patients:
    patient_dict_history = {
        f"{p[1]} (ID {p[0]})": p[0]
        for p in patients
    }

    selected_patient_history = st.selectbox(
        "Select Patient",
        list(patient_dict_history.keys()),
        key="history_patient"
    )

    patient_id = patient_dict_history[selected_patient_history]

    visits = get_visits_by_patient(patient_id, doctor_name)

    log_event("VIEW_HISTORY", selected_patient_history)

    if visits:
        for visit in visits:
            if len(visit) == 6:
                (
                    visit_id,
                    pid,
                    date,
                    complaint,
                    diagnosis,
                    notes
                ) = visit

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
                    plan
                ) = visit

            with st.expander(f"Visit on {date}"):
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
                    st.text(
                        examination
                        if examination
                        else "Not documented"
                    )

                    st.markdown(f"**Diagnosis:** {assessment}")

                    st.markdown("**Plan:**")
                    st.text(
                        plan
                        if plan
                        else "Not documented"
                    )

                # Legacy visit
                else:
                    st.markdown(f"**Complaint:** {complaint}")

                    st.markdown(f"**Diagnosis:** {diagnosis}")

                    st.markdown("**Notes:**")

                    st.text(
                        notes
                        if notes
                        else "No notes"
                    )
    else:
        st.write("No visits found")