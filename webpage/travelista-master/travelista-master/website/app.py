from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_session import Session
from flask_paginate import Pagination, get_page_args
from datetime import timedelta
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
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

    # Initialize dictionaries to store data for each room
    room_data = {}

    if request.method == 'POST':
        country = request.form.get('country')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        rooms = request.form.get('rooms')

        # Loop through each room to collect data
        for room_num in range(1, int(rooms) + 1):
            room_key = f'room_{room_num}'
            room_data[room_key] = {
                'adults': request.form.get(f'adults{room_num}'),
                'child': request.form.get(f'child{room_num}'),
                'childage': []  # Initialize an empty list for child ages in each room
            }

            child_count = int(room_data[room_key]['child']) if room_data[room_key]['child'] else 0
            if child_count > 0:
                for i in range(1, child_count + 1):
                    age = request.form.get(f'childage{room_num}_{i}')
                    if age is not None:
                        room_data[room_key]['childage'].append(int(age))
                        
        print(country, checkin, checkout, rooms, room_data)  # Print collected data for demonstration

    return render_template("index.html", account=account)


@app.route('/hotels', methods=["GET", "POST"])
def hotels():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""

    # Check if the selectedValue is already stored in the session
    selected_value = session.get('selectedValue')
    region = session.get('region')

    if request.method == 'POST':
        selected_value = request.form.get('country')  # Retrieve the selected value from the form
        region = request.form.get('region')
        session['selectedValue'] = selected_value
    # Check if hotel_list is already stored in the session
    hotel_list = session.get('hotel_list')

    if selected_value is None:
        session['selectedValue'] = 'all'

    if hotel_list is None or selected_value != session.get('last_selected_value') or region != session.get('region'):
        # If hotel_list is not stored or the selectedValue has changed, run the SQL query
        cursor = mysql.connection.cursor()
        if selected_value == 'all' or region is None:
            cursor.execute('SELECT * FROM hotelDatabase.hotels ORDER BY hotelReviews Desc;')
        else:
            cursor.execute(
                'SELECT * FROM hotelDatabase.hotels h JOIN hotelDatabase.region r ON h.gaiaId = r.gaiaId WHERE r.regionName LIKE %s',
                ("%" + region + "%",))
            print(region)
        hotel_list = cursor.fetchall()
        session['hotel_list'] = hotel_list
        session['last_selected_value'] = selected_value
        session['region'] = region
    # Pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 12  # Number of hotels to display per page
    total = len(hotel_list)
    total_pages = total // per_page + (1 if total % per_page > 0 else 0)

    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page

    hotels_on_page = hotel_list[offset: offset + per_page]

    pagination = Pagination(
        page=page,
        total=total_pages,
        record_name='hotels',
        per_page=per_page,
        css_framework='bootstrap4'
    )
    return render_template('hotels.html', account=account, hotels=hotels_on_page, pagination=pagination)


@app.route('/hotelinfo', methods=['POST', 'GET'])
def hotelinfo():
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""

    if request.method == 'POST':
        id = request.form.get('hotelid')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.hotels WHERE propertyId = %s', (id,)
        )
        hotel_info = cursor.fetchone()

    return render_template('hotelinfo.html', account=account, hotel=hotel_info)


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


@app.route('/userpage', methods=['GET', 'POST'])
def userpage():
    existing_account = {}
    account = {}
    # Validate if user is login, if not, redirect to login page
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
        # Retrieve user info from DB
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'])
        )
        existing_account = cursor.fetchone()
    else:
        account = ""
        return render_template("login.html")

    if request.method == 'POST':
        isDelete = request.form.get("delete")
        if isDelete == "delete":
            # Delete Account
            cursor = mysql.connection.cursor()
            cursor.execute(
                'DELETE FROM hotelDatabase.customer WHERE customerID = %s', (session['id'])
            )
            mysql.connection.commit()
            flash('Delete Account!')
            session.clear()
            flash("Successfully signed out")
            return redirect(url_for('index'))
        else:
            name = request.form.get('customerName')
            username = request.form.get('userName')
            contact = request.form.get('contactNum')
            dob = request.form.get('dob')
            nationality = request.form.get('nation')
            email = request.form.get('email')
            passport = request.form.get('passport')
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address !')
            elif not re.match(r'[A-Za-z0-9]+', username) or len(username) < 1:
                flash('name must contain only characters and numbers !')
            elif len(name) < 3:
                flash('Name must be greater than 3 character.')
            else:
                cursor.execute(
                    """
                    UPDATE hotelDatabase.customer 
                    SET customerName = %s, username = %s, contactNum = %s, dateOfBirth = %s, nationality = %s, email = %s, passport = %s
                    WHERE customerID = %s
                    """,
                    (name, username, contact, dob, nationality, email, passport, session['id'])
                )
                mysql.connection.commit()
                flash('Account changed!')
                cursor.execute(
                    'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'])
                )
                existing_account = cursor.fetchone()

    return render_template('userpage.html', account=account, user=existing_account)




@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/user/bookings", methods=['GET', 'POST'])
def userBookings():
    # Validate if user is login, if not, redirect to login page
    bookings = []
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
        #return render_template("login.html")

    if request.method == 'POST':
        # Delete booking from DB
        booking_id = request.form.get("booking_id")
        cursor = mysql.connection.cursor()
        cursor.execute(
            'DELETE FROM hotelDatabase.booking WHERE bookingId = %s', (booking_id)
        )
        mysql.connection.commit()

        cursor.execute("""
            SELECT b.bookingId, h.hotelName, h.hotelAddress, h.imageURL, b.totalPrice, b.checkInDate, b.checkOutDate
            FROM hotelDatabase.hotels AS h
            INNER JOIN hotelDatabase.booking AS b ON h.propertyId = b.propertyId
            WHERE b.customerID = %s
        """, (session['id'])
        )

        bookings = cursor.fetchall()
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT b.bookingId, h.hotelName, h.hotelAddress, h.imageURL, b.totalPrice, b.checkInDate, b.checkOutDate
            FROM hotelDatabase.hotels AS h
            INNER JOIN hotelDatabase.booking AS b ON h.propertyId = b.propertyId
            WHERE b.customerID = %s
        """, (session['id'])
                       )
        bookings = cursor.fetchall()

    return render_template("userBooking.html", account=session['username'], bookings=bookings)


@app.route("/user/password", methods=['GET', 'POST'])
def userPagePassword():
    # Validate if user is login, if not, redirect to login page
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
        return render_template("login.html")

    msg = {
        "is_error": False,
        "msg": ""
    }

    if request.method == 'POST':
        email = session['email']
        old_pwd = request.form.get('old_pwd')
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get("confirm_pwd")

        if new_pwd != confirm_pwd:
            msg["is_error"] = True
            msg["msg"] = "Please check your password, doesn't match"
            return render_template("userPassword.html", account=session['username'], msg=msg)

        # Get user info and compare password
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE email = %s AND userPassword = %s', (email, old_pwd)
        )
        account = cursor.fetchone()

        if account is None:
            msg["is_error"] = True
            msg["msg"] = "Please check your passwords, invalid password"
            return render_template("userPassword.html", account=session['username'], msg=msg)

        # Update user password
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE hotelDatabase.customer SET userPassword = %s WHERE email = %s AND userPassword = %s',
            (new_pwd, email, old_pwd)
        )
        mysql.connection.commit()

        msg["is_error"] = False
        msg["msg"] = "Successfully updated password"

    return render_template("userPassword.html", account=session['username'], msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
