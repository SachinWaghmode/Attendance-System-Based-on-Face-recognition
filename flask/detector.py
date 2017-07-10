import cv2
import numpy as np
import os
from uuid import uuid4
import base64
import PIL.Image
from base64 import decodestring
import MySQLdb
import smtplib
from flask import Flask, request, render_template, send_from_directory
import operator
from twilio.rest import Client

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def getProfile(id):
    db = MySQLdb.connect(host="localhost", user="root", passwd="",
                         db="CMPE273")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    cmd = "SELECT sjsu_id,name,email_id FROM student where sjsu_id = '" + id + "'"
    
    profile =None
    try:
        cursor.execute(cmd)
        numrows = cursor.fetchall()
        for row in numrows:
            profile=row
            print profile[0],profile[1],profile[2]
        db.close()
    except:
        print "Error: unable to fecth data"
    return profile

def compareimage():
    output_dict = {}

    rec = cv2.face.createLBPHFaceRecognizer()
    rec.load("recognizer/trainingData.yml")

    # Load the classifier xml from open cv2
    faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    #img = cv2.imread('/var/www/html/images/' + name)
    img_to_process = cv2.imread('image_to_compare.jpg')
    
    # Convert color image to Gray Scale
    gray = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2GRAY)
    
    # Draw rectangle around face
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    for(x, y, w, h) in faces:
        cv2.rectangle(img_to_process, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id,conf = rec.predict(gray[y:y+h,x:x+w])
        if (conf > 35):
            id = "Unknown"
        if(id=="Unknown"):
            #cv2.putText(img_to_process, "% Match: " + str(100 - conf), (x - 30, y + h), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            #cv2.putText(img_to_process, str(id), (x, y + h+30), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            output_dict["Unknown"] = "Unregistered User - " + str(100 - round(conf,2)) + " %"
            return output_dict
        else:
            profile = getProfile(str(id))
            if(profile!="None"):
                #cv2.putText(img_to_process, "% Match: "+str(100 - conf), (x -30, y + h), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #cv2.putText(img_to_process, str(profile[1]), (x, y + h+30), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #cv2.putText(img_to_process, str(profile[2]), (x, y + h+60), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #return str(conf)
                """if(mailSent==False):
                    sendAttendancerecord('manish.pandey@sjsu.edu',profile[0],profile[1])
                    mailSent= True"""
                
                output_dict["SJSU ID"] = profile[0]
                output_dict["Name"] = profile[1]
                output_dict["Email ID"] = profile[2]
                conf = round(conf,2)
                output_dict["Match Percentage"] = str(100 - conf) + " %"
                
                return output_dict
    output_dict["Error"] = "No Face Detected. Please Stand in front of the camera and click verify."

    return output_dict


def sendAttendancerecord():
    toEmail = 'manish.pandey@sjsu.edu'
    
    fromaddr = 'cmpe273.sjsuproject@gmail.com'

    if os.path.exists(APP_ROOT + "/email_list.txt"):
        file = open(APP_ROOT + "/email_list.txt","r") 
        
        file_content = str(file.readlines())

        studentList = file_content.split(" ")
        # Create the message
        content = 'Student with Student ID %s are present.' % studentList
        print content
        message = 'Subject: %s\n%s' % ("Attendance record for Class 273", content)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login("cmpe273.sjsuproject@gmail.com", "cmpe273@2017")
        #server.set_debuglevel(True)  # show communication with the server
        try:
            server.sendmail('cmpe273.sjsuproject@gmail.com', toEmail,message )
            """client = Client("ACa849a726136e5f820facb11184d9d0de", "43ef7096906dfa3d94126afea4c013b3")
                                    body = content
                                    client.messages.create(to="+16692121549",
                                                           from_="+13343848263",body = content)"""
        finally:
            server.quit()



def is_student_present():
    output_dict = {}

    rec = cv2.face.createLBPHFaceRecognizer()
    rec.load("recognizer/trainingData.yml")

    # Load the classifier xml from open cv2
    faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    #img = cv2.imread('/var/www/html/images/' + name)
    img_to_process = cv2.imread('student_to_compare.jpg')
    
    # Convert color image to Gray Scale
    gray = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2GRAY)
    
    # Draw rectangle around face
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    for(x, y, w, h) in faces:
        cv2.rectangle(img_to_process, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id,conf = rec.predict(gray[y:y+h,x:x+w])
        if (conf > 35):
            id = "Unknown"
        if(id=="Unknown"):
            #cv2.putText(img_to_process, "% Match: " + str(100 - conf), (x - 30, y + h), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            #cv2.putText(img_to_process, str(id), (x, y + h+30), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            output_dict["Unknown"] = "Unregistered User - " + str(100 - round(conf,2)) + " %"
            return output_dict
        else:
            profile = getProfile(str(id))
            if(profile!="None"):
                #cv2.putText(img_to_process, "% Match: "+str(100 - conf), (x -30, y + h), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #cv2.putText(img_to_process, str(profile[1]), (x, y + h+30), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #cv2.putText(img_to_process, str(profile[2]), (x, y + h+60), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
                #return str(conf)
                """if(mailSent==False):
                    sendAttendancerecord('manish.pandey@sjsu.edu',profile[0],profile[1])
                    mailSent= True"""
                if os.path.exists(APP_ROOT + "/email_list.txt"):

                    file = open("email_list.txt","a") 
     
                    file.write(profile[0] + " ") 
                    
                    file.close()
                else:
                    file = open("email_list.txt","w") 
     
                    file.write(profile[0] + " ") 
                    
                    file.close()
                
                output_dict["SJSU ID"] = profile[0]
                output_dict["Name"] = profile[1]
                output_dict["Email ID"] = profile[2]
                conf = round(conf,2)
                output_dict["Match Percentage"] = str(100 - conf) + " %"
                
                return output_dict
    output_dict["Error"] = "No Face Detected. \nPlease Stand in front of the camera and click verify."

    return output_dict

if __name__ == '__main__':
    app.run(port=4556, debug = True)