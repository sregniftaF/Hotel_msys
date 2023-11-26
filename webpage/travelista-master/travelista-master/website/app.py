from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_session import Session
from flask_paginate import Pagination, get_page_args
from datetime import timedelta
from datetime import datetime
import json
import MySQLdb.cursors
import requests
import ast
import re

# Define a function to return the maximum of two values
def max_value(a, b):
    return max(a, b)

# URL and headers for making requests to the RapidAPI endpoint for hotel offers
url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "2ae3c4b946msh0ad4e05fa122dedp15c03fjsnb50c606376b0",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# Initialize a Flask app
app = Flask(__name__)

# Set a secret key for the application's session encryption
app.secret_key = '8946d496b536a6b7601bb05a10e348bb61a0fba5ff05da0416f5dec5312ec2e1'

# Initialize a session object
sess = Session()

# Configuration for MySQL database connection
app.config['MYSQL_HOST'] = '34.143.183.171'
app.config['MYSQL_USER'] = 'weekian'
app.config['MYSQL_PASSWORD'] = '2201378@sit'
app.config['MYSQL_DB'] = 'hotelDatabase'

# Set session type and lifetime
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

# Register the 'max_value' function as a custom filter for Jinja templating
app.jinja_env.filters['max_value'] = max_value

# Initialize the session with the app
sess.init_app(app)

# Establishing a connection to the MySQL database using Flask-MySQLdb
mysql = MySQL(app)

# Route handling for the home page ('/') and '/index'
@app.route('/')
@app.route('/index', methods=('GET', 'POST'))
def index():
    # Check if the user is logged in, retrieve the username from the session if available
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""  # If not logged in, set account to an empty string
    
    rooms_data = []  # Initialize an empty list to store room data
    
    # Process POST request data (form submission)
    if request.method == 'POST':
        # Extract form data and store it in the session
        session['country'] = request.form.get('country')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        session['rooms'] = request.form.get('rooms')
        session['adults'] = 0
        session['child'] = 0
        
        # Iterate through each room to collect information
        for room_num in range(1, int(session['rooms']) + 1):
            # Collect the number of adults for the current room
            session['adults'] += int(request.form.get(f'adults{room_num}'))
            
            # Prepare data structure for the current room
            room_data = {
                'adults': int(request.form.get(f'adults{room_num}')),
                'children': []
            }
            
            # Count and collect information about children in the room
            child_count = int(request.form.get(f'child{room_num}')) if request.form.get(f'child{room_num}') else 0
            session['child'] += child_count
            
            if child_count > 0:
                children = []
                for i in range(1, child_count + 1):
                    age = request.form.get(f'childage{room_num}_{i}')
                    # Check if 'age' is not empty or whitespace before adding it
                    if age and age.strip():
                        children.append({'age': int(age)})
                
                # Add children information to the current room's data
                room_data['children'] = children
            
            # Append room data to the list
            rooms_data.append(room_data)
            
            # Convert check-in and check-out dates to the desired format and store in the session
            checkin_date = datetime.strptime(checkin, "%m/%d/%Y")
            checkout_date = datetime.strptime(checkout, "%m/%d/%Y")
            duration = checkout_date - checkin_date

            session['checkin'] = checkin_date.strftime('%Y-%m-%d')
            session['checkout'] = checkout_date.strftime('%Y-%m-%d')
            session['duration'] = duration.days
            
            
            # Fetch 'gaiaId' from the database based on the selected country
            cursor = mysql.connection.cursor()
            cursor.execute(
                'SELECT gaiaId FROM hotelDatabase.region WHERE regionName LIKE %s',
                ("%" + session['country'] + "%",)
            )
            regionid = cursor.fetchone()
            
            # Construct reservation data including check-in/out, destination, and room details
            reservation_data = {
                "propertyId": "nil",
                "checkInDate": {
                    "day": checkin_date.day,
                    "month": checkin_date.month,
                    "year": checkin_date.year
                },
                "checkOutDate": {
                    "day": checkout_date.day,
                    "month": checkout_date.month,
                    "year": checkout_date.year
                },
                "destination": {
                    "regionId": "nil"  # Placeholder for region ID
                },
                "rooms": rooms_data
            }
            
            # Set a flag in the session
            session['flag'] = 1
        
        # Redirect to the 'hotels' route while passing reservation data as JSON
        return redirect(url_for('hotels', reservation_data=json.dumps(reservation_data)))
    
    # Render the 'index.html' template with the account information
    return render_template("index.html", account=account)


