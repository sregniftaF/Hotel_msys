
import requests

#request the json file from the website
def api_res(api_url, payload, headers):
    response = requests.post(api_url, json=payload, headers=headers)
    resp = response.json()
    return resp #return the jsonfile



#request from get content; get the description
def request_get_content(payload):
    url = "https://hotels4.p.rapidapi.com/properties/v2/get-content"

    #payload = { "propertyId": "46753" }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "dd0669b18emsh00390ef73699b09p1ddfaejsnc38f1845b162",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    return api_res(url,payload,headers) #response


#request from detail; 
def request_details(payload):
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    # payload = {
    #     "siteId": 300000037,
    #     "propertyId": "66441177"
    # }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "40854cf97dmsh8c61addd00b4673p1b7c49jsn8ca53f266da9",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    return api_res(url, payload, headers)