import mysql.connector

# Connection info
host = "34.143.183.171"  # CloudSQl IP address
user = "damiansoh"  # Replace with your username
password = "2203598@sit"
database = "hotelDatabase"  # Replace with name of target database

# Create a connection
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Set new column name & type
new_column_name = "Testing"
new_column_data_type = "VARCHAR(255)"  # Adjust the data type based on your requirements - "INT" for integer

# ALTER TABLE *table name* to add the new column
alter_query = f"ALTER TABLE hotel ADD COLUMN {new_column_name} {new_column_data_type}"

# Execute the ALTER TABLE query
cursor.execute(alter_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
