
import requests

#request the json file from the website
def api_res(api_url, payload, headers ):
    response = requests.post(api_url, json=payload, headers=headers)
    resp = response.json()
    return resp #return the jsonfile
    