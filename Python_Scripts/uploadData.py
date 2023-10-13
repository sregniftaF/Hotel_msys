import mysql.connector
import csv

# Connection info
host = "34.143.183.171"
user = "damiansoh"
password = "2203598@sit"
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

# INSERT data into table name (row name, row name)
insert_query = "INSERT INTO hotel (PropertyID, HotelName) VALUES (%s, %s)"

# Read data from CSV file and insert into the database
with open(r"C:\Users\ZDDell\Desktop\hotel_id.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header row

    for row in csv_reader:
        cursor.execute(insert_query, (row[0], row[1]))

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
