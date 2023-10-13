import mysql.connector

# Replace these values with your MySQL server details
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

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# SELECT * FROM table_name
select_query = "SELECT * FROM hotel"

# Execute the SELECT query
cursor.execute(select_query)

# Fetch all rows from the result set
result = cursor.fetchall()

# Display the results
for row in result:
    print(row)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
