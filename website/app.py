# app.py
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_session import Session
from model.predict_m1 import predict_disease_m1
from model.predict_m2 import predict_disease_m2
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import shutil
from sql import *
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH, ALLOWED_EXTENSIONS
from help import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#making sure client gets new cache
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    error_message = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Perform username validation
        if not is_valid_username(username):
            error_message = "Username must be at least 4 characters long."

        # Perform password validation (as shown in the previous example)
        elif not is_valid_length(password):
            error_message = "Password must be at least 8 characters long."
        elif not has_special_characters(password):
            error_message = "Password must contain at least one special character."
        elif not has_numbers(password):
            error_message = "Password must contain at least one number."
        elif password != confirmation:
            error_message = "Passwords don't match."
        else:
            # Hash the password and insert user into the database
            hashed_password = generate_password_hash(password)
            execute_query("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))

            return redirect("/")

    return render_template("register.html", error_message=error_message)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html",message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html",message="must provide password")

        # Query database for username
        rows = fetch_query("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return  render_template("apology.html",message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/details")
@login_required
def details():
    return render_template("details.html", disease_info = cause_symptom_remedies)

@app.route("/predictions", methods=["GET", "POST"])
@login_required
def predictions():
    if request.method == "POST":
        if 'image' not in request.files:
            error = 'No file uploaded.'
            return render_template("predictions.html", error=error)

        file = request.files['image']

        if file.filename == '':
            error = 'No file selected.'
            return render_template("predictions.html", error=error)
        
        model = request.form['model']
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(image_path)
                if model == 'model1':
                    prediction = predict_disease_m1(image_path)
                elif model == 'model2':
                    prediction = predict_disease_m2(image_path)
                
                # Retrieve causes, symptoms, and remedies based on the prediction
                causes_symptoms_remedies = get_disease_info(prediction)
            except Exception as e:
                error = f'Error during prediction: {str(e)}'
                return render_template("predictions.html", error=error)
            
            return render_template("predictions.html", prediction=prediction, image_path=filename, causes_symptoms_remedies=causes_symptoms_remedies)

        else:
            error = 'Invalid file type. Only PNG, JPG, JPEG, and GIF files are allowed.'
            return render_template("predictions.html", error=error)
        
    return render_template("predictions.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Remove uploaded images from the uploads folder
    uploads_folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(uploads_folder):
        for filename in os.listdir(uploads_folder):
            file_path = os.path.join(uploads_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                 return render_template("apology.html",message=f"Error deleting file {file_path}: {e}")

    # Redirect user to login form
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)