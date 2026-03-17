import sqlite3
import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "hospital_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hospital.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
try:
    c.execute("ALTER TABLE tele_queue ADD COLUMN link TEXT")
except:
    pass

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# PATIENTS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    disease TEXT
)
""")

# APPOINTMENTS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT
)
""")

# TELEMEDICINE TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS telemedicine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient TEXT,
    doctor TEXT,
    time TEXT,
    status TEXT,
    link TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tele_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient TEXT,
    doctor TEXT,
    phone TEXT,
    time TEXT,
    status TEXT,
    link TEXT
)
""")

# c.execute("ALTER TABLE tele_queue ADD COLUMN phone TEXT")

conn.commit()
conn.close()
# ---------------- LOGIN PAGE ----------------

@app.route("/")
def login():
    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("hospital.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()

        if user:
            session["logged_in"] = True

        else:
            return "Invalid Login"

    if session.get("logged_in"):

        conn = sqlite3.connect("hospital.db")
        c = conn.cursor()

        # count patients
        c.execute("SELECT COUNT(*) FROM patients")
        patient_count = c.fetchone()[0]

        # count appointments
        c.execute("SELECT COUNT(*) FROM appointments")
        appointment_count = c.fetchone()[0]

        conn.close()

        return render_template(
            "dashboard.html",
            patient_count=patient_count,
            appointment_count=appointment_count
        )

    return render_template("login.html")

# ---------------- PATIENTS PAGE ----------------

@app.route("/patients")
def patients():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM patients")
    data = c.fetchall()

    conn.close()

    return render_template("patients.html", patients=data)


# ---------------- ADD PATIENT ----------------

@app.route("/add_patient")
def add_patient():
    return render_template("add_patient.html")


@app.route("/save_patient", methods=["POST"])
def save_patient():

    name = request.form["name"]
    age = request.form["age"]
    disease = request.form["disease"]

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("INSERT INTO patients (name, age, disease) VALUES (?, ?, ?)", (name, age, disease))
    conn.commit()

    conn.close()

    return redirect("/patients")


# ---------------- APPOINTMENTS ----------------

@app.route("/appointments")
def appointments():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM appointments")
    count = c.fetchone()[0]

    conn.close()

    if count > 0:
        return redirect("/view_appointments")
    else:
        return render_template("appointments.html")


# ---------------- SAVE APPOINTMENT ----------------

@app.route("/save_appointment", methods=["POST"])
def save_appointment():

    name = request.form["name"]
    doctor = request.form["doctor"]
    date = request.form["date"]

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("INSERT INTO appointments (patient, doctor, date) VALUES (?, ?, ?)", (name, doctor, date))
    conn.commit()

    conn.close()

    return redirect("/view_appointments")


# ---------------- VIEW APPOINTMENTS ----------------

@app.route("/view_appointments")
def view_appointments():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM appointments")
    data = c.fetchall()

    conn.close()

    return render_template("view_appointments.html", appointments=data)


# ---------------- DELETE APPOINTMENT ----------------

@app.route("/delete_appointment/<int:id>")
def delete_appointment(id):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit()

    conn.close()

    return redirect("/view_appointments")

@app.route("/telemedicine")
def telemedicine():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM tele_queue")
    consultations = c.fetchall()

    conn.close()

    return render_template("telemedicine.html", consultations=consultations)

@app.route("/start_consultation", methods=["POST"])
def start_consultation():

    patient = request.form["patient"]
    doctor = request.form["doctor"]
    phone = request.form["phone"]
    time = request.form["time"]

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute(
"INSERT INTO tele_queue (patient, doctor, phone, time, status, link) VALUES (?, ?, ?, ?, ?, ?)",
(patient, doctor, phone, time, "waiting", "")
)

    conn.commit()
    conn.close()

    return render_template(
        "consultation.html",
        patient=patient,
        doctor=doctor,
        time=time
    ) 

@app.route('/delete_patient/<int:id>')
def delete_patient(id):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("DELETE FROM patients WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/patients')

@app.route('/prescription')
def prescription():
    return render_template('prescription.html')

@app.route('/delete_tele/<int:id>')
def delete_tele(id):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("DELETE FROM tele_queue WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/telemedicine')

@app.route('/generate_link/<int:id>')
def generate_link(id):

    import random

    meeting_id = random.randint(100000,999999)

    link = f"https://meet.google.com/{meeting_id}"

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("UPDATE tele_queue SET link=? WHERE id=?", (link,id))

    conn.commit()
    conn.close()

    return redirect('/telemedicine')

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)