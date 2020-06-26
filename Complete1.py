import numpy as np
import cv2
import socket
import datetime
import threading
import logging
import os
import boto3
import http.client
import RPi.GPIO as GPIO

def Record():
    try:
        global flag
        global currFile
        v=str(datetime.datetime.now())
        currFile=v
        print('v: '+v)
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'X264')
        out = cv2.VideoWriter(v+'.mp4',fourcc, 20.0, (640,480))
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:
                out.write(frame)
                cv2.imshow('frame',frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                if GPIO.input(21)==0:
                    logging.info('down')
                    flag=1
                    break
            else:
                continue
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        threading.Thread(target=checkInternet, args=()).start()
        return 1
    except Exception as e:
        print('err '+ str(e))
        ite()
        

def ite():
    global flag
    while(flag):
#         print(str(flag)+'f')
        if(GPIO.input(21)==1):
            flag=0
            print('now '+'started')
            Record()
            ite()
        else:
            pass
#             print(GPIO.input(21))


def check_connection():
    conn=http.client.HTTPConnection('www.google.com', timeout=5)
    try:
        conn.request("HEAD","/")
        conn.close()
        return True
    except socket.error:
        conn.close()
        
def delFile():
    global uploadList
    for i in uploadList:
        if(os.path.isfile(r'/home/pi/New/'+i)):
            os.remove(r'/home/pi/New/'+i)
            print(i+' file removed')
    uploadList=[]
    print(uploadList)
        
    #if file exist inbucket del from local and also from the list
    

def upload():
    global uploadList
    try:
        for file in uploadList:
            if os.path.isfile(r'/home/pi/New/'+file):
                s3=boto3.client('s3')
                print('uploading  '+file)
                s3.upload_file(file,"pirecordings",file[:10]+'/'+file,ExtraArgs={'ACL':'public-read'})
                os.remove(r'/home/pi/New/'+file)
        uploadList=[]
    except Exception as e:
        print('error'+str(e))
        return 0
#     delFile()
        
        
def checkInternet():
    print('check internet')
    global uploadList
    if check_connection():
        # upload files in folder
        uploadList=[]
        for filename in os.listdir(r'/home/pi/New'):
            if filename.endswith(".mp4"): 
                print(filename)
                uploadList.append(filename)
                
            else:
                continue
            
        upload()

    else:
        checkInternet()


GPIO.setmode(GPIO.BCM)
GPIO.setup(21,GPIO.IN)
logging.basicConfig(filename='week.log', level=logging.DEBUG,)
flag=1
uploadList=[]
currFile=''
threading.Thread(target=ite, args=()).start()
threading.Thread(target=checkInternet, args=()).start()
print('done')

