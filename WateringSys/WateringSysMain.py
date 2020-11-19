import WateringSysPubSub as wps
import WateringSysVars
import socket
import threading
import json

sem = threading.BoundedSemaphore(1)

def PumpOnOff(client, userdata, message):
    print("Recevied shadow")
    print(message.payload)    
    data = json.loads(message.payload)
    sem.acquire()
    WateringSysVars.WaterSysShadow["pumpsw"] = data["state"]["reported"]["pumpsw"]
    WateringSysVars.WaterSysShadow["pumpdur"] = data["state"]["reported"]["pumpdur"]
    sem.release()
    print("Pump switch: " + WateringSysVars.WaterSysShadow["pumpsw"])
    print("Pump duration: " + WateringSysVars.WaterSysShadow["pumpdur"])
    print("Moisture: " + data["state"]["reported"]["moisture"])
    print("Water lvl: " + data["state"]["reported"]["waterlvl"])


wps.InitializeAWSIoT()
wps.SubscribeAWSIoT(PumpOnOff)

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((WateringSysVars.localIP, WateringSysVars.localPort))

###Receive from ESP
#MMMMLLLLSDDDE
#MMMM = moisture level
#LLLL = water level
#S = on or off (0 or 1)
#DDD = duration
#E = error code (0 or 1)
##
###Send to ESP
#SDDDE
while True:
    dataAddress = UDPServerSocket.recvfrom(WateringSysVars.bufferSize)
    sensorData = dataAddress[0]
    ESPAddress = dataAddress[1]
    print("Sensor data received : " + sensorData)    
    sem.acquire()
    if WateringSysVars.WaterSysShadow["pumpsw"] == "1":
        sendToESP = "1" + WateringSysVars.WaterSysShadow["pumpdur"] + "0"
        WateringSysVars.WaterSysShadow["pumpsw"] = "0"
        WateringSysVars.WaterSysShadow["pumpdur"] = "000"
        sem.release()
        UDPServerSocket.sendto(sendToESP, ESPAddress)
    else:
        sem.release()
    WateringSysVars.WaterSysShadow["moisture"] = sensorData[0:4]
    WateringSysVars.WaterSysShadow["waterlvl"] = sensorData[4:8]
    WateringSysVars.WaterSysShadow["pumperr"] = sensorData[8]
    wps.PublishAWSIoT()
    print("Published to AWS")
    




