import requests
import os
from time import sleep
from urllib.parse import quote


recheck_delay = 30
telegram_api_key = ""
telegram_chat_id = ""
incident_memory_file = "incidents.log"
incident_memory = []


def sendMsg(msg):
    msg = quote(msg)
    msgApi = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
        telegram_api_key, telegram_chat_id, msg)
    try:
        print("Sending telegram notification")
        requests.get(msgApi).text
        print("Telegram notification sent")
    except:
        print("Failed to send telegram notification")


def readIncidentLogs():
    global incident_memory
    if os.path.exists(incident_memory_file):
        with open(incident_memory_file, mode="r", encoding='utf-8') as f:
            for line in f:
                incident_memory.append(line.strip())


def checkOldIncident(incident_ids):
    global incident_memory
    non_matched = []
    for incident_id in incident_ids:
        matched = False
        for line in incident_memory:
            if str(incident_id) == line:
                matched = True
                break
        if not matched:
            non_matched.append(incident_id)
    return non_matched


def saveIncidentLogs():
    global incident_memory
    with open(incident_memory_file, mode="w", encoding='utf-8') as f:
        for incident in incident_memory:
            f.write(str(incident) + "\n")


def monitorIncident():
    link = "https://firewatch.44-control.net/status.json"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = requests.get(link, headers=headers).json()
    except:
        print("Failed to open {}".format(link))
        return
    incidents = resp.get('Fire')
    incident_mapping = {}
    incident_id_list = []
    print("Incidents detected: {}".format(len(incidents)))
    for incident in incidents:
        incident_id = incident.get('ID')
        incident_number = incident.get('Incident Number')
        if str(incident_id) not in incident_id_list:
            incident_id_list.append(str(incident_id))
            incident_mapping[incident_id] = {}
            incident_mapping[incident_id]["FD"] = []
        incident_type = incident.get('Incident Type')
        try:
            address = incident.get('Address') + " " + incident.get('Address2')
        except:
            address = ''
        friendly = incident.get('Friendly')
        time_reported = incident.get('Time Reported')
        time_dispatch = incident.get('Time Closed')
        fd = incident.get('FD', '').replace('FD', '').strip()
        incident_mapping[incident_id]["FD"].append(fd)
        incident_mapping[incident_id]["Incident Type"] = incident_type
        incident_mapping[incident_id]["Address"] = address
        incident_mapping[incident_id]["Friendly"] = friendly
        incident_mapping[incident_id]["Time Reported"] = time_reported
        incident_mapping[incident_id]["Time Dispatch"] = time_dispatch
        if incident_mapping[incident_id].get("Incident Number") is None:
            incident_mapping[incident_id]["Incident Number"] = []
        incident_mapping[incident_id]["Incident Number"].append(
            incident_number)
    custom_text = ""
    for incident_id in incident_id_list:
        incident_numbers = incident_mapping[incident_id]["Incident Number"]
        if not checkOldIncident(incident_numbers):
            continue
        print("Incident: {}".format(
            incident_mapping[incident_id]["Incident Type"]))
        print("Address: {}".format(incident_mapping[incident_id]["Address"]))
        print("Friendly: {}".format(incident_mapping[incident_id]["Friendly"]))
        print("Time Reported: {}".format(
            incident_mapping[incident_id]["Time Reported"]))
        print("Time Dispatch: {}".format(
            incident_mapping[incident_id]["Time Dispatch"]))
        print("Departments: {}".format(
            ', '.join(incident_mapping[incident_id]["FD"])))
        print("-" * 20)
        custom_text += "Incident: {}\nAddress: {}\nFriendly: {}\nTime Reported: {}\nTime Dispatch: {}\nDepartments: {}\n".format(
            incident_mapping[incident_id]["Incident Type"],
            incident_mapping[incident_id]["Address"],
            incident_mapping[incident_id]["Friendly"],
            incident_mapping[incident_id]["Time Reported"],
            incident_mapping[incident_id]["Time Dispatch"],
            ', '.join(incident_mapping[incident_id]["FD"])
        )
        sendMsg(custom_text)


if __name__ == "__main__":
    if not os.path.exists(incident_memory_file):
        with open(incident_memory_file, mode="w", encoding='utf-8') as f:
            f.write("")
    readIncidentLogs()
    print("Monitoring has started")
    while True:
        try:
            monitorIncident()
        except:
            print("An exception took place while querying the API")
            pass
        saveIncidentLogs()
        print("Sleeping for {} seconds".format(recheck_delay))
        sleep(recheck_delay)
