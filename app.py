import os
from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# app
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# directories
UPLOAD_DIR = "uploads"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist("logfiles")

        for f in files:
            rel_path = f.filename

            # normalize path and prevent escaping
            safe_path = os.path.normpath(rel_path)

            # mebuild folder structure inside uploads/
            full_path = os.path.join(UPLOAD_DIR, safe_path)

            # make sure parent folder exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # save the file
            f.save(full_path)

            print("Saved:", full_path)

        return render_template("index.html")
        
        # task_content = request.form['file']
        # new_task = Todo(content=task_content)

        # try:
        #     db.session.add(new_task)
        #     db.session.commit()
        #     return redirect('/')
        # except:
        #     return 'There was an issue adding your task'

    else:
        return render_template("index.html")
    

if __name__ == "__main__":
    app.run(debug=True)
