import mysql.connector

# Connection info
host = "34.143.183.171"  # CloudSQl IP address
user = "damiansoh"  # Replace with your username
password = "2203598@sit"

# Create connection
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Replace with your desired database name
database_name = "hotelDatabase"

# Execute SQL to create the database
cursor.execute(f"CREATE DATABASE {database_name}")

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
