import requests
from requests_ntlm import HttpNtlmAuth
import pyodbc
import datetime
import keyring

#connect to master database 
mastercnn = pyodbc.connect('DRIVER={SQL Server};SERVER=d1vdbopsdb7700;DATABASE=DBOps;Trusted_Connection=yes;')
mastercur = mastercnn.cursor()
mastercur.execute("EXECUTE dbo.ResourceStatusDelete")
mastercur.commit()

password = keyring.get_password('HNTB APP STATUS BOARD', 'solarwindssa') 
print (password)

#scan websites
def scan_websites(resourceID, address):
    session = requests.Session()
    session.auth = HttpNtlmAuth('HNTB\\solarwindssa', password)
    headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    try:
        startTime = datetime.datetime.now()
        r = session.get(address, headers=headers)
        endTime = datetime.datetime.now()
        elapsed = endTime - startTime

        print("ResponseTime: " + str(elapsed.microseconds/1000) + "ms")
        if (r.status_code == 200):
            status_code = "UP"
            print(address + " site is up")
        else:
            status_code = "DOWN - " + str(r.status_code)
            print (address + " site is down")
    except:
        status_code = "ERROR"
        print(address)
        print("check yo website fool")
    #Stored Proc Insert 
    mastercur.execute("EXECUTE dbo.ResourceStatusInsert @ResourceID=" + str(resourceID) + ",@ResourceStatus='" + status_code + "',@ResponseTimeMicroSeconds=" + str(elapsed.microseconds/1000))
    mastercur.commit()    

    
def check_databases(resourceID, server):  
    dbstarttime = datetime.datetime.now()
    cnn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=master;Trusted_Connection=yes;')
    dbendtime = datetime.datetime.now()
    dbelapsed = dbendtime - dbstarttime
    cur = cnn.cursor()
    cur.execute("SELECT GETDATE()")
    for row in cur:
        serverDate = row[0]
    if (serverDate != 0):
        status_code = "UP"
        print (server + str(serverDate))
        print("ResponseTime: " + str(dbelapsed.microseconds/1000) + "ms")
    else:
        status_code = "DOWN"
    cnn.close()
    mastercur.execute("EXECUTE dbo.ResourceStatusInsert @ResourceID=" + str(resourceID) + ",@ResourceStatus='" + status_code + "',@ResponseTimeMicroSeconds=" + str(dbelapsed.microseconds/1000))
    mastercur.commit()    

mastercur.execute("EXEC ResourceStatusSELECT @ResourceType = 'Website'")
websites = mastercur.fetchall()
for row in websites:
    scan_websites(row[0], row[2]) 
mastercur.execute("EXEC ResourceStatusSELECT @ResourceType = 'SharePoint'")
websites = mastercur.fetchall()
for row in websites:
    print (row[0])
    scan_websites(row[0], row[2]) 
mastercur.execute("EXEC ResourceStatusSELECT @ResourceType = 'Database'")
websites = mastercur.fetchall()
for row in websites:
    print (row[0])
    check_databases(row[0], row[2]) 

