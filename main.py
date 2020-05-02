from os import path
import datetime
import threading
import time
import json
import requests
from smtplib import SMTP

class BackgroundTask:
    def __init__(self,interval=10):
        self.interval=interval
    def runTask(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        oldDate=datetime.datetime.fromisoformat(getOldDateTime())
        website=getJsonFileDetail()['website']
        while True:
            if oldDate<datetime.datetime.now():
                updateDateTime(str(oldDate))
                oldDate=datetime.datetime.fromisoformat(getOldDateTime())
                try:
                    r = requests.get(website,headers={'Connection':'close'})
                    if r.status_code==200:
                        print("Website is okay")
                except requests.RequestException:
                    print("Send email")
                    sendServerDownEmail()



            time.sleep(self.interval)



def getJsonFileDetail():
    with open('data.json','r') as file:
        return json.load(file)
def checkDataFile():
    filename='data.json'
    if(path.exists(filename) and path.isfile(filename)):
        return True
    return False
def getOldDateTime():
    filename='data.json'
    with open(filename,'r',encoding='utf-8') as file:
        return json.load(file)['date']
def sendServerDownEmail():
    detail=getJsonFileDetail()['smtp']
    recvEmail=getJsonFileDetail()['email']
    sender = "Private Person <from@smtp.mailtrap.io>"
    receiver = "User <"+recvEmail+">"
    message = f"""\
    Subject: Hi Mailtrap
    To: {receiver}
    From: {sender}

    The website down"""
    with SMTP(detail['domain'],2525) as smtp:
        smtp.login(detail['username'],detail['password'])
        smtp.sendmail(sender,receiver,message)
        print(smtp.helo_resp)


def updateDateTime(oldDate):
    newDate=datetime.datetime.fromisoformat(oldDate)+datetime.timedelta(minutes=2)
    try:
        with open('data.json','r') as file:
            data=json.load(file)
            data['date']=str(newDate)
        with open('data.json','w') as file:
            json.dump(data,file)

    except IndexError:
        print("File doesn't provide any details or have date error")
        reset=bool(input("Do you wan't reset file:-"))


def createDataFile(url, email, mail):
    if url.startswith('http://') is not True or url.startswith('https://') is not True:
        url='http://'+url

    nextDate=datetime.datetime.today()+datetime.timedelta(minutes=1)
    f=open('data.json','w',encoding="utf-8")
    json.dump({'date':str(nextDate),'email':email,'website':url, 'smtp':mail}, f)
    f.close()

if __name__ == '__main__':
    print("Welcome:)")
    if checkDataFile() is not True:
        url = str(input("Enter url to check:- "))
        email = str(input("Enter email to send notification to you (when website downed):- "))
        smtpServer=str(input("Enter email Smtp server:- "))
        smtpUsername = str(input("Enter email Smtp username/email:- "))
        smtpPassword = str(input("Enter password Smtp password:- "))
        createDataFile(url, email, {
            'domain':smtpServer,
            'email':smtpUsername,
            'password':smtpPassword
        })
    else :
        updateDateTime(str(datetime.datetime.now()))
    task = BackgroundTask()
    task.runTask()
