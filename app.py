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
JOURNAL_DIR = "journals"
CONFIG_DIR = "config"

# mime types
JOURNAL_TYPE = 'application/x-linux-journal'

# constants
MIN_PARTS_JOURNAL = 8
MIN_PARTS_LOG = 3
NETWORK_KEY_OFFSET = 16
EXT_PAN_ID_OFFSET = 8


### database models
class LogEntry(db.Model):
    __tablename__ = "log_entries"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String)
    protocol = db.Column(db.String)
    logtype = db.Column(db.String)
    message = db.Column(db.String)


class ConfigEntry(db.Model):
    __tablename__ = "config_entries"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String)
    infotype = db.Column(db.String)
    value = db.Column(db.String)


### web
@app.route("/", methods=['GET'])
def index():
    # fetch all uploaded log entries and render 
    log_entries = LogEntry.query.order_by(LogEntry.timestamp).all()
    config_entries = ConfigEntry.query.order_by(ConfigEntry.infotype).all()
    return render_template("index.html", log_entries=log_entries, config_entries=config_entries)


@app.route("/uploadlogs", methods=['POST'])
def upload_logs():
    # make sure uploads folder exists and create it if it doesn't
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    is_uploaded: bool = False
    filetype: str = None

    # retrieve uploaded files
    uploaded_files = request.files.getlist("logfiles")
    
    for f in uploaded_files:
        is_uploaded = True

        # secure file
        rel_path = f.filename
        safe_path = os.path.normpath(rel_path)

        # prevent directory traversal attacks
        if safe_path in (".", "..") or not f.filename:
            continue

        # save file
        full_path = os.path.join(UPLOAD_DIR, safe_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        f.save(full_path)

        # get filetype
        filetype = magic.from_file(f'{full_path}', mime = True)

        # process the journal file using journalctl if journal-file
        if filetype == JOURNAL_TYPE:
            os.system(f"journalctl --file={full_path} >> {JOURNAL_DIR}/journal.log")
        else:
            os.system(f"cat {full_path} >> {JOURNAL_DIR}/journal.log")

    # create database entries y
    if is_uploaded:
        create_log_entries(filetype)
        remove_journal()
    
    return redirect('/')


@app.route("/clearlogs", methods=['GET'])
def remove_db_entries():
    with app.app_context():
            db.session.query(LogEntry).delete()
            db.session.commit()
    return redirect('/')


@app.route("/uploadconfigfiles", methods=['POST'])
def upload_config_files():
    # make sure uploads folder exists and create it if it doesn't
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # retrieve uploaded files
    f = request.files.get("configfiles")

    if f:

        # secure file
        rel_path = f.filename
        safe_path = os.path.normpath(rel_path)

        # prevent directory traversal attacks
        if safe_path in (".", "..") or not f.filename:
            return redirect('/')

         # save file
        full_path = os.path.join(UPLOAD_DIR, safe_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        f.save(full_path)

        # TODO consider removing and use the filepath instead? (as parameter)
        os.system(f"cat {full_path} >> {CONFIG_DIR}/config.log")

        # create database entries 
        # create_config_entries(f.filename)
        # remove_config()

    return redirect('/')


@app.route("/clearconfigfiles", methods=['GET'])
def clear_config_files():
    with app.app_context():
            db.session.query(ConfigEntry).delete()
            db.session.commit()
    return redirect('/')


def create_log_entries(filetype):
    journal_log_path = os.path.join(JOURNAL_DIR, "journal.log")
    with open(journal_log_path, 'r') as f:
        for line in f:
            # declare variables
            timestamp: str = None
            protocol: str = None
            logtype: str = None
            message: str = None

            # split line into parts
            parts = line.split()
                
            # filter out unneeded logs
            if filetype == JOURNAL_TYPE:
                # skip if malformed 
                if len(parts) < MIN_PARTS_JOURNAL:
                    continue
                match_words = ["audit", "kernel", "hass", "homeassistant", "fstrim", "systemd", "mosquitto", "rauc", "config", "vscode"]
                to_match = parts[4]
                if any(word in to_match.lower() for word in match_words):
                    continue
            else:
                if len(parts) < MIN_PARTS_LOG:
                    continue

            # get the protocol
            protocol = handle_protocol(parts)

             # extract logtype and message
            logtype, message = handle_logtype_and_message(parts)
            
            # find out timestamp format
            if protocol == "ring-mqtt":
                timestamp = handle_timestamp_ring(parts)
            elif filetype == JOURNAL_TYPE:
                timestamp = handle_timestamp_journal(parts)
            # elif protocol == "Zigbee2MQTT":
            #     timestamp = handle_z2m()
            # elif protocol == "ZHA":
            #     timestamp = handle_zha()
            # elif protocol == "Z-Wave":
            #     timestamp = handle_zwave()
            # elif protocol == "Thread":
            #     timestamp = handle_thread()
            else:
                timestamp = handle_timestamp(parts)
            
            if timestamp == None:
                continue

            if protocol == "Zigbee2MQTT":
                message = format_z2m_message(message)

            # create and add log entry to database
            log_entry = LogEntry(
                timestamp=timestamp,
                protocol=protocol,
                logtype=logtype,
                message=message
            )
            db.session.add(log_entry)
    
    db.session.commit()


# def create_config_entries(filename):
#     match filename:
#         case "configuration.yaml":
#             handle_configurations(filename)
#         # case "configuration.yaml (z2m)":
#         #     handle_configuration_z2m(filename) 
#         case _:
#             print("error")
#             return


### Handle timestamp
def handle_timestamp_journal(parts):
    timestamp = " ".join(parts[5:7])
    timestamp = remove_special_chars(timestamp, '[', ']')
    return timestamp


def handle_timestamp_ring(parts):
    timestamp = parts[5]

    # split timestamp appart
    datetime = timestamp.split('T')

    time = []
    if len(datetime) > 1:
        time = datetime[1].split('.')

    # rebuild timestamp
    if len(datetime) > 1 and len(time) > 1:
        timestamp = " ".join([datetime[0], time[0]])
        
    return timestamp


def handle_timestamp(parts):
    timestamp = " ".join(parts[0:2])
    timestamp = remove_special_chars(timestamp, '[', ']')
    return timestamp


### Handle parts of the log
def handle_protocol(parts):
    protocol = None
    match_words = ["z2m", "zh:", "zha", "thread", "zwave", "ring"]
    for part in parts:
        for word in match_words:
            if word in part:
                protocol = word
                break

    match protocol:
        case "z2m":
            return "Zigbee2MQTT"
        case "zh:": 
            return "Zigbee2MQTT"
        case "zha":
            return "ZHA"
        case "thread":
            return "Thread"
        case "zwave":
            return "Z-Wave"
        case "ring":
            return "ring-mqtt"
        case _:
            return "unknown"


def handle_logtype_and_message(parts):
    logtype: str
    message: str
    match_words = ["debug", "info", "warning", "error", "critical"]

    for i, part in enumerate(parts):
        for word in match_words:
            if word in part.lower():
                logtype = word
                message = " ".join(parts[i + 1:])
                return logtype, message
    # if no logtype found
    logtype = "unknown"
    message = " ".join(parts)
    return logtype, message


def format_z2m_message(message):
    parts = message.split()
    header = " ".join(parts[0:3])
    if not header == "z2m:mqtt: MQTT publish:":
        return message

    # search for index where payload starts
    for i, part in enumerate(parts):
        if part == "payload":
            break

    # rebuild message
    topic = "Topic: " + " ".join(parts[4:i])
    payload = "Payload: " + " ".join(parts[i + 1:])
    message = topic + "<br>" + payload

    return message


### Handle files
# def handle_configurations(filename):
#     config_log_path = os.path.join(CONFIG_DIR, "config.log")
#     with open(config_log_path, 'r') as f:
#         if "mqtt:" in f.read():
#             handle_configuration_z2m(filename)
#         else:
#             handle_configuration(filename)
#     return 


# def handle_configuration(filename):
#     config_log_path = os.path.join(CONFIG_DIR, "config.log")
#     match_words = ["debug", "info", "warning", "error", "critical", "logger"]
#     logger_detected: bool = False

#     with open(config_log_path, 'r') as f:
#         for line in f:
#             # declare variables
#             infotype: str = "Default"
#             value: str = None

#             # remove commented out part of the line
#             if '#' in line:
#                 line = line.split("#")[0]

#             # split into parts
#             parts = line.split(":")

#             # filter out line if no relevant information 
#             if len(parts) != 2:
#                 continue

#             if not any(word in line.lower() for word in match_words):
#                 # TODO do i want that?
#                 value = line
#                 # continue
#             elif "logger:" in line:
#                 infotype: str = "Logging"
#                 value = "Custom Logging Configuration Found"
#                 logger_detected = True
#             else:
#                 infotype = "Logging Configuration"
#                 value = line
            
#             # create and add config entry to database
#             config_entry = ConfigEntry(
#                 filename=filename,
#                 infotype=infotype,
#                 value=value
#             )
#             db.session.add(config_entry)

#     if not logger_detected:
#         infotype = "Logging"
#         value = "No relevant information regarding logging found which probably means that only Z2M logs are findable" \
#                 "since the other protocols configuration has to be set to debug mode"
#         config_entry = ConfigEntry(
#             filename=filename,
#             infotype=infotype,
#             value=value
#         )
#         db.session.add(config_entry)

#     db.session.commit()


# def handle_configuration_z2m(filename):
#     # variables
#     config_log_path = os.path.join(CONFIG_DIR, "config.log")
#     pre_infotype: str = ""
#     infotype: str = "Default"
#     value: str = ""
#     # match_words = ["debug", "info", "warning", "error", "critical", "logger"]

#     with open(config_log_path, 'r') as f:
#         # read file content
#         file_content = f.readlines()

#         for i, line in enumerate(file_content):
#             # remove commented out part of the line
#             if '#' in line:
#                 line = line.split("#")[0]
            
#             if "network_key:" in line:
#                 infotype = "network_key"
#                 decimals = file_content[i + 1 : i + NETWORK_KEY_OFFSET + 1]
#                 to_hex: str = convert_to_hex(decimals)
#                 value = to_hex

#                 # create and add config entry to database
#                 config_entry = ConfigEntry(
#                     filename=filename + " (z2m)",
#                     infotype=pre_infotype + infotype,
#                     value=value
#                 )
#                 db.session.add(config_entry)
#                 continue

#             # TODO method to encapsulate redundant code
#             if "ext_pan_id:" in line:
#                 infotype = "ext_pan_id"
#                 decimals = file_content[i + 1 : i + EXT_PAN_ID_OFFSET + 1]
#                 to_hex: str = convert_to_hex(decimals)
#                 value = to_hex

#                 # create and add config entry to database
#                 config_entry = ConfigEntry(
#                     filename=filename + " (z2m)",
#                     infotype=pre_infotype + infotype,
#                     value=value
#                 )
#                 db.session.add(config_entry)
#                 continue

#             if "devices:" in line: 
#                 pre_infotype = ""
#                 infotype = "device aliases"
#                 devices = file_content[i + 1:] # TODO nicht alle devices... BR LED stripes fehlt. (maaybe ganz file_content printen als test?)
#                                                 # TODO actually es fehlt immer das letzte.... (bzw eins davon, zb mqtt - server) hat safe was mit den i's zu tun 

#                 value = " ".join(devices)

#                 # create and add config entry to database
#                 config_entry = ConfigEntry(
#                     filename=filename + " (z2m)",
#                     infotype=infotype,
#                     value=value
#                 )
#                 db.session.add(config_entry)
#                 break
            
#             ## default behaviour

#             # split into parts
#             parts = line.split(":")

#             # filter out line if no relevant information 
#             if len(parts) != 2:
#                 continue

#             # default behaviour
#             value = parts[1]

#             if value in "\n":
#                 pre_infotype = parts[0] + " - "
#                 continue

#             infotype = parts[0]
            
#             # create and add config entry to database
#             config_entry = ConfigEntry(
#                 filename=filename + " (z2m)",
#                 infotype=pre_infotype + infotype,
#                 value=value
#             )
#             db.session.add(config_entry)

#     db.session.commit()
#     return


### Helper functions
def remove_journal():
    journal_log_path = os.path.join(JOURNAL_DIR, "journal.log")
    os.system(f"echo '' > {journal_log_path}")


def remove_config():
    config_log_path = os.path.join(CONFIG_DIR, "config.log")
    os.system(f"echo '' > {config_log_path}")


def remove_special_chars(to_parse, left, right):
    if to_parse.startswith(left):
        to_parse = to_parse.replace(left, '')
    else:
        return None
    
    if to_parse.endswith(right):
        to_parse = to_parse.replace(right, '')
    else: 
        return None
    
    return to_parse


def convert_to_hex(decimals):
    hex_list = []
    for decimal in decimals:
        decimal = decimal.replace("    - ", "")
        hex_list.append(hex(int(decimal)))
        # to_hex += hex(decimal) + " "
    return " ".join(hex_list)


if __name__ == "__main__":
    app.run(debug=True)