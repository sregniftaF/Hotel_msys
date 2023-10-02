import requests
import csv

api_url = "https://hotels4.p.rapidapi.com/properties/v2/list"

# opening the CSV file
with open('data/gaiaId_regionNames.csv', mode ='r')as file:
    # reading the CSV file
    csvFile = csv.reader(file)

    # displaying the contents of the CSV file
    for lines in csvFile:
        regionId = lines[0]
        query = {"regionId":str(regionId)}
        payload = {
            "siteId": 300000037,
            "destination": query,
            "checkInDate": {
                "day": 10,
                "month": 10,
                "year": 2025
            },
            "checkOutDate": {
                "day": 13,
                "month": 10,
                "year": 2025
            },
            "rooms": [
                {
                    "adults": 2
                }
            ]
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "2ae3c4b946msh0ad4e05fa122dedp15c03fjsnb50c606376b0",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        resp = response.json()
        data = resp['data'].get('propertySearch', [])

        properties = data.get('properties')
        # Write data rows
        for item in properties:
            try:
                hotelId = item['id']
                hotelName = item['name']
                print(hotelId, hotelName)
            except:
                print("bubu")
