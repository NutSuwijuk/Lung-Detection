from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import cv2
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
app.secret_key = 'your-secret-key'

class_names = ['COVID2_CT', 'Normal_CT', 'Cancer_CT', 'Pneumonia_CT']
model = load_model('Xception_Model.hdf5')

# Dummy user data (replace with actual user authentication logic)
# users = {
#     'john@jn.com': 'password123',
#     'jane@jn.com': 'abc123'
# }
# users = {
#     'john@jn.com': {'password': 'password123', 'username': 'john'},
#     'jane@jn.com': {'password': 'abc123', 'username': 'jane'},
# }

# Home
# @app.route('/')
# def index():
#      if 'email' in session:
#           return render_template("home.html", username = session['email'])
#      else:
#           return render_template("home.html")
     
@app.route('/')
def index():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        username = session.get('username')
        email = session.get('email')
        email == user[1] 
        return render_template('home.html', username=username, email=email)

    return render_template('home.html')

#### User ####

# Update
@app.route('/update')
def update():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        username = session.get('username')
        email = session.get('email')
        email == user[1] 
    return render_template('update2.html', username=username, email=email)
    #  return render_template("update2.html", logged_in='email' in session)

# Feature
def predict_cnn(test_img):
     test_img = cv2.resize(test_img, (128, 128))
     test_input = test_img.reshape((1, 128, 128, 3))

     predictions_cnn = model.predict(test_input)
     predicted_class_index = np.argmax(predictions_cnn)
     predicted_class_name = class_names[predicted_class_index]

     return predicted_class_name

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        username = session.get('username')
        email = session.get('email')
        email == user[1] 
        if request.method == 'POST':
            file = request.files['file']
            if file:
                img_bytes = file.read()
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                prediction = predict_cnn(img)
                return render_template('result.html', prediction=prediction, username=username, email=email)
    return render_template('predict.html', username=username, email=email)
     # return render_template("predict.html")

@app.route('/information')
def information():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        username = session.get('username')
        email = session.get('email')
        email == user[1] 
        return render_template('information.html', username=username, email=email)
    #  return render_template("post copy.html", logged_in='email' in session)

# About
@app.route('/about')
def about():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        username = session.get('username')
        email = session.get('email')
        email == user[1] 
        return render_template('about.html', username=username, email=email)
    return render_template("about.html")

# My Profile
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `users` WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        username = user[3]
        email = user[1]
        return render_template('profile.html', username=username, email=email)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session:
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')
        
        cur = mysql.connection.cursor()
        if new_email:
            # Update the user's email in the database if new_email is provided
            cur.execute("UPDATE users SET email = %s WHERE user_id = %s",
                        (new_email, session['user_id']))
            session['email'] = new_email  # Update session data with new email
            flash('Email updated successfully!', 'success')

        if new_password:
            # Update the user's password in the database if new_password is provided
            cur.execute("UPDATE users SET password = %s WHERE user_id = %s",
                        (new_password, session['user_id']))
            flash('Password updated successfully!', 'success')

        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('profile'))


import MySQLdb

### MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
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
            return render_template('home.html', username=username, email=email)
        else:
            # Login failed
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')

    #     if email in users and users[email]['password'] == password:
    #         session['email'] = email
    #         flash('Login successful!', 'success')
    #         username = user.get('username', 'Guest')
    #         return redirect(url_for('index'), username=username)  # Redirect to the home page or any other desired page after login
    #     else:
    #         flash('Invalid email or password. Please try again.', 'error')
    # return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session variables related to the user
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('username', None)
    # Optionally, you can add a flash message for logout
    flash('You have been logged out.', 'info')
    # Redirect to the login page or any other page after logout
    # return redirect(url_for('login'))
    # session.pop('email', None)
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
    return render_template('register.html')

    # if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']
    #     username = request.form['username']
    #     if email not in users:
    #         users[email] = {'password': password, 'username': username}
    #         session['email'] = email
    #         return redirect(url_for('index'))  # Redirect to the home page or any other desired page after signup
    # return render_template('register.html')

# SignIn
@app.route('/signin')
def signin():
     if request.method == 'POST':
          username = request.form['username']
          pwd = request.form['password']
          cur = mysql.connection.cursor()
          cur.execute(f"select username, password from tbl_users where username = '{username}'")
          user = cur.fetchone()
          cur.close()
          if user and pwd == user[1]:
               session['username'] = user[0]
               return render_template(url_for('home'))
          else:
               return render_template("signin.html", error = 'Invalid username or password')

#### Admin ####

@app.route('/admin/', methods=['GET', 'POST'])
def adminIndex():
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
            return redirect('/admin/dashboard')
            # return render_template('home.html', username=username, email=email)
        else:
            # Login failed
            flash('Invalid email or password. Please try again.', 'error')
            return redirect('/admin/')
    return render_template('admin/index.html')
    #  # chect the request is post or not
    # if request.method == 'POST':
    #     # get the value of field
    #     username = request.form.get('username')
    #     password = request.form.get('password')
    #     # check the value is not empty
    #     if username=="" and password=="":
    #         flash('Please fill all the field','danger')
    #         return redirect('/admin/')
    #     else:
    #         # login admin by username 
    #         admins=Admin().query.filter_by(username=username).first()
    #         if admins and bcrypt.check_password_hash(admins.password,password):
    #             session['admin_id']=admins.id
    #             session['admin_name']=admins.username
    #             flash('Login Successfully','success')
    #             return redirect('/admin/dashboard')
    #         else:
    #             flash('Invalid Email and Password','danger')
    #             return redirect('/admin/')
    # else:
    #     return render_template('admin/index.html', logged_in='email' in session)
   
# admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if 'user_id' in session:
            user_id = session['user_id']
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM `users` WHERE id = %s", (user_id,))
            user = cur.fetchone()
            cur.close()
            username = user[3]
            email = user[1]
            return render_template('/admin/dashboard.html', username=username, email=email)
    # return render_template('/admin/dashboard.html')

# import os
# from PIL import Image
# from werkzeug.utils import secure_filename
# UPLOAD_FOLDER = 'static/images'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/index')
# def index():
#      return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return 'No file part'
#     file = request.files['file']
#     if file.filename == '':
#         return 'No selected file'
#     if file:
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
        
#         # Preprocess the uploaded image
#         img = Image.open(file_path)
#         img = img.resize((224, 224))  # Assuming your model requires input images of size 224x224
#         img_array = np.array(img) / 255.0  # Normalize pixel values
#         img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
#         # Make predictions
#         predictions = model.predict(img_array)
#         # Convert predictions to human-readable labels
#         labels = ['COVID2_CT', 'Cancer_CT', 'Normal_CT', 'Pneumonia_CT']
#         result = labels[np.argmax(predictions)]
#         return render_template('index.html', filename=filename, result=result) 

# Register
# @app.route('/register')
# def register():
#      return render_template("register.html")

# @app.route('/signin')
# def signin():
#      return render_template("signin.html")
 
if __name__ == "__main__":
     app.run(debug=True)
     # app.run()