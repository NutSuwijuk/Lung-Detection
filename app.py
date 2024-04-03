from flask import Flask,render_template, request
import cv2
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
class_names = ['COVID2_CT', 'Normal_CT', 'Cancer_CT', 'Pneumonia_CT']
model = load_model('Xception_Model.hdf5')

# Home
@app.route('/')
def index():
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

# SignIn
@app.route('/signin')
def signin():
     return render_template("signin.html")

# Register
@app.route('/register')
def register():
     return render_template("register.html")
 
if __name__ == "__main__":
     # app.run(debug=True)
     app.run()