from dataclasses import dataclass
from flask import Flask, render_template

status = Flask(__name__)
import pyodbc

def connection():
    cstr = 'DRIVER={SQL Server};SERVER=D1VDBOPSDB7700;DATABASE=DBOPS;Trusted_Connection=yes;'
    conn = pyodbc.connect(cstr)
    return conn

@status.route("/") 
def main():
#grabs the websites 
    websites = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("EXEC HNTResources_SELECT_V2 @ResourceType = 'Website'")
    for row in cursor.fetchall():
        websites.append({"ResourceName": row[1], "ResourceType": row[3], "ResourceStatus": row[4], "StatusTime": row[5], "ResponseTime": row[6], "ResponseTimeAvg": row[7], "ResponseTimeLast2Hours": row[8], "ResponseStDev": row[9], "ResourceAddress": row[2]})
    conn.close()
#grabs the sharepoint sites
    sharepoint = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("EXEC HNTResources_select_V2 @ResourceType = 'Sharepoint'")
    for row in cursor.fetchall():
        sharepoint.append({"ResourceName": row[1], "ResourceType": row[3], "ResourceStatus": row[4], "StatusTime": row[5], "ResponseTime": row[6], "ResponseTimeAvg": row[7], "ResponseTimeLast2Hours": row[8], "ResponseStDev": row[9], "ResourceAddress": row[2]})
    conn.close()
#grabs the databases
    database = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("EXEC HNTResources_select_V2 @ResourceType = 'database'")
    for row in cursor.fetchall():
        database.append({"ResourceName": row[1], "ResourceType": row[3], "ResourceStatus": row[4], "StatusTime": row[5], "ResponseTime": row[6], "ResponseTimeAvg": row[7], "ResponseTimeLast2Hours": row[8], "ResponseStDev": row[9]})
    conn.close()

    displayTime = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("EXEC ResourceStatus_LastUpdated")
    for row in cursor.fetchall():
      displayTime.append({"StatusTime": row[0]})
      
    conn.close()

    return render_template("status.html", websites=websites, sharepoint=sharepoint, database=database, displayTime=displayTime)
if(__name__ == "__main__"):
    status.run(host='0.0.0.0', port=5000, debug=False)
