import os
import socket
import subprocess
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "../../uploads"
MOUNT_DIR = "/mnt/hassos"

def get_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port



@app.post("/use-image")
def use_image():
    # TODO datum und uhrzeit spanne hier retrieven und in query mit einbauen? wenn nicht geht dann in code

    db_path = "file:" + MOUNT_DIR + "/supervisor/homeassistant/home-assistant_v2.db?mode=ro"

    conn = sqlite3.connect(db_path, uri=True)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATETIME(IIF(states.last_changed_ts IS NULL,states.last_updated_ts,states.last_changed_ts), 'unixepoch', 'localtime') AS ts, 
        states_meta.entity_id AS entityID,
        state_attributes.shared_attrs AS attributes,
        states.state AS state

        FROM states LEFT JOIN states_meta ON (states.metadata_id=states_meta.metadata_id) 

        LEFT JOIN state_attributes ON (states.attributes_id=state_attributes.attributes_id)

        WHERE state_attributes.shared_attrs LIKE '%sensor%';
     """)
     # removed: , hex(states.context_id_bin) AS ctxID
     #            states.state_id AS stateID,
    
    query = cursor.fetchall()

    conn.close()

    return jsonify(query)


if __name__ == "__main__":
    port = get_port()
    print(f"PORT:{port}", flush=True)
    app.run(port=port, debug=False, use_reloader=False)