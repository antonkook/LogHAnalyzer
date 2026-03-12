import os
import socket
import subprocess
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "uploads"
MOUNT_DIR = "mountpoint"


def get_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@app.post("/use-image")
def use_image():
    # check for errors
    if not Path(MOUNT_DIR).is_dir():
        print("Error: Image file not mounted", flush=True)
        return "error"

    # retrieve json
    data = request.get_json()

    # get parameters
    min_ts = data["min_ts"]
    max_ts = data["max_ts"]
    checked = data["checked"]
    filterMore = data["filterMore"]
    selected = data["selected"]

    min_str = f" AND ts >= '{min_ts}'"
    max_str = f" AND ts <= '{max_ts}'"
    checked_str = f" AND (entityID LIKE 'sensor.%' OR entityID LIKE 'binary_sensor.%')"
    filterMore_str = f""" 
        AND entityID NOT LIKE '%battery' 
        AND entityID NOT LIKE '%voltage' 
        AND entityID NOT LIKE '%battery_state' 
        AND entityID NOT LIKE '%sun_next_dawn' 
        AND entityID NOT LIKE '%sun_next_setting' 
        AND entityID NOT LIKE '%sun_next_midnight' 
        AND entityID NOT LIKE '%sun_next_rising' 
        AND entityID NOT LIKE '%sun_next_dusk' 
        AND entityID NOT LIKE '%sun_next_noon'
        AND entityID NOT LIKE '%battery_low' 
        AND entityID NOT LIKE '%version' 
        AND entityID NOT LIKE '%backup' 
        AND entityID NOT LIKE '%battery_level' 
        AND entityID NOT LIKE '%charger_type' 
        AND entityID NOT LIKE '%connection_type'
        AND entityID NOT LIKE '%power_status' 
        AND entityID NOT LIKE '%last_update_trigger'
        AND entityID NOT LIKE '%backup_manager_state'
        AND entityID NOT LIKE '%connection_state'
    """ 
    # AND entityID NOT LIKE '%ssid'
    # AND entityID NOT LIKE '%bssid'
    # AND entityID NOT LIKE '%sim_1'
    # AND entityID NOT LIKE '%sim_2'
    # AND entityID NOT LIKE '%audio_output'

    tail: str = ""

    if checked:
        tail += checked_str

    if filterMore:
        tail += filterMore_str

    if min_ts:
        tail += min_str
    
    if max_ts: 
        tail += max_str

    match (int(selected)):
        case 1: tail += f" ORDER BY ts;"
        case 2: tail += f" ORDER BY entityID;"
        case 3: tail += f" ORDER BY attributes;"
        case 4: tail += f" ORDER BY state;"
        case 5: tail += f" ORDER BY device_class;"
        case _: tail += f" ORDER BY ts;"

    # debugging
    # print(f"TAIL IS {tail}", flush=True)

    db_path = "file:" + MOUNT_DIR + "/supervisor/homeassistant/home-assistant_v2.db?mode=ro"
    conn = sqlite3.connect(db_path, uri=True)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT DATETIME(IIF(states.last_changed_ts IS NULL,states.last_updated_ts,states.last_changed_ts), 'unixepoch') AS ts, 
        states_meta.entity_id AS entityID,
        state_attributes.shared_attrs AS attributes,
        states.state AS state,
        json_extract(state_attributes.shared_attrs, '$.device_class') AS device_class

        FROM states LEFT JOIN states_meta ON (states.metadata_id=states_meta.metadata_id) 

        LEFT JOIN state_attributes ON (states.attributes_id=state_attributes.attributes_id)

        WHERE 1=1
     """ + tail)
     # removed: , hex(states.context_id_bin) AS ctxID
     #            states.state_id AS stateID,
    
    query = cursor.fetchall()

    # debug
    # print(query, flush=True)

    conn.close()

    return jsonify(query)


if __name__ == "__main__":
    port = get_port()
    print(f"PORT:{port}", flush=True)
    app.run(port=port, debug=False, use_reloader=False)