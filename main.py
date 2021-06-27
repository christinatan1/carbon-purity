from flask import Flask, redirect, url_for, render_template,request, session, flash
from datetime import timedelta, datetime, date, time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime

app = Flask(__name__)
app.secret_key = "environmentisimportant!"
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    username = db.Column("username", db.String(100))
    password = db.Column("password",db.String(100))
    score = db.Column(db.Integer)
    checkedInTime = db.Column(DateTime, default=None)

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.score = 100 #default score
        self.checkedInTime = None

# create the table 
db.create_all()
db.session.commit()

@app.route("/home")
@app.route("/")
def home():
    if "username" in session:
        if users == None or len(users.query.all())==0:
            return redirect("logout")
        return render_template("index.html")
    else:
        flash("Hello there! Either head over to questionnaire to check your ability in helping the environment, or go to login to login/create an account!")
        return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods=["POST","GET"])
def login():
    # already logged in 
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]

        #check login information
        found_user = users.query.filter_by(username=username).first()
        if found_user and found_user.password == password:
            session["username"] = found_user.username
            session['password'] = found_user.password
            flash("Login Successful! ")
            return redirect(url_for("dashboard"))
        #if user is found but password is incorrect
        elif found_user:
            flash("incorrect username/password")
            return render_template("login.html")
            
        #if account not found, create new account
        else:
            flash("Username not recognized, please create an account!")
            return redirect(url_for("create"))
    else:
        if "username" in session:
            flash("Already logged in! ")
            return redirect(url_for("dashboard"))
        return render_template("login.html")

@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        flash(f"You have been logged out, {username}!")
        session.pop("username",None)
    else:
        flash("You have not yet logged in!")
    return redirect(url_for("login"))

@app.route("/create", methods=["POST","GET"])
def create():
    if request.method == "POST":
        username = request.form["newusername"]
        password = request.form["newpassword"]
        name = request.form["newname"]
        email = request.form["newemail"]
        found_user = users.query.filter_by(username=username).first()

        if found_user:
            #username is already taken
            flash("Username is already taken! Please choose another.")
            return render_template("create.html")
        else:
            user = users(name,email,username,password)
            session['username'] = username
            db.session.add(user)
            db.session.commit()
            flash("Account created! Begin by filling out the questionnaire to check-in")
            return redirect(url_for("dashboard"))
    return render_template("create.html")

@app.route("/questionnaire", methods=["POST","GET"])
def questionnaire():
    if request.method == "POST":
        #get number of questions users clicked
        selections = request.form.getlist('q')
        
        #update user's score count
        if "username" in session:
            username = session['username']
            user = users.query.filter_by(username=username).first()
            updated_score = 100 - (5 * len(selections))
            user.score = updated_score
            user.checkedInTime = datetime.now()
            db.session.commit()
            flash("Thanks for checking-in!")
            return redirect(url_for("score",newscore=user.score))
        else:
            flash("You must login to have your answers saved!")
            score = 100 - (5 * len(selections))
            return redirect(url_for("score",newscore=score))
    return render_template("questionnaire.html")

@app.route("/score/<newscore>", methods=["POST","GET"])
def score(newscore):
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("score.html",score=int(newscore))

@app.route("/dashboard")
def dashboard():
    #the two dates we need
    # sampleDate = datetime(2021,6,24,3,4,20)
    # today = datetime.now()
    # timedelta object
    # timePassed = today-sampleDate
    if "username" in session:
        username = session['username']
        user = users.query.filter_by(username=username).first()

        # if user has not yet checked in 
        if (user.checkedInTime == None):
            return render_template("dashboard.html",username=user.username,score=user.score,daysPassed=None)
        
        lastCheckedIn = user.checkedInTime
        difference = datetime.now() - lastCheckedIn
        daysPassed = difference.days
        hoursPassed, remainder = divmod(difference.seconds, 3600)
        minutesPassed,seconds = divmod(remainder,60)

        return render_template("dashboard.html",username=user.username,score=user.score,daysPassed=daysPassed,hoursPassed=hoursPassed,minutesPassed=minutesPassed)
    flash("Please login first!")
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
