#!/usr/bin/env python3
from datetime import datetime, timedelta
import json
import requests
import time
import ewelink
import hw as hw
import car
import asyncio
import logging
import notification
import os

logging.basicConfig(level=logging.INFO)
logging.getLogger('asyncio').setLevel(logging.INFO)
# set log location
logging.basicConfig(filename='log.txt', level=logging.INFO)
# add a timestamp to the log
logging.Formatter.converter = time.gmtime

# log to log.txt
# if ran on a raspberry pi, change the path to /home/pi/automation
if os.name == 'posix':
    os.chdir('/home/ewout/automation')
else:
    os.chdir('C:/Users/ewama/Documents/charger automation')




with open('credentials.json', 'r') as f:
    credentials = json.load(f)
password = credentials['ewelink']['password']
email = credentials['ewelink']['email']

def get_target_date(day_str):
    """Converts 'today', 'tomorrow', or 'day-after-tomorrow' into a datetime.date object."""
    today = datetime.now().date()
    if day_str == "today":
        return today
    elif day_str == "tomorrow":
        return today + timedelta(days=1)
    elif day_str == "day-after-tomorrow":
        return today + timedelta(days=2)
    else:
        return None

def is_time_to_activate(scheduled_time, target_date):
    """Checks if the current time is past the scheduled time on the target date."""
    now = datetime.now()
    scheduled_datetime = datetime.strptime(f"{target_date} {scheduled_time}", "%Y-%m-%d %H:%M")
    return now >= scheduled_datetime

def check_mogelijkheid_opladen():
    verbruik = hw.get_energy_usage()
    verbruik = verbruik.get('active_power_w')
    with open('config.json', 'r') as f:
        config = json.load(f)
    max_piek_verbruik = config['max_piek_verbruik']
    auto_oplaad_verbruik = config['auto_oplaad_verbruik']
    with open('config.json', 'r') as f:
        config = json.load(f)
    max_piek_verbruik = config['max_piek_verbruik']
    if verbruik + auto_oplaad_verbruik > max_piek_verbruik:
        return False
    else:
        return True
    
async def auto_opladen_actief():
    with open('config.json', 'r') as f:
        config = json.load(f)
    auto_oplaad_verbruik = config['auto_oplaad_verbruik']
    client = ewelink.Client(password=password, email=email)
    
    # Login and create a session for the client
    await client.login()

    # Now, call the specific function you want with the authenticated client
    # For example, to get the status:
    usage = await car.get_usage(client)


    await client.http.session.close()
    await client.ws.close()
    return float(usage) > auto_oplaad_verbruik/2

async def auto_oplader_staat_aan():
    client = ewelink.Client(password=password, email=email)
    await client.login()
    status = await car.get_device_status(client)
    status = status["Power"].value
    await client.http.session.close()
    await client.ws.close()
    return status == 'on'

# auto opladen actief en huidig verbruik > max_piek_verbruik => opladen uitschakelen
# auto opladen actief en huidig verbruik < max_piek_verbruik => niets doen
# auto opladen inactief en huidig verbruik + auto_oplaad_verbruik < max_piek_verbruik => opladen inschakelen
# auto opladen inactief en huidig verbruik + auto_oplaad_verbruik > max_piek_verbruik => niets doen

async def auto_aan():
    client = ewelink.Client(password=password, email=email)
    await client.login()
    await car.turn_on(client)
    await client.http.session.close()
    await client.ws.close()

async def auto_uit():
    client = ewelink.Client(password=password, email=email)
    await client.login()
    await car.turn_off(client)
    await client.http.session.close()
    await client.ws.close()

def toggle_overwrite_charging():
    with open('config.json', 'r') as f:
        config = json.load(f)
    config['overwrite_charging'] = not config['overwrite_charging']


def manage_opladen():
    with open('config.json', 'r') as f:
        config = json.load(f)
    OVERWRITE_CHARGING = config['overwrite_charging']
    ONLY_CHARGE_WHEN_SOLAR = config['only_charge_when_solar']
    max_piek_verbruik = config['max_piek_verbruik']
    auto_oplaad_verbruik = config['auto_oplaad_verbruik']
    loop = asyncio.get_event_loop()
    auto_opladen = loop.run_until_complete(auto_opladen_actief())
    oplader_aan = loop.run_until_complete(auto_oplader_staat_aan())
    huidig_verbruik = hw.get_energy_usage().get('active_power_w')
# if overwrite charging is enabled, charge the car regardless of the current energy usage
    if OVERWRITE_CHARGING:
        if not oplader_aan:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(auto_aan())
        return
# only charge the car when there is enough solar energy
    if ONLY_CHARGE_WHEN_SOLAR:
        # the car charging is allowed when the current energy usage plus the car charging usage is less than 100 W
        print(huidig_verbruik)
        charging_allowed = huidig_verbruik + auto_oplaad_verbruik < 100
        if oplader_aan and not charging_allowed:
            loop.run_until_complete(auto_uit())
            logging.info(f'Auto opladen uitgeschakeld, verbruik + opladen: {huidig_verbruik + auto_oplaad_verbruik} W < 100 W')
            for i in config['notification_contacts']:
                notification.send_email('Mercedes A250 Oplader Status Update', 'Er is niet genoeg zonne-energie om de auto op te laden.', False, i)
        elif not oplader_aan and charging_allowed:
            loop.run_until_complete(auto_aan())
            logging.info(f'Auto opladen ingeschakeld, verbruik + opladen: {huidig_verbruik + auto_oplaad_verbruik} W > 100 W')
            for i in config['notification_contacts']:
                notification.send_email('Mercedes A250 Oplader Status Update', 'Er is genoeg zonne-energie om de auto op te laden.', True, i)
        return
            
# regular peak power management    
    if oplader_aan:
        if huidig_verbruik > max_piek_verbruik:
            loop.run_until_complete(auto_uit())
            logging.info(f'Auto opladen uitgeschakeld, huidig verbruik: {huidig_verbruik} W > max verbruik: {max_piek_verbruik} W')
            for i in config['notification_contacts']:
                notification.send_email('Mercedes A250 Oplader Status Update', 'De status van de oplader is gewijzigd.', False, i)
        else:
            pass
    else:
        if check_mogelijkheid_opladen():
            loop.run_until_complete(auto_aan())
            logging.info(f'Auto opladen ingeschakeld, verbruik + opladen: {huidig_verbruik + auto_oplaad_verbruik} W < max verbruik: {max_piek_verbruik} W')
            try:
                for i in config['notification_contacts']:
                    notification.send_email('Mercedes A250 Oplader Status Update', 'De status van de oplader is gewijzigd.', True, i)
            except:
                pass
        else:
            pass





if __name__ == '__main__':
    manage_opladen()
