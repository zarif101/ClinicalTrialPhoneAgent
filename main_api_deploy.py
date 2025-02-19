from fastapi import FastAPI, Request
import pgeocode
from geopy.distance import geodesic
import uvicorn

app = FastAPI()


BEACON_ZIP = '94104'  # Define your main ZIP code
RADIUS_MILES = 50  # Radius limit in miles
NUMBER2NAME_DICT = {"+19254759601":"Zarif Azher",
                    "+16502235434":"Sohit"}
def getdistance(zip1, zip2, country="US"):
    nomi = pgeocode.Nominatim(country)
    loc1, loc2 = nomi.query_postal_code(zip1), nomi.query_postal_code(zip2)
    return geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).miles


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