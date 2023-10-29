import requests
import csv

api_url = "https://hotels4.p.rapidapi.com/properties/v2/list"
previousRegionId = ""
count = 0

# Open the input CSV file
with open('xExtration_code/gaiaId_regionNames_SG.csv', mode='r', newline='') as file:
    # Read the input CSV file
    csvFile = csv.reader(file)

    # Open the output CSV file
    csv_file = 'propertyId_SG.csv'
    with open(csv_file, mode='w', newline='', encoding= 'utf-8') as file2:
        writer = csv.writer(file2)

        # Write the header row
        writer.writerow(["siteId", "gaiaId", "regionName", "propertyId", "hotelName"])

        # Iterate through the rows in the input file
        for lines in csvFile:
            regionId = lines[0]
            regionName = lines[1]


            query = {"regionId": str(regionId)}
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
                "X-RapidAPI-Key": "bfcd09eba4msh998d868b5f62f18p158ed2jsn7f51163458d9",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            }

            response = requests.post(api_url, json=payload, headers=headers)
            resp = response.json()

            if resp.get('data') is not None:
                try:
                    data = resp['data'].get('propertySearch', {})
                    properties = data.get('properties', [])
                    gaiaId = regionId
                except KeyError:
                    print("No 'data' key found in the response")
            else:
                print("No valid 'data' found in the response")

            # Write data rows
            count = 0
            for item in properties:
                count+=1
                if count <15:
                    try:
                        hotelId = item.get('id')
                        hotelName = item.get('name')
                        if hotelId is not None and hotelName is not None:
                            writer.writerow([300000037, gaiaId, regionName, hotelId, hotelName])
                            print(300000037, gaiaId, regionName, hotelId, hotelName)
                        else:
                            print("Missing hotelId or hotelName")
                    except KeyError:
                        print("Error accessing 'id' or 'name' in property")
                    except TypeError:
                        print("Property data is not in the expected format")
                else:   break
