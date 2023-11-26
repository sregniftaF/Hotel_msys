import csv
import random
from datetime import datetime, timedelta
import faker
import pandas as pd

fake = faker.Faker()

room_types = ['Standard Single', 'Standard Double', 'Deluxe Single', 'Deluxe Double', 'Suite', 'Presidential Suite']
empty = ['']
import csv


# Define the start and end dates for the range (November to December)
start_date = datetime(2023, 11, 1)
end_date = datetime(2023, 12, 31)

# Calculate the number of days between start and end dates
days_between = (end_date - start_date).days

# Generate a random number of days for the check-in date
random_checkin_days = random.randint(0, days_between)

# Generate a random number of days for the length of stay (e.g., 1 to 14 days)
random_length_of_stay = random.randint(1, 14)

# Calculate the check-out date by adding the random length of stay to the check-in date
checkin_date = start_date + timedelta(days=random_checkin_days)
checkout_date = checkin_date + timedelta(days=random_length_of_stay)

def generate_random_data():
    # Generate a list of unique
    unique_digits = random.sample(range(0, 10), 10)
    # Ensure the first digit is not 0
    if unique_digits[0] == 0:
        unique_digits[0], unique_digits[random.randint(1, 9)] = unique_digits[random.randint(1, 9)], unique_digits[
        0]

    # Take the first 7 digits to form a unique 7-digit number
    bookingID = ''.join(map(str, unique_digits[:7]))
    customerID = random.choice(empty)
    propertyID = random.choice(empty)
    roomType = random.choice(empty)
    no_of_pax = random.randint(1, 6)
    totalPrice = random.choice(empty)
    checkInDate = checkin_date.strftime('%Y-%m-%d')
    checkOutDate = checkout_date.strftime('%Y-%m-%d')
    durationOfStay = random_length_of_stay
    return [bookingID, customerID, propertyID, roomType, no_of_pax, totalPrice, checkInDate, checkOutDate,
            durationOfStay]

# Generate 1000 lines of random data
data = []
for _ in range(1000):
    data.append(generate_random_data())
    random_checkin_days = random.randint(0, (end_date - start_date).days)
    random_length_of_stay = random.randint(1, 14)
    checkin_date = start_date + timedelta(days=random_checkin_days)
    checkout_date = checkin_date + timedelta(days=random_length_of_stay)
# Write the data to a CSV file
with open('bookingDatasets.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header row
    csvwriter.writerow(
        ['bookingID', 'customerID', 'propertyID', 'roomType', 'no_of_pax', 'totalPrice', 'checkInDate', 'checkOutDate',
         'durationOfStay'])  # Write data rows
    csvwriter.writerows(data)
