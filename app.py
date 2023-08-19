from flask import Flask, render_template, request, redirect, url_for
import pymysql
import boto3
import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os

ACCESS_KEY = ""
SECRET_KEY =""


ENDPOINT="o.us-east-1.rds.amazonaws.com"
PORT=3306
USR=""
PASSWORD=""
DBNAME="default"

app = Flask(__name__
app.config['template_folder'] = 'templates'


@app.route('/')
def main():
     return render_template("login.html")

@app.route('/notfound')
def notfound():
     return render_template("usernotfound.html")

@app.route('/login')
def login():
    render_template("login")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/add', methods=["POST"])
def add():
    email = request.form.get("email")
    password= request.form.get("password")
    desc=request.form.get("description")
  #  imagepath=request.form.get("imagefilepath")
    f = request.files['file']
    filename=f.filename.split("\\")[-1]
    f.save(secure_filename(filename))
    #filename=imagepath.split("\\")[-1]

    client= boto3.client("ses",
    ACCESS_KEY = "",
    SECRET_KEY ="",
    ACCESS_REGION="us-east-1"

)
    client.upload_file(filename, "applab1", "images/"+filename,ExtraArgs={'GrantRead': 'uri="http://acs.amazonaws.com/groups/global/AllUsers"'})

    conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO userdetails(email,password,description,imagelocation) VALUES('"+email+"','"+password+"','"+desc+"', '"+filename+"');")
    print("Insert Success")
    conn.commit()
    os.remove(filename)

    lambda_client = boto3.client('khan_lambda',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-east-2')

    lambda_payload={"email":email}
    lambda_client.invoke(FunctionName='khan_lambda',
                     InvocationType='Event',
                     Payload=json.dumps(lambda_payload))

    return redirect("/")


@app.route('/mainpage',methods=["GET"])
def mainpage():
    email= request.args.get('email')
    password= request.args.get('password')
    print(email,password)
    try:
            conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
            cur = conn.cursor()
            qry= "SELECT * FROM userdetails Where email ='"+email+"' AND password = '"+password+"';"
            print(qry)
            cur.execute("SELECT * FROM khan;")
            query_results = cur.fetchall()
            print(query_results)
            cur.execute("SELECT * FROM khan Where email ='"+email+"' AND password = '"+password+"';")
            query_results = cur.fetchall()
            print(query_results)
            if len(query_results)==1:
               return render_template("mainpage.html")
            else:
                return redirect("/notfound")
    except Exception as e:
            print("Database connection failed due to {}".format(e))
            return redirect("/")

@app.route('/search',methods=["POST"])
def search():
    email = request.form.get("email")
    print(email)
    return redirect("viewdetails/"+str(email))

@app.route('/viewdetails/<email>')
def viewdetails(email):

    try:
            conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM khan Where email ='"+email+"';")
            conn.commit()
            query_results = cur.fetchall()
            print(query_results)
            client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
            url = client.generate_presigned_url('get_object',
                                        Params={
                                            'Bucket': 'khan6',
                                            'Key': 'file/'+str(query_results[0][3]),
                                        },
                                        ExpiresIn=3600)
            url=str(url).split('?')[0]
            item={'email':query_results[0][0],'password':query_results[0][1],'desc':query_results[0][2],'link':url}
            print(item)
            return render_template("viewdetails.html", item=item)
    except Exception as e:
            print("Database connection failed due to {}".format(e))
            return redirect("/")

@app.route('/initialize')
def initialize():
    try:
        print("INITIALIZING DATABASE")
        conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
        cur = conn.cursor()
        try:
            cur.execute("DROP TABLE userdetails;")
            print("table deleted")
        except Exception as e:
            print("cannot delete table")
        cur.execute("CREATE TABLE khan(email VARCHAR(20), password VARCHAR(20), description VARCHAR(50), imagelocation VARCHAR(50));")
        print("table created")
        cur.execute("INSERT INTO khan(email,password,description,imagelocation) VALUES('test1@gmail.com','password','this is a desc', 'Default.png');")
        print("Insert Success")
        cur.execute("INSERT INTO khan(email,password,description,imagelocation) VALUES('test2@gmail.com','password','this is a desc', 'Default.png');")
        print("Insert Success")
        cur.execute("INSERT INTO khan(email,password,description,imagelocation) VALUES('test3@gmail.com','password','this is a desc', 'Default.png');")
        print("Insert Success")
        cur.execute("INSERT INTO khan(email,password,description,imagelocation) VALUES('test4@gmail.com','password','this is a desc', 'Default.png');")
        print("Insert Success")
        conn.commit()

        cur.execute("SELECT * FROM khan;")
        query_results = cur.fetchall()
        print(query_results)
        return redirect("/")
    except Exception as e:
        print("Database connection failed due to {}".format(e))
        return redirect("/")

@app.route('/share')
def share():
    email = request.args.get('email')
    file_name = request.args.get('file_name')

    conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
    cur = conn.cursor()

    cur.execute("INSERT INTO sharefiles(email, file_name, shared_with) VALUES('"+email+"','"+file_name+"','[]');")
    conn.commit()

    return redirect('/mainpage')


if __name__=="__main__":
    app.run(debug=True)
