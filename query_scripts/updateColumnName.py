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

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Input old & new column names
old_column_name = "siteID"
new_column_name = "siteId"

# ALTER TABLE to rename the column
alter_query = f"ALTER TABLE country CHANGE {old_column_name} {new_column_name} VARCHAR(255)"

# Execute the ALTER TABLE query
cursor.execute(alter_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
