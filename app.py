from flask import Flask, request, render_template, session, redirect, url_for,flash
from os import urandom
import util.bazinga as dbtools
import sqlite3

app = Flask(__name__)
app.secret_key = urandom(32)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for('userHome'))
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
                return redirect(url_for('userHome'))
            else:
                #case for bad password
                error="bad password"
        else:
            #case for bad username
            error="bad username"
    if "user" in session:
        flash("You tried to access the login page while logged in! If you wish to log in to another account, log out first!")
        return redirect(url_for('userHome'))
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
            return redirect(url_for('userHome'))
    if "user" in session:
        flash("You tried to access the register page while logged in! If you wish to create a new account, log out first!")
        return redirect(url_for('userHome'))
    flash(error)
    return render_template("register.html")


@app.route("/userHome")
def userHome():
    if "user" not in session:
        flash("You tried to access the user home page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    id = userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
    stories = dbtools.not_edit(c,id)
    return render_template("userHome.html",username = session["user"],storyList = stories)

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        contrib = request.form["content"]
        db = sqlite3.connect('stories.db')
        c = db.cursor()
        forID = c.execute("SELECT storyid FROM stories ORDER BY storyid DESC LIMIT 1")
        id = forID.fetchone()[0]
        currID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
        dbtools.add_story(c,id+1,contrib,currID,title)
        db.commit()
        db.close()
        flash("Successfully created new story")
        return redirect(url_for('userHome'))
    if "user" not in session:
        flash("You tried to access the add page without being logged in! If you wish to add a new story, log in or register an account first!")
        return redirect(url_for('home'))
    return render_template("add_story.html")

@app.route("/choose")
def edit():
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    id = userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
    stories = dbtools.all_edit(c,id)
    return render_template("edit_stories.html", storyList = stories)


@app.route("/edit", methods=["POST","GET"])
def edit_story():
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    if request.method == "POST":
        storyID = request.form["storyID"]
        title = dbtools.title_story(c,storyID)
        content = dbtools.last_story(c,storyID)
        contrib = request.form["content"]
        userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
        dbtools.edit_story(c,storyID,contrib,userID)
        db.commit()
        db.close()
        flash("Successfully added to story")
        return redirect(url_for('userHome'))
    if "user" not in session:
        flash("You tried to access the edit page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    flash("You tried to access /edit. If you wish to edit a story, please click on Add to an existing story if you wish to add to a storym")
    return redirect(url_for('userHome'))

@app.route("/editPage", methods=["POST","GET"])
def editPage():
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    if request.method == "POST":
        storyID = request.form["storyID"]
        storyTitle = dbtools.title_story(c,storyID)
        prevContrib = dbtools.last_story(c,storyID)
        return render_template("edit_story.html",title=storyTitle,contrib = prevContrib,id=storyID)
    if "user" not in session:
        flash("You tried to access the edit page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    flash("You tried to access edit page directly, if you wish to edit a story please do so through the home page")
    return redirect(url_for('userHome'))

@app.route("/view/<int:storyid>")
def view(storyid):
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    wholeStory = dbtools.hole_story(c,storyid)
    titleStory = dbtools.title_story(c,storyid)
    return render_template("view_story.html",story = wholeStory,title = titleStory)

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
