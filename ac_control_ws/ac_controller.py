import math
import time
import paho.mqtt.client as mqtt
import json

# MQTT settings
broker = "192.168.57.129"
port = 1883
topic_control_pmv = "ac/control/pmv"
topic_control_ppd = "ac/control/ppd"
topic_control_airTemperature = "ac/control/airTemperature"
topic_control_radiantTemperature = "ac/control/radiantTemperature"
topic_control_airVelocity = "ac/control/airVelocity"
topic_control_relativeHumidity = "ac/control/relativeHumidity"
topic_control_metabolicRate = "ac/control/metabolicRate"
topic_control_clothingLevel = "ac/control/clothingLevel"

# Initialize variables
clothingLevel = 0.0
metabolicRate = 0.0
airTemperature = 0.0
radiantTemperature = 0.0
airVelocity = 0.0
relativeHumidity = 0.0
wme = 0.0
pa = 0.0
pmv = 0.0
ppd = 0.0

# Previous values for comparison
prev_clothingLevel = clothingLevel
prev_metabolicRate = metabolicRate
prev_airTemperature = airTemperature
prev_radiantTemperature = radiantTemperature
prev_airVelocity = airVelocity
prev_relativeHumidity = relativeHumidity

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global clothingLevel, metabolicRate, airTemperature, radiantTemperature, airVelocity, relativeHumidity
    global prev_clothingLevel, prev_metabolicRate, prev_airTemperature, prev_radiantTemperature, prev_airVelocity, prev_relativeHumidity

    payload = json.loads(message.payload)
    if message.topic == topic_control_airTemperature:
        airTemperature = payload["ta"]
    elif message.topic == topic_control_radiantTemperature:
        radiantTemperature = payload["tr"]
    elif message.topic == topic_control_airVelocity:
        airVelocity = payload["vel"]
    elif message.topic == topic_control_relativeHumidity:
        relativeHumidity = payload["rh"]
    elif message.topic == topic_control_metabolicRate:
        metabolicRate = payload["met"]
    elif message.topic == topic_control_clothingLevel:
        clothingLevel = payload["clo"]

# Function to calculate PMV and PPD
def calculate_pmv_ppd(clo, met, wme, ta, tr, vel, rh, pa):

    def fnps(ta):
        return math.exp(16.6536 - 4030.183 / (ta + 235))

    if pa == 0:
        pa = rh * 10 * fnps(ta)
    
    icl = 0.155 * clo
    m = met * 58.15
    w = wme * 58.15
    mw = m - w
    
    if icl < 0.078:
        fcl = 1 + 1.29 * icl
    else:
        fcl = 1.05 + 0.645 * icl
    
    hcf = 12.1 * math.sqrt(vel)
    taa = ta + 273
    tra = tr + 273
    
    tcla = taa + (35.5 - ta) / (3.5 * (6.45 * icl + 0.1))
    
    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * math.pow(tra / 100, 4)
    
    xn = tcla / 100
    xf = xn
    eps = 0.00015
    n = 0
    
    while True:
        xf = (xf + xn) / 2
        hcn = 2.38 * abs(100 * xf - taa) ** 0.25
        hc = max(hcf, hcn)
        xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
        n += 1
        if n > 150 or abs(xn - xf) <= eps:
            break
    
    tcl = 100 * xn - 273
    
    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa)
    hl2 = 0
    if mw > 58.15:
        hl2 = 0.42 * (mw - 58.15)
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    hl4 = 0.0014 * m * (34 - ta)
    hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
    hl6 = fcl * hc * (tcl - ta)
    
    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100 - 95 * math.exp(-0.03353 * pmv ** 4 - 0.2179 * pmv ** 2)
    
    return pmv, ppd

# Setup MQTT client
client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port)
client.subscribe([
    (topic_control_airTemperature, 0), 
    (topic_control_radiantTemperature, 0),
    (topic_control_airVelocity, 0),
    (topic_control_relativeHumidity, 0),
    (topic_control_metabolicRate, 0),
    (topic_control_clothingLevel, 0)
])
client.loop_start()

try:
    while True:
        # Check if any parameter has changed
        if (clothingLevel != prev_clothingLevel or metabolicRate != prev_metabolicRate or 
            airTemperature != prev_airTemperature or radiantTemperature != prev_radiantTemperature or 
            airVelocity != prev_airVelocity or relativeHumidity != prev_relativeHumidity):

            if metabolicRate >= 1.0:
                vsg = airVelocity + 0.3 * (metabolicRate - 1)
            else:
                vsg = airVelocity
            #clodyn = clothingLevel * (0.6 + 0.4 / metabolicRate)
            
            # Calculate PMV and PPD
            pmv, ppd = calculate_pmv_ppd(
                clo=clothingLevel, met=metabolicRate, wme=wme, ta=airTemperature, 
                tr=radiantTemperature, vel=vsg, rh=relativeHumidity, pa=pa
            )

            # Ensure calculation is finished before publishing
            '''if pmv is not None and ppd is not None:
                client.publish(topic_control_pmv, json.dumps({"pmv": pmv}))
                client.publish(topic_control_ppd, json.dumps({"ppd": ppd}))'''

            # Update previous values
            prev_clothingLevel = clothingLevel
            prev_metabolicRate = metabolicRate
            prev_airTemperature = airTemperature
            prev_radiantTemperature = radiantTemperature
            prev_airVelocity = airVelocity
            prev_relativeHumidity = relativeHumidity

        if pmv is not None and ppd is not None:
                client.publish(topic_control_pmv, json.dumps({"pmv": pmv}))
                client.publish(topic_control_ppd, json.dumps({"ppd": ppd}))

        # Wait before next control update
        time.sleep(1)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
