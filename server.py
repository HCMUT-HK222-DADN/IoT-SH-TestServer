import asyncio
import websockets
import json

# SERVERIP = '127.0.0.1'
SERVERIP = '192.168.1.106'
SERVERPORT = '8000'
SEND_INTERVAL = 5

async def handle_websocket(websocket, path):
    # Connection opened
    client_ip, client_port = websocket.remote_address
    print(f"New connection from {client_ip}:{client_port}")
    try:
        while True:
            # Received message
            message = await websocket.recv()
            # Try to read the json file
            try:
                jsonObj = json.loads(message)
                # Process JSON object here
                if jsonObj['Type'] == 'Hello': 
                    sendMessage = replyHello(jsonObj)
                    await websocket.send(json.dumps(sendMessage))
                elif jsonObj['Type'] == 'RequestUpdateSensor':
                    sendMessage = replyRequestUpdateSensor(jsonObj)
                    await websocket.send(json.dumps(sendMessage))
                elif jsonObj['Type'] == 'RequestDeviceControl':
                    sendMessage = replyRequestDeviceControl(jsonObj)
                    await websocket.send(json.dumps(sendMessage))
                elif jsonObj['Type'] == 'RequestDeviceTimerSchedule':
                    sendMessage = replyRequestDeviceTimerSchedule(jsonObj)
                    await websocket.send(json.dumps(sendMessage))
                elif jsonObj['Type'] == 'RequestDeviceTimerBook':
                    handleRequestDeviceTimerBook(jsonObj)
                elif jsonObj['Type'] == 'RequestDeviceTimerDelete':
                    handleRequestDeviceTimerDelete(jsonObj)
            except json.JSONDecodeError:
                # Invalid JSON received
                continue
    except websockets.exceptions.ConnectionClosedOK:
        # Connection closed
        print(f"Connection from {client_ip}:{client_port} closed")
        pass

# ---------------- Function to handle messages
def replyHello(jsonObj):
    return {
        'Type': 'ReplyHello',
        'Message': jsonObj['Value']
    }

def replyRequestUpdateSensor(jsonObj):
    with open('sensor.json', 'r') as file:
        data = json.load(file)
    return data

def replyRequestDeviceControl(jsonObj):
    # Read the json file
    deviceType = jsonObj['Device']
    deviceValue = jsonObj['Value']
    # Write a new JSONFile
    with open('device.json', 'r') as file:
        data = json.load(file)
    if deviceType == 'Fan':
        data['Fan'] = deviceValue
    elif deviceType == 'Light':
        data['Light'] = deviceValue
    with open('device.json', 'w') as file:
        json.dump(data, file)
    # Print to terminal
    print("Control " + deviceType + ": " + str(deviceValue))

def replyRequestDeviceTimerSchedule(jsonObj):
    # return a dict object
    data = {
        "Type": "DeviceTimerSchedule",
        "Data": []
    } 
    with open('deviceSchedule.json', 'r') as file:
        list = json.load(file)['Data']
        data['Data'] += list
    return data

def handleRequestDeviceTimerBook(jsonObj):
    # Read the deviceSchedule file
    with open('deviceSchedule.json', 'r') as file:
        data = json.load(file)
    # Read the incomming jsonObj
    newDict = {
        'Device': jsonObj['Device'],
        'Value': jsonObj['Value'],
        'TimeStart': jsonObj['TimeStart']
    }
    # Write new file
    data['Data'] += [newDict]
    with open('deviceSchedule.json', 'w') as file:
        json.dump(data, file, indent=4)

def handleRequestDeviceTimerDelete(jsonObj):
    # Read the deviceSchedule file
    with open('deviceSchedule.json', 'r') as file:
        data = json.load(file)
    # Read the incomming jsonObj
    position = jsonObj['Position']
    # Write new file
    data['Data'].pop(position)
    with open('deviceSchedule.json', 'w') as file:
        json.dump(data, file, indent=4)

# ----------------------------------------------------------------
async def main():
    async with websockets.serve(handle_websocket, SERVERIP, SERVERPORT):
        # Websocket Wait forever
        await asyncio.Future()  

asyncio.run(main())
