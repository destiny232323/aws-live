from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/salary", methods=['GET', 'POST'])
def salary():
    return render_template('salary.html')

@app.route("/examine", methods=['GET', 'POST'])
def examine():
    return render_template('examine.html')
    
@app.route("/update", methods=['GET', 'POST'])
def update():
    return render_template('update.html')

@app.route("/view", methods=['GET', 'POST'])
def view():
    return render_template('view.html')

@app.route("/search2", methods=['POST'])
def search2():
    emp_id = request.form['emp2_id']
    overtime = request.form['ot']
    penalty = request.form['penalty']
    epf = request.form['epf']
    cursor = db_conn.cursor()
    
    selectSql = "Select salary From employee Where emp_id = %s"
    id = (emp_id)
    cursor.execute(selectSql, id)
    result1 = cursor.fetchone()

    total = int(result1[1]) + int(overtime * 10) - int(penalty)
    final = int((epf * total) / 100)

    updateSql = "Update employee set salary = %s Where emp_id = %s"
    money = (final)
    id = (emp_id)
    cursor.execute(updateSql, money, id)
    finalSalary = cursor.fetchone()
    db_conn.commit()
    cursor.close()

    return render_template('update.html', result1 = result1, finalSalary = finalSalary)

@app.route("/search", methods=['POST'])
def search():
    emp_id = request.form['emp1_id']
    
    cursor = db_conn.cursor()
    selectSql = "Select salary From employee Where emp_id = %s"
    id = (emp_id)
    cursor.execute(selectSql, id)
    result2 = cursor.fetchone()
    db_conn.commit()

    cursor.close()  
    return render_template('examine.html', result2 = result2)

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']   
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    position = request.form['position']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location, position, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    if position == 'Senior':
        salary = 6000
    else:
        salary = 3000
    cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, position, salary))
    db_conn.commit()   
    
        
    emp_name = "" + first_name + " " + last_name
    # Uplaod image file in S3 #
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3 = boto3.resource('s3')


    try:
        print("Data inserted in MySQL RDS... uploading image to S3...")
        s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])

        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

        object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            s3_location,
            custombucket,
            emp_image_file_name_in_s3)

    except Exception as e:
        return str(e)


    cursor.close()
                
    print("all modification done...")
    return render_template('salary.html', name = result1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


