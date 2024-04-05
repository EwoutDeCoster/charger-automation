import json
import requests
import time
import ewelink
import nmap

with open('credentials.json', 'r') as f:
    credentials = json.load(f)

hwendpoint = "/api/v1/data"
hw_mac = credentials['hw']['mac']
hwip = credentials['hw']['ip']

with open('credentials.json', 'r') as f:
    credentials = json.load(f)
password = credentials['ewelink']['password']
email = credentials['ewelink']['email']

def get_hw_address(mac_address: str) -> str:
    iprange = "192.168.0.0/24"

    nm = nmap.PortScanner()
    nm.scan(hosts=iprange, arguments='-sP')

    for host in nm.all_hosts():
        if 'mac' in nm[host]['addresses']:
            if nm[host]['addresses']['mac'] == mac_address:
                print(f"Device found at {host}")
                break
    else:
        print("Device not found")
    return host


def get_energy_usage(rerun=False):
    try:
        url = f"http://{hwip}{hwendpoint}"
        response = requests.get(url)
        if response.status_code == 404:
            refresh_ip()
            url = f"http://{hwip}{hwendpoint}"
            response = requests.get(url)
        return response.json()
    # If the device is not found, get the new IP address and try again
    except requests.exceptions.ConnectionError:
        if rerun:
            return "Device not found"
        refresh_ip()
        # replace the IP address in the credentials file
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
        credentials['hw']['ip'] = hwip
        with open('credentials.json', 'w') as f:
            json.dump(credentials, f)
        return get_energy_usage(rerun=True)


def refresh_ip():
    global hwip
    hwip = get_hw_address(hw_mac)

if __name__ == '__main__':
    print(get_energy_usage())