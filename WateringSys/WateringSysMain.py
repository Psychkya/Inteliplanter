import WateringSysPubSub as wps
import WateringSysVars
import socket
import threading
import json
import sys
import time

sem_publish_AWS = threading.BoundedSemaphore(1)
sem_cmd_water = threading.BoundedSemaphore(1)
sem_cmd_light = threading.BoundedSemaphore(1)

#Bind sockets
UDPServerSocket_water = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket_water.bind((WateringSysVars.localIP, WateringSysVars.localPort_water))

UDPServerSocket_light = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket_light.bind((WateringSysVars.localIP, WateringSysVars.localPort_light))

def ServiceCommands(client, userdata, message):
    print("Recevied shadow")
    print(message.payload)    
    sem_cmd_water.acquire()  #lock the semaphore to update local vars
    sem_cmd_light.acquire()  #lock the semaphore to update local vars
    data = json.loads(message.payload)
    WateringSysVars.WaterSysShadow["pumpsw"] = data["state"]["reported"]["pumpsw"]
    WateringSysVars.WaterSysShadow["pumpdur"] = data["state"]["reported"]["pumpdur"]
    WateringSysVars.LightSysShadow["lightswitch"] = data["state"]["reported"]["lightswitch"]
    WateringSysVars.LightSysShadow["lightSwitchCmd"] = data["state"]["reported"]["lightSwitchCmd"]
    WateringSysVars.LightSysShadow["lightinit"] = data["state"]["reported"]["lightinit"] #Need to discuss (one time vs always)
    WateringSysVars.LightSysShadow["clicks"] = data["state"]["reported"]["clicks"]
    WateringSysVars.LightSysShadow["nextlstate"] = data["state"]["reported"]["nextlstate"]
    sem_cmd_water.release()
    sem_cmd_light.release()

def GetWaterSysData(): 
    while True:
        dataAddress = UDPServerSocket_water.recvfrom(WateringSysVars.bufferSize_wtr)
        sensorData = dataAddress[0]
        ESPAddress = dataAddress[1]
        print("Sensor data received - water: " + sensorData)
        sem_publish_AWS.acquire()
        WateringSysVars.WaterSysShadow["moisture"] = sensorData[0:4]
        WateringSysVars.WaterSysShadow["waterlvl"] = sensorData[4]
        WateringSysVars.WaterSysShadow["pumperr"] = sensorData[5]
        WateringSysVars.WaterSysShadow["pumpcmd"] = "1"
        #publish the current items to AWS
        wps.PublishAWSIoT()
        sem_publish_AWS.release()
        time.sleep(2) #sleep for 1 seconds for subscribe to get latest data
        sem_cmd_water.acquire() #lock the semaphore to process local vars
        if WateringSysVars.WaterSysShadow["pumpsw"] == "1":
            sendToESP = "1" + WateringSysVars.WaterSysShadow["pumpdur"] + "0"
            WateringSysVars.WaterSysShadow["pumpsw"] = "0"
            WateringSysVars.WaterSysShadow["pumpdur"] = "000"
            sem_cmd_water.release()
            UDPServerSocket_water.sendto(sendToESP, ESPAddress)
            #in case of a command operation publish processed info back to AWS
            sem_publish_AWS.acquire()
            wps.PublishAWSIoT()
            sem_publish_AWS.release()            
        else:
            sem_cmd_water.release()    
        #sem_water.acquire()
        #sem_water.release()

def GetLightSysData():
    while True:
        dataAddress = UDPServerSocket_light.recvfrom(WateringSysVars.bufferSize_lgt)
        sensorData = dataAddress[0]
        ESPAddress = dataAddress[1]
        print("Sensor data received - light: " + sensorData)
        sem_publish_AWS.acquire()
        WateringSysVars.LightSysShadow["vis"] = sensorData[0:4]
        WateringSysVars.LightSysShadow["ir"] = sensorData[4:8]
        WateringSysVars.LightSysShadow["uv"] = sensorData[8:12]
        wps.PublishAWSIoT()        
        sem_publish_AWS.release()
        time.sleep(2)
        sem_cmd_light.acquire()
        if WateringSysVars.LightSysShadow["lightSwitchCmd"] == "1" or WateringSysVars.LightSysShadow["lightDimCmd"] == "1":
            if WateringSysVars.LightSysShadow["lightSwitchCmd"] == "1":
                sendToESP = WateringSysVars.LightSysShadow["lightswitch"]
            else:
                sendToESP = "x"
            if WateringSysVars.LightSysShadow["lightDimCmd"] == "1":
                #sendToESP += WateringSysVars.LightSysShadow["nextlstate"]
                sendToESP += WateringSysVars.LightSysShadow["clicks"]
            else:
                sendToESP += "x"
            WateringSysVars.LightSysShadow["lightSwitchCmd"] = "0"
            WateringSysVars.WaterSysShadow["lightDimCmd"] = "0"
            sem_cmd_light.release()
            UDPServerSocket_water.sendto(sendToESP, ESPAddress)
            sem_publish_AWS.acquire()
            wps.PublishAWSIoT()
            sem_publish_AWS.release()            
        else:
            sem_cmd_light.release()    


wps.InitializeAWSIoT()
wps.SubscribeAWSIoT(ServiceCommands)

thread1 = threading.Thread(target=GetWaterSysData)
thread2 = threading.Thread(target=GetLightSysData)

thread1.setDaemon(True)
thread1.start()
thread2.setDaemon(True)
thread2.start()

try:
    while True:
        time.sleep(10000000)

except (KeyboardInterrupt, SystemExit):
    thread_signal = 0
    sem_publish_AWS.acquire()
    sem_cmd_light.acquire()
    sem_cmd_water.acquire()
    sem_publish_AWS.release()
    sem_cmd_light.release()
    sem_cmd_water.release()
    sys.exit(0)

    




