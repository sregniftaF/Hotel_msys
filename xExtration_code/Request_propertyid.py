import requests

url = "https://hotels4.p.rapidapi.com/properties/list"

querystring = {"destinationId":"10805","pageNumber":"1","pageSize":"25","checkIn":"2023-10-15","checkOut":"2023-10-19","adults1":"1"}

headers = {
	"X-RapidAPI-Key": "40854cf97dmsh8c61addd00b4673p1b7c49jsn8ca53f266da9",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())