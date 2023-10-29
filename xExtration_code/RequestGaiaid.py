import requests

url = "https://hotels4.p.rapidapi.com/locations/v3/search"

querystring = {"q":"Singapore, Bukit Panjang","locale":"en_US","langid":"1033"}

headers = {
	"X-RapidAPI-Key": "bfcd09eba4msh998d868b5f62f18p158ed2jsn7f51163458d9",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

response = (requests.get(url, headers=headers, params=querystring))

print(response.json())