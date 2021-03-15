import paho.mqtt.client as mqtt
import serial
import time

#MQTT client setup:
mqttBroker = "192.168.100.2"
client = mqtt.Client("pipub")
client.connect(mqttBroker)

#Serial connection properties:
ser = serial.Serial(
    port = '/dev/ttyS0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

lastSN = "0"#Variable for Station Number(0 = SN not read => incoming data invlaid)


#Loop for reading from serial and publishing to MQTT:
while True:
    #Read from Serial and convert binary data to string:
    ZBdata = str(ser.readline().rstrip())
    ZBdata = ZBdata[2:-1]#removes b''
    print(ZBdata)

##Publishing all data to a common "all" topic:
#    client.publish("All", ZBdata)
#    print ("Published " + ZBdata + " to \"All\"")

#Check what data is being sent and publish it to a respective MQTT topic:
    if ("SN" in ZBdata):#Checks if the line contains SN(Station Number) and saves it to a variable
        lastSN = ZBdata[3]
        client.publish("readings", ZBdata)
    #if T is present => the value refers to temperature and is published to topic readings/temperature:
    elif ("T" in ZBdata):
        client.publish("readings/temperature", lastSN + ": " + ZBdata[3:])
        print("Published " + lastSN + ": " + ZBdata[3:] + " to \"readings/temperature\"")
    #if H is present => the value refers to humidity and is published to topic readings/humidity:
    elif ("H" in ZBdata):
        client.publish("readings/humidity", lastSN + ": " + ZBdata[3:])
        print("Published " + lastSN + ": " + ZBdata[3:] + " to \"readings/humidity\"")
    #if L is present => the value refers to ambient light and is published to topic readings/light:
    elif ("L" in ZBdata):
        client.publish("readings/light", lastSN + ": " + ZBdata[3:])
        print("Published " + lastSN + ": " + ZBdata[3:] + " to \"readings/light\"\n")        

    time.sleep(0.25)