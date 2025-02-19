from fastapi import FastAPI, Request
import geopy
from pyzipcode import ZipCodeDatabase
from geopy.distance import great_circle
import uvicorn

app = FastAPI()


BEACON_ZIP = '94104'  # Define your main ZIP code
RADIUS_MILES = 50  # Radius limit in miles

def getdistance(zipcode1, zipcode2, measure="miles"):
    zcdb = ZipCodeDatabase()
    
    ## get long/lat for zipcodes
    long1 = zcdb[zipcode1].longitude
    lat1 = zcdb[zipcode1].latitude
    long2 = zcdb[zipcode2].longitude
    lat2 = zcdb[zipcode2].latitude
    
    ## create coordinates for zipcodes
    zip1 = (lat1, long1)
    zip2 = (lat2, long2)
    
    ## calculate distance
    distance = great_circle(zip1, zip2)
    
    ## print
    if measure == "miles":
        return distance.miles
    else:
        return distance.km


@app.post("/process-data")
async def process_data(request: Request):
    try:
        data = await request.json() #contains a bunch, including transcript
        data = data.get("args")
        age = int(data.get("age"))
        zip_code = str(data.get("zip"))
        alz = data.get("alz")
        try:
            distance = getdistance(BEACON_ZIP, zip_code)
            within_radius = distance <= RADIUS_MILES
            if within_radius:
                zip_elig = "Y"
            else:
                zip_elig = "N"
        except:
            zip_elig="INVALID ZIP CODE"
        if age >= 18 and age <= 65:
            age_elig = "Y"
        else:
            age_elig = "N"
        if str(alz).upper() == "N":
            alz_elig = "Y"
        else:
            alz_elig = "N"
        return {"age":age_elig, "zip_code":zip_elig, "alz":alz_elig}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "Invalid request"}, 400
    

NUMBER2NAME_DICT = {"+19254759600":"Zarif Azher",
                    "+16502235434":"Sohit"}
@app.post("/namehook")
async def name_webhook(request: Request):
    try:
        data = await request.json()
        from_number=data['from_number']
        if from_number in NUMBER2NAME_DICT:
            return {
            "user_name": NUMBER2NAME_DICT[from_number]
                }
        else:
             return {
            "user_name": "NOUSERFOUND"
                }


    except Exception as e:
        print(f"Error in webhook: {e}")
        print(data, type(data))
        return {"message": "Invalid webhook request"}, 400


#uvicorn.run(app, host="0.0.0.0", port=8080)  # Run on port 8080