import os
import magic
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "uploads"



### web
@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


@app.route("/uploadimage", methods=['POST'])
def upload_image():
    # make sure uploads folder exists and create it if it doesn't
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # retrieve uploaded files
    uploaded_file = request.files.get("image")
    
    return redirect('/')


@app.route("/clear", methods=['GET'])
def remove_db_entries():
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)