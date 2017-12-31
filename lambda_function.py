import urllib2
import os
import json
import uuid
import time

maxSwitchNum = 5

# Class to define a home device that to be controlled by Alexa. eg. Lamp
class AlexaHomePowerController:
    def __init__(self, applianceId, name):
        self.endpointId = applianceId
        self.friendlyName = name
        self.manufacturerName = 'Tang'
        self.displayCategories = ['SMARTPLUG']
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


# The function that Lambad will call to handle any events.
def lambda_handler(event, context):
    eventname = {}
    eventname = event['directive']['header']['namespace']
    if eventname == 'Alexa.Discovery':
        return handleDiscovery()
    else:
        return handleControl(event) 

smart_plug_list = []
rf_control_dict = {}
for i in range(maxSwitchNum):
    endpoint_id = "endpoint-00" + str(i+1)
    smart_plug_list.append(AlexaHomePowerController(endpoint_id, "SmartPlug" + str(i+1)))
    rf_control = {
    endpoint_id:{
        "TurnOn": os.environ["RF" + str(i+1) + "_ON"], 
        "TurnOff": os.environ["RF" + str(i+1) + "_OFF"]
        }
    }
    rf_control_dict.update(rf_control)

base_url = os.environ['BASE_URL']

def get_uuid():
    return str(uuid.uuid4())

def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))

# This function return all the devices in a JSON body.
# see document in https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages
def handleDiscovery():
    endpoints = []
    # endpoints.append(smart_plug3.__dict__)
    # endpoints.append(smart_plug_list)
    for appliance in smart_plug_list:
        endpoints.append(appliance.__dict__)
    response ={
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": get_uuid()
            },
            "payload": {
                "endpoints": endpoints
            }
        }
    }
    return response

# This is the function to handle the event request. The event will be generated when you talk to Alexa Echo with a valid request.
# See https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
def handleControl(request):
    # on = RF_ON
    # name = "TurnOnConfirmation"
    print "event: "+str(request)

    event_type = request['directive']['header']['namespace']
    event_name = request['directive']['header']['name']

    for appliance in smart_plug_list:
        if appliance.endpointId ==  request['directive']['endpoint']['endpointId']:
            event_appliance = appliance.endpointId
            break

    print "string slice: " + event_name[4:].upper()

    # print rf_control_dict[event_appliance][event_name]
    url = base_url + "/rf?number=" + rf_control_dict[event_appliance][event_name]
    print "url: " + url
    urllib2.urlopen(url)

    context = {
        "properties": [ 
            {
                "namespace": "Alexa.PowerController",
                "name": "powerState",
                "value": rf_control_dict[event_appliance][event_name][4:],
                "timeOfSample": get_utc_timestamp(),
                "uncertaintyInMilliseconds": 500
            } 
        ]
    }
    evemt = {
        "header": {
            "namespace": "Alexa"
            "name": "Response"
            "payloadVersion": "3"
            "messageId": get_uuid()
            "correlationToken": request["directive"]["header"]["correlationToken"]
        }
    }
    endpoint = {
        "scope": {
            "type": "BearerToken"
            "token":
        },
        "endpointId": request["directive"]["endpoint"]["endpointId"]
    }

    return {
        'header': context,
        'payload': {}
    }


