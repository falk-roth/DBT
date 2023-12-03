#libraries importieren

import upip
upip.install("micropython-bme680")
import bme680
import network
import time
import ssd1306
import ujson
import requests
import machine
from machine import I2C, Pin
from umqtt.simple import MQTTClient

#WLAN Verbindung herstellen

wifi_ssid = "DEIN_WIFI_SSID"
wifi_password = "DEIN_WIFI_PASSWORT"

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Verbinde mit WLAN...", end= "")
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            pass

    print("Erfolgreich mit WLAN verbunden")


#Verbindung zu MQTT Client aufbauen

MQTT_CLIENT_ID = "Deine_Client_ID"
MQTT_BROKER = "broker.hivemq.com"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_TOPIC = "Dein_Topic"

def connect_to_MQTT():
    print("Connecting to MQTT server... ", end="")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print("Erfolgreich mit MQTT-Broker verbunden")


# BME680 Sensor initialisieren

i2c_BME = I2C(0,scl=Pin(5), sda=Pin(4))

sensor = bme680.BME680(i2c=i2c_BME)

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)

sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# OLED Display initialisieren
WIDTH = 128
HEIGHT = 64
i2c_oled = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c_oled)

#Eindeutige ID in EEprom speichern -> Nur einmalig eigentlich nicht Teil des Programms
eeprom_adress = 0x50
i2c_eeprom = I2C(0, scl=Pin(27), sda=Pin(26))

def write_id_in_eeprom (address, id):
    i2c.writeto_mem(eeprom_address, address, id)

device_id = "Eindeutige ID des ESP32/Würfels"
write_id_in_eeprom(0, device_id)

#Eindeutige ID aus EEPROM auslesen
def read_data_from_eeprom(address, length):
    return i2c.readfrom_mem(eeprom_address, address, length)




#Konfiguration über REST auslesen
url = "http://deine-REST-API-URL/device/{}".format(device_id)

def get_configuration(device_id):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            aas = response.json()
            id_config = aas.get("ID")
            return id_config
        else:
            print("Kein gültiger ID-Wert.")

    except Exception as e:
        # Fang Ausnahmen ab, z.B. Netzwerkfehler
        print(f"Fehler beim Auslesen der ID: {str(e)}")

#Variabeln zum Speichern der vorherigen Messwerte

prev_temperature = None
prev_humidity = None
prev_pressure = None
prev_gas = None
prev_values = (prev_temperature,prev_humidity,prev_pressure,prev_gas)

#Sensordaten auslesen
def measure_sensor_data():
    temperature = bme.temperature
    humidity = bme.humidity
    pressure = bme.pressure
    gas = bme.gas
    values = (temperature,humidity,pressure,gas)
    return values, temperature, humidity, pressure, gas

#Sensordatenn auf Display ausgeben
def display_sensor_data():
    global prev_temperature, prev_humidity, prev_pressure, prev_gas
    global prev_values

    values, temperature, humidity, pressure, gas = measure_sensor_data()
    id_confiq = get_configuration()


    if values != prev_values:
        if id_confiq == 5:
            oled.fill(0)
            oled.text("Temp: {:.2f} C".format(temperature), 0, 0)
            oled.text("Humidity: {:.2f}%".format(humidity), 0, 20)
            oled.text("Pressure: {:.2f} hPa".format(pressure), 0, 40)
            oled.show()
            prev_temperature = temperature
            prev_humidity = humidity
            prev_pressure = pressure
            prev_gas = gas
            prev_values = values

        elif id_confiq == 3:
            oled.fill(0)
            oled.text("Temp: {:.2f} C".format(temperature), 0, 0)
            oled.text("Humidity: {:.2f}%".format(humidity), 0, 20)
            oled.show()
            prev_temperature = temperature
            prev_humidity = humidity
        else:
            oled.text ("Konfiguration nicht gefunden")

# Daten per MQTT publishen - muss noch an confiq angepasst werden
def send_MQTT():
    values, temperature, humidity, pressure, gas = measure_sensor_data()

    message = ujson.dumps({
        "temp": temperature,
        "Humidity": humidity,
        "Pressure": pressure,
        "Gas": gas,
    })
    client.publish(MQTT_TOPIC,message)

#Luftqualität bewerten
def evaluate_data():
    values, temperature, humidity, pressure, gas = measure_sensor_data()
    if temperature >= 20 and humidity <=40:
        display_happy_smiley()
    else:
        display_sad_smiley()

#Smiley anzeigen

def display_happy_smiley():
    smiley_coordinates = [
        (22, 55), (23, 56), (24, 57), (25, 57), (26, 57), (27, 57), (28, 57), (29, 57), (30, 57), (31, 57), (32, 57),
        (33, 57),
        (24, 56), (25, 56), (26, 56), (27, 56), (28, 56), (29, 56), (30, 56), (31, 56), (32, 56), (33, 56),
        (25, 52), (26, 52), (25, 51), (26, 51), (31, 52), (30, 52), (31, 51), (30, 51),
        (22, 56), (23, 57), (20, 54), (20, 53), (21, 54), (21, 55), (23, 57), (31, 55),
    ]
    for x, y in smiley_coordinates:
        oled.pixel(x, y, 1)
    oled.show()


def display_sad_smiley():
    smiley_coordinates = [
        (22, 55), (23, 56), (24, 57), (25, 57), (26, 57), (27, 57), (28, 57), (29, 57), (30, 57), (31, 57), (32, 57),
        (33, 57),
        (24, 56), (25, 56), (26, 56), (27, 56), (28, 56), (29, 56), (30, 56), (31, 56), (32, 56), (33, 56),
        (25, 52), (26, 52), (25, 51), (26, 51), (31, 52), (30, 52), (31, 51), (30, 51),
        (22, 56), (23, 57), (20, 54), (20, 53), (21, 54), (21, 55), (23, 57), (31, 55),
    ]
    for x, y in smiley_coordinates:
        oled.pixel(x, y, 1)
    oled.show()



# Programm Start:

#1. WLAN verbinden:

connect_to_wifi(wifi_ssid, wifi_password)

#2. MQTT verbinden:
connect_to_MQTT()

#3. Konfiguration abfragen:
device_id = read_data_from_eeprom(0, len(device_id))
get_configuration(device_id)

#Hauptschleife:

while True:
    measure_sensor_data()
    display_sensor_data()
    evaluate_data()
    send_MQTT()
    # Wartezeit zwischen den Messungen (in Sekunden)
    time.sleep(2)
