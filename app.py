import os
import subprocess
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "uploads"
JOURNAL_DIR = "journals"


class LogEntry(db.Model):
    __tablename__ = "log_entries"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String)
    protocol = db.Column(db.String)
    logtype = db.Column(db.String)
    message = db.Column(db.String)


@app.route("/", methods=['GET', 'POST'])
def index():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if request.method == 'POST':
        # retrieve uploaded files
        uploaded_files = request.files.getlist("logfiles")
        
        for f in uploaded_files:
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

            # process the journal file using journalctl
            os.system(f"journalctl --file={full_path} >> {JOURNAL_DIR}/journal.log")

        # create database entries 
        create_entries()
        remove_journal()
        
        return redirect('/')

    else:
        # fetch all uploaded log entries and render 
        log_entries = LogEntry.query.order_by(LogEntry.timestamp).all()
        return render_template("index.html", log_entries=log_entries)


def create_entries():
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

            # skip if malformed 
            if len(parts) < 5:
                continue

            # extract protocol
            protocol = parts[4]

            # check if relevant protocol is present
            match_words = ["zigbee2mqtt", "zha", "zwave", "thread"]
            if any(word in protocol.lower() for word in match_words):
                protocol = refactor_protocol(protocol)
            else:
                continue

            # assemble timestamp
            timestamp = " ".join(parts[0:3])
            timestamp = refactor_timestamp(timestamp)

            # extract log type
            match_words = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            for i, part in enumerate(parts):
                if any(word in part.upper() for word in match_words):
                    logtype = refactor_type(part)
                    message = " ".join(parts[i + 1:])
                    break
            
            # if no logtype found
            if logtype == None:
                logtype = "None"
                message = " ".join(parts[5:])

            # create and add log entry to database
            log_entry = LogEntry( 
                timestamp=timestamp,
                protocol=protocol,
                logtype=logtype,
                message=message
            )
            db.session.add(log_entry)
    
    db.session.commit()


@app.route("/clearlogs", methods=['GET'])
def remove_db_entries():
    with app.app_context():
            db.session.query(LogEntry).delete()
            db.session.commit()
    return redirect('/')


def remove_journal():
    journal_log_path = os.path.join(JOURNAL_DIR, "journal.log")
    os.system(f"echo '' > {journal_log_path}")


def refactor_protocol(to_parse):
    if "zigbee2mqtt" in to_parse.lower():
        return "Zigbee2MQTT"
    elif "zha" in to_parse.lower():
        return "ZHA"
    elif "thread" in to_parse.lower():
        return "Thread"
    elif "zwave" in to_parse.lower():
        return "Z-Wave"
    else:
        return None


def refactor_type(to_parse):
    text = to_parse.upper()
    match_words = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    for word in match_words:
        if word in text:
            return word
    return None


def refactor_timestamp(to_parse):
    # split timestamp into month, day and time
    parts = to_parse.split()
    old_month, day, time = parts
    new_month: str

    # refactor date and time; Format: MM-DD HH:MM:SS
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for month in months: 
        if old_month in month:
            new_month = str(months.index(month) + 1)
            if len(new_month) < 2:
                new_month = "0" + new_month
    
    # rejoin timestamp
    date = "-".join([new_month, day])
    new_timestamp = " ".join([date, time])

    return new_timestamp


if __name__ == "__main__":
    app.run(debug=True)