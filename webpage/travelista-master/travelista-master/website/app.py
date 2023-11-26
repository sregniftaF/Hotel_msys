from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_session import Session
from flask_paginate import Pagination, get_page_args
from datetime import timedelta
from datetime import datetime
import json
import MySQLdb.cursors
import requests
import re


def max_value(a, b):
    return max(a, b)

url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "d54251d0d0msh2c71c303b8b375ap16db3bjsn6835d5c34d91",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

app = Flask(__name__)

app.secret_key = '8946d496b536a6b7601bb05a10e348bb61a0fba5ff05da0416f5dec5312ec2e1'
sess = Session()

app.config['MYSQL_HOST'] = '34.143.183.171'
app.config['MYSQL_USER'] = 'weekian'
app.config['MYSQL_PASSWORD'] = '2201378@sit'
app.config['MYSQL_DB'] = 'hotelDatabase'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
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
    rooms_data = []
    
    if request.method == 'POST':
        session['country'] = request.form.get('country')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        session['rooms'] = request.form.get('rooms')
        session['adults'] = 0
        session['child'] = 0
        for room_num in range(1, int(session['rooms']) + 1):
            session['adults'] += int(request.form.get(f'adults{room_num}'))
            room_data = {
                'adults': int(request.form.get(f'adults{room_num}')),
                'children': []
            }

            child_count = int(request.form.get(f'child{room_num}')) if request.form.get(f'child{room_num}') else 0
            session['child'] += child_count
            if child_count > 0:
                children = []
                for i in range(1, child_count + 1):
                    age = request.form.get(f'childage{room_num}_{i}')
                    if age and age.strip():  # Check if 'age' is not empty or whitespace
                        children.append({'age': int(age)})
                room_data['children'] = children
            
            rooms_data.append(room_data)
            
            checkin_date = datetime.strptime(checkin, "%m/%d/%Y") 
            checkout_date = datetime.strptime(checkout, "%m/%d/%Y")
            session['checkin'] = checkin_date.strftime('%Y-%m-%d')
            session['checkout'] = checkout_date.strftime('%Y-%m-%d')
            
            cursor = mysql.connection.cursor()
            cursor.execute(
                'SELECT gaiaId FROM hotelDatabase.region WHERE regionName LIKE %s',
                    ("%" + session['country'] + "%",)
            )
            regionid = cursor.fetchone()
            reservation_data = {
                "propertyId": "nil",
                "checkInDate": { 
                    "day": checkin_date.day, 
                    "month":  checkin_date.month, 
                    "year": checkin_date.year 
                }, 
                "checkOutDate": { 
                    "day": checkout_date.day, 
                    "month": checkout_date.month, 
                    "year": checkout_date.year 
                }, 
                "destination": { 
                    "regionId": "nil"
                },
                "rooms": rooms_data
            }
            session['flag'] = 1
        return redirect(url_for('hotels', reservation_data=json.dumps(reservation_data)))
    return render_template("index.html", account=account)


@app.route('/hotels', methods=["GET", "POST"])
def hotels():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
    
    if request.method == 'GET' and session['flag'] == 1:
        session['flag'] = 0
        reservation_data = request.args.get('reservation_data')
        json_temp = json.loads(reservation_data)
        cursor = mysql.connection.cursor()
        cursor.execute(
                'SELECT * FROM hotelDatabase.hotels h JOIN hotelDatabase.region r ON h.gaiaId = r.gaiaId WHERE r.regionName LIKE %s;',
                ("%" + session['country'] + "%",))
        session['hotel_list'] = cursor.fetchall()
        i = 0
        for hotel in session['hotel_list']:
            json_temp['propertyId'] = str(hotel[1]) #change the name in the jsontemp 
            json_temp['destination']['regionId'] = str(hotel[0]) # change the region if for each temp
            cursor.execute(
                'SELECT propertyId FROM hotelDatabase.cache_collection WHERE propertyId = %s AND checkIn = %s AND checkOut = %s AND adult = %s AND child = %s;',
                (hotel[1], session['checkin'], session['checkout'], session['adults'], session['child'],)
            )
            check_exist_request = cursor.fetchone()
            if check_exist_request is None:
                response = requests.post(url, json=json_temp, headers=headers)
                res = response.json()
                units_data = {}
                data = res['data'].get('propertyOffers').get('units')
                if data is not None:
                    room_counter = 1
                    for _ in range(9):
                        room_key = f'room{room_counter}'
                        units_data[room_key] = []
                        for unit in data:
                            if unit is None:
                                break
                            try:
                                header = unit['header'].get('text')
                                price = unit['ratePlans']
                                price1 = price[0].get('priceDetails')
                                price2 = price1[0].get('totalPriceMessage')
                                image = unit['unitGallery'].get('gallery')
                                image1 = image[0].get('image').get('url')
                                units_data[room_key].append(header)
                                units_data[room_key].append(price2)
                                units_data[room_key].append(image1)
                            except IndexError:
                                print("Unit sold out")
                        room_counter += 1
                    if len(units_data['room1']) != 0:
                        json_units_data = json.dumps(units_data)
                        print("start")
                        cursor.execute(
                            'INSERT INTO hotelDatabase.cache_collection VALUES (%s, %s, %s, %s, %s, %s)',
                            (hotel[1],session['checkin'], session['checkout'], session['adults'], session['child'], json_units_data,)
                        )
                        print("stop")
                        mysql.connection.commit()
                    else:
                        try:
                            session['hotel_list'].remove(hotel)
                        except AttributeError:
                            print('session is not initialised')
                else:
                    try:
                        session['hotel_list'].remove(hotel)
                    except AttributeError:
                        print('session is not initialised')

    # if request.method == 'POST':
    
    # Pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 12  # Number of hotels to display per page
    total = len(session['hotel_list'])
    total_pages = total // per_page + (1 if total % per_page > 0 else 0)

    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page

    hotels_on_page = session['hotel_list'][offset: offset + per_page]

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
        session['p_id'] = id
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
            session['email'] = account[8]

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
    # Validate if user is login, if not, redirect to login page
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
        # Retrieve user info from DB
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
        )
        existing_account = cursor.fetchone()
        print(existing_account)

    if request.method == 'POST':
        isDelete = request.form.get("delete")
        if isDelete == "delete":
            # Delete Account
            cursor = mysql.connection.cursor()
            try:
                cursor.execute(
                    'DELETE FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
                )
                mysql.connection.commit()
                flash('Delete Account!')
                session.clear()
                return redirect(url_for('index'))
            except:
                flash('Booking(s) made. Cancellation required.')

        else:
            name = request.form.get('customerName')
            username = request.form.get('userName')
            contact = request.form.get('contactNum')
            dob = request.form.get('dob')
            nationality = request.form.get('nation')
            email = request.form.get('email')
            passport = request.form.get('passport')
            cursor.execute(
                'SELECT * FROM hotelDatabase.customer WHERE email = %s', (email,)
            )
            existing_account = cursor.fetchone()
            if existing_account is not None:
                flash('Email already exists.')
            else:
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
                        (name, username, contact, dob, nationality, email, passport, session['id'],)
                    )
                    mysql.connection.commit()
                    flash('Account changed!')
                    cursor.execute(
                        'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
                    )
                    existing_account = cursor.fetchone()

    return render_template('userpage.html', account=account, user=existing_account)




