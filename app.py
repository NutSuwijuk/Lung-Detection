from flask import Flask,render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import cv2
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
app.secret_key = 'your-secret-key'

class_names = ['COVID2_CT', 'Normal_CT', 'Cancer_CT', 'Pneumonia_CT']
model = load_model('Xception_Model.hdf5')

# Home
@app.route('/')
def index():
     if 'email' in session:
          return render_template("home.html", username = session['email'])
     else:
          return render_template("home.html")

# Update
@app.route('/update')
def update():
     return render_template("update.html")

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
     if request.method == 'POST':
          file = request.files['file']
          if file:
               img_bytes = file.read()
               nparr = np.frombuffer(img_bytes, np.uint8)
               img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
               prediction = predict_cnn(img)
               return render_template('result.html', prediction=prediction)
     return render_template('predict.html')
     # return render_template("predict.html")

@app.route('/information')
def information():
     return render_template("information.html")
 
# About
@app.route('/about')
def about():
     return render_template("about.html")
 
# My Profile
@app.route('/profile')
def profile():
     return render_template("profile.html")

### MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_users'

mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT email, password FROM user_list WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['email'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        pwd = request.form["password"]
        gender = request.form["gender"]
        
        # Check if the username or email already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM user_list WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            return render_template('register.html', error='Username or email already exists')

        # If username and email are unique, proceed with registration
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user_list (username, email, password, gender) VALUES (%s, %s, %s, %s)", (username, email, pwd, gender))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('home'))
    return render_template('register.html')



@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for("home"))

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

# Register
# @app.route('/register')
# def register():
#      return render_template("register.html")
 
if __name__ == "__main__":
     app.run(debug=True)
     # app.run()