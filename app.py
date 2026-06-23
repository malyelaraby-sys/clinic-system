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
# Add Patient Section
# -------------------------

st.header("Add New Patient")

name = st.text_input("Patient Name")
phone = st.text_input("Phone Number")
gender = st.selectbox("Gender", ["Male", "Female"])

if st.button("Add Patient"):
    if name:
        add_patient(name, phone, gender)
        log_event("ADD_PATIENT", name)
        st.success("Patient added successfully ✅")
    else:
        log_event("ERROR_ADD_PATIENT", "Missing name")
        st.error("Name is required ❌")

# -------------------------
# Search + Display Patients Section (UPDATED)
# -------------------------

st.header("Patients")

patients = get_all_patients()

search = st.text_input("Search patient by name or phone")

if patients:
    df = pd.DataFrame(
        patients,
        columns=["ID", "Name", "Phone", "Gender", "Created At"]
    )

    # ✅ Apply search filter
    if search:
        df = df[
            df["Name"].str.contains(search, case=False, na=False) |
            df["Phone"].astype(str).str.contains(search, case=False, na=False)
        ]
        log_event("SEARCH_PATIENT", search)

    st.dataframe(df)
else:
    st.write("No patients found")

# -------------------------
# Add Visit Section
# -------------------------

st.header("Add Visit")

if patients:
    # use filtered df for dropdown
    patient_dict = {f"{row['Name']} (ID {row['ID']})": row["ID"]
                    for _, row in df.iterrows()} if search else \
                   {f"{p[1]} (ID {p[0]})": p[0] for p in patients}

    if patient_dict:
        selected_patient = st.selectbox(
            "Select Patient for Visit",
            list(patient_dict.keys())
        )

        complaint = st.text_area("Complaint")
        diagnosis = st.text_area("Diagnosis")
        notes = st.text_area("Notes")

        if st.button("Add Visit"):
            patient_id = patient_dict[selected_patient]

            if complaint and diagnosis:
                add_visit(patient_id, complaint, diagnosis, notes)
                log_event("ADD_VISIT", selected_patient)
                st.success("Visit added successfully ✅")
            else:
                log_event("ERROR_ADD_VISIT", selected_patient)
                st.error("Complaint and Diagnosis are required ❌")
    else:
        st.write("No matching patient found for visit")
else:
    st.write("Add a patient first before adding visits.")

# -------------------------
# View Visit History Section
# -------------------------

st.header("Patient Visit History")

if patients:
    patient_dict_history = {f"{p[1]} (ID {p[0]})": p[0] for p in patients}

    selected_patient_history = st.selectbox(
        "Select Patient to View History",
        list(patient_dict_history.keys())
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
        st.write("No visits found for this patient")