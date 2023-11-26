import mysql.connector

# Replace these values with your MySQL server details
host = "34.143.183.171"
user = "liwen"
password = "2201929@sit"
database = "hotelDatabase"

# Create a connection
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Arguments for table creation
create_table_query = """CREATE TABLE IF NOT EXISTS booking (    
    bookingId INT NOT NULL AUTO_INCREMENT,    
    customerID INT NOT NULL,
    propertyId INT NOT NULL, 
    roomType VARCHAR(255),
    numOfPax INT NOT NULL,
    totalPrice VARCHAR(255),
    checkInDate DATE NOT NULL,
    checkOutDate DATE NOT NULL,
    durationOfStay INT NOT NULL,
    PRIMARY KEY (bookingId),
    FOREIGN KEY (customerID) REFERENCES customer(customerID),
    FOREIGN KEY (propertyId) REFERENCES hotels(propertyId)
)
"""
# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
