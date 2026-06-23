import streamlit as st
import pandas as pd

from database.models import create_tables
from modules.patients import add_patient, get_all_patients
from modules.visits import add_visit, get_visits_by_patient
from utils.tracker import log_event

# Title
st.title("Clinic System MVP")

# Ensure database + tables exist
create_tables()

# -------------------------
# SIDEBAR → Add Patient
# -------------------------

st.sidebar.header("Add New Patient")

name = st.sidebar.text_input("Patient Name")
phone = st.sidebar.text_input("Phone Number")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])

if st.sidebar.button("Add Patient"):
    if name:
        add_patient(name, phone, gender)
        log_event("ADD_PATIENT", name)
        st.sidebar.success("Added ✅")
    else:
        log_event("ERROR_ADD_PATIENT", "Missing name")
        st.sidebar.error("Name required ❌")

# -------------------------
# MAIN → Patients + Search
# -------------------------

st.header("Patients")

patients = get_all_patients()

search = st.text_input("🔍 Search by name or phone")

if patients:
    df = pd.DataFrame(
        patients,
        columns=["ID", "Name", "Phone", "Gender", "Created At"]
    )

    if search:
        df = df[
            df["Name"].str.contains(search, case=False, na=False) |
            df["Phone"].astype(str).str.contains(search, case=False, na=False)
        ]
        log_event("SEARCH_PATIENT", search)

    st.dataframe(df)
else:
    st.write("No patients yet")

# -------------------------
# MAIN → Add Visit
# -------------------------

st.header("Add Visit")

if patients:
    if search:
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
            key="visit_patient"   # ✅ FIX
        )

        complaint = st.text_area("Complaint")
        diagnosis = st.text_area("Diagnosis")
        notes = st.text_area("Notes")

        if st.button("Add Visit"):
            patient_id = patient_dict[selected_patient]

            if complaint and diagnosis:
                add_visit(patient_id, complaint, diagnosis, notes)
                log_event("ADD_VISIT", selected_patient)
                st.success("Visit added ✅")
            else:
                log_event("ERROR_ADD_VISIT", selected_patient)
                st.error("Fill required fields ❌")
    else:
        st.write("No matching patient")
else:
    st.write("Add a patient first")

# -------------------------
# MAIN → Visit History
# -------------------------

st.header("Visit History")

if patients:
    patient_dict_history = {
        f"{p[1]} (ID {p[0]})": p[0]
        for p in patients
    }

    selected_patient_history = st.selectbox(
        "Select Patient",
        list(patient_dict_history.keys()),
        key="history_patient"   # ✅ FIX
    )

    patient_id = patient_dict_history[selected_patient_history]

    visits = get_visits_by_patient(patient_id)

    log_event("VIEW_HISTORY", selected_patient_history)

    if visits:
        visits_df = pd.DataFrame(
            visits,
            columns=["Visit ID", "Patient ID", "Date", "Complaint", "Diagnosis", "Notes"]
        )
        st.dataframe(visits_df)
    else:
        st.write("No visits found")
