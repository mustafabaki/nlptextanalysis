from flask import Flask, render_template, request,redirect, url_for
from flask import send_file
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

@app.route('/')

def index():
    
    return render_template("index.html")

@app.route('/', methods =['POST'])
def test():
    select = request.form['language']
    f = request.files["file1"]
    f.save(os.path.join("uploads",f.filename))
    return 'OK'

@app.route('/', methods =['POST'])
def upload():
    
    return 'mission completed  :)'

if __name__=="__main__":
    app.run(debug=True)