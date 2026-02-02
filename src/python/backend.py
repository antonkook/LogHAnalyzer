import os
import magic
import socket
import subprocess
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "../../uploads"
MOUNT_DIR = "/mnt/hassos"

### web
# @app.route("/", methods=['GET'])
# def index():
#     return render_template("index.html")


# @app.route("/uploadimage", methods=['POST'])
# def upload_image():
#     # make sure uploads folder exists and create it if it doesn't
#     os.makedirs(UPLOAD_DIR, exist_ok=True)

#     # retrieve uploaded files
#     uploaded_file = request.files.get("image")
    
#     return redirect('/')


# @app.route("/clear", methods=['GET'])
# def remove_db_entries():
#     return redirect('/')


@app.post("/use-image")
def use_image():
    # get path
    path = request.json["path"]

    # debug
    print(path)

    # TODO do stuff with the mounted image file

    return "ok"


def get_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


if __name__ == "__main__":
    port = get_port()
    print(f"PORT:{port}", flush=True)
    app.run(port=port, debug=False, use_reloader=False)