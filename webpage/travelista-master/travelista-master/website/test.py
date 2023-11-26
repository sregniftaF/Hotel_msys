import requests

url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"

payload = {
	"propertyId": "3981115",
	"checkInDate": {
		"day": 10,
		"month": 12,
		"year": 2023
	},
	"checkOutDate": {
		"day": 15,
		"month": 12,
		"year": 2023
	},
	"destination": { "regionId": "2655" },
	"rooms": [
		{
			"adults": 1,
			"children": []
		}
	]
}
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "2ae3c4b946msh0ad4e05fa122dedp15c03fjsnb50c606376b0",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
res = response.json()
units_data = {}
data = res['data'].get('propertyOffers').get('units')
if data is not None:
    room_counter = 1
    for room in range(9):
        room_key = f'room{room_counter}'
        units_data[room_key] = []
        try:
            header = data[room]['header'].get('text')
            price = data[room]['ratePlans']
            price1 = price[0].get('priceDetails')
            price2 = price1[0].get('totalPriceMessage')
            image = data[room]['unitGallery'].get('gallery')
            image1 = image[0].get('image').get('url')
            print(header, price2, image1)
            units_data[room_key].append(header)
            units_data[room_key].append(price2)
            units_data[room_key].append(image1)
        except IndexError:
            print("Unit sold out")
            break
        room_counter += 1