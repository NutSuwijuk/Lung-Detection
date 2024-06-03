from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import numpy as np
import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img , img_to_array
from tensorflow_addons.metrics import FBetaScore
import os
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

### MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_users'

mysql = MySQL(app)

#### User ####
@app.route('/')
def index():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        email = user[1] 
        email = email
        username = user[3]
        username = username
        return render_template('user/home.html', username=username, email=email)
    return render_template('user/home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `users` WHERE email = %s", (email,))
        user = cur.fetchone()
        username = session.get('username')
        email = session.get('email')
        cur.close()
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['user_email'] = user[1]
            session['username'] = user[3]
            username = session.get('username')
            email = session.get('email')
            return render_template('user/home.html', username=username, email=email)
    return render_template('user/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('index'))  

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        age = request.form['age']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, password, username, age, role) VALUES (%s, %s, %s, %s, %s)", (email, password, username, age, role))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('user/register.html')

#Information
@app.route('/information')
def information():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        email = user[1] 
        email = email
        username = user[3]
        username = username
        return render_template('user/information.html', username=username, email=email)
    return render_template('user/information.html')

# About
@app.route('/about')
def about():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        email = user[1] 
        email = email
        username = user[3]
        username = username
        return render_template('user/about.html', username=username, email=email)
    return render_template("user/about.html")

# My Profile
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `users` WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        username = user[3]
        email = user[1]
        data = fetch_data_table_user()
        formatted_data = [(row[3].strftime('%d-%m-%Y %H:%M:%S'), row[2], row[1]) for row in data]
        return render_template('user/profile.html', user=user, username=username, email=email, data=formatted_data)

# Edit My Profile
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `users` WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        username = user[3]
        email = user[1]
        if request.method == 'POST':
            new_username = request.form['username']
            new_email = request.form['email']
            new_password = request.form['password']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE user_id = %s", (new_username, new_email, new_password, user_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('profile'))
        return render_template('user/edit profiles.html', user=user, username=username, email=email, profile=profile)

# Prediction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR , 'Xception_Model_Final-bests.hdf5'))

ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif','JPG'])
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = ['Covid-19', 'Cancer','Normal', 'Pneumonia']

def prediction(filename, model):
    img = load_img(filename, target_size=(224, 224))
    img = img_to_array(img)
    img = img.reshape(1, 224, 224, 3)
    img = img.astype('float32') / 255.0
    result = model.predict(img)
    class_indices = result.argsort()[0][-4:][::-1]
    probabilities = result[0][class_indices]
    class_result = [classes[i] for i in class_indices]
    prob_result = [(prob * 100).round(2) for prob in probabilities]
    return class_result, prob_result

@app.route('/predict' , methods = ['GET' , 'POST'])
def predict():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        user_id = user[0]
        user_id = user_id
        username = user[3]
        username = username
        error = ''
        target_img = os.path.join(os.getcwd() , 'static/images/lung_ct_scan')
        if request.method == 'POST':
            image_files  = request.files['file']
            datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if image_files  and allowed_file(image_files .filename):
                image_bytes = image_files .read()
                bytes_stream = BytesIO(image_bytes)
                img = Image.open(bytes_stream)
                file = img
                file.save(os.path.join(target_img , image_files.filename))
                image_path = os.path.join(target_img , image_files.filename)
                image_name = image_files.filename
                class_result , prob_result = prediction(image_path , model)
                predictions = {
                        "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "class4":class_result[3],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "prob4": prob_result[3],
                }
                class_result = predictions["class1"]
                prob_result = predictions["prob1"]
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO predictions (prediction_time, user_id, image_name, class_result, prob_result, image_bytes) VALUES (%s, %s, %s, %s, %s, %s)",
                    (datetime_now, user_id, image_name, class_result, prob_result, image_bytes)
                )
                mysql.connection.commit()
                cur.close()
            else:
                error = "Please upload images of jpg , jpeg and png extension only"
            if(len(error) == 0):
                return  render_template('user/result.html' , img  = image_name , predictions = predictions, username=username)
            else:
                return render_template('user/predict.html' , error = error, username=username)
        else:
            return render_template('user/predict.html', username=username)


def fetch_data_table_user():
    if 'user_id' in session:
            user_id = session['user_id']
            cur = mysql.connection.cursor()
            cur.execute("SELECT user_id, class_result, image_name, prediction_time FROM `predictions` WHERE user_id = %s ORDER BY prediction_time DESC;", (user_id,))
            user = cur.fetchall()
            cur.close()
    return user

#### Admin ####
@app.route('/admin/', methods=['GET', 'POST'])
def adminIndex():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `admin` WHERE email = %s", (email,))
        user = cur.fetchone()
        username = session.get('username')
        email = session.get('email')
        cur.close()
        if user and user[2] == password:
            session['admin_id'] = user[0]
            session['user_email'] = user[1]
            session['username'] = user[3]
            username = session.get('username')
            email = session.get('email')
            return redirect('/admin/home')
        else:
            return redirect('/admin/')
    return render_template('admin/index.html')

