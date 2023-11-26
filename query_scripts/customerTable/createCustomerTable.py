import mysql.connector

# Replace these values with your MySQL server details
host = "34.143.183.171"
user = "yihe"
password = "2203627@sit"
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
create_table_query = """
CREATE TABLE IF NOT EXISTS customer (
    customerID INT AUTO_INCREMENT PRIMARY KEY,
    customerName VARCHAR(255),
    userName VARCHAR(255),
    userPassword VARCHAR(255),
    contactNum INT UNIQUE,
    dateOfBirth VARCHAR(255),
    gender VARCHAR(255),
    nationality VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    passport VARCHAR(255)
)
"""

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()