from flask import Flask, render_template, request,redirect, url_for,send_from_directory
from flask import send_file
from flask_bootstrap import Bootstrap
from flask_login.utils import logout_user
from flask_wtf import FlaskForm, form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  LoginManager, UserMixin, login_user, login_required, current_user
from flask.globals import current_app
import os
import word_cloud
import naivebayes
import nltk 
from PIL import Image
import numpy as np
import lda_70
import nmf_ready_to_use
import xlwt
import lda_en_30_with_saved_model
import pam_eng
import sendemail
import nmf_with_user_data_en
import tr_lda_choice
import en_lda_choice
import nmf_with_user_data_tr
from multiprocessing import Process, freeze_support, Queue



app = Flask(__name__)
bootstrap = Bootstrap(app)
picFolder = os.path.join('static', 'pics')
app.config['EXCEL_FILES'] = os.path.join('static', 'excelfiles')
app.config['UPLOAD_FOLDER'] = picFolder
app.config['TEXT_FOLDER'] = os.path.join('static','texts')
app.config["SECRET_KEY"] = "any string works here"
# location of the database/ you should change this to your relative path directory 
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///database.db"


# initializing the database and using  helper tools
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# defines the database for storing user details  / creating the model
class User(UserMixin, db.Model):
    """
    This User class has 4 attributes:
    id : user's id
    username: username of the user
    email: email of the user
    password: password of the user
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    """ 
    This function is used to authenticate the users
    """
    return User.query.get(int(user_id))


def __repr__(self):
    return "<username %r >" % self.id

# login class
class LoginForm(FlaskForm):
    """ 
     This class collects the username and password  textfields  as stringfields from the login html (Login class)
    """
    username = StringField(
        "username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "password", validators=[InputRequired(), Length(min=8, max=80)]
    )
    remember = BooleanField("remember me")

# sign up class
class RegisterForm(FlaskForm):
    """ 
    This class collects the username and password  textfields  as stringfields from the registerform html (register class)
    """
    email = StringField(
        "email",
        validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)],
    )
    username = StringField(
        "username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "password", validators=[InputRequired(), Length(min=8, max=80)]
    )

     
@app.route("/login", methods=["GET", "POST"])

def login():
    """ 
    login function / where i compare the hashed password
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if  check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return  '<h1> Invaild username or password </h1>'
        #return "<h1>" + form.username.data + " " + form.password.data + "</h1>"
    return render_template("login.html", form=form)



@app.route("/signup", methods=["GET", "POST"])
def signup():
    """ 
     sign up function/ where the passwords are hashed
     """
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method= 'sha256')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        return "<h1> New user has been created! <!h1>"
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template("signup.html", form=form)



@app.route('/dashboard')
@login_required
def dashboard():
    """ 
    routes the user into the application with login check
     """
    return render_template('index.html', name=current_user.username, auth = 'yes')

# routes the user into the application without login check
@app.route('/free')
def free():
    """This function redirects the guest users to the appropriate page. """
    return render_template('index.html', name= "Guest User", auth = 'no')

 # sign the user out 
@app.route('/logout')
@login_required
def logout():
   """Logs out the user """
   logout_user()
   return redirect(url_for('index'))

@app.route('/')
def index():
    """ 
    app route for the index2 html
     """
    return render_template("index2.html")

