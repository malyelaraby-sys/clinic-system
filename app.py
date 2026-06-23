import streamlit as st
import pandas as pd

from database.models import create_tables
from modules.patients import add_patient, get_all_patients
from modules.visits import add_visit, get_visits_by_patient

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
        st.success("Patient added successfully ✅")
    else:
        st.error("Name is required ❌")

# -------------------------
# Display Patients Section
# -------------------------

st.header("All Patients")

patients = get_all_patients()

if patients:
    df = pd.DataFrame(
        patients,
        columns=["ID", "Name", "Phone", "Gender", "Created At"]
    )
    st.dataframe(df)
else:
    st.write("No patients found")

# -------------------------
# Add Visit Section
# -------------------------

st.header("Add Visit")

if patients:
    patient_dict = {f"{p[1]} (ID {p[0]})": p[0] for p in patients}
    selected_patient = st.selectbox("Select Patient for Visit", list(patient_dict.keys()))

    complaint = st.text_area("Complaint")
    diagnosis = st.text_area("Diagnosis")
    notes = st.text_area("Notes")

    if st.button("Add Visit"):
        patient_id = patient_dict[selected_patient]

        if complaint and diagnosis:
            add_visit(patient_id, complaint, diagnosis, notes)
            st.success("Visit added successfully ✅")
        else:
            st.error("Complaint and Diagnosis are required ❌")
else:
    st.write("Add a patient first before adding visits.")

# -------------------------
# View Visit History Section (NEW)
# -------------------------

st.header("Patient Visit History")

if patients:
    selected_patient_history = st.selectbox(
        "Select Patient to View History",
        list(patient_dict.keys())
    )

    patient_id = patient_dict[selected_patient_history]

    visits = get_visits_by_patient(patient_id)

    if visits:
        visits_df = pd.DataFrame(
            visits,
            columns=["Visit ID", "Patient ID", "Date", "Complaint", "Diagnosis", "Notes"]
        )
        st.dataframe(visits_df)
    else:
        st.write("No visits found for this patient")