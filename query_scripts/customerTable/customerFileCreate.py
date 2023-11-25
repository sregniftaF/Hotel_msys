import csv
import random
import faker
import string
import pandas as pd
fake = faker.Faker()

# Function to generate random data for the CSV file
def generate_random_data():
    # Generate a list of unique digits
    unique_digits = random.sample(range(0, 10), 10)
    # Ensure the first digit is not 0
    if unique_digits[0] == 0:
        unique_digits[0], unique_digits[random.randint(1, 9)] = unique_digits[random.randint(1, 9)], unique_digits[0]
    # Take the first 7 digits to form a unique 7-digit number
    customerID = ''.join(map(str, unique_digits[:7]))
    customerName = fake.name()
    # Extract first six characters from customer_name
    shortened_name = customerName[:6]
    # Calculate the maximum length for the random part of the username
    max_random_length = 10 - len(shortened_name)
    # Generate random username with first six characters of customer_name and random numbers/letters
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=max_random_length))
    # Combine the shortened name and random part to form the username
    userName = shortened_name + random_part

    password = fake.password()

    contact= str(random.choice([8, 9])) + ''.join(random.choices('0123456789', k=7))

    dateOfBirth = fake.date_of_birth(minimum_age=18, maximum_age=70)

    gender = random.choice(['Male', 'Female'])

    nationality = random.choice(['Singapore', 'China', 'Malaysia', 'Indonesia','US','India'])

    # Generate a random string of numbers and letters
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    emailName = shortened_name + random_part
    emailName = emailName.replace(" ","")
    # Generate the email address using customer_name and random part
    email = f"{emailName}@gmail.com"

    passport = 'S' + ''.join(random.choices(string.digits, k=7)) + random.choice(string.ascii_uppercase)

    return [customerID, customerName, userName, password, contact, dateOfBirth, gender, nationality, email, passport]

# Generate 1000 lines of random data
data = []
for _ in range(1000):
    data.append(generate_random_data())

# Write the data to a CSV file
with open('customertestset.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header row
    csvwriter.writerow(['Customer_id', 'customer_name', 'Username', 'password', 'contact', 'Date_of_birth', 'Gender', 'Nationality', 'Email', 'Passport_Number'])
    # Write data rows
    csvwriter.writerows(data)


