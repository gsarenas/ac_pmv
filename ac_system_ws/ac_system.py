import time
import paho.mqtt.client as mqtt
import json

# MQTT settings
broker = "192.168.57.129"
port = 1883
topic_control_airTemperature = "ac/control/airTemperature"
topic_control_pmv = "ac/control/pmv"
topic_control_enableFollower = "ac/control/enableFollower"
topic_system_airTemperatureFix = "ac/system/airTemperatureFix"

# Initialize variables
airTemp = 0.0
enFollower = False

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global airTemperature, pmv, enFollower

    payload = json.loads(message.payload)
    if message.topic == topic_control_airTemperature:
        airTemperature = payload["ta"]
    elif message.topic == topic_control_pmv:
        pmv = payload["pmv"]
    elif message.topic == topic_control_enableFollower:
        enFollower = payload["enFollower"]

# Setup MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port)
client.subscribe([
    (topic_control_airTemperature, 2),
    (topic_control_pmv, 2),
    (topic_control_enableFollower, 2),
])
client.loop_start()

try:
    while True:
        if enFollower:
            if pmv < -0.05 or pmv > 0.05:
                if pmv < -0.05:
                    airTemperature += 0.5
                elif pmv > 0.05:
                    airTemperature -= 0.5

                # Publish the fixed air temperature
                client.publish(topic_system_airTemperatureFix, json.dumps({"tafix": airTemperature}))
                print(f"Published temperature fix: {airTemperature}")

        # Wait before next control update
        time.sleep(5)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
