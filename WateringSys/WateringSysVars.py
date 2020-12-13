#ESP vars
localIP = "0.0.0.0"
localPort_water = 20001
localPort_light = 20002
bufferSize_wtr = 1024
bufferSize_lgt = 1024

#AWS vars
host = "a1fp1sv7eionud-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "../../certs/AmazonRootCA1.pem"
certificatePath = "../../certs/57c8e4bd23-certificate.pem.crt"
privateKeyPath = "../../certs/57c8e4bd23-private.pem.key"
port = 8883
clientId = "WateringSys"
topic_pub = "$aws/things/PlantSoilWater/shadow/update"
topic_sub = "$aws/things/PlantSoilWater/shadow/update"
publish_water_AWS = 0
publish_light_AWS = 0
plantShadow = {"id": "ip11111"}
WaterSysShadow = {
    "moisture": "", #moisture level
    "waterlvl": "", #water level
    "pumpsw": "0", #turn pump on or off; off=0, on=1
    "pumpdur": "10", #how long should pump be on in seconds
    "pumperr": "0", #Any error encountered during pump operations
    "waterUnlock": "1" #Indicate lambda it can send a pump on operation
}
LightSysShadow = {
    "vis": "", #visible light
    "ir": "", #ir
    "uv": "", #uv index
    "lightDimCmd": "0", #dictates whether a dimmer command was sent
    "dimmerCurrent": "", #dimmer value
    "dimmerPrev": "", #dimmer value
    "lightSwitchCmd": "0", #dictates whether a light command was sent
    "lightswitch": "1", #Any error encountered during pump operations
    "lightinit":"0",
    "clicks":"0",
    "nextlstate":"x",
    "lightUnlock": "1"
}