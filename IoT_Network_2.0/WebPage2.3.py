from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_mqtt import Mqtt
import time

#MQTT definining:
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '192.168.100.2'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'subclient'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)


global lastSN #value of last message with SN
lastSN=0
global sensors #list of dicts for the sensor readings
sensors = []
global prev_num_of_sensors #used for checking if new sensors have appeared and need to be displayed on web page

#function checking for sensors which are no longer transmitting:
def check_for_expired():
	global sensors
	for sensor in sensors:
		if(time.time()-sensor["last_seen"]>20):
			sensors.remove(sensor)
#Called when connection with mqtt broker is established:
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
	mqtt.subscribe("readings/#", 0)
	print("Connected to MQTT broker")

#on_message() is called when a new mqtt message is recieved. It stores the data recieved into sensors[]
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
	data = dict(
		topic=message.topic,
		payload=message.payload.decode()
	)
	print(data['payload'])
	
	global sensors
	if ("SN" in data['payload']):#saves the SN number to keep check of sensor staions transmitting
		global lastSN
		lastSN = int(data['payload'][3])
		SN_exists = False

		for i in range(len(sensors)):
			if (sensors[i]["SN"] == lastSN):
				SN_exists = True
				break
		if (SN_exists == False):#if new station is transmitting a list element is created for it:
			sensors.append({
				"SN":lastSN,
				"last_seen":int(time.time()),
				"Temperature":0.0,
				"Humidity":0.0,
				"Ambient_light":0.0
				})
		else:
			sensors[i]["last_seen"] = int(time.time())
	#According to the message topic, a value is saved to corresponding list item
	elif (data['topic'] == "readings/temperature" and lastSN != 0):
		for i in range(len(sensors)):
			if (sensors[i]["SN"] == int(data['payload'][0])):
				break
		sensors[i]["Temperature"] = float(data['payload'][3:])
		
	elif (data['topic'] == "readings/humidity" and lastSN != 0):
		for i in range(len(sensors)):
			if (sensors[i]["SN"] == int(data['payload'][0])):
				break
		sensors[i]["Humidity"] = float(data['payload'][3:])
		
	elif (data['topic'] == "readings/light" and lastSN != 0):
		for i in range(len(sensors)):
			if (sensors[i]["SN"] == int(data['payload'][0])):
				break
		sensors[i]["Ambient_light"] = float(data['payload'][3:])

#Flask functions defined:

#Send the SNs of the connected stations (done once per page reload)
@app.route("/SNumber", methods = ['POST'])
def SNumber():
	return jsonify(SN = request.form["SN"], result = sensors[int(request.form["SN"])]["SN"])

#Updating WebPage sensor measurements:
@app.route("/temperature", methods = ['POST'])
def temperature():
	return jsonify(SN = request.form["SN"], result = sensors[int(request.form["SN"])]["Temperature"])

@app.route("/humidity", methods = ['POST'])
def humidity():
	return jsonify(SN = request.form["SN"], result = sensors[int(request.form["SN"])]["Humidity"])

@app.route("/ambient_light", methods = ['POST'])
def ambient_light():
	return jsonify(SN = request.form["SN"], result = sensors[int(request.form["SN"])]["Ambient_light"])

@app.route("/check_for_changes", methods =['GET'])
def check_for_changes():
	global prev_num_of_sensors
	check_for_expired()
	if(len(sensors) != prev_num_of_sensors):
		prev_num_of_sensors = len(sensors)
		return jsonify(result = 1)
	return jsonify(result = 0)

##index:
@app.route("/")
def index():
	return render_template("index.html", num_of_sensors = len(sensors))
	#^renders the html with number of sensors(if number is 0, no sensors detected message should be shown)^
time.sleep(2)
prev_num_of_sensors = len(sensors)
if (__name__ == "__main__"):
	app.run(host='0.0.0.0')

#######################################################
#
#Sensors is list with a dict for each station
#-example:
#sensors = [{}, {}, ..., {}]
#		    "SN":1
#	  "last_seen":time.time() - called whenever a message is recieved from given SN
#  "Temperature":*temperature reading*
#	  "Humidity":*humidity reading*
#"Ambient_light":*ambient_light reading*
#
#Whenever a message with an unrecorded SN is recieved a new element is appendend
#
#######################################################
