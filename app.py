from flask import Flask, render_template, request,redirect, url_for,send_from_directory
from flask import send_file
from flask_bootstrap import Bootstrap
from flask_login.utils import logout_user
from flask_wtf import FlaskForm
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
import lda_70
import nmf_ready_to_use
import xlwt
import pam_eng
import sendemail



app = Flask(__name__)
bootstrap = Bootstrap(app)
picFolder = os.path.join('static', 'pics')
app.config['EXCEL_FILES'] = os.path.join('static', 'excelfiles')
app.config['UPLOAD_FOLDER'] = picFolder
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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


def __repr__(self):
    return "<username %r >" % self.id

# login class
class LoginForm(FlaskForm):
    username = StringField(
        "username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "password", validators=[InputRequired(), Length(min=8, max=80)]
    )
    remember = BooleanField("remember me")

# sign up class
class RegisterForm(FlaskForm):
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

     # login function / where i compare the hashed password
@app.route("/login", methods=["GET", "POST"])
def login():
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


# sign up function/ where the passwords are hashed
@app.route("/signup", methods=["GET", "POST"])
def signup():
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


# routes the user into the application with login check
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', name=current_user.username)

# routes the user into the application without login check
@app.route('/free')
def free():
    return render_template('index.html', name= "Guest User")

 # sign the user out 
@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect(url_for('index'))

@app.route('/')

def index():
    
    return render_template("index2.html")

@app.route('/', methods =['POST'])
def test():
    language = request.form['language']
    algorithm = request.form['algorithm']
    f = request.files["file1"]
  
    f.save(os.path.join("uploads",current_user.username+"-"+f.filename))
    word_cloud.cloudify(current_user.username+"-"+f.filename)

    outname = current_user.username+"-"+f.filename+"_out.png"
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], outname)
    file1 = open("uploads/"+current_user.username+"-"+f.filename, 'r', encoding='utf-8')
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
        workbook.save("static/excelfiles/"+current_user.username+"-"+f.filename+".xls")
        name = current_user.username+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        
        sendemail.send_email(pic1,excelfile, current_user.email)

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

        workbook.save("static/excelfiles/"+current_user.username+"-"+f.filename+".xls")
        name = current_user.username+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        sendemail.send_email(pic1,excelfile, current_user.email)

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

        workbook.save("static/excelfiles/"+current_user.username+"-"+f.filename+".xls")
        name = current_user.username+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        sendemail.send_email(pic1,excelfile, current_user.email)


        return render_template("resultpage.html",img_file =pic1, algorithm = "nmf", tpcs = results , excelfile = excelfile)
    elif language == 'english' and algorithm == 'pam':
        results = pam_eng.pam_english("uploads/"+f.filename)
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

        workbook.save("static/excelfiles/"+current_user.username+"-"+f.filename+".xls")
        name = current_user.username+"-"+f.filename+".xls"
        excelfile = os.path.join(app.config['EXCEL_FILES'], name)
        sendemail.send_email(pic1,excelfile, current_user.email)

        return render_template("resultpage.html",img_file =pic1, algorithm = "pam", tpcs = results, excelfile = excelfile)
        



if __name__=="__main__":
    app.run(debug=True)