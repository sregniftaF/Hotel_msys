import requests
import csv

url = "https://hotels4.p.rapidapi.com/properties/v2/get-content"

# Create a list to store the updated rows with additional data
updated_rows = []
count = 0

with open("xExtration_code/propertyId_SG.csv", mode='r') as file:
    # Reading the CSV file
    csvFile = csv.reader(file)
    # Define the CSV file name
    csv_file = 'description_SG.csv'
    
    with open(csv_file, mode='w', newline='', encoding= 'utf-8') as file2:
        writer = csv.writer(file2)
        writer.writerow(["siteId", "gaiaId", "regionName", "propertyId", "hotelName","hotelDesc"])
        
        for lines in csvFile:
            count+= 1
            print(count)
            if (count == 210):
                exit()
            propertyId = lines[3]

            payload = {"propertyId": str(propertyId)}
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": "405b6a1b2dmshb0155c3c4d3f00fp17293bjsn6d806e9e4daf",
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
                    line_property = property_des[0].get('content').get('text')
                    writer.writerow([lines[0], lines[1], lines[2], lines[3],lines[4], line_property])
                    # Append the updated row to the list
                except KeyError:
                    print("No 'data' key found in the response")
            else:
                print("No valid 'data' found in the response")
