from flask import Flask,render_template

app = Flask(__name__)

# Home
@app.route('/')
def index():
    return render_template("home.html")

# Update
@app.route('/update')
def update():
     return render_template("update.html")

# Feature
@app.route('/predict')
def predict():
     return render_template("predict.html")

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
    