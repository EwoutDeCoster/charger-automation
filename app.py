from flask import Flask, flash, render_template, request, jsonify, redirect, send_from_directory, url_for
import json

import requests
import main
import asyncio
import hw
import car
import os
import main
from threading import Thread

loop = asyncio.get_event_loop()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)

# Load or initialize the configuration
def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"overwrite_charging": False}

def save_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file)

def async_wrapper(loop, coroutine):
    """Run the given coroutine in the provided event loop."""
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)

@app.route('/')
def home():
    try:
        config = load_config()
        # Dummy data for demonstration; replace with real data retrieval
        car_charging_status = loop.run_until_complete(main.auto_opladen_actief())  # or "Not Charging"
        car_charging_status = "Ingeschakeld"  if car_charging_status else "Uitgeschakeld"
        house_energy_usage = ""
        return render_template('index.html', 
                            car_charging_status="Data ophalen...", 
                            house_energy_usage=f"{hw.get_energy_usage().get('active_power_w')} W",
                            overwrite_charging=config["overwrite_charging"], only_charge_when_solar=config["only_charge_when_solar"])
    except RuntimeError as e:
        asyncio.wait(3)
        config = load_config()
        # Dummy data for demonstration; replace with real data retrieval
        car_charging_status = loop.run_until_complete(main.auto_opladen_actief())  # or "Not Charging"
        car_charging_status = "Ingeschakeld"  if car_charging_status else "Uitgeschakeld"
        house_energy_usage = ""
        return render_template('index.html', 
                            car_charging_status="Data ophalen...", 
                            house_energy_usage=f"{hw.get_energy_usage().get('active_power_w')} W",
                            overwrite_charging=config["overwrite_charging"], only_charge_when_solar=config["only_charge_when_solar"])
    
@app.route('/settings')
def settings():
    config = load_config()
    return render_template('settings.html', config=config)

@app.route('/update-settings', methods=['POST'])
def update_settings():
    config = load_config()
    config['auto_oplaad_verbruik'] = int(request.form.get('auto_oplaad_verbruik'))
    config['max_piek_verbruik'] = int(request.form.get('max_piek_verbruik'))
    
    # Handle the dynamic list of notification contacts
    notification_contacts = request.form.getlist('notification_contacts')
    # Only update if we have any contacts or if we went from having contacts to not having any
    if notification_contacts or config.get('notification_contacts'):
        config['notification_contacts'] = notification_contacts
    
    save_config(config)
    
    flash('Instellingen zijn succesvol aangepast.', 'success')
    return redirect(url_for('settings'))

@app.route('/car-charging-status')
def car_charging_status():
    # Dummy data for demonstration; replace with real data retrieval
    try:
        auto_opladen = loop.run_until_complete(main.auto_oplader_staat_aan())
        car_charging_status = "Ingeschakeld"  if auto_opladen else "Uitgeschakeld"
        return jsonify(car_charging_status=car_charging_status)
    except RuntimeError as e:
        asyncio.wait(3)
        auto_opladen = loop.run_until_complete(main.auto_oplader_staat_aan())
        car_charging_status = "Ingeschakeld"  if auto_opladen else "Uitgeschakeld"
        return jsonify(car_charging_status=car_charging_status)

