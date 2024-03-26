import asyncio
import ewelink
from ewelink import DeviceOffline, Client
import os
import json
with open('credentials.json', 'r') as f:
    credentials = json.load(f)

email = credentials['ewelink']['email']
password = credentials['ewelink']['password']


async def turn_on(client: ewelink.Client):
    device = client.get_device("100169269c")
    # Uncomment the following lines if you wish to execute these operations.
    # print(device.state)
    # print(device.online)
    await device.on()

async def turn_off(client: ewelink.Client):
    device = client.get_device("100169269c")
    # Uncomment the following lines if you wish to execute these operations.
    # print(device.state)
    # print(device.online)
    await device.off()

async def get_status(client: ewelink.Client):
    device = client.get_device("100169269c")
    print(type(device.online))
    print(device.online)

async def get_usage(client: ewelink.Client):
    device = client.get_device("100169269c")
    return device.params['power']

async def main():
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)

    email = credentials['ewelink']['email']
    password = credentials['ewelink']['password']
    
    # Initialize the client
    client = ewelink.Client(password=password, email=email)
    
    # Login and create a session for the client
    await client.login()

    # Now, call the specific function you want with the authenticated client
    # For example, to get the status:
    await get_usage(client)


    await client.http.session.close()
    await client.ws.close()
    # Or, to turn off the device, you would call:
    # await turn_off(client)

if __name__ == '__main__':
    asyncio.run(main())