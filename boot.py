# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import machine 
import network
import time
import ubinascii

from umqtt.simple import MQTTClient  # The MQTT Client Library 


WLAN_SSID = "S23 von Falk"
WLAN_PW = "1224512345"

MQTT_BROKER = "mq.jreichwald.de"
MQTT_USERNAME = "dbt"
MQTT_PW = "dbt" 


"""
Connect to WLAN (enter SSID and password!)
""" 

station = network.WLAN(network.STA_IF)
station.active(True) 
wlan_mac = station.config('mac')
print("WLAN MAC Adress: " + ubinascii.hexlify(wlan_mac).decode())

station.connect(WLAN_SSID, WLAN_PW)
print("Connecting ...")

while not station.isconnected():
    print(".")
    time.sleep(1)
    
print("Connected, my IP is " + str(station.ifconfig()[0]))

"""
Connect to MQTT broker
"""

mqttClient = MQTTClient("NSP", MQTT_BROKER, 1883, MQTT_USERNAME, MQTT_PW, keepalive=60)
