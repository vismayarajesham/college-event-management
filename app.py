import random
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, session, redirect, send_from_directory
import sqlite3
from reportlab.pdfgen import canvas
import os
app = Flask(__name__)
app.secret_key = "event_secret_key"
def send_otp_email(receiver_email, otp):

    try:
        sender_email = os.getenv("EMAIL_ADDRESS")
        app_password = os.getenv("EMAIL_APP_PASSWORD")

        message = MIMEText(
            f"Your OTP for password reset is: {otp}"
        )

        message["Subject"] = "Event Management System OTP"
        message["From"] = sender_email
        message["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(sender_email, app_password)
        server.send_message(message)
        server.quit()

        print("✅ Email sent successfully to:", receiver_email)

    except Exception as e:
        print("❌ Email Error:", e)
# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Login Page

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return "Email or Password not received from login form."

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM students WHERE email=? AND password=?",
            (email, password)
        )

        student = cursor.fetchone()

        if student:

            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()
           
            session['student_name'] = student[0]
            session['student_email'] = email

            conn.close()
            return render_template(
                'dashboard.html',
                name=student[0],
                events=events
            )

        conn.close()

        return "Invalid Email or Password"

    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        name = request.form['student_name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO students(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )

            conn.commit()

            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()

            conn.close()
            session['student_name'] = name

            return render_template(
                'dashboard.html',
                name=name,
                events=events
            )

        except sqlite3.IntegrityError:

            conn.close()

            return "Email already registered. Please Login."

    return render_template('signup.html')
# Dashboard Page
@app.route('/dashboard')
def dashboard():

    student_name = session.get("student_name", "Student")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=student_name,
        events=events
    )

# Individual Event Registration
@app.route('/registration')
def registration():
    return render_template(
        'registration.html',
        name='Student'
    )


# Group Event Registration
@app.route('/group_registration')
def group_registration():
    return render_template('group_registration.html')


# Group Registration Success
@app.route('/group_success')
def group_success():

    team = request.args.get('team_name')
    leader = request.args.get('leader')
    participants = request.args.get('participants')
    m1 = request.args.get('member1')
    m2 = request.args.get('member2')
    m3 = request.args.get('member3')

    return render_template(
        'group_success.html',
        team=team,
        leader=leader,
        participants=participants,
        m1=m1,
        m2=m2,
        m3=m3
    )
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():

    if request.method == 'POST':

        email = request.form['email']

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email=?",
            (email,)
        )

        student = cursor.fetchone()

        conn.close()

        if student:

            otp = random.randint(100000, 999999)

            session['otp'] = str(otp)
            session['reset_email'] = email

            print("Email:", email)
            print("OTP:", otp)

            send_otp_email(email, otp)

            return render_template('otp.html')

        else:

            return "Email not registered."

    return render_template('forgot.html')

@app.route('/otp', methods=['GET', 'POST'])
def otp():

    if request.method == 'POST':

        entered_otp = request.form['otp']

        if entered_otp == session.get('otp'):
            return render_template('reset_password.html')

        else:
            return "Invalid OTP"

    return render_template('otp.html')
@app.route('/reset_password', methods=['POST'])
def reset_password():

    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        return "Passwords do not match."

    email = session.get('reset_email')

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET password=? WHERE email=?",
        (new_password, email)
    )

    conn.commit()
    conn.close()

    # Remove OTP and email from session
    session.pop('otp', None)
    session.pop('reset_email', None)

    return render_template("password_changed.html")
@app.route('/events')
def events():

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    conn.close()

    return render_template(
        'events.html',
        events=events
    )
