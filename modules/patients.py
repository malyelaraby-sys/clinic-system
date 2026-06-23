from database.db import connect_db

# ✅ Add a new patient
def add_patient(name, phone, gender):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients (name, phone, gender)
    VALUES (?, ?, ?)
    """, (name, phone, gender))

    conn.commit()
    conn.close()


# ✅ Get all patients
def get_all_patients():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()
    return patients