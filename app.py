# Importing essential libraries
from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, scale
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re  
app = Flask(__name__,static_url_path="/static")

app.secret_key = 'xyzsdfg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'heartdb' 
mysql = MySQL(app)

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully !'
            return render_template('main.html', message = message)
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not userName or not password or not email:
            message = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            message = 'You have successfully registered !'
            return render_template('login.html',message=message)
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message = message)

filename = 'finall.pkl'
model = pickle.load(open(filename, 'rb'))


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/predict', methods=['GET','POST'])
def predict():
    name=session['name']
    if request.method == 'POST':
        age = int(request.form['age'])
        sex = int(request.form.get('sex'))
        cp = int(request.form.get('cp'))
        trestbps = int(request.form['trestbps'])
        chol = int(request.form['chol'])
        fbs = int(request.form.get('fbs'))
        restecg = int(request.form['restecg'])
        thalach = int(request.form['thalach'])
        exang = int(request.form.get('exang'))
        oldpeak = float(request.form['oldpeak'])
        slope = int(request.form.get('slope'))
        ca = int(request.form['ca'])
        thal = int(request.form.get('thal'))
        x = 220 - thalach
        #data = ['cp','thalach','exang','oldpeak','slope','thal']
        #op=pd.DataFrame(data)
        data = [[cp,ca,thalach,exang,oldpeak,slope,thal]]
        my_prediction = model.predict(data)
        return render_template('result.html',prediction=my_prediction,name=name,age=age,sex=sex,chestpain=cp,trestbps=trestbps,
        chol=chol,fbs=fbs,restecg=restecg,
        maxHrate=thalach,x=x,angina=exang,oldpeak=oldpeak,slope=slope,vessels=ca,thalassemia=thal)
if __name__ == '__main__':
	app.run(debug=True)

