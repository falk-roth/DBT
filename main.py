#Netzwerk SMart Produktion - Projekt DBT1 Team NSP
#Versiom 1.0
#13.12.2023


#--------------------Libraries importieren-----------------------------------------

import machine
from machine import I2C, Pin
import sh1107
import bme680
from bme680 import *
import framebuf
import ujson
from umqtt.simple import MQTTClient
import socket
import _thread

#--------------------Variabeln definieren-------------------------------------------
#-----------------------------------------------------------------------------------
MQTT_TOPIC = "NSP Test"

#Konfiguration aus der Verwaltungsschale
configuration = get_configuration()

#Framebuffer Smiley 
buffer_good = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf8\x00\x00?\xfe\x00\x00\xff\xff\x80\x01\xff\xff\xc0\x03\xff\xff\xe0\x07\xff\xff\xf0\x07\xff\xff\xf0\x0f\xff\xff\xf8\x0f\xff\xff\xfc\x1f\x8f\xf8\xfc\x1f\x87\xf0|\x1f\x87\xf0|\x1f\x8f\xf8\xfc\x1f\xff\xff\xfc\x1f\xff\xff\xfc\x1f\xff\xff\xfc\x1f\xff\xff\xfc\x0f\xff\xff\xfc\x0f\x80\x00\xf8\x0f\x80\x00\xf8\x07\xc0\x01\xf0\x03\xe0\x03\xe0\x01\xfc\x1f\xc0\x00\xff\xff\x80\x00\x7f\xff\x00\x00\x1f\xfc\x00\x00\x01\x80\x00')
buffer_ok = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf0\x00\x00?\xfe\x00\x00\xff\xff\x00\x01\xff\xff\x80\x03\xff\xff\xc0\x07\xff\xff\xe0\x07\xff\xff\xf0\x0f\xff\xff\xf0\x0f\xdf\xfb\xf0\x0f\x8f\xf1\xf8\x1f\x87\xf0\xf8\x1f\x8f\xf1\xf8\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x0f\xff\xff\xf8\x0f\xff\xff\xf0\x0f\x9f\xf9\xf0\x07\xcf\xf3\xf0\x07\xe3\xc7\xe0\x03\xf8\x1f\xc0\x01\xff\xff\x80\x00\xff\xff\x00\x00?\xfc\x00\x00\x0f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00')
buffer_bad = bytearray (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xfc\x00\x00?\xff\x00\x00\x7f\xff\x80\x00\xff\xff\xc0\x01\xff\xff\xe0\x03\xff\xff\xf0\x03\xff\xff\xf8\x07\xff\xff\xf8\x07\xef\xfd\xf8\x0f\xc7\xf8\xfc\x0f\xc3\xf8|\x0f\xc7\xf8\xfc\x0f\xef\xff\xfc\x0f\xff\xff\xfc\x0f\xff\xff\xfc\x0f\xff\xff\xfc\x07\xfc\x0f\xf8\x07\xf1\xe3\xf8\x03\xe7\xf9\xf8\x03\xcf\xfc\xf0\x01\xff\xff\xe0\x00\xff\xff\xc0\x00\x7f\xff\x80\x00?\xff\x00\x00\x0f\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') 

#---------------------Funktionen definieren------------------------------------------
#------------------------------------------------------------------------------------


#-------------- 1. Sensordaten auslesen und auf OLED ausgeben------------------------

def bme_temperature(x,y):
    temperature = sensor.temperature
    oled.text("Temp: {:.2f} C".format(temperature), x, y)
    return temperature
    
def bme_humidity(x,y):
        humidity = sensor.humidity
        oled.text("Humidity: {:.2f}%".format(humidity), x, y)
        return humidity
    
def bme_pressure(x,y):
        pressure = sensor.pressure
        oled.text("Pressure: {:.2f} hPa".format(pressure), x, y)
        return pressure

def bme_altitude ():
    altitude = sensor.altitude(x)
    print (altitude)

#-----------------2. Daten über MQTT verschicken------------------------------------
    
def send_MQTT():
    if str(configuration)[3] == "1":
        temperature = bme_temperature(10,10)
        humidity = bme_humidity(10,10)
        pressure = bme_pressure(10,10)
    
    
        message = ujson.dumps({
            "Temp": temperature,
            "Humidity": humidity,
            "Pressure": pressure,
        })
    
        mqttClient.publish(MQTT_TOPIC, message)
    else:
        pass
    
#------------------3. Sensordaten bewerten--------------------------------------------
    
def temp_score():
    if 18 <= sensor.temperature <= 24:
        return 0
    elif 15 <= sensor.temperature < 18 or 24 < sensor.temperature <= 27:
        return 0.5
    elif sensor.temperature < 15 or sensor.temperature > 27:
        return 1
    else:
        return None 

def pres_score():
    if 30 <= sensor.pressure <= 50:
        return 0
    elif 20 <= sensor.pressure < 30 or 50 < sensor.pressure <= 60:
        return 0.5
    elif sensor.pressure < 20 or sensor.pressure > 60:
        return 1
    else:
        return None

def calculate_total_score():
    score_temp = temp_score() * 0.1
    score_pres = pres_score() * 0.1
    score_res = ((500000-sensor.gas)/500000) * 0.8

    if score_temp is not None and score_pres is not None:
        total_score = score_temp + score_pres + score_res
        return total_score
    else:
        return None

total_score = calculate_total_score()

def room_ambience (total_score):
    if str(configuration)[2] == "1":
        if 0 <= total_score < 0.34:
            fb = framebuf.FrameBuffer(buffer_good, 32, 29, framebuf.MONO_HLSB)
            oled.blit(fb, 90, 0)
            return "good"
        elif 0.34 <= total_score < 0.67:
            fb = framebuf.FrameBuffer(buffer_ok, 32, 28, framebuf.MONO_HLSB)
            oled.blit(fb, 90, 0)
            return "ok"
        elif 0.67 <= total_score <= 1:
            fb = framebuf.FrameBuffer(buffer_bad, 32, 31, framebuf.MONO_HLSB)
            oled.blit(fb, 90, 0)
            return "bad"
        else:
            return None
    else:
        return "---"



#------------------4. Daten über Webserver ausgeben--------------------------------------------

def web_bme():
    if str(configuration)[1] == "1":
        Data = {"Temperature": str(round(sensor.temperature, 2)), "Humidity": "---", "Pressure": "---"}
        return Data
    elif str(configuration)[1] == "2":
        Data = {"Temperature": str(round(sensor.temperature, 2)), "Humidity": str(round(sensor.humidity, 2)), "Pressure": "---"}
        return Data
    elif str(configuration)[1] == "3":
        Data = {"Temperature": str(round(sensor.temperature, 2)), "Humidity": str(round(sensor.humidity, 2)), "Pressure": str(round(sensor.humidity, 2))}
        return Data
    else:
        Data = {"Temperature": "Error", "Humidity": "Error", "Pressure": "Error"}
        return Data
        
def web_page():
  Data = web_bme()
  html = """<!DOCTYPE html>
  <html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="3">
  <title>Netzwerk Smart Production</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
  <link rel="icon" href="data:,">
  <style>
    html {font-family: Arial; display: inline-block; text-align: center;}
    p {  font-size: 1.2rem;}
    body {  margin: 0;}
    .topnav { overflow: hidden; background-color: #FFFFFF; color: white; font-size: 1.7rem; }
    .content { padding: 20px; }
    .card { background-color: white; box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5); }
    .cards { max-width: 700px; margin: 0 auto; display: grid; grid-gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .reading { font-size: 2.8rem; }
    .card.temperature { color: #990000; }
    .card.humidity { color: #008080; }
    .card.pressure { color: #CC9900; }
    .card.gas { color: #00008B; }
  </style>
</head>
<body>
  <div class="topnav">
    <img src="https://www.smartproduction.de/basisTheme/common/logo.png" alt="Logo" style="max-width: 100%; height: auto;">
  </div>
  <div class="content">
    <div class="cards">
      <div class="card temperature" style="color: #990000;">
        <h4><i class="fas fa-thermometer-half"></i> TEMPERATURE</h4><p><span class="reading"><span id="temp">""" + Data["Temperature"] + """</span> &deg;C</span></p>
      </div>
      <div class="card humidity" style="color: #008080;">
        <h4><i class="fas fa-tint"></i> HUMIDITY</h4><p><span class="reading"><span id="hum">""" + Data["Humidity"] + """</span> &percnt;</span></p>
      </div>
      <div class="card pressure" style="color: #CC9900;">
        <h4><i class="fas fa-angle-double-down"></i> PRESSURE</h4><p><span class="reading"><span id="pres">""" + Data["Pressure"] + """</span> hPa</span></p>
      </div>
      <div class="card gas" style="color: #00008B;">
        <h4><i class="fas fa-wind"></i> AIR QUALITY</h4><p><span class="reading"><span id="gas">""" + room_ambience(total_score) + """</span> </span></p>
      </div>
    </div>
  </div>
<img src="https://www.cemos.org/images/cemos_logo_text_rgb_zw-p-500.png" alt="Bild am unteren Ende" style="max-width: 200px; height: auto; display: block; margin: 10px auto 20px;">
</body>
</html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def Webserver():
    while True:
        if str(configuration)[4] == "1":
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
        else:
            pass

#------------------5. Hauptschleife - Abhängig von der Konfiguration in der Verwaltungsschale--------------------------------------------
        
def main_loop():
    while True:
        if str(configuration)[1] == "3":
            oled.sleep(False)
            oled.fill(0)
            oled.text ("CeMos", 0, 10, 1)
            bme_temperature(0, 40)
            oled.hline (0, 60, 128, 1)
            bme_humidity(0, 70)
            oled.hline (0, 90, 128, 1)
            bme_pressure(0, 100)
            room_ambience(total_score)
            oled.show()
            send_MQTT()
            time.sleep(3)
        elif str(configuration)[1] == "2":
            oled.sleep(False)
            oled.fill(0)
            oled.text ("CeMos", 0, 10, 1)
            bme_temperature(0, 50)
            oled.hline (0, 70, 128, 1)
            bme_humidity(0, 80)
            room_ambience(total_score)
            oled.show()
            send_MQTT()
            time.sleep(3)
        elif str(configuration)[1] == "1":
            oled.sleep(False)
            oled.fill(0)
            oled.text ("CeMos", 0, 10, 1)
            bme_temperature(0, 70)
            room_ambience(total_score)
            oled.show()
            send_MQTT()
            time.sleep(3)
        else:
            oled.sleep(False)
            oled.fill(0)
            oled.text ("Konfiguration nicht gefunden:", 0, 50, 1)
       
#------------------Starten der Hauptschleife + neuer Thread für den Webserver --------
#-------------------------------------------------------------------------------------
            
_thread.start_new_thread(Webserver, ())
main_loop()

    