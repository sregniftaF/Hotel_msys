import requests

url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

payload = {
	"siteId": 300000037,
	"propertyId": "66441177"
}
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "40854cf97dmsh8c61addd00b4673p1b7c49jsn8ca53f266da9",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

# get image, re
print(response.json())