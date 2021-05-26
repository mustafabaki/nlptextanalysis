from flask import Flask, render_template, request,redirect, url_for,send_from_directory
from flask import send_file
import os

from flask.globals import current_app
import word_cloud
import naivebayes
import nltk 
import lda_70
import nmf_ready_to_use
import xlwt



app = Flask(__name__)
picFolder = os.path.join('static', 'pics')
app.config['EXCEL_FILES'] = os.path.join('static', 'excelfiles')
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

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=0
        for value in topics:
            sheet.write(i,0,i )
            sheet.write(i,1, value)
            i = i+1        
        workbook.save("static/excelfiles/"+f.filename+".xls")
        name = f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        
        

        return render_template("resultpage.html", img_file =pic1, algorithm = 'naivebayes', tpcs = topics, dominant = dominant_topic, excelfile =excelfile)
    elif language == 'turkish' and algorithm == 'lda':

        results = lda_70.lda70(text)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Score')
        sheet.write(0,1,'Topic Vocabulary')
        for value in results:
            sheet.write(i,0, value.topic)
            sheet.write(i,1,value.score)
            i=i+1

        workbook.save("static/excelfiles/"+f.filename+".xls")
        name = f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)

        return render_template("resultpage.html", img_file = pic1, algorithm = "lda", tpcs = results, excelfile = excelfile)
    
    elif language == 'english' and algorithm == 'nmf':
        results = nmf_ready_to_use.nmf_algorithm(text)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Topic Vocabulary')
        sheet.write(0,1,'Accuracy Score')
        for value in results:
            sheet.write(i,0, value.topic)
            sheet.write(i,1,value.score)
            i=i+1

        workbook.save("static/excelfiles/"+f.filename+".xls")
        name = f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)


        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results , excelfile = excelfile)
        

@app.route('/', methods =['POST'])
def upload():
    
    return 'mission completed  :)'

@app.route('/download')
def download(thepath):
    return send_file(thepath, as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)