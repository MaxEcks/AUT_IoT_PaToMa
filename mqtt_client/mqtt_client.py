import paho.mqtt.client as mqtt
from database.database import DatabaseConnector
import json
from datetime import date

# MQTT Server Configuration
broker = "158.180.44.197"
port = 1883
topic = "iot1/teaching_factory/#"
payload = "on"

# Topic definitions
recipe = "iot1/teaching_factory/recipe"
temperature = "iot1/teaching_factory/temperature"
dispenser_red = "iot1/teaching_factory/dispenser_red"
dispenser_blue = "iot1/teaching_factory/dispenser_blue"
dispenser_green = "iot1/teaching_factory/dispenser_green"
scale_final_weight = "iot1/teaching_factory/scale/final_weight"
drop_oscillation = "iot1/teaching_factory/drop_oscillation"
ground_truth = "iot1/teaching_factory/ground_truth"

def table_name_from_topic(topic: str) -> str:
    if topic == recipe:
        return "recipe"
    elif topic == temperature:
        return "temperature"
    elif topic == dispenser_red:
        return "dispenser_red"
    elif topic == dispenser_blue:
        return "dispenser_blue"
    elif topic == dispenser_green:
        return "dispenser_green"
    elif topic == scale_final_weight:
        return "final_weight"
    elif topic == drop_oscillation:
        return "drop_oscillation"
    elif topic == ground_truth:
        return "ground_truth"
    else:
        raise ValueError(f"Unknown topic: {topic}")

"""
class Recipe:
    def __init__ (self, id : str, creation_date : date, color_levels_grams : dict) -> None:
        pass
    pass
class Temperature:
    def __init__ (self, dispenser : str, time, temperature_C : float) -> None:
        pass
    pass
class DispenserRed:
    def __init__ (self, dispenser : str, bottle : int, time, fill_level_grams : float, recipe : int, vibration_index : float) -> None:
        pass
    pass
class DispenserBlue:
    def __init__ (self, dispenser : str, bottle : int, time, fill_level_grams : float, recipe : int, vibration_index : float) -> None:
        pass
    pass
class DispenserGreen:
    def __init__ (self, dispenser : str, bottle : int, time, fill_level_grams : float, recipe : int, vibration_index : float) -> None:
        pass
    pass
class ScaleFinalWeight:
    def __init__ (self, bottle : int, time, final_weight : float) -> None:
        pass
    pass
class DropOscillation:
    def __init__ (self, bottle : int, drop_oscillation : list) -> None:
        pass
    pass
class GroundTruth:
    def __init__ (self, bottle : int, is_cracked : bool) -> None:
        pass
    pass
"""

# create function for callback
def on_message(client, userdata, message):
    # write data in database.json
    db = DatabaseConnector()
    try:
        payload_raw = message.payload.decode()
        try:
            payload = json.loads(payload_raw)
        except json.JSONDecodeError:
            payload = {"raw": payload_raw}  # Fallback
        
        table_name = table_name_from_topic(message.topic)
        table = db.get_table(table_name)
        table.insert({
            "topic": message.topic,
            "payload": payload
        })
        print(f"Data inserted into table \"{table_name}\"")

    except Exception as e:
        print(f"Error inserting data into database!")

"""
    topic_parts = message.topic.split('/')
    topic_key = topic_parts[-1]

    payload = message.payload.decode()

    try:
        table = db.table(topic_key)
        table.insert({"topic": message.topic, "payload": payload})
        print(f"Data inserted into table -> Topic: {topic_key}")
    except Exception as e:
        print(f"Error inserting data into table")

    # console output
    #print("message received:")
    #print("message: ", message.payload.decode())
    # print("\n")
"""
# create client object
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set("bobm", "letmein")              

# assign function to callback
mqttc.on_message = on_message                          

# establish connection
mqttc.connect(broker,port)                                 

# subscribe
mqttc.subscribe(topic, qos=0)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
#mqttc.loop_forever()

while True:
    mqttc.loop(0.5)