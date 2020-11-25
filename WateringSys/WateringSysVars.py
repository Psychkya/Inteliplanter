#ESP vars
localIP = "0.0.0.0"
localPort = 20001
bufferSize = 1024

#AWS vars
host = "a1fp1sv7eionud-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "../../certs/AmazonRootCA1.pem"
certificatePath = "../../certs/57c8e4bd23-certificate.pem.crt"
privateKeyPath = "../../certs/57c8e4bd23-private.pem.key"
port = 8883
clientId = "WateringSys"
topic_pub = "$aws/things/PlantSoilWater/shadow/update"
topic_sub = "$aws/things/PlantSoilWater/shadow/update"
WaterSysShadow = {
    "moisture": "", #moisture level
    "waterlvl": "", #water level
    "pumpsw": "0", #turn pump on or off; off=0, on=1
    "pumpdur": "10", #how long should pump be on in seconds
    "pumperr": "0", #Any error encountered during pump operations
    "pumpcmd" : "1" #Indicate lambda it can send a pump on operation
}