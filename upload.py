import boto3
import numpy as np
import cv2
import datetime
cap = cv2.VideoCapture(0)

def upload(v):
    print(v)
    s3 = boto3.client('s3')
    s3.upload_file(v+'.avi', "pirecordings", v+".avi")


while True:
    v=datetime.datetime.now()
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    x=str(v).split('.')[0]
    x=x.replace(":","-")
    # x=x.replace(" ","")
    print(x)
    out = cv2.VideoWriter(x+'.avi',fourcc, 20.0, (640,480))
    flag=1
    while(cap.isOpened() and flag):
        if(datetime.datetime.now()-v>= datetime.timedelta(seconds=120, microseconds=520083)):
            flag=0
            upload(x)
            print('stopped')
        ret, frame = cap.read()
        if ret==True:
            # frame = cv2.flip(frame,0)
            # write the flipped frame
            out.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
