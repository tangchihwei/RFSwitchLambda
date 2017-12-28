import urllib2
import os
import json
import uuid

# Class to define a home device that to be controlled by Alexa. eg. Lamp
class AlexaHomeApp:
    def __init__(self, applianceId, name, id):
        self.endpointId = applianceId
        self.friendlyName = name
        self.manufacturerName = 'Tang'
        self.displayCategories = ['SWITCH']
        self.cookie = {
            "extraDetail1": "optionalDetailForSkillAdapterToReferenceThisDevice",
            "extraDetail2": "There can be multiple entries",
            "extraDetail3": "but they should only be used for reference purposes",
            "extraDetail4": "This is not a suitable place to maintain current device state"

        }
        self.capabilities = [
        {             
                "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [
                    { "name": "powerState" }
                ],
            "proactivelyReported": True,
            "retrievable": True
            }
        },
        {
                "type": "AlexaInterface",
                "interface": "Alexa.EndpointHealth",
                "version": "3",
                "properties": {
                "supported":[
                    { "name":"connectivity" }
                ],
            "proactivelyReported": True,
            "retrievable": True
                }
        },
        {
                "type": "AlexaInterface",
                "interface": "Alexa",
                "version": "3"
        }
    ]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

SAMPLE_APPLIANCES = [
    {
        "applianceId": "endpoint-001",
        "manufacturerName": "Sample Manufacturer",
        "modelName": "Smart Switch",
        "version": "1",
        "friendlyName": "Switch",
        "friendlyDescription": "001 Switch that can only be turned on/off",
        "isReachable": True,
        "actions": [
            "turnOn",
            "turnOff"
        ],
        "additionalApplianceDetails": {
            "detail1": "For simplicity, this is the only appliance",
            "detail2": "that has some values in the additionalApplianceDetails"
        }
    }
]

# The function that Lambad will call to handle any events.
def lambda_handler(event, context):
    eventname = {}
    eventname = event['directive']['header']['namespace']
    if eventname == 'Alexa.Discovery':
        return handleDiscovery()
    elif eventname == 'Alexa.ConnectedHome.Control':
        return handleControl(event) 

# bigLightOnly = AlexaHomeApp("only1", "light only", "light1")
# smallLightOnly = AlexaHomeApp("only2", "small only", "light2")
# deskLightOnly = AlexaHomeApp("only3", "desk only", "light3")
# windowLightOnly = AlexaHomeApp("only4", "window only", "light4")
bigLight = AlexaHomeApp("endpoint-001", "Switch1", "light1")
# smallLight = AlexaHomeApp("light2", "small light", "light2")
# deskLight = AlexaHomeApp("light3", "desk light", "light3")
# windowLight = AlexaHomeApp("light4", "window light", "light4")
# allLights = AlexaHomeApp("light1234", "all the lights", "light1234")

base_url = os.environ['BASE_URL']
RF1_ON = os.environ['RF1_ON']
RF1_OFF = os.environ['RF1_OFF']
RF2_ON = os.environ['RF2_ON']
RF2_OFF = os.environ['RF2_OFF']
RF3_ON = os.environ['RF3_ON']
RF3_OFF = os.environ['RF3_OFF']
RF4_ON = os.environ['RF4_ON']
RF4_OFF = os.environ['RF4_OFF']
RF_ON = "on"
RF_OFF = "off"

LIGHT1 = {RF_ON: RF1_ON, RF_OFF: RF1_OFF}
LIGHT2 = {RF_ON: RF2_ON, RF_OFF: RF2_OFF}
LIGHT3 = {RF_ON: RF3_ON, RF_OFF: RF3_OFF}
LIGHT4 = {RF_ON: RF4_ON, RF_OFF: RF4_OFF}
RF_MAP = {"light1": LIGHT1,
          "light2": LIGHT2,
          "light3": LIGHT3,
          "light4": LIGHT4, }

def get_uuid():
    return str(uuid.uuid4())

