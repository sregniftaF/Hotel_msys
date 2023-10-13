import mysql.connector

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

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Specify the column you want to delete
column_to_delete = "Testing1"

# Construct the ALTER TABLE query to drop the column
alter_query = f"ALTER TABLE hotel DROP COLUMN {column_to_delete}"

# Execute the ALTER TABLE query
cursor.execute(alter_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
