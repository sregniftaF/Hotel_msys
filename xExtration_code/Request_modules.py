
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
        "X-RapidAPI-Key": "f68a531d22msh0fd5494dfa334ddp111ac6jsn16c89a1595b4",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    return api_res(url,payload,headers) #response


#request from detail; 
def request_details(payload):
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    # payload = {
    #     "siteId": 300000040,
    #     "propertyId": "66441177"
    # }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "f68a531d22msh0fd5494dfa334ddp111ac6jsn16c89a1595b4",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    return api_res(url, payload, headers)