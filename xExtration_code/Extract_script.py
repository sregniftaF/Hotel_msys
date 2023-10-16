import Request_modules as rm
import pandas as pd
import csv


count =0 
# hotelId_arr = []
# imagesurl_arr = []
# address_arr = []
# rs_arr = [] 
updated_rows = []

with open('data/description_JAP2.csv', mode ='r')as file:
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
            propertyinfo = resp['data'].get('propertyInfo', {})
            
            # get review score
            reviewinfo = propertyinfo.get('reviewInfo', [])
            review_summary = reviewinfo.get('summary', [])
            review_score = (review_summary.get('overallScoreWithDescriptionA11y', [])).get('value')
            lines.append(review_score)
            #print(review_score)

            #get address
            summary = propertyinfo.get('summary', [])
            location = summary.get('location')
            address = (location.get('address')).get('addressLine')
            # print(address)
            lines.append(address)
            
            #get image url
            propertyGallery = propertyinfo.get("propertyGallery")
            images = (propertyGallery.get("images",[]))
            image = (images[1]).get("image")
            imageurl = image.get("url")
            lines.append(imageurl)
            
            updated_rows.append(lines)
            
            #imagesurl = (image).get("url")
            #imagesurl_arr.append(imagesurl)
            
            
        except:
            print("No 'data' key found in the response: {}".format(hotelId))
        # if (count >20 ):
        # Define the CSV file name


        csv_file = 'hoteldetailJP.csv'

        # Write the updated rows back to the CSV file
        with open(csv_file, mode='w', newline='' , encoding= 'utf-8') as file2:
            writer = csv.writer(file2)
            writer.writerows(updated_rows)


# print(address_arr)
# print(rs_arr)
# print (imagesurl_arr)
# print(hotelId_arr)

# data = {
    
#     'pid': hotelId_arr,
#     'ReveiwScore': rs_arr,
#     'Address': address_arr,
#     'Image': imagesurl_arr
# }

# df = pd.DataFrame(data)
# df.to_csv('Hotel_details.csv', mode='w', index=False, header=True)
# print ("Data appended succesfully")


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