@app.route('/house-energy-usage')
def house_energy_usage():
    # Dummy data for demonstration; replace with real data retrieval
    data = hw.get_energy_usage()
    # timestamp format 240310191500 to dd/mm/yyyy om 19:15
    timestamp = str(data.get('montly_power_peak_timestamp'))
    timestamp = f"{timestamp[4:6]}/{timestamp[2:4]}/{timestamp[0:2]} om {timestamp[6:8]}:{timestamp[8:10]}"
    print(data.get('wifi_strength'))
    one = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iMTgiIHI9IjIiIGZpbGw9IndoaXRlIi8+PC9zdmc+"
    two = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMTIgMTZjLTEuMSAwLTIgLjktMiAycy45IDIgMiAyczItLjkgMi0ycy0uOS0yLTItMm0tNi42Mi0xLjYzYy0uNjMtLjYzLS41OS0xLjcxLjEzLTIuMjRDNy4zMyAxMC43OSA5LjU3IDEwIDEyIDEwYzIuNDMgMCA0LjY3Ljc5IDYuNDkgMi4xM2MuNzIuNTMuNzYgMS42LjEzIDIuMjRjLS41My41NC0xLjM3LjU3LTEuOTguMTJBNy45MjUgNy45MjUgMCAwIDAgMTIgMTNjLTEuNzMgMC0zLjMzLjU1LTQuNjQgMS40OWMtLjYxLjQ0LTEuNDUuNDEtMS45OC0uMTIiLz48L3N2Zz4="
    three = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMi4wNiAxMC4wNmMuNTEuNTEgMS4zMi41NiAxLjg3LjFjNC42Ny0zLjg0IDExLjQ1LTMuODQgMTYuMTMtLjAxYy41Ni40NiAxLjM4LjQyIDEuODktLjA5Yy41OS0uNTkuNTUtMS41Ny0uMS0yLjFjLTUuNzEtNC42Ny0xMy45Ny00LjY3LTE5LjY5IDBjLS42NS41Mi0uNyAxLjUtLjEgMi4xbTcuNzYgNy43NmwxLjQ3IDEuNDdjLjM5LjM5IDEuMDIuMzkgMS40MSAwbDEuNDctMS40N2MuNDctLjQ3LjM3LTEuMjgtLjIzLTEuNTlhNC4yOCA0LjI4IDAgMCAwLTMuOTEgMGMtLjU3LjMxLS42OCAxLjEyLS4yMSAxLjU5bS0zLjczLTMuNzNjLjQ5LjQ5IDEuMjYuNTQgMS44My4xM2E3LjA2NCA3LjA2NCAwIDAgMSA4LjE2IDBjLjU3LjQgMS4zNC4zNiAxLjgzLS4xM2wuMDEtLjAxYy42LS42LjU2LTEuNjItLjEzLTIuMTFjLTMuNDQtMi40OS04LjEzLTIuNDktMTEuNTggMGMtLjY5LjUtLjczIDEuNTEtLjEyIDIuMTIiLz48L3N2Zz4="
    return jsonify(house_energy_usage=f"{data.get('active_power_w')} W", montly_power_peak_w=data.get('montly_power_peak_w'), timestamp=timestamp, wifi_strength=three if data.get('wifi_strength') > 75 else two if data.get('wifi_strength') > 50 else one)

@app.route('/weather-data')
def weather_data():
    url = "http://api.weatherapi.com/v1/current.json?key=ae936d975e654b3db48164532241803&q=Heurne&aqi=no&lang=nl"
    response = requests.get(url)
    data = response.json()
    temp = data["current"]["temp_c"]
    text = data["current"]["condition"]["text"]
    icon = data["current"]["condition"]["icon"]
    sunriseurl = "https://api.sunrisesunset.io/json?lat=50.88&lng=3.62"
    sunrisedata = requests.get(sunriseurl).json()
    sunrise = sunrisedata["results"]["sunrise"]
    sunset = sunrisedata["results"]["sunset"]
    return jsonify(weather_data={"temperature": f"{temp}°C", "condition": text, "icon": icon, "sunrise": sunrise, "sunset": sunset})


@app.route('/toggle-charging', methods=['POST'])
def toggle_charging():
    config = load_config()
    config["overwrite_charging"] = not config["overwrite_charging"]
    save_config(config)
    return jsonify({"success": True, "overwrite_charging": config["overwrite_charging"]})

@app.route('/update-solar-charging', methods=['POST'])
def update_solar_charging():
    try:
        data = request.get_json()
        only_charge_when_solar = data.get('only_charge_when_solar', False)
        
        # Load, update, and save the configuration
        config = load_config()  # Assuming you have a function to load your current config
        config['only_charge_when_solar'] = only_charge_when_solar
        save_config(config)  # Assuming you have a function to save your updated config      
        return jsonify({"success": True, "message": "Solar charging setting updated successfully."})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update-daytime-charging', methods=['POST'])
def update_daytime_charging():
    try:
        data = request.get_json()
        daytime_charging = data.get('only_charge_at_daytime', False)
        
        # Load, update, and save the configuration
        config = load_config()  # Assuming you have a function to load your current config
        config['only_charge_at_daytime'] = daytime_charging
        save_config(config)  # Assuming you have a function to save your updated config
        return jsonify({"success": True, "message": "Daytime charging setting updated successfully."})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/check-notifications')
def check_notifications():
    # Dummy function to simulate server deciding to send a notification
    return {'title': 'Server Alert', 'body': 'Something important happened!'}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
