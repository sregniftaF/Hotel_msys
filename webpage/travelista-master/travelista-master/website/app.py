from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_session import Session
from flask_paginate import Pagination, get_page_args
import MySQLdb.cursors
import re

def max_value(a, b):
    return max(a, b)


app = Flask(__name__)

app.secret_key = '8946d496b536a6b7601bb05a10e348bb61a0fba5ff05da0416f5dec5312ec2e1'
sess = Session()

app.config['MYSQL_HOST'] = '34.143.183.171'
app.config['MYSQL_USER'] = 'weekian'
app.config['MYSQL_PASSWORD'] = '2201378@sit'
app.config['MYSQL_DB'] = 'hotelDatabase'
app.config['SESSION_TYPE'] = 'filesystem'
app.jinja_env.filters['max_value'] = max_value

sess.init_app(app)

mysql = MySQL(app)

@app.route('/')
@app.route('/index', methods=('GET', 'POST'))
def index():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
    
    childage = []  # Initialize an empty list to store child ages

    if request.method == 'POST':
        country = request.form.get('country')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        adults = request.form.get('adults')
        child = request.form.get('child')
        if child and int(child) > 0:
            for i in range(1, int(child) + 1):
                age = request.form.get('child' + str(i))
                if age is not None:  # Check if 'age' is not None before conversion
                    childage.append(int(age))
        print(country, checkin, checkout, adults, child)
    
    return render_template("index.html", account=account)

@app.route('/hotels', methods=['GET'])
def hotels():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT * FROM hotelDatabase.hotels'
    )
    hotel_list = cursor.fetchall()

    # Pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 12  # Number of hotels to display per page

    hotels_on_page = hotel_list[offset: offset + per_page]

    total = len(hotel_list)

    pagination = Pagination(page=page, total=total, record_name='hotels', per_page=per_page, css_framework='bootstrap4')

    return render_template('hotels.html', account=account, hotels=hotels_on_page, pagination=pagination)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get("password")
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE email = %s AND userPassword = %s', (email, password)
        )
        account = cursor.fetchone()
        if account is not None:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[2]

            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect username / password!')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    flash("Successfully signed out")
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Check if email already exists
        email = request.form.get('email')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT email FROM hotelDatabase.customer WHERE email = %s', (email,)
        )
        existing_account = cursor.fetchone()
        print(existing_account)

        if existing_account is not None:
            flash('Email already exists.')
        else:
            # Insert the new account into the database
            name = request.form.get('name')
            username = request.form.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            contact = request.form.get('contact')
            dob = request.form.get('dob')
            gender = request.form.get('gender')
            nationality = request.form.get('nationality')
            passport = request.form.get('passport')
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address !')
            elif not re.match(r'[A-Za-z0-9]+', username) or len(username) < 1:
                flash('name must contain only characters and numbers !')
            elif len(name) < 3:
                flash('Name must be greater than 3 character.')
            elif password1 != password2:
                flash('Passwords don\'t match.')
            elif len(password1) < 7:
                flash('Password must be at least 7 characters.')
            elif gender == "":
                flash('Select a gender')
            elif dob == "":
                flash('Select your DOB')
            elif nationality == "":
                flash('Enter your nationality')
            elif passport == "":
                flash('Enter your passport number')
            else:
                cursor.execute(
                    'INSERT into hotelDatabase.customer VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (name, username, password1, contact, dob, gender, nationality, email, passport)
                )
                mysql.connection.commit()
                flash('Account created!')
                return redirect(url_for('index'))

    return render_template("signup.html")


@app.route('/userpage')
def userpage():
    # Clear session data
    return render_template('userpage.html')
    
if __name__ == '__main__':
    app.run(debug=True)
