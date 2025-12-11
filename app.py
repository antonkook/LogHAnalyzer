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

# model for uploaded log files
# class LogFile(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(200), nullable=False)       # file name
#     filepath = db.Column(db.String(500), nullable=False)       # full path on server
#     processed = db.Column(db.Boolean, default=False)           # whether the log was processed
#     date_uploaded = db.Column(db.DateTime, default=datetime.now)

#     def __repr__(self):
#         return f'<LogFile {self.filename}>'

# class LogFile(db.Model):
#     __tablename__ = "log_files"
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String, nullable=False)
#     filepath = db.Column(db.String, nullable=False)
#     processed = db.Column(db.Boolean, default=False)
#     date_uploaded = db.Column(db.DateTime, default=datetime.now)
#     entries = db.relationship("LogEntry", backref="logfile", lazy=True)


class LogEntry(db.Model):
    __tablename__ = "log_entries"
    id = db.Column(db.Integer, primary_key=True)
    # logfile_id = db.Column(db.Integer, db.ForeignKey("log_files.id"), nullable=False)
    timestamp = db.Column(db.String)
    logtype = db.Column(db.String)
    device = db.Column(db.String)
    attributes = db.Column(db.String)


# route for uploading and viewing log files
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("logfiles")

        for f in uploaded_files:
            # save files safely
            # safe_name = secure_filename(f.filename)
            # save_path = os.path.join(UPLOAD_DIR, safe_name)
            # os.makedirs(os.path.dirname(save_path), exist_ok=True)  # ensure folder exists
            # f.save(save_path)

            rel_path = f.filename
            filename_only = os.path.basename(f.filename)
            safe_path = os.path.normpath(rel_path)
            full_path = os.path.join(UPLOAD_DIR, safe_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            f.save(full_path)

            # print(f"Saved uploaded file to {full_path}")
            # print(f"Original filename: {filename_only}")

            # process the journal file using journalctl
            # os.system(f"journalctl --file={full_path} > {JOURNAL_DIR}/{filename_only}.log")
            os.system(f"journalctl --file={full_path} >> {JOURNAL_DIR}/journal.log")

            # TODO consider removing the uploaded files



            # create a database entry for the log file
            # new_log = LogFile(filename=safe_name, filepath=safe_path)
            # db.session.add(new_log)

        # create_entries()

        # db.session.commit()
        
        return redirect('/')

    else:
        # fetch all uploaded log files to display
        create_entries()
        #log_files = LogFile.query.order_by(LogFile.date_uploaded).all()
        return render_template("index.html")
        # return render_template("index.html", log_files=log_files)


def create_entries():
    journal_log_path = os.path.join(JOURNAL_DIR, "journal.log")
    with open(journal_log_path, 'r') as f:
        for line in f:
            parts = line.split()

            # TODO write it in a cleaner way (if contains zigbee2mqtt make it Zigbee2MQTT and concat the type like info, etc)
            logtype = parts[4]

            match_words = ["zigbee2mqtt"]
            if not any(word in logtype for word in match_words):
                continue

            # assemble timestamp
            timestamp = " ".join(parts[0:3])

            # TODO find out how other protocols log this so i can adjust
            device = parts[7]
            attributes = " ".join(parts[8:])

            # debug
            to_parse = f"Parsed entry - Timestamp: {timestamp}, Type: {logtype}, Device: {device}, Attributes: {attributes}"
            os.system(f"echo '{to_parse}' >> {JOURNAL_DIR}/debug.log")

            log_entry = LogEntry( 
                timestamp=timestamp,
                logtype=logtype,
                device=device,
                attributes=attributes
            )
            #db.session.add(log_entry)
    #db.session.commit()



if __name__ == "__main__":
    app.run(debug=True)