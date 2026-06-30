from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db():
    conn = sqlite3.connect("leaveease.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------
# CREATE TABLES AUTOMATICALLY
# ---------------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        department TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty_name TEXT,
        department TEXT,
        leave_type TEXT,
        from_date TEXT,
        to_date TEXT,
        reason TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# LOGIN
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            db = get_db()
            cursor = db.cursor()

            email = request.form['email']
            password = request.form['password']

            cursor.execute(
                "SELECT * FROM faculty WHERE email=? AND password=?",
                (email, password)
            )

            user = cursor.fetchone()

            db.close()

            if user:
                return render_template('dashboard.html')
            else:
                return "Invalid Email or Password"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('login.html')


# ---------------------------
# REGISTER
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db = get_db()
            cursor = db.cursor()

            name = request.form['name']
            email = request.form['email']
            department = request.form['department']
            password = request.form['password']

            cursor.execute(
                "INSERT INTO faculty (name, email, department, password) VALUES (?, ?, ?, ?)",
                (name, email, department, password)
            )

            db.commit()
            db.close()

            return "Registration Successful!"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('register.html')


# ---------------------------
# APPLY LEAVE
# ---------------------------
@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if request.method == 'POST':
        try:
            db = get_db()
            cursor = db.cursor()

            faculty_name = request.form['faculty_name']
            department = request.form['department']
            leave_type = request.form['leave_type']
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            reason = request.form['reason']

            cursor.execute("""
                INSERT INTO leave_requests
                (faculty_name, department, leave_type, from_date, to_date, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                faculty_name,
                department,
                leave_type,
                from_date,
                to_date,
                reason,
                "Pending"
            ))

            db.commit()
            db.close()

            return "Leave Applied Successfully!"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('apply_leave.html')


# ---------------------------
# ADMIN PANEL
# ---------------------------
@app.route('/admin')
def admin():
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM leave_requests")
        leaves = cursor.fetchall()

        suggestions = {}

        for leave in leaves:
            department = leave["department"]
            faculty_name = leave["faculty_name"]

            cursor.execute("""
                SELECT name FROM faculty
                WHERE department=? AND name != ?
                LIMIT 1
            """, (department, faculty_name))

            substitute = cursor.fetchone()

            suggestions[leave["id"]] = substitute["name"] if substitute else "No Substitute Found"

        db.close()

        return render_template('admin.html', leaves=leaves, suggestions=suggestions)

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------
# APPROVE
# ---------------------------
@app.route('/approve/<int:id>')
def approve(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Approved' WHERE id=?",
        (id,)
    )

    db.commit()
    db.close()

    return redirect('/admin')


# ---------------------------
# REJECT
# ---------------------------
@app.route('/reject/<int:id>')
def reject(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    db.commit()
    db.close()

    return redirect('/admin')


# ---------------------------
# HISTORY
# ---------------------------
@app.route('/history')
def history():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM leave_requests")
    leaves = cursor.fetchall()

    db.close()

    return render_template('history.html', leaves=leaves)


# ---------------------------
# LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    return redirect('/')


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    init_db()
    app.run()