@app.route('/admin/home')
def adminHome():
    if 'admin_id' in session:
            admin_id = session['admin_id']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM `admin` WHERE admin_id = %s", (admin_id,))
            user = cur.fetchone()
            cur.close()
            username = user[3]
            email = user[1]
            return render_template('admin/home.html', username=username, email=email)


def fetch_data_to_admin(time_range):
    cur = mysql.connection.cursor()
    
    query1 = """
                SELECT predictions.user_id, users.username,  COUNT(predictions.prediction_id) AS total_prediction, predictions.prediction_time
                FROM predictions
                INNER JOIN users ON predictions.user_id = users.user_id
                WHERE predictions.prediction_time >= CURDATE() - INTERVAL %s DAY
                GROUP BY users.username
                ORDER BY total_prediction DESC;
                """
    cur.execute(query1, (time_range,))
    data_table = cur.fetchall()

    query2 = """
                SELECT class_result, COUNT(class_result) AS number_of_class_result  
                FROM predictions 
                GROUP BY class_result 
                """
    cur.execute(query2)
    chat_result = cur.fetchall()

    query3 = "SELECT COUNT(prediction_id) AS number_of_prediction_id FROM predictions "
    cur.execute(query3)
    prediction = cur.fetchone()
    
    query4 = "SELECT COUNT(user_id) AS number_of_user_id FROM users"
    cur.execute(query4)
    account = cur.fetchone()

    query5 = """
                SELECT predictions.user_id, predictions.prediction_time, users.username, predictions.class_result, predictions.image_name
                FROM predictions
                INNER JOIN users ON predictions.user_id = users.user_id
                ORDER BY predictions.prediction_time DESC;
            """
    cur.execute(query5)
    all_user = cur.fetchall()
    cur.close()
    return data_table, chat_result, prediction, account, all_user

@app.route('/admin/profile', methods=['GET', 'POST'])
def adminProfile():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `admin` WHERE admin_id = %s", (admin_id,))
        user = cur.fetchone()
        cur.close()
        username = user[3]
        email = user[1]
        if request.method == 'POST':
            time_range = request.form['time_range']
            data_table,chat_result, prediction, account, all_user = fetch_data_to_admin(time_range)
        else:
            time_range = '7'
            data_table,chat_result, prediction, account, all_user = fetch_data_to_admin(time_range)

        return render_template('admin/profile admin.html', user=user, username=username, email=email, data_table=data_table, chat_result=chat_result, prediction=prediction, account=account, all_user=all_user)

#Admin Information
@app.route('/admin/information')
def adminInformation():
    if 'admin_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE admin_id = %s", (session['admin_id'],))
        user = cur.fetchone()
        cur.close()
        email = user[1] 
        email = email
        username = user[3]
        username = username
        return render_template('admin/information.html', username=username, email=email)
    return render_template('admin/information.html')

#Admin About
@app.route('/admin/about')
def adminAbout():
    if 'admin_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE admin_id = %s", (session['admin_id'],))
        user = cur.fetchone()
        cur.close()
        email = user[1] 
        email = email
        username = user[3]
        username = username
        return render_template('admin/about.html', username=username, email=email)
    return render_template("admin/about.html")

@app.route('/admin/predict' , methods = ['GET' , 'POST'])
def adminPredict():
    if 'admin_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE admin_id = %s", (session['admin_id'],))
        admin = cur.fetchone()
        cur.close()
        admin_id = admin[0]
        admin_id = admin_id
        username = admin[3]
        username = username
        error = ''
        target_img = os.path.join(os.getcwd() , 'static/images/lung_ct_scan')
        if request.method == 'POST':
            image_files  = request.files['file']
            datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if image_files  and allowed_file(image_files .filename):
                image_bytes = image_files .read()
                bytes_stream = BytesIO(image_bytes)
                img = Image.open(bytes_stream)
                file = img
                file.save(os.path.join(target_img , image_files.filename))
                image_path = os.path.join(target_img , image_files.filename)
                image_name = image_files.filename
                class_result , prob_result = prediction(image_path , model)
                predictions = {
                        "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "class4":class_result[3],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                        "prob4": prob_result[3],
                }
                class_result = predictions["class1"]
                prob_result = predictions["prob1"]
                cur = mysql.connection.cursor()
            else:
                error = "Please upload images of jpg , jpeg and png extension only"
            if(len(error) == 0):
                return  render_template('admin/result.html' , img  = image_name , predictions = predictions, username=username)
            else:
                return render_template('admin/predict.html' , error = error, username=username)
        else:
            return render_template('admin/predict.html', username=username)

@app.route('/admin/logout')
def adminLogout():
    session.pop('admin_id', None)
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('adminIndex'))

@app.route('/admin/register', methods=['GET', 'POST'])
def adminRegister():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        role = 'admin'
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin (email, password, username, role) VALUES (%s, %s, %s, %s)", (email, password, username, role))
        mysql.connection.commit()
        cur.close()
        return render_template(url_for('admin/index'))
    return render_template('admin/register.html')

if __name__ == "__main__":
    app.run(debug=True)