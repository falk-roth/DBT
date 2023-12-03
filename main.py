import machine
from machine import I2C, Pin
import sh1107
import bme680
from bme680 import *
import framebuf
import ujson
from umqtt.simple import MQTTClient
import usocket as socket

x = 1013.25
MQTT_TOPIC = "NSP Test"

def bme_temperature():
    temperature = sensor.temperature
    oled.text("Temp: {:.2f} C".format(temperature), 0, 40)
    return temperature
    
def bme_humidity():    
    humidity = sensor.humidity
    oled.text("Humidity: {:.2f}%".format(humidity), 0, 70)
    return humidity
    
def bme_pressure():
    pressure = sensor.pressure
    oled.text("Pressure: {:.2f} hPa".format(pressure), 0, 100)
    return pressure

def bme_altitude ():
    altitude = sensor.altitude(x)
    print (altitude)

buffer_positive = bytearray(b'\x00\x0f\xf0\x00\x00\x7f\xfe\x00\x01\xff\xff\x80\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc?\xff\xff\xfc\x7f\xff\xff\xfe\x7f\x9f\xf9\xfe\x7f\x9f\xf1\xfe\xff\x9f\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc\x00\x00\x7f~\x00\x00~~\x00\x00~\x7f\x00\x00\xfe?\x00\x01\xfc?\x80\x01\xfc\x1f\xe0\x07\xf8\x0f\xf8\x1f\xf0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x00\x7f\xfe\x00\x00\x0f\xf0\x00')

def evaluate_room_ambience():
    fb = framebuf.FrameBuffer(buffer_positive, 32, 32, framebuf.MONO_HLSB)
    oled.blit(fb, 90, 0)

def send_MQTT():
    temperature = bme_temperature()
    humidity = bme_humidity()
    pressure = bme_pressure()
    
    
    message = ujson.dumps({
        "Temp": temperature,
        "Humidity": humidity,
        "Pressure": pressure,
    })
    
    mqttClient.publish(MQTT_TOPIC, message)
    
def web_page():

  html = """<html><head><title>Netzwerk Smart Production</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Trebuchet MS", Arial;}
  table { border-collapse: collapse; margin-left:auto; margin-right:auto; }
  th { padding: 12px; background-color: #0043af; color: white; }
  tr { border: 1px solid #ddd; padding: 12px; }
  tr:hover { background-color: #00FF00; }
  td { border: none; padding: 12px; }
  .sensor { color:white; font-weight: bold; background-color: #bcbcbc; padding: 1px;
  </style></head><body><h1>Netzwerk Smart Production</h1>
  <table><tr><th>MEASUREMENT</th><th>VALUE</th></tr>
  <tr><td>Temp. Celsius</td><td><span class="sensor">""" + str(round(sensor.temperature, 2)) + """ C</span></td></tr>
  <tr><td>Temp. Fahrenheit</td><td><span class="sensor">""" + str(round((sensor.temperature) * (9/5) + 32, 2))  + """ F</span></td></tr>
  <tr><td>Pressure</td><td><span class="sensor">""" + str(round(sensor.pressure, 2)) + """ hPa</span></td></tr>
  <tr><td>Humidity</td><td><span class="sensor">""" + str(round(sensor.humidity, 2)) + """ %</span></td></tr>
  <tr><td>Gas</td><td><span class="sensor">""" + str(round(sensor.gas/1000, 2)) + """ KOhms</span></td></tr></body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def Webserver():
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')

while True:
    oled.sleep(False)
    oled.fill(0)
    oled.text ("BME 680:", 0, 10, 1)
    bme_temperature()
    oled.hline (0, 60, 128, 1)
    bme_humidity()
    oled.hline (0, 90, 128, 1)
    bme_pressure()
    evaluate_room_ambience()
    oled.show()
    send_MQTT()
    #Webserver()
    time.sleep(3)
    
    






print (sensor.temperature)