@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/userbookings", methods=['GET', 'POST'])
def userBookings():
    if request.method == 'POST':
        # Delete booking from DB
        booking_id = request.form.get("booking_id")
        cursor = mysql.connection.cursor()
        cursor.execute(
            'DELETE FROM hotelDatabase.booking WHERE bookingId = %s', (booking_id,)
        )
        mysql.connection.commit()

        cursor.execute("""
            SELECT b.bookingId, h.hotelName, h.hotelAddress, h.imageURL, b.totalPrice, b.checkInDate, b.checkOutDate, b.durationOfStay
            FROM hotelDatabase.hotels AS h
            INNER JOIN hotelDatabase.booking AS b ON h.propertyId = b.propertyId
            WHERE b.customerID = %s
        """, (session['id'],)
        )

        bookings = cursor.fetchall()
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT b.bookingId, h.hotelName, h.hotelAddress, h.imageURL, b.totalPrice, b.checkInDate, b.checkOutDate, b.durationOfStay
            FROM hotelDatabase.hotels AS h
            INNER JOIN hotelDatabase.booking AS b ON h.propertyId = b.propertyId
            WHERE b.customerID = %s
        """, (session['id'],)
                       )
        bookings = cursor.fetchall()

    return render_template("userBooking.html", account=session['username'], bookings=bookings)


@app.route("/userpassword", methods=['GET', 'POST'])
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
        old_pwd = request.form.get('old_pwd')
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get("confirm_pwd")

        if len(new_pwd) < 7:
            msg["is_error"] = True
            msg["msg"] = "Password must be at least 7 characters."
            return render_template("userPassword.html", account=session['username'], msg=msg)
        elif new_pwd != confirm_pwd:
            msg["is_error"] = True
            msg["msg"] = "Please check your password, doesn't match"
            return render_template("userPassword.html", account=session['username'], msg=msg)


        # Get user info and compare password
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE customerID = %s AND userPassword = %s', (session['id'], old_pwd,)
        )
        account = cursor.fetchone()

        if account is None:
            msg["is_error"] = True
            msg["msg"] = "Please check your passwords, invalid password"
            return render_template("userPassword.html", account=session['username'], msg=msg)

        # Update user password
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE hotelDatabase.customer SET userPassword = %s WHERE customerID = %s AND userPassword = %s',
            (new_pwd, session['id'], old_pwd,)
        )
        mysql.connection.commit()

        msg["is_error"] = False
        msg["msg"] = "Successfully updated password"

    return render_template("userPassword.html", account=session['username'], msg=msg)

@app.route('/hotelBooking', methods=['POST', 'GET'])
def hotelbooking():
    check_in = session.get('checkin')
    check_out = session.get('checkout')
    date_duration = session.get('duration')
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""

    if request.method == 'POST':
        cursor = mysql.connection.cursor()

        rtype = 'single'
        t_price = '10'
        n_pax = '1'
        r_d = session.get('room_data')
        t_room = session.get('rooms')

        # for room_num in range(1, int(session['rooms']) + 1):
        #     x = r_d.get(f'room_{room_num}')
        #     print(x.get('adults'), x.get('child'), x.get('childage'))

        if check_in is None:
            flash('Please enter Detail in the Homepage!')
        elif check_out is None:
            flash('Please enter Detail in the Homepage!')
        elif date_duration is None:
            flash('Please enter Detail in the Homepage!')
        else:
            print(rtype, t_price, n_pax, check_in, check_out, date_duration, r_d)
            cursor.execute(
                'INSERT into hotelDatabase.booking VALUES( NULL, %s, %s, %s, %s, %s, %s, %s, %s)',
                (session['id'], session['p_id'], rtype, n_pax, t_price, check_in, check_out, date_duration)
            )
            mysql.connection.commit()

    return render_template('hotelBooking.html')

if __name__ == '__main__':
    app.run(debug=True)
