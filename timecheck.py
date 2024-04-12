from datetime import datetime
import json

import requests

def sunisup():
    # Convert uphour string to datetime 12h format with AM/PM
    with open('data.json', 'r') as f:
        data = json.load(f)
    uphour = data["sundata"]["sunrise"]
    downhour = data["sundata"]["sunset"]
    uphour = datetime.strptime(uphour, "%I:%M:%S %p")
    # Convert downhour string to datetime 12h format with AM/PM
    downhour = datetime.strptime(downhour, "%I:%M:%S %p")
    now = datetime.now().time()
    # Check if current time is between sunrise and sunset
    if uphour.time() < now < downhour.time():
        return True
    else:
        return False
    
def check_sun_data():
    with open('data.json', 'r') as f:
        config = json.load(f)
    # get the current date
    now = datetime.now().date()
    if config["sundata"]["date"] == now.strftime("%Y-%m-%d"):
        return True
    else:
        config["sundata"]["date"] = now.strftime("%Y-%m-%d")
        sunrise, sunset = fetch_sun_up_down()
        config["sundata"]["sunrise"] = sunrise
        config["sundata"]["sunset"] = sunset
        with open('data.json', 'w') as f:
            json.dump(config, f)
        return False

def fetch_sun_up_down():
    # Fetch the sunrise and sunset time
    url = "https://api.sunrisesunset.io/json?lat=50.88&lng=3.62"
    response = requests.get(url)
    data = response.json()
    sunset = data["results"]["sunset"]
    sunrise = data["results"]["sunrise"]
    return sunrise, sunset