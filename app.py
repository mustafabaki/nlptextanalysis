from flask import Flask, render_template, request,redirect, url_for
from flask import send_file
import os
import word_cloud
import naivebayes
import nltk 
import lda_70
import nmf_ready_to_use


app = Flask(__name__)
picFolder = os.path.join('static', 'pics')

app.config['UPLOAD_FOLDER'] = picFolder

@app.route('/')

def index():
    
    return render_template("index.html")

@app.route('/', methods =['POST'])
def test():
    language = request.form['language']
    algorithm = request.form['algorithm']
    f = request.files["file1"]
  
    f.save(os.path.join("uploads",f.filename))
    word_cloud.cloudify(f.filename)




    outname = f.filename+"_out.png"
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], outname)
    file1 = open("uploads/"+f.filename, 'r', encoding='utf-8')
    text = file1.read()
    if language == 'english' and algorithm == 'naivebayes':
       
        sentences = nltk.tokenize.sent_tokenize(text)
        topics =[]
        dominant_topic = naivebayes.predict_category(text)
        for i in range(len(sentences)):
            topics.append(naivebayes.predict_category(sentences[i]))

        topics = set(topics)
        return render_template("resultpage.html", img_file =pic1, algorithm = 'naivebayes', tpcs = topics, dominant = dominant_topic)
    elif language == 'turkish' and algorithm == 'lda':

        results = lda_70.lda70(text)


        return render_template("resultpage.html", img_file = pic1, algorithm = "lda", tpcs = results)
    
    elif language == 'english' and algorithm == 'nmf':
        results = nmf_ready_to_use.nmf_algorithm(text)
        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results)
        

@app.route('/', methods =['POST'])
def upload():
    
    return 'mission completed  :)'

if __name__=="__main__":
    app.run(debug=True)