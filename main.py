import machine
from machine import I2C, Pin
#import ssd1306
import sh1107
import bme680
from bme680 import *

# OLED Display initialisieren
i2c_oled = I2C(0, scl=Pin(22), sda=Pin(21))

oled = sh1107.SH1107_I2C(128, 128, i2c_oled, address = 0x3c, rotate=0)

#oled = ssd1306.SSD1306_I2C(128, 128, i2c_oled, 0x3c)
oled.sleep(False)
oled.fill(0)
oled.text ("Scheiss Joel", 10, 10, 1)
oled.text ("Super scheisse", 10, 40, 1)

i2c_BME = I2C(0,scl=Pin(22), sda=Pin(21))

sensor = BME680_I2C(i2c=i2c_BME, address = 0x77)

temperature = sensor.temperature
humidity = sensor.humidity
pressure = sensor.pressure

oled.text("Temp: {:.2f} C".format(temperature), 0, 60)
oled.text("Humidity: {:.2f}%".format(humidity), 0, 70)
oled.text("Pressure: {:.2f} hPa".format(pressure), 0, 80)
oled.show()

message = ujson.dumps({
        "temp": temperature,
        "Humidity": humidity,
        "Pressure": pressure,
    })
    client.publish(MQTT_TOPIC,message)

print (sensor.temperature)