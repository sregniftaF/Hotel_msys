import Request_modules as rm
import csv
payload = {
    "propertyId": "66441177"
}
count =0 
address_arr = []
rs_arr = [] 
with open('data/hotel_id.csv', mode ='r')as file:
    # reading the CSV file
    csvFile = csv.reader(file)

    # displaying the contents of the CSV file
    for lines in csvFile:
        hotelId = lines[0]
        payload = {'propertyId': hotelId}
        count+=1
        try:
            resp = (rm.request_details(payload))
        except:
            print("No data")
            
            
        try:
            # get review score
            propertyinfo = resp['data'].get('propertyInfo', {})
            reviewinfo = propertyinfo.get('reviewInfo', [])
            review_summary = reviewinfo.get('summary', [])
            review_score = (review_summary.get('overallScoreWithDescriptionA11y', [])).get('value')
            #print(review_score)

            summary = propertyinfo.get('summary', [])
            location = summary.get('location')
            address = (location.get('address')).get('addressLine')
            # print(address)
            address_arr.append(address)
            rs_arr.append(review_score)
        except:
            print("No 'data' key found in the response: {}".format(hotelId))
        
        if (count == 100):
            break
print(address_arr)
print(rs_arr)



# resp = (rm.request_details(payload))
# try:
#     # get review score
#     propertyinfo = resp['data'].get('propertyInfo', {})
#     reviewinfo = propertyinfo.get('reviewInfo', [])
#     review_summary = reviewinfo.get('summary', [])
#     review_score = (review_summary.get('overallScoreWithDescriptionA11y', [])).get('value')
#     #print(review_score)
    
#     summary = propertyinfo.get('summary', [])
#     location = summary.get('location')
#     address = (location.get('address')).get('addressLine')
#     print(address)
 
# except KeyError:
#     print("No 'data' key found in the response")