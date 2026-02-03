import os
import magic
import socket
import subprocess
import sqlite3
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
    # path = request.json["path"]

    # debug
    # print("XD", flush=True)

    # TODO maybe make it less hardcoded or at least throw a warning if not found and stuff
    db_path = "file:" + MOUNT_DIR + "/supervisor/homeassistant/home-assistant_v2.db?mode=ro"

    conn = sqlite3.connect(db_path, uri=True)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name;
    """)

    tables = cursor.fetchall()

    for table in tables:
        print(table[0], flush=True)

    cursor.execute("""
        SELECT entity_id, state, last_changed
        FROM states
        ORDER BY last_changed DESC
        LIMIT 10;
    """)

    rows = cursor.fetchall()

    for entity_id, state, last_changed in rows:
        print(entity_id, state, last_changed)
        
    conn.close()

    print("test, if we even get here", flush=True)

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