# Route handling for '/hotels' with both GET and POST methods
@app.route('/hotels', methods=["GET", "POST"])
def hotels():
    # Check if the user is logged in, retrieve the username from the session if available
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""  # If not logged in, set account to an empty string
        
    # Handling GET method and flag checking
    if request.method == 'GET' and session['flag'] == 1:
        # Reset the flag in the session to 0 after processing
        session['flag'] = 0
        
        # Retrieve reservation data from the query parameters and convert it from JSON
        reservation_data = request.args.get('reservation_data')
        json_temp = json.loads(reservation_data)
        
        # Retrieve hotels information from the database based on the selected country
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.hotels h JOIN hotelDatabase.region r ON h.gaiaId = r.gaiaId WHERE r.regionName LIKE %s;',
            ("%" + session['country'] + "%",)
        )
        rows = cursor.fetchall()
        hotel_list = [list(row) for row in rows]
        hotel_remove = []
        
        # Iterate through each hotel retrieved
        for hotel in hotel_list:
            # Update propertyId and regionId in the reservation data for each hotel
            json_temp['propertyId'] = str(hotel[1])
            json_temp['destination']['regionId'] = str(hotel[0])
            
            # Check if the hotel details exist in the cache_collection table
            cursor.execute('''SELECT 
                                propertyId 
                              FROM 
                                hotelDatabase.cache_collection 
                              WHERE propertyId = %s 
                              AND checkIn = %s 
                              AND checkOut = %s 
                              AND adult = %s 
                              AND child = %s;''',
                           (hotel[1], session['checkin'], session['checkout'], session['adults'], session['child'],)
                           )
            check_exist_request = cursor.fetchone()
            
            # If the hotel details don't exist, fetch data from the external API and update cache_collection
            if check_exist_request is None:
                # Make a POST request to the external API
                response = requests.post(url, json=json_temp, headers=headers)
                res = response.json()
                
                units_data = {}
                data = res['data'].get('propertyOffers').get('units')
                if data is not None:
                    # Iterate to get all room types and price
                    room_counter = 1 
                    for room in range(9):
                        try:
                            # Process and collect units' data from the API response
                            room_key = f'room{room_counter}'
                            units_data[room_key] = []
                            header = data[room]['header'].get('text')
                            price = data[room]['ratePlans']
                            price1 = price[0].get('priceDetails')
                            price2 = price1[0].get('totalPriceMessage')
                            image = data[room]['unitGallery'].get('gallery')
                            image1 = image[0].get('image').get('url')
                            units_data[room_key].append(header)
                            units_data[room_key].append(price2)
                            units_data[room_key].append(image1)
                        except IndexError:
                            # Exit loop when no room is found
                            print("Unit sold out")
                            break
                        room_counter += 1
                    # Store into SQL when room1 content is not empty
                    if len(units_data['room1']) != 0:
                        json_units_data = json.dumps(units_data)
                        cursor.execute(
                            'INSERT INTO hotelDatabase.cache_collection VALUES (%s, %s, %s, %s, %s, %s)',
                            (hotel[1],session['checkin'], session['checkout'], session['adults'], session['child'], json_units_data,)
                        )
                        mysql.connection.commit()
                    else:
                        # Store all hotel that need to be deleted
                        try:
                            hotel_remove.append(hotel)
                        except AttributeError:
                            print('session is not initialised')
                            
             # Fetch price data from the cache_collection table for each hotel
            cursor.execute('''SELECT
                           response -> "$.room1[1]" 
                           FROM hotelDatabase.cache_collection WHERE propertyId = %s and checkIn = %s and checkOut = %s and adult = %s and child = %s;''',
                           (hotel[1],session['checkin'], session['checkout'], session['adults'], session['child'],))
            hprice = cursor.fetchone()
            # Insert hotel price retrieved into individual hotel list
            try:
                hprice = hprice[0]
                print(hprice, hotel[1])
                hotel.append(hprice)
            except TypeError:
                print("Price not added")
        # Iterate through list to remove hotels with no room available
        for item in hotel_remove:
            hotel_list.remove(item)
            
        # Store into session
        session['hotel_list'] = hotel_list
    
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
        cursor.execute('''SELECT 
                            response ->>"$.room1[0 to 2]",
                            response ->>"$.room2[0 to 2]",
                            response ->>"$.room3[0 to 2]"
                        FROM 
                            hotelDatabase.cache_collection
                        WHERE propertyId = %s
                        AND checkin = %s
                        AND checkout = %s
                        AND adult = %s
                        AND child = %s''', (session['p_id'], session['checkin'], session['checkout'], session['adults'], session['child']))
        roomdetails = cursor.fetchone()
        roomList= []
        for room in roomdetails:
            roomList.append(ast.literal_eval(room))
        session['roomList'] = roomList
        print(roomList)
    return render_template('hotelinfo.html', account=account, hotel=hotel_info, roomdetails = roomList)


