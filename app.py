from flask import Flask, flash, render_template, request, jsonify, redirect, url_for
import json

import requests
import main
import asyncio
import hw
import car
import os

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

@app.route('/')
def home():
    try:
        config = load_config()
        # Dummy data for demonstration; replace with real data retrieval
        car_charging_status = loop.run_until_complete(main.auto_opladen_actief())  # or "Not Charging"
        car_charging_status = "Ingeschakeld"  if car_charging_status else "Uitgeschakeld"
        house_energy_usage = "5.2 kWh"
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
        house_energy_usage = "5.2 kWh"
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
    return jsonify(house_energy_usage=f"{data.get('active_power_w')} W", montly_power_peak_w=data.get('montly_power_peak_w'), timestamp=timestamp)

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
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
