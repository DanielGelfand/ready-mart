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


@app.route("/userHome")
def userHome():
    return render_template("userHome.html",username = session["user"],stories = {'1':'title1','2':'title2'})

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        contrib = request.form["content"]
        db = sqlite3.connect('stories.db')
        c = db.cursor()
        forID = c.execute("SELECT storyid FROM stories ORDER BY storyid DESC LIMIT 1")
        id = forID.fetchone()[0]
        #print(session["user"])
        #val = session["user"]
        currID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
        print(currID)
        dbtools.add_story(c,id+1,contrib,currID,title)
        db.commit()
        db.close()
        # put all the code to handle what you want with creating a story here
        # after you do all that code just redirect to userHome or something
        return redirect(url_for('userHome'))

    return render_template("add_story.html")

@app.route("/choose")
def edit():
    return render_template("edit_stories.html", stories = {'1':'title1','2':'title2'}) 


@app.route("/edit", methods=["POST"])
def edit_story():
    return render_template("edit_story.html", story = ['storyid1','story_title','story_content'])


@app.route("/view/<int:storyid>")
def view(storyid):
    return render_template("view_story.html") 

@app.route("/logout")
def logout():
    session.pop("user")

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
