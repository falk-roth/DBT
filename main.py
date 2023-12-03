import machine
from machine import I2C, Pin
#import ssd1306
import sh1107
import bme680
from bme680 import *
import framebuf

# OLED Display initialisieren
i2c_oled = I2C(0, scl=Pin(22), sda=Pin(21))

oled = sh1107.SH1107_I2C(128, 128, i2c_oled, address = 0x3c, rotate=0)

#oled = ssd1306.SSD1306_I2C(128, 128, i2c_oled, 0x3c)
oled.sleep(False)
oled.fill(0)
oled.text ("BME 680:", 0, 10, 1)


i2c_BME = I2C(0,scl=Pin(22), sda=Pin(21))

sensor = BME680_I2C(i2c=i2c_BME, address = 0x77)

temperature = sensor.temperature
humidity = sensor.humidity
pressure = sensor.pressure


buffer = bytearray(b'\x00\x0f\xf0\x00\x00\x7f\xfe\x00\x01\xff\xff\x80\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc?\xff\xff\xfc\x7f\xff\xff\xfe\x7f\x9f\xf9\xfe\x7f\x9f\xf1\xfe\xff\x9f\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc\x00\x00\x7f~\x00\x00~~\x00\x00~\x7f\x00\x00\xfe?\x00\x01\xfc?\x80\x01\xfc\x1f\xe0\x07\xf8\x0f\xf8\x1f\xf0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x00\x7f\xfe\x00\x00\x0f\xf0\x00')
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)

oled.blit(fb, 90, 0)


oled.text("Temp: {:.2f} C".format(temperature), 0, 40)
oled.hline (0, 60, 128, 1)
oled.text("Humidity: {:.2f}%".format(humidity), 0, 70)
oled.hline (0, 90, 128, 1)
oled.text("Pressure: {:.2f} hPa".format(pressure), 0, 100)
oled.show() 

print (sensor.temperature)