# Route handling for '/login' with GET and POST methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        # Retrieve email and password from the login form
        email = request.form.get('email')
        password = request.form.get("password")
        
        # Establish a cursor to execute SQL queries on the database
        cursor = mysql.connection.cursor()
        
        # Execute a query to fetch user account data based on provided email and password
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE email = %s AND userPassword = %s', (email, password)
        )
        account = cursor.fetchone()  # Fetch the account details
        
        # Check if the account exists and the credentials are correct
        if account is not None:
            # If the credentials are correct, set session variables for the logged-in user
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[2]
            session['email'] = account[8]

            flash('Logged in successfully!')
            roomlist = session.get('roomlist')
            if roomlist is not None:
                return redirect(url_for('hotelbooking'))
            else:
                return redirect(url_for('index'))
  # Redirect to the 'index' route after successful login
        else:
            flash('Incorrect username / password!')  # Flash an error message for incorrect credentials
    
    # If the request method is GET or if login fails, render the 'login.html' template
    return render_template('login.html')


# Route handling for '/logout'
@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    
    # Flash a message indicating successful sign-out
    flash("Successfully signed out")
    
    # Redirect the user to the 'index' route after logout
    return redirect(url_for('index'))


# Route handling for '/signup' with both GET and POST methods
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Check if the provided email already exists in the database
        email = request.form.get('email')
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT email FROM hotelDatabase.customer WHERE email = %s', (email,)
        )
        existing_account = cursor.fetchone()

        if existing_account is not None:
            flash('Email already exists.')
        else:
            # Retrieve form data for new account creation
            name = request.form.get('name')
            username = request.form.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            contact = request.form.get('contact')
            dob = request.form.get('dob')
            gender = request.form.get('gender')
            nationality = request.form.get('nationality')
            passport = request.form.get('passport')

            # Validation checks for form data
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username) or len(username) < 1:
                flash('Username must contain only characters and numbers!')
            elif len(name) < 3:
                flash('Name must be greater than 3 characters.')
            elif password1 != password2:
                flash('Passwords do not match.')
            elif len(password1) < 7:
                flash('Password must be at least 7 characters.')
            elif gender == "":
                flash('Select a gender.')
            elif dob == "":
                flash('Select your date of birth.')
            elif nationality == "":
                flash('Enter your nationality.')
            elif passport == "":
                flash('Enter your passport number.')
            else:
                # Insert new account details into the database
                cursor.execute(
                    'INSERT into hotelDatabase.customer VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (name, username, password1, contact, dob, gender, nationality, email, passport)
                )
                mysql.connection.commit()
                flash('Account created!')
                return redirect(url_for('index'))

    # Render the 'signup.html' template for GET requests or when form submission fails
    return render_template("signup.html")



@app.route('/userpage', methods=['GET', 'POST'])
def userpage():
    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
        # Retrieve user info from the database based on the session ID
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
        )
        existing_account = cursor.fetchone()

    # Handling form submissions via POST method
    if request.method == 'POST':
        isDelete = request.form.get("delete")
        
        # Check if the user wants to delete their account
        if isDelete == "delete":
            cursor = mysql.connection.cursor()
            try:
                # Attempt to delete the user account based on the session ID
                cursor.execute(
                    'DELETE FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
                )
                mysql.connection.commit()
                flash('Account deleted!')
                session.clear()  # Clear session data after deletion
                return redirect(url_for('index'))  # Redirect to the 'index' route after successful deletion
            except:
                flash('Booking(s) made. Cancellation required before deletion.')

        else:
            # Retrieve updated user account information from the form fields
            name = request.form.get('customerName')
            username = request.form.get('userName')
            contact = request.form.get('contactNum')
            dob = request.form.get('dob')
            nationality = request.form.get('nation')
            email = request.form.get('email')
            passport = request.form.get('passport')

            # Check if the email already exists in the database (for updates)
            cursor.execute(
                'SELECT * FROM hotelDatabase.customer WHERE email = %s', (email,)
            )
            existing_account = cursor.fetchone()

            if existing_account is not None:
                flash('Email already exists.')
            else:
                # Validate updated user information before updating the database
                if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    flash('Invalid email address!')
                elif not re.match(r'[A-Za-z0-9]+', username) or len(username) < 1:
                    flash('Name must contain only characters and numbers!')
                elif len(name) < 3:
                    flash('Name must be greater than 3 characters.')
                else:
                    # Update the user account information in the database
                    cursor.execute(
                        """
                        UPDATE hotelDatabase.customer 
                        SET customerName = %s, username = %s, contactNum = %s, dateOfBirth = %s, nationality = %s, email = %s, passport = %s
                        WHERE customerID = %s
                        """,
                        (name, username, contact, dob, nationality, email, passport, session['id'],)
                    )
                    mysql.connection.commit()
                    flash('Account updated!')

                    # Fetch the updated user account information from the database
                    cursor.execute(
                        'SELECT * FROM hotelDatabase.customer WHERE customerID = %s', (session['id'],)
                    )
                    existing_account = cursor.fetchone()


    # Render the 'userpage.html' template with user account information
    return render_template('userpage.html', account=account, user=existing_account)