@app.route('/my_registrations')
def my_registrations():

    student_name = session.get('student_name')

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM registrations WHERE student_name=?",
        (student_name,)
    )

    registrations = cursor.fetchall()

    conn.close()

    return render_template(
        'my_registrations.html',
        registrations=registrations
    )
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("event_management.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE email=? AND password=?",
            (email, password)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:

            session["admin"] = admin[1]
            session["admin_email"] = admin[2]

            return redirect("/admin_dashboard")

        else:
            return "Invalid Email or Password"

    return render_template("admin_login.html")
@app.route('/registered_students')
def registered_students():

    if "admin" not in session:
        return redirect("/admin_login")

    search = request.args.get("search", "")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM registrations
        WHERE student_name LIKE ?
        OR event_name LIKE ?
        """,
        (f"%{search}%", f"%{search}%")
    )

    registrations = cursor.fetchall()

    conn.close()

    return render_template(
        "registered_students.html",
        registrations=registrations,
        search=search
    )
@app.route('/manage_events')
def manage_events():
    if "admin" not in session:
        return redirect("/admin_login")
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")

    events = cursor.fetchall()

    conn.close()

    return render_template(
        'manage_events.html',
        events=events
    )

@app.route('/admin_forgot', methods=['GET', 'POST'])
def admin_forgot():

    if request.method == 'POST':

        email = request.form['email']

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE email=?",
            (email,)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:

            otp = random.randint(100000, 999999)

            session['admin_otp'] = str(otp)
            session['admin_reset_email'] = email

            send_otp_email(email, otp)

            return redirect("/admin_otp")

        else:

            return "Admin email not found."

    return render_template("admin_forgot.html")

@app.route('/admin_otp', methods=['GET', 'POST'])
def admin_otp():

    if request.method == 'POST':

        entered_otp = request.form['otp']

        if entered_otp == session.get('admin_otp'):
            return render_template("admin_reset_password.html")

        else:
            return "Invalid OTP"

    return render_template("admin_otp.html")
@app.route('/change_admin_password', methods=['GET', 'POST'])
def change_admin_password():

    if request.method == 'POST':

        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            return "New Password and Confirm Password do not match"

        return "Password Changed Successfully"

    return render_template('change_admin_password.html')
@app.route('/verify_admin_otp', methods=['POST'])
def verify_admin_otp():

    otp = request.form['otp']

    if otp == "123456":
        return render_template('admin_dashboard.html')

    return "Invalid OTP"
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if "admin" not in session:
        return redirect("/admin_login")
    if request.method == 'POST':

        event_name = request.form['event_name']
        event_type = request.form['event_type']
        event_time = request.form['event_time']
        min_members = request.form['min_members']
        max_members = request.form['max_members']

        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO events
            (event_name,event_type,event_time,min_members,max_members)
            VALUES(?,?,?,?,?)
            """,
            (
                event_name,
                event_type,
                event_time,
                min_members,
                max_members
            )
        )

        conn.commit()
        conn.close()

        return render_template('event_added.html')

    return render_template('add_event.html')
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    if request.method == "POST":

        event_name = request.form['event_name']
        event_type = request.form['event_type']
        event_time = request.form['event_time']
        min_members = request.form['min_members']
        max_members = request.form['max_members']

        cursor.execute(
            """
            UPDATE events
            SET event_name=?,
                event_type=?,
                event_time=?,
                min_members=?,
                max_members=?
            WHERE id=?
            """,
            (
                event_name,
                event_type,
                event_time,
                min_members,
                max_members,
                event_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/manage_events")

    cursor.execute(
        "SELECT * FROM events WHERE id=?",
        (event_id,)
    )

    event = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_event.html",
        event=event
    )
@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    if "admin" not in session:
        return redirect("/admin_login")
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM events WHERE id=?",
        (event_id,)
    )

    conn.commit()
    conn.close()

    return render_template('event_deleted.html')
@app.route('/delete_registration/<int:registration_id>')
def delete_registration(registration_id):
    if "admin" not in session:
        return redirect("/admin_login")
    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM registrations WHERE id=?",
        (registration_id,)
    )

    conn.commit()
    conn.close()

    return render_template(
    'registration_deleted.html'
)
@app.route('/register_event/<event_name>')
def register_event(event_name):

    student_name = session.get('student_name')

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    # Get student's email
    cursor.execute(
        "SELECT email FROM students WHERE name=?",
        (student_name,)
    )

    student = cursor.fetchone()

    if student:
        student_email = student[0]
    else:
        student_email = ""

    # Register the event
    cursor.execute(
        "INSERT INTO registrations(student_name,event_name) VALUES(?,?)",
        (student_name, event_name)
    )

    conn.commit()
    conn.close()

    # Send confirmation email
    if student_email:
        send_registration_email(
            student_email,
            student_name,
            event_name
        )

    return render_template(
        'registration_success.html',
        student_name=student_name,
        event_name=event_name
    )
@app.route('/test_email')
def test_email():

    otp = random.randint(100000,999999)

    send_otp_email(
        "vismayarajesham@gmail.com",
        otp
    )

    return f"OTP Sent: {otp}"
@app.route('/admin_logout')
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin_login")
@app.route('/admin_profile')
def admin_profile():

    if "admin" not in session:
        return redirect("/admin_login")

    return render_template("admin_profile.html")
