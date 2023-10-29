import Request_modules as rm
import pandas as pd
import csv


count =0 
# hotelId_arr = []
# imagesurl_arr = []
# address_arr = []
# rs_arr = [] 
updated_rows = []
count = 0
with open('xExtration_code/description_JP.csv', mode ='r', encoding='utf-8')as file:
    # reading the CSV file
    csvFile = csv.reader(file)
    csv_file = 'hoteldetailJP.csv'

    # Write the updated rows back to the CSV file
    with open(csv_file, mode='w', newline='', encoding= 'utf-8') as file2:
        writer = csv.writer(file2)
        writer.writerow(["siteId", "gaiaId", "regionName", "propertyId", "hotelName","hotelDesc","rating","address","imageURL"])

        # displaying the contents of the CSV file
        for lines in csvFile:
            count+=1
            if count >1:
                exit()
            hotelId = lines[3]
            payload = {'propertyId': hotelId}
            try:
                resp = (rm.request_details(payload))
                print(resp)
            except:
                print("No data")
                
            try:
                propertyinfo = resp['data'].get('propertyInfo', {})
                # get review score
                reviewinfo = propertyinfo.get('reviewInfo', [])
                review_summary = reviewinfo.get('summary', [])
                review_score = (review_summary.get('overallScoreWithDescriptionA11y', [])).get('value')
                lines.append(review_score)
            except:
                print("no review")
                #print(review_score)
            try:
                #get address
                summary = propertyinfo.get('summary', [])
                location = summary.get('location')
                address = (location.get('address')).get('addressLine')
                # print(address)
                lines.append(address)
            except:
                print("no address")
                
            try:
                #get image url
                propertyGallery = propertyinfo.get("propertyGallery")
                images = (propertyGallery.get("images",[]))
                image = (images[1]).get("image")
                imageurl = image.get("url")
                lines.append(imageurl)
                
                # updated_rows.append(lines)
                writer.writerow(lines)
                print(f"{count}: {payload}")
                #imagesurl = (image).get("url")
                #imagesurl_arr.append(imagesurl)          
            except:
                print("No image found")
            # if (count >20 ):



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