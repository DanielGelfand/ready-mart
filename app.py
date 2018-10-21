from flask import Flask, request, render_template, session, redirect, url_for,flash
from os import urandom
import util.bazinga as dbtools
import sqlite3

app = Flask(__name__)
app.secret_key = urandom(32)

@app.route("/")
def home():
    if "user" in session:
        return render_template("userHome.html",username=session["user"])
    return render_template("landing.html")

@app.route("/login",methods=["GET","POST"])
def login():
    db = sqlite3.connect('stories.db')
    c = db.cursor()
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #checks if the username exists in the database
        if(dbtools.user_exists(c,username)):
            #checks username & password
            if(dbtools.check_user(c,username,password)):
                #if correct then user is added to session and redirected
                session["user"] = username
                return redirect(url_for('home'))
            else:
                #case for bad password
                error="bad password"
        else:
            #case for bad username
            error="bad username"
    flash(error)
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    db = sqlite3.connect('stories.db')
    c = db.cursor()
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        #checks if the username already exists
        if(dbtools.user_exists(c,username)):
            error="the username you inputted already exists!"
        #confirming password
        elif password != password2:
            error="the passwords do not match"
        else:
            #fetching most recently added id
            forID = c.execute("SELECT userid FROM users ORDER BY userid DESC LIMIT 1")
            id = forID.fetchone()[0]
            #adds user to database
            dbtools.add_user(c,id+1,username,password)
            #adds user to session
            session["user"] = username
            db.commit()
            db.close()
            #redirects user to home
            return redirect(url_for('home'))
    flash(error)
    return render_template("register.html")


@app.route("/userHome", methods=["POST"])
def userHome():
    return render_template("userHome.html")

@app.route("/add", methods=["POST"])
def add():
    return render_template("add_story.html")

@app.route("/edit", methods=["POST"])
def edit():
    return render_template("edit_stories.html")

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