@app.route('/', methods =['POST'])
def test():
    language = request.form['language']
    algorithm = request.form['algorithm']
    shape = request.form['Word']
    f = request.files["file1"]
    dataset = request.files["file2"]
    if current_user.is_authenticated:
        usernameee = current_user.username
        isAuthenticated = 'yes'
    else:
        usernameee = "guest"
        isAuthenticated = 'no'
    f.save(os.path.join("uploads",usernameee+"-"+f.filename))
    f.save(os.path.join("static/texts",usernameee+"-"+f.filename))

    
    word_cloud.cloudify(usernameee+"-"+f.filename, shape)
    
    outname = usernameee+"-"+f.filename+"_out.png"
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], outname)
    file1 = open("uploads/"+usernameee+"-"+f.filename, 'r', encoding='utf-8')
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
        workbook.save("static/excelfiles/"+usernameee+"-"+f.filename+".xls")
        name = usernameee+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        if current_user.is_authenticated:
            sendemail.send_email(pic1,excelfile, current_user.email)

        return render_template("resultpage.html", img_file =pic1, algorithm = 'naivebayes', tpcs = topics, dominant = dominant_topic, excelfile =excelfile)
    elif language == 'turkish' and algorithm == 'lda':
        
        stopwords = request.files['file3']
        if stopwords.filename != "":
            choice = True
            stopwords.save(os.path.join("uploads",usernameee+"-"+stopwords.filename))
        else:
            choice = False
        if  request.form['ngram'] == 'True':
            ngram_choice = True
            ngram_num = int(request.form['number'])
        else:
            ngram_choice = False  

        results = lda_70.lda_70(text,ngram_num,ngram_choice, choice, "uploads/"+usernameee+"-"+stopwords.filename)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Score')
        sheet.write(0,1,'Topic Vocabulary')
        for value in results:
            sheet.write(i,0, value.topic)
            sheet.write(i,1,value.score)
            i=i+1

        workbook.save("static/excelfiles/"+usernameee+"-"+f.filename+".xls")
        name = usernameee+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        if current_user.is_authenticated:
            sendemail.send_email(pic1,excelfile, current_user.email)

        return render_template("resultpage.html", img_file = pic1, algorithm = "lda", tpcs = results, excelfile = excelfile)
    
    elif language == 'english' and algorithm == 'nmf':
        results = nmf_ready_to_use.nmf_algorithm(text, int(request.form['number']))
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Topic Vocabulary')
        sheet.write(0,1,'Accuracy Score')
        for value in results:
            sheet.write(i,0, value.topic)
            sheet.write(i,1,value.score)
            i=i+1

        workbook.save("static/excelfiles/"+usernameee+"-"+f.filename+".xls")
        name = usernameee+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        if current_user.is_authenticated:
            sendemail.send_email(pic1,excelfile, current_user.email)


        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results , excelfile = excelfile)
    elif language == 'english' and algorithm == 'pam':
        results = pam_eng.pam_english("uploads/"+usernameee+"-"+f.filename)
        workbook = xlwt.Workbook()
        
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Topic')
        sheet.write(0,1,'Sub Topics')
        sheet.write(0,2,'Accuracy Score')

        for value in results:
            sheet.write(i,0, value['topic'])
            
            sheet.write(i,1,str(value['subs']))
            sheet.write(i,2,value['prob'])
            i=i+1

        workbook.save("static/excelfiles/"+usernameee+"-"+f.filename+".xls")
        name = usernameee+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        if current_user.is_authenticated:
            sendemail.send_email(pic1,excelfile, current_user.email)

        return render_template("resultpage.html",img_file =pic1, algorithm = "pam", tpcs = results, excelfile = excelfile)
    elif language == 'turkish' and dataset.filename != "" and request.form['algorithm']=='lda2':
        
        dataset.save(os.path.join("uploads",usernameee+"-"+dataset.filename))
        stopwords = request.files['file3']
        if stopwords.filename != "":
            choice = True
            stopwords.save(os.path.join("uploads",usernameee+"-"+stopwords.filename))
        else:
            choice = False
        if  request.form['ngram'] == 'True':
            ngram_choice = True
            ngram_num = int(request.form['number'])
        else:
            ngram_choice = False  
        
        freeze_support()
        Q = Queue()
        p1=Process(target=tr_lda_choice.f,args=("uploads/"+usernameee+"-"+dataset.filename, request.form['column'], choice, "uploads/"+usernameee+"-"+stopwords.filename, ngram_choice,ngram_num, "uploads/"+usernameee+"-"+f.filename,int(request.form['topic_number']), Q,))

        p1.start()
        p1.join()

        results = Q.get()
        

        return render_template("resultpage.html",img_file =pic1, algorithm = "lda", tpcs = results)

    elif language == 'english' and dataset.filename != "" and algorithm == "nmf2":
        dataset.save(os.path.join("uploads",usernameee+"-"+dataset.filename))
        stopwords = request.files['file3']
        if stopwords.filename != "":
            choice = True
            stopwords.save(os.path.join("uploads",usernameee+"-"+stopwords.filename))
        else:
            choice = False
        if  request.form['ngram'] == 'True':
            ngram_choice = True
            ngram_num = int(request.form['number'])
        else:
            ngram_choice = False  
        file3 = open("uploads/"+usernameee+"-"+stopwords.filename, 'r', encoding='utf-8')
        stopwordss = file3.read()
        results = nmf_with_user_data_en.nmf_with_dataset("uploads/"+usernameee+"-"+dataset.filename,request.form['column'], choice,stopwordss,ngram_num,text)
        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results )
    elif language == 'english' and dataset.filename != "" and algorithm == 'lda2':
        dataset.save(os.path.join("uploads",usernameee+"-"+dataset.filename))
        stopwords = request.files['file3']
        if stopwords.filename != "":
            choice = True
            stopwords.save(os.path.join("uploads",usernameee+"-"+stopwords.filename))
        else:
            choice = False
        if  request.form['ngram'] == 'True':
            ngram_choice = True
            ngram_num = int(request.form['number'])
        else:
            ngram_choice = False  
        
        freeze_support()
        Q = Queue()
        p1=Process(target=en_lda_choice.f,args=("uploads/"+usernameee+"-"+dataset.filename, request.form['column'], choice, "uploads/"+usernameee+"-"+stopwords.filename, ngram_choice,ngram_num, "uploads/"+usernameee+"-"+f.filename, int(request.form['topic_number']),Q,))
        p1.start()
        p1.join()

        results = Q.get()
        return render_template("resultpage.html",img_file =pic1, algorithm = "lda", tpcs = results)
    elif language == 'turkish' and dataset.filename != "" and algorithm == "nmf2":
        dataset.save(os.path.join("uploads",usernameee+"-"+dataset.filename))
        stopwords = request.files['file3']
        if stopwords.filename != "":
            choice = True
            stopwords.save(os.path.join("uploads",usernameee+"-"+stopwords.filename))
        else:
            choice = False
        if  request.form['ngram'] == 'True':
            ngram_choice = True
            ngram_num = int(request.form['number'])
        else:
            ngram_choice = False  
        file3 = open("uploads/"+usernameee+"-"+stopwords.filename, 'r', encoding='utf-8')
        stopwordss = file3.read()
        results = nmf_with_user_data_tr.nmf_with_dataset("uploads/"+usernameee+"-"+dataset.filename,request.form['column'], choice,stopwordss,ngram_num,text)
        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results )
    elif language == 'english' and algorithm == 'lda':
        results = lda_en_30_with_saved_model.lda(text)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("results")
        i=1
        sheet.write(0,0,'Score')
        sheet.write(0,1,'Topic Vocabulary')
        for value in results:
            sheet.write(i,0, value.topic)
            sheet.write(i,1,value.score)
            i=i+1

        workbook.save("static/excelfiles/"+usernameee+"-"+f.filename+".xls")
        name = usernameee+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        if current_user.is_authenticated:
            sendemail.send_email(pic1,excelfile, current_user.email)

        return render_template("resultpage.html", img_file = pic1, algorithm = "lda", tpcs = results, excelfile = excelfile)


@app.route('/previous')
@login_required
def pull_previous():
    """
    This function is used to list the previous results.
    It returns the previous files and results.
    """
    pics = []
    texts = []
    excels = []

    all = []

    directory = r'static\\pics'
    for filename in os.listdir(directory):
        if current_user.username in filename:
            pics.append(os.path.join(directory,filename))
    
    directory = r'static\\texts'
    for filename in os.listdir(directory):
        if current_user.username in filename:
            texts.append(os.path.join(directory,filename))

    directory = r'static\\excelfiles'
    for filename in os.listdir(directory):
        if current_user.username in filename:
            excels.append(os.path.join(directory,filename))

    for i in range(len(pics)):
        add = {'picture': pics[i], 'text': texts[i], 'excel': excels[i]}
        all.append(add)


    print('here is the all:')
    print(all)
    return render_template('display_previous.html', passed = all)
    

if __name__=="__main__":
    

    app.run(debug=True)