def get_display_categories_from_v2_appliance(appliance):
    model_name = appliance["modelName"]
    if model_name == "Smart Switch": displayCategories = ["SWITCH"]
    elif model_name == "Smart Light": displayCategories = ["LIGHT"]
    elif model_name == "Smart White Light": displayCategories = ["LIGHT"]
    elif model_name == "Smart Thermostat": displayCategories = ["THERMOSTAT"]
    elif model_name == "Smart Lock": displayCategories = ["SMARTLOCK"]
    elif model_name == "Smart Scene": displayCategories = ["SCENE_TRIGGER"]
    elif model_name == "Smart Activity": displayCategories = ["ACTIVITY_TRIGGER"]
    elif model_name == "Smart Camera": displayCategories = ["CAMERA"]
    else: displayCategories = ["OTHER"]
    return displayCategories

def get_endpoint_from_v2_appliance(appliance):
    endpoint = {
        "endpointId": appliance["applianceId"],
        "manufacturerName": appliance["manufacturerName"],
        "friendlyName": appliance["friendlyName"],
        "description": appliance["friendlyDescription"],
        "displayCategories": [],
        "cookie": appliance["additionalApplianceDetails"],
        "capabilities": []
    }
    endpoint["displayCategories"] = get_display_categories_from_v2_appliance(appliance)
    endpoint["capabilities"] = get_capabilities_from_v2_appliance(appliance)
    return endpoint

# This function return all the devices in a JSON body.
# see document in https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages
def handleDiscovery():
    endpoints = []
    for appliance in SAMPLE_APPLIANCES:
        endpoints.append(get_endpoint_from_v2_appliance(appliance))
    newendpoints = []
    newendpoints.append(bigLight.__dict__)
    print "old end"
    print endpoints
    
    print "new end"
    print newendpoints
    # endpoints.append(bigLight.__dict__)
    response ={
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": get_uuid()
            },
            "payload": {
                "endpoints": newendpoints
            }
        }
    }
    return response

# This is the function to handle the event request. The event will be generated when you talk to Alexa Echo with a valid request.
# See https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
def handleControl(event):
    on = RF_ON
    name = "TurnOnConfirmation"

    event_name = event['header']['name']
    if event_name == 'TurnOnRequest':
        on = RF_ON
        name = "TurnOnConfirmation"
    elif event_name == 'TurnOffRequest':
        on = RF_OFF
        name = "TurnOffConfirmation"

    applianceId = event['payload']['appliance']['applianceId']
    if applianceId == allLights.applianceId:
        rf_list = map(lambda m: m[on], RF_MAP.values())
        send_request_batch(rf_list)
    elif applianceId.startswith('only'):
        rf_list = map(lambda m: m[RF_OFF], RF_MAP.values())
        light_id = event['payload']['appliance']['additionalApplianceDetails']['id']
        rf_list.remove(RF_MAP[light_id][RF_OFF])
        rf_list.append(RF_MAP[light_id][RF_ON])
        send_request_batch(rf_list)
    else:
        send_request(applianceId, on)

    header = {
        "namespace": "Alexa.ConnectedHome.Control",
        "name": name,
        "payloadVersion": "2",
    }
    return {
        'header': header,
        'payload': {}
    }

# Send the HTTP request to Raspberry Pi server
def send_request(id, on):
    url = base_url + "/rf?frequency=" + RF_MAP[id][on]
    urllib2.urlopen(url)

# Since our Raspberry Pi server support batch, this is the command for sending multiple RF transmitter request in one Http Request.
def send_request_batch(frequency_list):
    url = base_url + "/rf?frequency=" + ','.join(frequency_list)
    urllib2.urlopen(url)


def get_capabilities_from_v2_appliance(appliance):

    capabilities = [
        {             
                "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [
                    { "name": "powerState" }
                ],
            "proactivelyReported": True,
            "retrievable": True
            }
        },
        {
                "type": "AlexaInterface",
                "interface": "Alexa.EndpointHealth",
                "version": "3",
                "properties": {
                "supported":[
                    { "name":"connectivity" }
                ],
            "proactivelyReported": True,
            "retrievable": True
                }
        },
        {
                "type": "AlexaInterface",
                "interface": "Alexa",
                "version": "3"
        }
    ]
    return capabilities