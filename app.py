from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import numpy as np
# from datetime import datetime
import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img , img_to_array
from tensorflow_addons.metrics import FBetaScore
import os
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your-secret-key'

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

#### User ####
### MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_users'

mysql = MySQL(app)

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
        print(user)
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['user_email'] = user[1]
            session['username'] = user[3]
            username = session.get('username')
            email = session.get('email')
            # Login successful
            flash('Login successful!', 'success')
            return render_template('user/home.html', username=username, email=email)
        else:
            # Login failed
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('user/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
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
        
        flash('Registration successful! Please log in.', 'success')
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
        print(user)
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
        print(user)
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

#### Admin ####

def fetch_data():
    data = [
            {'name': 'John Doe', 'age': 30, 'email': 'john.doe@example.com'},
            {'name': 'Jane Smith', 'age': 25, 'email': 'jane.smith@example.com'},
    ]
    return data
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
        print(user)
        if user and user[2] == password:
            session['admin_id'] = user[0]
            session['user_email'] = user[1]
            session['username'] = user[3]
            username = session.get('username')
            email = session.get('email')
            # Login successful
            flash('Login successful!', 'success')
            return redirect('/admin/home')
        else:
            # Login failed
            flash('Invalid email or password. Please try again.', 'error')
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
            data = fetch_data()
            return render_template('admin/home.html', data=data, username=username, email=email)

# Admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if 'admin_id' in session:
            admin_id = session['admin_id']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM `admin` WHERE admin_id = %s", (admin_id,))
            user = cur.fetchone()
            cur.close()
            username = user[3]
            email = user[1]
            data = fetch_data()
            return render_template('admin/profile admin copy 2.html', data=data, username=username, email=email)
        
@app.route('/admin/profile', methods=['GET', 'POST'])
def adminProfile():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `admin` WHERE admin_id = %s", (admin_id,))
        user = cur.fetchone()
        cur.close()
        print(user)
        username = user[3]
        email = user[1]
        if request.method == 'POST':
            time_range = request.form['time_range']
            # print(time_range)
            data_table,chat_result, prediction, account = fetch_data_to_admin(time_range)
        else:
            # Default to last 5 days if no time range selected
            time_range = '9'
            data_table,chat_result, prediction, account = fetch_data_to_admin(time_range)

        return render_template('admin/profile admin.html', user=user, username=username, email=email, data_table=data_table, chat_result=chat_result, prediction=prediction, account=account)

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
    print(class_result,prob_result)
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
        # print(datetime.datetime.now())
        error = ''
        target_img = os.path.join(os.getcwd() , 'static/images/lung_ct_scan')
        if request.method == 'POST':
            image_files  = request.files['file']
            datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(datetime)
            # print(datetime_now)
            if image_files  and allowed_file(image_files .filename):
                image_bytes = image_files .read()
                # print(image_bytes)
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
            cur.execute("SELECT user_id, class_result, image_name, prediction_time FROM `predictions` WHERE user_id = %s", (user_id,))
            user = cur.fetchall()
            cur.close()
    return user

@app.route('/data')
def data():
    data = fetch_data_table_user()
    # Format date and time before passing to template
    formatted_data = [(row[3].strftime('%d-%m-%Y %H:%M:%S'), row[2], row[1]) for row in data]
    
    print(formatted_data)
    return render_template('profile copy 3.html', data=formatted_data)

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
    print(data_table)

    query2 = """
                SELECT class_result, COUNT(class_result) AS number_of_class_result  
                FROM predictions 
                GROUP BY class_result 
                """
    cur.execute(query2)
    chat_result = cur.fetchall()
    print(chat_result)

    query3 = "SELECT COUNT(prediction_id) AS number_of_prediction_id FROM predictions "
    cur.execute(query3)
    prediction = cur.fetchone()
    print(prediction)
    
    query4 = "SELECT COUNT(user_id) AS number_of_user_id FROM users"
    cur.execute(query4)
    account = cur.fetchone()
    print(account)
    cur.close()
    return data_table, chat_result, prediction, account


@app.route('/data_admin', methods=['GET', 'POST'])
def data_admin():
    if request.method == 'POST':
        time_range = request.form['time_range']
        print(time_range)
        data_table,chat_result, prediction, account = fetch_data_to_admin(time_range)
    else:
        # Default to last 5 days if no time range selected
        time_range = '8'
        data_table,chat_result, prediction, account = fetch_data_to_admin(time_range)
    return render_template('admin/profile admin.html', data_table=data_table, chat_result=chat_result, prediction=prediction, account=account)

if __name__ == "__main__":
    app.run(debug=True)