@app.route("/userbookings", methods=['GET', 'POST'])
def userBookings():
    if request.method == 'POST':
        # Delete booking from the database based on the provided booking_id
        booking_id = request.form.get("booking_id")
        cursor = mysql.connection.cursor()
        cursor.execute(
            'DELETE FROM hotelDatabase.booking WHERE bookingId = %s', (booking_id,)
        )
        mysql.connection.commit()

        # Retrieve bookings associated with the logged-in user from the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT b.bookingId, h.hotelName, h.hotelAddress, h.imageURL, b.totalPrice, b.checkInDate, b.checkOutDate, b.durationOfStay
            FROM hotelDatabase.hotels AS h
            INNER JOIN hotelDatabase.booking AS b ON h.propertyId = b.propertyId
            WHERE b.customerID = %s
        """, (session['id'],))
        bookings = cursor.fetchall()
    else:
        # Retrieve bookings associated with the logged-in user from the database
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
    # Validate if the user is logged in; if not, redirect to the login page
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        account = ""
        return render_template("login.html")  # Redirect to the login page if the user is not logged in

    msg = {
        "is_error": False,
        "msg": ""
    }
    
    if request.method == 'POST':
        # Fetch password change details from the form
        old_pwd = request.form.get('old_pwd')
        new_pwd = request.form.get('new_pwd')
        confirm_pwd = request.form.get("confirm_pwd")

        # Password validation checks
        if len(new_pwd) < 7:
            msg["is_error"] = True
            msg["msg"] = "Password must be at least 7 characters."
            return render_template("userPassword.html", account=session['username'], msg=msg)
        elif new_pwd != confirm_pwd:
            msg["is_error"] = True
            msg["msg"] = "Please check your password, it doesn't match"
            return render_template("userPassword.html", account=session['username'], msg=msg)


        # Verify old password matches the one in the database for the user
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM hotelDatabase.customer WHERE customerID = %s AND userPassword = %s', (session['id'], old_pwd,)
        )
        account = cursor.fetchone()

        if account is None:
            # Display error message if the old password doesn't match
            msg["is_error"] = True
            msg["msg"] = "Please check your passwords, invalid password"
            return render_template("userPassword.html", account=session['username'], msg=msg)

       # Update the user's password with the new one
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE hotelDatabase.customer SET userPassword = %s WHERE customerID = %s AND userPassword = %s',
            (new_pwd, session['id'], old_pwd,)
        )
        mysql.connection.commit()

        # Display success message for the password update
        msg["is_error"] = False
        msg["msg"] = "Successfully updated password"

    return render_template("userPassword.html", account=session['username'], msg=msg)

@app.route('/hotelBooking', methods=['POST', 'GET'])
def hotelbooking():

# Retrieve session data: check-in, check-out dates, and duration
    
    if request.form.get('roomprice') is not None:
        session['price'] = request.form.get('roomprice')
        session['roomtype'] = request.form.get('roomtype')


    # Check if the user is logged in
    if 'loggedin' in session and session['loggedin']:
        account = session['username']
    else:
        flash('Login required')
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        print(request.form.get('chosen_room'))

    if request.method == 'POST':
        tprice = session['price'].split()[0][1:]
        print(tprice, session['roomtype'])
        
        cursor = mysql.connection.cursor()

        if session['checkin'] is None:
            flash('Please enter Detail in the Homepage!')
        elif session['checkout'] is None:
            flash('Please enter Detail in the Homepage!')
        else:
            if request.form.get('cardNumber') is not None:
                cursor.execute(
                    'INSERT into hotelDatabase.booking VALUES( NULL, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (session['id'], session['p_id'], session['roomtype'], session['adults'] + session['child'], tprice, session['checkin'], session['checkout'],session["duration"],)
                )
                mysql.connection.commit()
                return redirect(url_for('userBookings'))

    return render_template('hotelBooking.html')

if __name__ == '__main__':
    app.run(debug=True)
