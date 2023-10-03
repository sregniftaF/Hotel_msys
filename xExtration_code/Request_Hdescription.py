import requests
import csv

url = "https://hotels4.p.rapidapi.com/properties/v2/get-content"

# Create a list to store the updated rows with additional data
updated_rows = []

with open('hotel_id_SG.csv', mode='r') as file:
    # Reading the CSV file
    csvFile = csv.reader(file)

    for lines in csvFile:
        propertyId = lines[0]

        payload = {"propertyId": str(propertyId)}
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "d54251d0d0msh2c71c303b8b375ap16db3bjsn6835d5c34d91",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response = requests.post(url, json=payload, headers=headers)
        res = response.json()

        if res['data'] is not None:
            try:
                data = res['data'].get('propertyInfo').get('propertyContentSectionGroups').get('aboutThisProperty').get(
                    'sections')
                property = data[0].get('bodySubSections')
                property2 = property[0].get('elements')
                property_des = property2[0].get('items')

                # Add the new data to the third column
                lines.append(property_des[0].get('content').get('text'))

                # Append the updated row to the list
                updated_rows.append(lines)
            except KeyError:
                print("No 'data' key found in the response")
        else:
            print("No valid 'data' found in the response")

        # Define the CSV file name
        csv_file = 'description.csv'

        # Write the updated rows back to the CSV file
        with open(csv_file, mode='w', newline='') as file2:
            writer = csv.writer(file2)
            writer.writerows(updated_rows)
