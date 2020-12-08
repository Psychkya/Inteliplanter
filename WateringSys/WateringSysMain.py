import WateringSysPubSub as wps
import WateringSysVars
import socket
import threading
import json
import sys

sem_water = threading.BoundedSemaphore(1)
sem_light = threading.BoundedSemaphore(1)
sem_cmd = threading.BoundedSemaphore(2)

thread_signal = 1


#Bind sockets
UDPServerSocket_water = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket_water.bind((WateringSysVars.localIP, WateringSysVars.localPort_water))

UDPServerSocket_light = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket_light.bind((WateringSysVars.localIP, WateringSysVars.localPort_light))

def ServiceCommands(client, userdata, message):
    print("Recevied shadow")
    print(message.payload)    
    data = json.loads(message.payload)
    sem_cmd.acquire()
    WateringSysVars.WaterSysShadow["pumpsw"] = data["state"]["reported"]["pumpsw"]
    WateringSysVars.WaterSysShadow["pumpdur"] = data["state"]["reported"]["pumpdur"]
    WateringSysVars.LightSysShadow["lightswitch"] = data["state"]["reported"]["lightswitch"]
    WateringSysVars.LightSysShadow["lightSwitchCmd"] = data["state"]["reported"]["lightSwitchCmd"]
    sem_cmd.release()
    print("Pump switch: " + WateringSysVars.WaterSysShadow["pumpsw"])
    print("Pump duration: " + WateringSysVars.WaterSysShadow["pumpdur"])
    print("Moisture: " + data["state"]["reported"]["moisture"])
    print("Water lvl: " + data["state"]["reported"]["waterlvl"])

def GetWaterSysData(): 
    while thread_signal:
        dataAddress = UDPServerSocket_water.recvfrom(WateringSysVars.bufferSize_wtr)
        sensorData = dataAddress[0]
        ESPAddress = dataAddress[1]
        print("Sensor data received - water: " + sensorData)
        #set water sensor variables
        sem_cmd.acquire()
        if WateringSysVars.WaterSysShadow["pumpsw"] == "1":
            sendToESP = "1" + WateringSysVars.WaterSysShadow["pumpdur"] + "0"
            WateringSysVars.WaterSysShadow["pumpsw"] = "0"
            WateringSysVars.WaterSysShadow["pumpdur"] = "000"
            sem_cmd.release()
            UDPServerSocket_water.sendto(sendToESP, ESPAddress)
        else:
            sem_cmd.release()    
        sem_water.acquire()
        WateringSysVars.WaterSysShadow["moisture"] = sensorData[0:4]
        WateringSysVars.WaterSysShadow["waterlvl"] = sensorData[4]
        WateringSysVars.WaterSysShadow["pumperr"] = sensorData[5]
        WateringSysVars.WaterSysShadow["pumpcmd"] = "1"
        sem_water.release()

def GetLightSysData():
    while thread_signal:
        dataAddress = UDPServerSocket_light.recvfrom(WateringSysVars.bufferSize_lgt)
        sensorData = dataAddress[0]
        ESPAddress = dataAddress[1]
        print("Sensor data received - light: " + sensorData)
        #set water sensor variables
        sem_cmd.acquire()
        if WateringSysVars.LightSysShadow["lightSwitchCmd"] == "1" or WateringSysVars.LightSysShadow["lightDimCmd"] == "1":
            if WateringSysVars.LightSysShadow["lightSwitchCmd"] == "1":
                sendToESP = "1"
            else:
                sendToESP = "0"
            if WateringSysVars.LightSysShadow["lightDimCmd"] == "1":
                sendToESP += WateringSysVars.LightSysShadow["dimmer"]
            else:
                sendToESP += "x"
            WateringSysVars.LightSysShadow["lightSwitchCmd"] = "0"
            WateringSysVars.WaterSysShadow["lightDimCmd"] = "0"
            sem_cmd.release()
            UDPServerSocket_water.sendto(sendToESP, ESPAddress)
        else:
            sem_cmd.release()    
        sem_light.acquire()
        WateringSysVars.LightSysShadow["vis"] = sensorData[0:4]
        WateringSysVars.LightSysShadow["ir"] = sensorData[4:8]
        WateringSysVars.LightSysShadow["uv"] = sensorData[8:12]
        sem_light.release()


#wps.InitializeAWSIoT()
#wps.SubscribeAWSIoT(ServiceCommands)

thread1 = threading.Thread(target=GetWaterSysData)
thread2 = threading.Thread(target=GetLightSysData)

thread1.start()
thread2.start()

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
try:
    while True:
        sem_cmd.acquire()
        sem_light.acquire()
        sem_water.acquire()
        wps.PublishAWSIoT()
        sem_cmd.release()
        sem_light.release()
        sem_water.release()
        sleep(1)
        print("Published to AWS")
except (KeyboardInterrupt, SystemExit):
    thread_signal = 0
    thread1.join()
    thread2.join()
    sys.exit(0)

    




