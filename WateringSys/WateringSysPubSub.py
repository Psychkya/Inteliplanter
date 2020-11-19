from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import random
import subprocess
import WateringSysVars


def InitializeAWSIoT():
    # Configure logging
    logging.info("Configuring and connecting...")
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    global myAWSIoTMQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(WateringSysVars.clientId)
    myAWSIoTMQTTClient.configureEndpoint(WateringSysVars.host, WateringSysVars.port)
    myAWSIoTMQTTClient.configureCredentials(WateringSysVars.rootCAPath, WateringSysVars.privateKeyPath, WateringSysVars.certificatePath)    
    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()

#Subscribe
def SubscribeAWSIoT(var):
    myAWSIoTMQTTClient.subscribe(WateringSysVars.topic_sub, 1, var)
    time.sleep(5)

#Publish
def  PublishAWSIoT():
    JSONPayload = '{"state": {"reported": {"moisture":"' + WateringSysVars.WaterSysShadow["moisture"] + \
    '","waterlvl":"' + WateringSysVars.WaterSysShadow["waterlvl"] + \
    '", "pumperr":"' + WateringSysVars.WaterSysShadow["pumperr"] + '"} }}'
    myAWSIoTMQTTClient.publish(WateringSysVars.topic_pub, JSONPayload, 1)    

