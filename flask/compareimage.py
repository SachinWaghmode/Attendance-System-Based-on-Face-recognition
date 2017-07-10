
from flask import Flask,render_template
app = Flask(__name__)
import os
import cv2
import numpy as np
from PIL import Image, ImagePath
from uuid import uuid4
import base64
from base64 import decodestring
import detector
import MySQLdb
from flask import Flask, request, render_template, send_from_directory
import insertDB

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
   return render_template('face_recognizer.html')

@app.route('/face_recognizer.html')
def home():
   return render_template('face_recognizer.html')

@app.route('/attendance.html')
def attendance():
    output_dict = {}
    return render_template('attendance.html',output_dict=output_dict)

@app.route('/send_mail', methods=["POST"])
def send_mail():
    output_dict = {}
    if os.path.exists(APP_ROOT + "/email_list.txt"):
        file = open(APP_ROOT + "/email_list.txt","r") 
        
        detector.sendAttendancerecord()
        return render_template('face_recognizer.html')
    else:
        return render_template('attendance.html',output_dict=output_dict)

@app.route('/verify_attendance', methods=["POST"])
def verify_attendance():
    data = dict(request.form)
    img_data = data['img_val'][0].split(',')[1]
    img = decodestring(str(img_data))
    with open('student_to_compare.jpg', 'wb') as f:
        f.write(img)

    response =  detector.is_student_present()

    return render_template('attendance.html', output_dict=response)

@app.route('/upload', methods=["POST"])
def createdataset():

    # Extract the data submited from the create user html form.
    data = dict(request.form)

    # Get other details from the form
    name = request.form['name']
    email = request.form['email']
    sjsu_id = str(int(request.form['sjsu_id']))

    target = os.path.join(APP_ROOT, 'images')
    
    filename = name + '_' + sjsu_id +'.jpg'
    destination = "/".join([target,filename])
    
    if not os.path.isdir(target):
        os.mkdir(target)

    if request.form['which_image']:
        print "CAPTURED IMAGE"
        #Fetch and decode the image data from the 'img_val' variable.
        img_data = data['img_val'][0].split(',')[1]
        img = decodestring(str(img_data))
        
        # Write the image captured from the 'Create_User.html' page and save it to database.
        with open(destination, 'wb') as f:
            f.write(img)
    else:
        print "UPLOADED IMAGE"
        for file in request.files.getlist("pic"):
            file.save(destination)
   
    # Load the classifier xml from open cv2
    faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

    img_to_process = cv2.imread(destination)

    gray = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2GRAY)

    faces = faceDetect.detectMultiScale(gray, 1.3, 5)

    # Loop over the coordinates
    for (x, y, w, h) in faces:
        
        # Save the image of the face
        cv2.imwrite("dataset/studentId." + sjsu_id + ".jpg", gray[y:y + h, x:x + w])

        # Draw a rectangle to display which portion of the face was saved.
        cv2.rectangle(img_to_process, (x, y), (x + w, y + h), (0, 255, 0), 2)

    servername = "localhost"
    username="root"
    password=""
    DBName="CMPE273"
    
    insertDB.insertValue(name,sjsu_id,email,servername,username,password,DBName)

    # -------- Recognizer Begins -------- #

    recognizer = cv2.face.createLBPHFaceRecognizer()

    path = 'dataset/'

    # Get Path of each Image in the data set folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    #print imagePaths
    faces = []

    IDs=[]

    for imagePath in imagePaths:
        faceImg=Image.open(imagePath).convert('L')

        faceNp=np.array(faceImg,'uint8')

        ID= int(os.path.split(imagePath)[-1].split('.')[1])

        faces.append(faceNp)

        IDs.append(ID)
    
    Ids, faces = np.array(IDs), faces

    recognizer.train(faces,Ids)
    recognizer.save('recognizer/trainingData.yml')

    cv2.destroyAllWindows()

    return render_template('user_creation_success.html')

@app.route('/user_creation_success.html')
def user_creation_success():
   return render_template('user_creation_success.html')

@app.route('/create_user.html')
def create_user():
   return render_template('create_user.html')

@app.route('/verify_user.html')
def verify_user():
    output_dict = {}
    return render_template('verify_user.html',output_dict=output_dict)

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

@app.route('/match_user', methods=["POST"])
def match_user():
    data = dict(request.form)
    img_data = data['img_val'][0].split(',')[1]
    img = decodestring(str(img_data))
    with open('image_to_compare.jpg', 'wb') as f:
        f.write(img)

    response =  detector.compareimage()

    return render_template('verify_user.html', output_dict=response)


if __name__ == '__main__':
    app.run(debug = True)
   # Ids,faces = getImagesWithID(path)
   # recognizer.train(faces,Ids)
   # recognizer.save('CMPE273-teamproject/trainingData.yml')
   # cv2.destroyAllWindows()
