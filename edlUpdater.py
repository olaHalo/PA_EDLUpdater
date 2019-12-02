import xml.etree.ElementTree as ET
import sys
import os
import datetime
import requests

ip_address = '10.x.x.x'
apiKey = '&key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
apiCommand1 = '&cmd=<set><system><setting><target-vsys>vsys1</target-vsys></setting></system></set>' #Only needed if you have multiple VSYS
apiCommand2 = '&cmd=<request><system><external-list><refresh><type><ip><name>NAME_OF_EDL</name></ip></type></refresh></external-list></system></request>'
setVsysUrl = 'https://'+ ip_address +'/api/?type=op'+ apiKey + apiCommand1
refreshEdlUrl = 'https://'+ ip_address +'/api/?type=op'+ apiKey + apiCommand2
proxies = {
    'http': 'http://x.x.x.x:3128',
    'https': 'https://x.x.x.x:3128',
}
filePath = os.path.join('./logs/', 'edlUpdater-log.txt')

def refreshEDL(): #Make API calls to change VSYS and refresh the EDL
    try:
        #API CALL 1
        vsysHtml = requests.get( setVsysUrl , verify=False)    
        xmlContents = ET.fromstring(vsysHtml.content)

        #Check if the API call worked
        if xmlContents.attrib == {'status': 'success'}:
            if xmlContents[0].text != 'Session target vsys changed to vsys1':
                sendTeamsMessage(' : API VSYS call failed')
        else:
            sendTeamsMessage(' : API VSYS call failed. No success response received')
            setLog('API VSYS call failed. No success response received')

        #API CALL 2
        refreshEDLhtml = requests.get( refreshEdlUrl , verify=False)
        xmlContents2 = ET.fromstring(refreshEDLhtml.content)

        #Check if the API call 2 worked
        if xmlContents2.attrib == {'status': 'success'}:
            if xmlContents2[0].text != 'EDL refresh job enqueued':
                sendTeamsMessage(' : API EDL refresh call failed')        
        else:
            sendTeamsMessage(' : API refresh EDL call failed. No success response received')
            setLog('API refresh EDL call failed. No success response received')

    except:
        sendTeamsMessage(' : RefreshEDL method failed')
        setLog('RefreshEDL method failed')

def sendTeamsMessage(messageString): #Take a string and pass it to Webex Teams Channel
    try:
        teamsURL = 'https://api.ciscospark.com/v1/messages'
        teamsAPIkey = 'xxxxxxxx'
        room = 'xxxxx'
        messageText = getTime() + messageString
        headers = {'Authorization': 'Bearer ' + teamsAPIkey,
                   'Content-type': 'application/json;charset=utf-8'}
        post_data = {'roomId': room,
                     'text': messageText}
        response = requests.post(teamsURL, json=post_data, headers=headers, proxies=proxies)

    except: #Try again with no proxy 
        teamsURL = 'https://api.ciscospark.com/v1/messages'
        teamsAPIkey = 'xxxxxxxx'
        room = 'xxxxx'
        messageText = getTime() + messageString + ' ERROR - no proxy used'

        headers = {'Authorization': 'Bearer ' + teamsAPIkey,
                   'Content-type': 'application/json;charset=utf-8'}
        post_data = {'roomId': room,
                     'text': messageText}
        response = requests.post(teamsURL, json=post_data, headers=headers)
        logMessage = getTime() + ' : Unable to send Webex Teams Message to NetSec Alerts'
        setLog(logMessage)

def getTime(): #Gets the current time and formats it
	time = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S")
	return time

def setLog(str): #Logs to a file and appends newlines
	with open(filePath, 'a+') as logFile:
		logFile.write(getTime() + " : " + str + '\n')

#Run the primary method
setLog("EDL Updater Script running")
refreshEDL()

#Code Below was used to grab the API key                       

#html = requests.get('https://'+ip_address+'/api/?type=keygen&user='+username+'&password='+password , verify=False)
#print(html.content)
#contents = ET.fromstring(html.content)

#if contents.attrib == {'status': 'success'}:
#    for item in contents.iter('key'): #loop through the contents and search for key
#        string = 'API Key = ' + item.text
#        print(string)


