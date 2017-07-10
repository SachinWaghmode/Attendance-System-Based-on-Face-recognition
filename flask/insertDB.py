import MySQLdb as mdb

def insertValue(name,id,email_id,servername,username,password,DBName):

    # Connect to the database
    con = mdb.connect(servername, username,
                      password, DBName);

    # Query the database tables to check if the student already registered.
    cmd = "select sjsu_id from student WHERE sjsu_id = '" + id + "'"

    # Execute the select query

    cur = con.cursor()
    cur.execute(cmd)
    rows = cur.fetchall()
    #make blob object to save color image in DB
    #pick the color image from dataset

    print "dataset/studentId." + id + ".jpg"
    blob_value = open("dataset/studentId." + id + ".jpg","rb").read()

    # Variable to check if student is present
    isStudentPresent = 0
    for row in rows:
        """ If row is returned by the select query indicating that the student is already present in database then
        set the 'isStudentPresent variable to 1. """
        isStudentPresent = 1

    # If student record is already present in the database then ask the user if he wants to update the existing record.
    if(isStudentPresent==1):
    
        # If user wants to update the record then
        cmd= "UPDATE student SET name= %s ,image= %s , email_id = %s Where sjsu_id = %s "
        print cmd
        cur.execute(cmd,(name,blob_value,email_id,id))
        
    else:
        # There is no record for the user in database hence insert new record in Student table.
        #cmd = "INSERT INTO student(sjsu_id,name,image,email_id) VALUES('" + id + "','" + name + "','" + blob_value + "','" + email_id + "')"
        cmd = "INSERT INTO student(sjsu_id,name,image,email_id) VALUES(%s,%s,%s,%s)"
        cur.execute(cmd,(id,name,blob_value,email_id))
    print cmd
    con.commit()