from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import date
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter  


app = Flask(__name__)
app.secret_key = 'your_secret_key'

import sqlite3
today = date.today()
formatted_date = today.strftime('%B %d, %Y')

c = datetime.now()
current_time = c.strftime('%H:%M:%S')

def get_db_connection():
    conn = sqlite3.connect('toll.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM Admin WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin['adminID']  # Store admin ID in session
            return redirect(url_for('admin_page'))
        else:
            return render_template('admin_login.html', error="Incorrect username or password")
    return render_template('admin_login.html')


@app.route("/admin_page", methods=['GET', 'POST'])
def admin_page():
    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('admin_login'))  # Redirect to login if not logged in

    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM Admin WHERE adminID = ?', (admin_id,)).fetchone()
    conn.close()

    if not admin:
        return "User not found", 404  # Handle no user found case

    # Convert Row to dict and remove password
    admin_dict = dict(admin)
    admin_dict.pop('password', None)  # Remove password from dict

    return render_template('admin_page.html', admin=admin_dict)



@app.route('/admin_dashboard')
def admin_dashboard():
    return "Welcome to the Admin Dashboard!"

@app.route("/staff_login", methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Staff WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        print(user)
        conn.close()

        if user:
            session['staff_id'] = user['staffID']  # Store user's ID in session
            return redirect(url_for('staff_page'))  # Redirect to the staff page
        else:
            return render_template('staff_login.html', error="Invalid username or password")

    return render_template('staff_login.html')

@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        print(user)
        conn.close()

        if user:
            session['user_id'] = user['userID']  # Store user's ID in session
            return redirect(url_for('user_page'))  # Redirect to the staff page
        else:
            return render_template('user_login.html', error="Invalid username or password")
        
    return render_template('user_login.html')






@app.route("/profile", methods = ['GET', 'POST'])
def profile():
    return render_template('profile.html')


@app.route("/transaction")
def transaction():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Transactions')
    transactions_list = cursor.fetchall()  # Fetch all transaction records
    conn.close()
    return render_template('transaction.html', transactions_list=transactions_list)



@app.route("/add_staff", methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        staffid = request.form['staffid']
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        dob = request.form['dob']
        state = request.form['state']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']  # Consider hashing the password before storage

        conn = get_db_connection()
        cursor = conn.cursor()
        # Insert new staff into the database
        cursor.execute('INSERT INTO Staff (staffID, userID, name, phone, email, date_of_birth, state, address, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (staffid, name, phone, email, dob, state, address, username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('all_staff'))  # Redirect to a confirmation page or the list of staff
    return render_template('add_staff.html')



@app.route("/all_staff", methods=['GET', 'POST'])
def all_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Staff')
    staff_list = cursor.fetchall()  # Fetch all staff records
    conn.close()
    return render_template('all_staff.html', staff_list=staff_list)


@app.route("/all_user", methods=['GET', 'POST'])
def all_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User')
    users_list = cursor.fetchall()  # Fetch all user records
    conn.close()
    return render_template('all_user.html', users_list=users_list)



@app.route("/user_entry", methods=['GET', 'POST'])
def user_entry():
    

    if request.method == 'POST':
        staffID = request.form['staffid']
        userID =""
        date = today = formatted_date
        time = current_time
        amount = request.form['amount']
        vehicle_number = request.form['plate_number']
        vehicle_owner = request.form['vehicle_owner']
        phone = request.form['phone']
        address = request.form['address']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Transactions (staffID, userID,  date, time, amount, vehicle_number,  vehicle_owner, phone, address) VALUES (?, ?, ?, ?, ?, ?,?,?,?)', 
                       (staffID, userID, date, time, amount, vehicle_number, vehicle_owner, phone, address))
        conn.commit()
        conn.close()
        return redirect(url_for('user_entry'))  # Redirect to the same page or a confirmation page

    # If GET request or after POST, return the page
    return render_template('user_entry.html')



@app.route("/print_receipt", methods=['GET', 'POST'])
def print_receipt():
    if request.method == 'POST':
        plate_number = request.form['plate_number']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Transactions WHERE vehicle_number = ?', (plate_number,))
        transaction = cursor.fetchone()
        conn.close()

        if transaction:
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter  # Get dimensions of the letter size

            # Header
            p.setFont("Helvetica-Bold", 14)
            p.drawCentredString(width / 2.0, 770, "UNIVERSITY OF NIGERIA")
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(width / 2.0, 750, "DEPARTMENT OF COMPUTER SCIENCE")
            p.line(50, 740, width - 50, 740)  # Draw line after header

            # Title
            p.setFont("Helvetica-Bold", 10)
            p.drawString(100, 710, "************************ UNN Toll Ticket **********************")

            # Receipt Details
            p.setFont("Helvetica", 10)
            p.drawString(100, 690, "Vehicle Owner:          " + str(transaction['vehicle_owner']))
            p.drawString(100, 670, "Date:                            " + str(transaction['date']))
            p.drawString(100, 650, "Time:                            " + str(transaction['time']))
            p.drawString(100, 630, "Amount:                      N " + str(transaction['amount']))
            p.drawString(100, 610, "Plate Number:           " + str(transaction['vehicle_number']))

            p.showPage()
            p.save()
            buffer.seek(0)

            response = make_response(buffer.getvalue())
            response.headers['Content-Disposition'] = "attachment; filename='receipt.pdf'"
            response.mimetype = 'application/pdf'
            return response
        else:
            flash('No transaction found for this plate number.', 'info')
            return render_template('print_receipt.html')

    return render_template('print_receipt.html')

@app.route("/staff_page", methods=['GET', 'POST'])
def staff_page():
    staff_id = session.get('staff_id')  # Assuming you store staff_id in session upon login
    if not staff_id:
        return redirect(url_for('staff_login'))  # Redirect to login if not logged in

    conn = get_db_connection()
    staff = conn.execute('SELECT * FROM Staff WHERE staffID = ?', (staff_id,)).fetchone()
    conn.close()

    if not staff:
        return "Staff not found", 404  # Handle no staff found case

    return render_template('staff_page.html', staff=staff)


@app.route("/staff_profile", methods = ['GET', 'POST'])
def staff_profile():
    return render_template('staff_profile.html')

@app.route("/user_transaction", methods = ['GET', 'POST'])
def user_transaction():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Transactions')
    transactions_list = cursor.fetchall()  # Fetch all transaction records
    conn.close()
    return render_template('user_transaction.html', transactions_list=transactions_list)
    
    #return render_template('user_transaction.html')


@app.route("/vuser_transaction", methods = ['GET', 'POST'])
def vuser_transaction():
    return render_template('vuser_transaction.html')

@app.route("/vuser_profile", methods = ['GET', 'POST'])
def vuser_profile():
    return render_template('vuser_profile.html')



@app.route("/vuser_entry", methods = ['GET', 'POST'])
def vuser_entry():
    if request.method == 'POST':
        staffID =""
        userID = request.form['userid']
        date = today = formatted_date
        time = current_time
        amount = request.form['amount']
        vehicle_number = request.form['plate_number']
        vehicle_owner = request.form['vehicle_owner']
        phone = request.form['phone']
        address = request.form['address']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Transactions (staffID, userID,  date, time, amount, vehicle_number,  vehicle_owner, phone, address) VALUES (?, ?, ?, ?, ?, ?,?,?,?)', 
                       (staffID, userID, date, time, amount, vehicle_number, vehicle_owner, phone, address))
        conn.commit()
        conn.close()
        return redirect(url_for('vuser_entry'))  

    # If GET request or after POST, return the page
    return render_template('vuser_entry.html')




@app.route("/vprint_receipt", methods = ['GET', 'POST'])
def vprint_receipt():
    if request.method == 'POST':
        plate_number = request.form['plate_number']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Transactions WHERE vehicle_number = ?', (plate_number,))
        transaction = cursor.fetchone()
        conn.close()

        if transaction:
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter  # Get dimensions of the letter size

            # Header
            p.setFont("Helvetica-Bold", 14)
            p.drawCentredString(width / 2.0, 770, "UNIVERSITY OF NIGERIA")
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(width / 2.0, 750, "DEPARTMENT OF COMPUTER SCIENCE")
            p.line(50, 740, width - 50, 740)  # Draw line after header

            # Title
            p.setFont("Helvetica-Bold", 10)
            p.drawString(100, 710, "************************ UNN Toll Ticket **********************")

            # Receipt Details
            p.setFont("Helvetica", 10)
            p.drawString(100, 690, "Vehicle Owner:          " + str(transaction['vehicle_owner']))
            p.drawString(100, 670, "Date:                            " + str(transaction['date']))
            p.drawString(100, 650, "Time:                            " + str(transaction['time']))
            p.drawString(100, 630, "Amount:                      N " + str(transaction['amount']))
            p.drawString(100, 610, "Plate Number:           " + str(transaction['vehicle_number']))

            p.showPage()
            p.save()
            buffer.seek(0)

            response = make_response(buffer.getvalue())
            response.headers['Content-Disposition'] = "attachment; filename='receipt.pdf'"
            response.mimetype = 'application/pdf'
            return response
        else:
            flash('No transaction found for this plate number.', 'info')
            return render_template('vprint_receipt.html')

    return render_template('vprint_receipt.html')

@app.route("/user_page", methods = ['GET', 'POST'])
def user_page():
    user_id = session.get('user_id')  # Assuming you store staff_id in session upon login
    if not user_id:
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE userID = ?', (user_id,)).fetchone()
    conn.close()

    if not user:
        return "Staff not found", 404  # Handle no staff found case

    return render_template('user_page.html', user=user)

@app.route('/logout')
def logout():
    # Clear the session, effectively logging the user out
    session.clear()
    flash('You have been logged out.', 'info') 
    return redirect(url_for('admin_login'))  


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    import random
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        dob = request.form['dob']
        state = request.form['state']
        plate_number = request.form['plate_number']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        
        userId =  random.randint(1000, 9999)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new user into the User table
        cursor.execute('INSERT INTO User (userID, name, phone, email, password, date_of_birth, state, plate_number, address, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)', 
                       (userId, name, phone, email, password, dob, state, plate_number, address, username))
        conn.commit()
        conn.close()

        flash('User registered successfully!')
        return render_template('user_login.html')
#return redirect(url_for('user_login'))  # Redirect to login page after registration

    return render_template('user_registration.html')  # Fallback in case of non-POST request


if __name__ == '__main__':
    app.run(debug=True)
