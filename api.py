import flask
from flask import request, send_file
import tweepy
import dotenv
import os
from sys import exit
import re
import requests
import json
import random
from collections import OrderedDict

dotenv.load_dotenv()

# Flask setup
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "Invalid method"

@app.route('/v1/status', methods=['POST'])
def status():
    if 'key' not in request.form:
        return "Missing API key", 401
    
    if request.form.get('key') != os.getenv('MC_API_KEY'):
        return "Invalid API key", 403

    statuses = OrderedDict({'Service Closed': [], 'Part Closure': [], 'Severe Delays': [], 'Minor Delays': [], 'Good Service': []})
    status_json = requests.get("https://api.tfl.gov.uk/line/mode/tube,overground,dlr,tflrail/status").json()

    for line in status_json:
        #print(line)
        for line_status in line['lineStatuses']:
            if line_status['statusSeverityDescription'] in statuses.keys():
                statuses[line_status['statusSeverityDescription']].append(line['name'])
    
    
    print(statuses)

    message = ""

    # TODO: Make this a lot nicer! This could all be a for loop instead of re-writing the code... but I wanted the W&C customisation

    # Service closed
    mode = 'Service Closed'
    if statuses[mode] != []:
        statuses[mode] = list(dict.fromkeys(statuses[mode]))
        print(f"there are {len(statuses[mode])} services closed")
        if len(statuses[mode]) == 1:
            if statuses[mode] == ["Waterloo & City"]:
                message += "The Waterloo & City line is now closed."
            else:
                message += random.choice([f"There is a closure on the {statuses[mode][0]} line.", f" The {statuses[mode][0]} line is currently closed.", f" The {statuses[mode][0]} line is fully closed."])
        else:
            closed_list = ', '.join(statuses[mode][:-1]) + ', and ' + statuses[mode][-1]
            message += random.choice([f"The {closed_list} lines are all closed.", f" There are full closures on the {closed_list} lines right now."])

    # Part closed
    mode = 'Part Closure'
    if statuses[mode] != []:
        statuses[mode] = list(dict.fromkeys(statuses[mode]))
        #print(f"there are {len(statuses[mode])} services partly closed")
        if len(statuses[mode]) == 1:
            message += "\n" + random.choice([f"There is a partial closure on the {statuses[mode][0]} line.", f"The {statuses[mode][0]} line is currently partially closed.", f"The {statuses[mode][0]} line has partial closures right now."])
        else:
            part_list = ', '.join(statuses[mode][:-1]) + ', and ' + statuses[mode][-1]
            message += "\n" + random.choice([f"The {part_list} lines are all partially closed.", f"There are partial closures on the {part_list} lines right now."])

    # Severe delays
    mode = 'Severe Delays'
    if statuses[mode] != []:
        statuses[mode] = list(dict.fromkeys(statuses[mode]))
        #print(f"there are {len(statuses[mode])} with severe delays")
        if len(statuses[mode]) == 1: services_delayed = statuses[mode][0]
        else: services_delayed = ', '.join(statuses[mode][:-1]) + ', and ' + statuses[mode][-1]
        delay_type = 'severe delays'
        message += "\n" + random.choice([f"{services_delayed} services have {delay_type} at the moment.", f"There are {delay_type} on {services_delayed} services right now.", f"{services_delayed} services are currently experiencing {delay_type}.", f"Expect {delay_type} on {services_delayed} services."])

    # Minor delays
    mode = 'Minor Delays'
    if statuses[mode] != []:
        statuses[mode] = list(dict.fromkeys(statuses[mode]))
        #print(f"there are {len(statuses[mode])} with minor delays")
        if len(statuses[mode]) == 1: services_delayed = statuses[mode][0]
        else: services_delayed = ', '.join(statuses[mode][:-1]) + ', and ' + statuses[mode][-1]
        delay_type = 'minor delays'
        message += "\n" + random.choice([f"{services_delayed} services have {delay_type} at the moment.", f"There are {delay_type} on {services_delayed} services right now.", f"{services_delayed} services are currently experiencing {delay_type}.", f"Expect {delay_type} on {services_delayed} services."])

    # Good service
    mode = 'Good Service'
    if statuses[mode] != None:
        #print(f"there are {len(statuses[mode])} with good service")
        message += "\n" + random.choice(["All other services are running normally.", "Everything else is running smoothly.", "There's good service everywhere else.", "Everywhere else has good service.", "All is well elsewhere on the network."])

    output = json.dumps({'speech': message, 'closed': statuses['Service Closed'], 'partially_closed': statuses['Part Closure'], 'severe_delays': statuses['Severe Delays'], 'minor_delays': statuses['Minor Delays'], 'good_service': statuses['Good Service']})

    return output

@app.route('/v1/status/<service>', methods=['POST'])
def service_status(service):
    if 'key' not in request.form:
        return "Missing API key", 401
    
    if request.form.get('key') != os.getenv('MC_API_KEY'):
        return "Invalid API key", 403

    service_json = requests.get(f'https://api.tfl.gov.uk/Line/{service}/Status').json()
    if type(service_json) == list: service_json = service_json[0]
    if 'httpStatusCode' in service_json.keys(): return f"No service with ID {service}", 404
    print(service_json)
    print(len(service_json['lineStatuses']))

    if len(service_json['lineStatuses']) > 1:
        alert_types = {'Service Closed': ['full closure', 0], 'Part Closure': ['part closure', 0], 'Severe Delays': ['severe delay', 0], 'Minor Delays': ['minor delay', 0]}
        for alert in service_json['lineStatuses']:
            if alert['statusSeverityDescription'] in alert_types.keys(): alert_types[alert['statusSeverityDescription']][1] += 1
        
        alert_summary = []
        for alert_name in alert_types.keys():
            if alert_types[alert_name][1] > 0:
                alert_summary.append(f"{alert_types[alert_name][1]} {alert_types[alert_name][0]}")
        if len(alert_summary) > 1:
            return json.dumps({'speech': f"There are {', '.join(alert_summary[:-1]) + ', and ' + alert_summary[-1]} alerts for {service_json['name']} services."})
        elif alert_summary[0][0] == "1":
            return json.dumps({'speech': f"There is {alert_summary[-1]} alert for {service_json['name']} services."})
        else:
            return json.dumps({'speech': f"There are {alert_summary[-1]} alerts for {service_json['name']} services."})
    elif service_json['lineStatuses'][0]['statusSeverityDescription'] == "Good Service":
        return json.dumps({'speech': random.choice([f"{service_json['name']} services are currently running normally.", f"There are currently no alerts for {service_json['name']} services."])})
    else:
        alert_types = {'Service Closed': 'full closure', 'Part Closure': 'part closure', 'Severe Delays': 'severe delay', 'Minor Delays': 'minor delay'}

        return json.dumps({'speech': f"There is a {alert_types[service_json['lineStatuses'][0]['statusSeverityDescription']]} alert for {service_json['name']} services.", 'reason': service_json['lineStatuses'][0]['reason']})

app.run(host="0.0.0.0", port=5050)