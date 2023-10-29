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

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Arguments for table creation
create_table_query = """
CREATE TABLE IF NOT EXISTS region (
    siteId INT NOT NULL,
    gaiaId INT PRIMARY KEY,
    regionName VARCHAR(255)
)
"""

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()