@app.route('/admin_reset_password', methods=['POST'])
def admin_reset_password():

    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        return "Passwords do not match."

    email = session.get('admin_reset_email')

    conn = sqlite3.connect('event_management.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE admins SET password=? WHERE email=?",
        (new_password, email)
    )

    conn.commit()
    conn.close()

    session.pop("admin_otp", None)
    session.pop("admin_reset_email", None)

    return render_template("admin_password_changed.html")
@app.route('/admin_dashboard')
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    # Total Events
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Registrations
    cursor.execute("SELECT COUNT(*) FROM registrations")
    total_registrations = cursor.fetchone()[0]

    # Group Events
    cursor.execute("SELECT COUNT(*) FROM events WHERE event_type='Group'")
    group_events = cursor.fetchone()[0]

    # Solo Events
    cursor.execute("SELECT COUNT(*) FROM events WHERE event_type='Solo'")
    solo_events = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_events=total_events,
        total_students=total_students,
        total_registrations=total_registrations,
        group_events=group_events,
        solo_events=solo_events
    )
def send_registration_email(receiver_email, student_name, event_name):

    print("========== REGISTRATION EMAIL ==========")
    print("Receiver Email :", receiver_email)
    print("Student Name  :", student_name)
    print("Event Name    :", event_name)

    try:

        sender_email = os.getenv("EMAIL_ADDRESS")
        app_password = os.getenv("EMAIL_APP_PASSWORD")
        message = MIMEText(
            f"""
Hello {student_name},

Congratulations!

You have successfully registered for:

{event_name}

Your registration has been confirmed.

Thank you for participating.

Regards,
College Event Management System
"""
        )

        message["Subject"] = "Event Registration Successful"
        message["From"] = sender_email
        message["To"] = receiver_email

        print("Connecting to Gmail...")

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        print("Logging in...")

        server.login(sender_email, app_password)

        print("Sending email...")

        server.send_message(message)

        print("✅ Registration Email Sent Successfully!")

        server.quit()

    except Exception as e:

        print("❌ Registration Email Error:")
        print(e)
@app.route('/generate_certificate/<int:registration_id>')
def generate_certificate(registration_id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT registrations.student_name,
               students.email,
               registrations.event_name
        FROM registrations
        JOIN students
        ON registrations.student_name = students.name
        WHERE registrations.id=?
    """, (registration_id,))

    data = cursor.fetchone()

    if not data:
        conn.close()
        return "Registration not found."

    student_name = data[0]
    student_email = data[1]
    event_name = data[2]

    # Create certificates folder if it doesn't exist
    certificate_folder = os.path.join(app.root_path, "certificates")
    os.makedirs(certificate_folder, exist_ok=True)

    # PDF filename
    filename = f"{student_name}_{event_name}.pdf"
    filepath = os.path.join(certificate_folder, filename)

    # Create PDF
    pdf = canvas.Canvas(filepath)

    pdf.setTitle("Participation Certificate")

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(300, 760, "CERTIFICATE OF PARTICIPATION")

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        300,
        700,
        "This certificate is proudly presented to"
    )

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(
        300,
        650,
        student_name
    )

    pdf.setFont("Helvetica", 18)
    pdf.drawCentredString(
        300,
        600,
        "For successfully participating in"
    )

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        300,
        560,
        event_name
    )

    pdf.setFont("Helvetica", 14)
    pdf.drawString(50, 120, "College Event Management System")

    pdf.save()

    cursor.execute(
        """
        INSERT INTO certificates
        (student_name, student_email, event_name, certificate_file)
        VALUES (?,?,?,?)
        """,
        (
            student_name,
            student_email,
            event_name,
            filename
        )
    )

    conn.commit()
    conn.close()

    return render_template(
    "certificate_generated.html",
    student_name=student_name,
    event_name=event_name
)
@app.route('/my_certificates')
def my_certificates():

    student_email = session.get("student_email")

    conn = sqlite3.connect("event_management.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT event_name, certificate_file
        FROM certificates
        WHERE student_email=?
        """,
        (student_email,)
    )

    certificates = cursor.fetchall()

    conn.close()

    return render_template(
        "my_certificates.html",
        certificates=certificates
    )
@app.route('/download_certificate/<filename>')
def download_certificate(filename):

    if "student_email" not in session:
        return redirect("/login")

    certificate_folder = os.path.join(app.root_path, "certificates")

    return send_from_directory(
        certificate_folder,
        filename,
        as_attachment=True
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)