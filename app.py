from flask import Flask, render_template, request,redirect, url_for
from flask import send_file
import os
import word_cloud


app = Flask(__name__)
picFolder = os.path.join('static', 'pics')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route('/')

def index():
    
    return render_template("index.html")

@app.route('/', methods =['POST'])
def test():
    select = request.form['language']
    f = request.files["file1"]
  
    f.save(os.path.join("uploads",f.filename))
    word_cloud.cloudify(f.filename)




    outname = f.filename+"_out.png"
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], outname)
     
    
    return render_template("resultpage.html", img_file =pic1)

@app.route('/', methods =['POST'])
def upload():
    
    return 'mission completed  :)'

if __name__=="__main__":
    app.run(debug=True)