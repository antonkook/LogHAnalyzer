import os
# import magic
from flask import jsonify
import socket
import subprocess
import sqlite3
import matplotlib.pyplot as plt
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
    # TODO datum und uhrzeit spanne hier retrieven und in query mit einbauen? wenn nicht geht dann in code

    db_path = "file:" + MOUNT_DIR + "/supervisor/homeassistant/home-assistant_v2.db?mode=ro"

    conn = sqlite3.connect(db_path, uri=True)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT states.state_id AS stateID, states.state AS state, states_meta.entity_id AS entityID,
        DATETIME(IIF(states.last_changed_ts IS NULL,states.last_updated_ts,states.last_changed_ts), 'unixepoch', 'localtime') AS ts,
        state_attributes.shared_attrs AS attributes, hex(states.context_id_bin) AS ctxID

        FROM states LEFT JOIN states_meta ON (states.metadata_id=states_meta.metadata_id) 

        LEFT JOIN state_attributes ON (states.attributes_id=state_attributes.attributes_id)

        WHERE state_attributes.shared_attrs LIKE '%sensor%';
     """)
    
    query = cursor.fetchall()

    
    sensors: list = []
    for line in query:
        # TODO cut everything before and after date / time
        
        # timestamps
        # print(line[3], flush=True)
        pass


        
    # columns = [col[0] for col in cursor.description]
    # rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # print(jsonify(rows), flush=True)

    conn.close()

    return jsonify(query)


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