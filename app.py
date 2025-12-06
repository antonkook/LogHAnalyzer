import os
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

# model for uploaded log files
class LogFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)       # file name
    filepath = db.Column(db.String(500), nullable=False)       # full path on server
    processed = db.Column(db.Boolean, default=False)           # whether the log was processed
    date_uploaded = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<LogFile {self.filename}>'

# route for uploading and viewing log files
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("logfiles")

        for f in uploaded_files:
            # save files safely
            safe_name = secure_filename(f.filename)
            save_path = os.path.join(UPLOAD_DIR, safe_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # ensure folder exists
            f.save(save_path)

            # create a database entry for the log file
            new_log = LogFile(filename=safe_name, filepath=save_path)
            db.session.add(new_log)

        db.session.commit()
        return redirect('/')

    else:
        # fetch all uploaded log files to display
        log_files = LogFile.query.order_by(LogFile.date_uploaded).all()
        return render_template("index.html", log_files=log_files)

if __name__ == "__main__":
    app.run(debug=True)