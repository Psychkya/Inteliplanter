import WateringSysPubSub as wps
import WateringSysVars
import socket
import threading

sem = threading.BoundedSemaphore(1)

def PumpOnOff(client, userdata, message):
    data = json.loads(mesage.payload)
    sem.acquire()
    WateringSysVars.WaterSysShadow["pumpsw"] = data["state"]["reported"]["pumpsw"]
    WateringSysVars.WaterSysShadow["pumpdur"] = data["state"]["reported"]["pumpdur"]
    sem.release()


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
    espAddress = dataAddress[1]
    sem.acquire()
    if WateringSysVars.WaterSysShadow["pumpsw"] == "1":
        WateringSysVars.WaterSysShadow["pumpsw"] = sensorData[8:9]
        WateringSysVars.WaterSysShadow["pumpdur"] = sensorData[9:12]
        sendToESP = "1" + WateringSysVars.WaterSysShadow["pumpdur"] + "0"
        sem.release()
        UDPServerSocket.sendto(sendToESP, espaddress)
    else:
        WateringSysVars.WaterSysShadow["pumpsw"] = sensorData[8:9]
        WateringSysVars.WaterSysShadow["pumpdur"] = sensorData[9:12]        
        sem.release()
    WateringSysVars.WaterSysShadow["moisture"] = sensorData[0:4]
    WateringSysVars.WaterSysShadow["waterlvl"] = sensorData[4:8]
    WateringSysVars.WaterSysShadow["pumperr"] = sensorData[12:13]
    wps.PublishAWSIoT()
    




