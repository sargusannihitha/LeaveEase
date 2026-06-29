from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
db = mysql.connector.connect(
    host="reseau.proxy.rlwy.net",
    user="root",
    password="TREUQuawNtwlzjNPYqxJyGuSedPdEGhK",
    database="railway",
    port=53503
)

# ---------------------------
# HOME / LOGIN
# ---------------------------
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        db = get_db()
        cursor = db.cursor()

        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM faculty WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            return render_template('dashboard.html')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')


# ---------------------------
# REGISTER
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        db = get_db()
        cursor = db.cursor()

        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        password = request.form['password']

        sql = """
        INSERT INTO faculty (name, email, department, password)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (name, email, department, password))
        db.commit()

        cursor.close()
        db.close()

        return "Registration Successful!"

    return render_template('register.html')


# ---------------------------
# APPLY LEAVE
# ---------------------------
@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():

    if request.method == 'POST':

        db = get_db()
        cursor = db.cursor()

        faculty_name = request.form['faculty_name']
        department = request.form['department']
        leave_type = request.form['leave_type']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form['reason']

        sql = """
        INSERT INTO leave_requests
        (faculty_name, department, leave_type, from_date, to_date, reason, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            faculty_name,
            department,
            leave_type,
            from_date,
            to_date,
            reason,
            "Pending"
        ))

        db.commit()

        cursor.close()
        db.close()

        return "Leave Applied Successfully!"

    return render_template('apply_leave.html')


# ---------------------------
# ADMIN PANEL
# ---------------------------
@app.route('/admin')
def admin():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM leave_requests")
    leaves = cursor.fetchall()

    suggestions = {}

    for leave in leaves:

        department = leave[7]
        faculty_name = leave[1]

        if department:

            sql = """
            SELECT name FROM faculty
            WHERE department=%s AND name != %s
            LIMIT 1
            """

            cursor.execute(sql, (department, faculty_name))
            substitute = cursor.fetchone()

            if substitute:
                suggestions[leave[0]] = substitute[0]
            else:
                suggestions[leave[0]] = "No Substitute Found"
        else:
            suggestions[leave[0]] = "-"

    cursor.close()
    db.close()

    return render_template('admin.html', leaves=leaves, suggestions=suggestions)


# ---------------------------
# APPROVE
# ---------------------------
@app.route('/approve/<int:id>')
def approve(id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE leave_requests SET status='Approved' WHERE id=%s",
        (id,)
    )

    db.commit()
    cursor.close()
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
        "UPDATE leave_requests SET status='Rejected' WHERE id=%s",
        (id,)
    )

    db.commit()
    cursor.close()
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

    cursor.close()
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
    app.run(debug=True)