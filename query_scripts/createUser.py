import mysql.connector

# Connection Info
host = "34.143.183.171"
user = "damiansoh"
password = "2203598@sit"
database = "hotelDatabase"

# Create Connection
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Enter details of new user
new_user = "damiansoh1"
new_user_password = "2203598@sit"

# Execute the CREATE USER query
create_user_query = f"CREATE USER '{new_user}'@'%' IDENTIFIED BY '{new_user_password}'"
cursor.execute(create_user_query)

# List of privileges to grant
privileges = [
    "ALTER", "ALTER ROUTINE", "CREATE", "CREATE ROUTINE", "CREATE TEMPORARY TABLES",
    "CREATE USER", "CREATE VIEW", "DELETE", "DROP", "EVENT", "GRANT OPTION",
    "INDEX", "INSERT", "LOCK TABLES", "PROCESS", "RELOAD", "SELECT", "SHOW DATABASES",
    "SHOW VIEW", "TRIGGER", "UPDATE"
]

# Grant privileges to the new user with GRANT OPTION - transferring of existing privileges
grant_query = f"GRANT {', '.join(privileges)} ON *.* TO '{new_user}'@'%' WITH GRANT OPTION"
cursor.execute(grant_query)

# Flush privileges to apply the changes
cursor.execute("FLUSH PRIVILEGES")

# Commit changes, close cursor, close connection
conn.commit()
cursor.close()
conn.close()
