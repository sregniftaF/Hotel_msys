import csv
import requests

url = "https://hotels4.p.rapidapi.com/locations/v3/search"
''', '''
querystring = [{"q": "Fukuoka"}, {"q": "Hakodate"}, {"q": "Hakone"}, {"q": "Hakuba"}, {"q": "Himeji"},
               {"q": "Hiroshima"}, {"q": "Ise"}, {"q": "Ishigaki"}, {"q": "Kagoshima"}, {"q": "Kamakura"},
               {"q": "Kanazawa"}, {"q": "Kawagoe"}, {"q": "Kawaguchi"}, {"q": "Kawasaki"}, {"q": "Kawasaki"},
               {"q": "Kawasaki Ward"}, {"q": "Kitakyushu"}, {"q": "Kobe"}, {"q": "Kochi"}, {"q": "Kumamoto"},
               {"q": "Kurashiki"}, {"q": "Kyoto"}, {"q": "Matsue"}, {"q": "Matsumoto"}, {"q": "Matsuyama"},
               {"q": "Nagano"}, {"q": "Nagasaki"}, {"q": "Nagoya"}, {"q": "Naha"}, {"q": "Naoshima"}, {"q": "Nara"},
               {"q": "Niigata"}, {"q": "Nikko"}, {"q": "Oita"}, {"q": "Okinawa"}, {"q": "Onomichi"}, {"q": "Osaka"},
               {"q": "Otaru"}, {"q": "Saitama"}, {"q": "Sapporo"}, {"q": "Sendai"}, {"q": "Shirakawa"},
               {"q": "Takamatsu"}, {"q": "Takayama"}, {"q": "Tokyo"}, {"q": "Tokyo City"}, {"q": "Tottori"},
               {"q": "Utsunomiya"}, {"q": "Yanagawa"}, {"q": "Yokohama"}, {"q": "japan"}, {"q": "tokyo"}]

headers = {
    "X-RapidAPI-Key": "2ae3c4b946msh0ad4e05fa122dedp15c03fjsnb50c606376b0",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# Define the CSV file name
csv_file = 'data/gaiaId_regionNames.csv'

# Create and open the CSV file for writing
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['gaiaId', 'fullName'])

    for querystring in querystring:
        response = requests.get(url, headers=headers, params=querystring)
        resp = response.json()
        sr_data = resp.get('sr', [])

        # Write data rows
        for item in sr_data:
            try:
                gaiaId = item['gaiaId']
                regionNames = item['regionNames']['fullName']
                writer.writerow([gaiaId, regionNames])
            except:
                print(querystring)

print(f'Data saved as {csv_file}')
