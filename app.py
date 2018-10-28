from flask import Flask, request, render_template, session, redirect, url_for,flash
from os import urandom
import util.bazinga as dbtools
import sqlite3
'''This code is the python behind our app'''
app = Flask(__name__)
app.secret_key = urandom(32)

@app.route("/")
def home():
    '''This function sends the user to either their home page if they're signed in or the generaal log-in page if they're not'''
    if "user" in session:
        return redirect(url_for('userHome'))
    return render_template("landing.html")

@app.route("/login",methods=["GET","POST"])
def login():
    '''This function logins the user'''
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
    #checks if the user is logged in already and tries to access the page
    if "user" in session:
        #flashes an error if they try to do so then redirects to userHome
        flash("You tried to access the login page while logged in! If you wish to log in to another account, log out first!")
        return redirect(url_for('userHome'))
    #displays the error the user faced when logging in
    flash(error)
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    '''This function lets the user register'''
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
    #checks if the user is logged in already and tries to access the page
    if "user" in session:
        #flashes an error if they try to do so then redirects to userHome
        flash("You tried to access the register page while logged in! If you wish to create a new account, log out first!")
        return redirect(url_for('userHome'))
    #displays the error the user faced when registering an account
    flash(error)
    return render_template("register.html")


@app.route("/userHome")
def userHome():
    '''This is the home page for a signed-in user.'''
    #checks if the user is not logged in
    if "user" not in session:
        #flashes the error messsage below if they are not logged in
        flash("You tried to access the user home page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    #gets the userid of the user in session
    userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
    #fetches all the stories that the user has contributed to
    stories = dbtools.not_edit(c,userID)
    return render_template("userHome.html",username = session["user"],storyList = stories)

@app.route("/add",methods=["GET","POST"])
def add():
    '''This function facilitates adding a story'''
    if request.method == "POST":
        title = request.form["title"]
        contrib = request.form["content"]
        db = sqlite3.connect('stories.db')
        c = db.cursor()
        #fetches id of most recently added story
        forID = c.execute("SELECT storyid FROM stories ORDER BY storyid DESC LIMIT 1")
        id = forID.fetchone()[0]
        #fetches user id of current user
        currID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
        #adds story to databae
        dbtools.add_story(c,id+1,contrib,currID,title)
        db.commit()
        db.close()
        #message to let user know that the story was successfully created
        flash("Successfully created new story")
        return redirect(url_for('userHome'))
    #checks if the user is not logged in
    if "user" not in session:
        #flashes the error messsage below if they are not logged in
        flash("You tried to access the add page without being logged in! If you wish to add a new story, log in or register an account first!")
        return redirect(url_for('home'))
    return render_template("add_story.html")

@app.route("/choose")
def edit():
    '''This function facilitates choosing a story to edit'''
    #checks if the user is not logged in
    if "user" not in session:
        #flashes the error messsage below if they are not logged in
        flash("You tried to access the edit page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    #gets userid of current user in session
    userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
    #fetches all the stories the user can edit
    stories = dbtools.all_edit(c,userID)
    #renders template using the stories the user can edit
    return render_template("edit_stories.html", storyList = stories)


@app.route("/edit", methods=["POST","GET"])
def edit_story():
    '''This function facilitates editing a story'''
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    if request.method == "POST":
        storyID = request.form["storyID"]
        title = dbtools.title_story(c,storyID)
        content = dbtools.last_story(c,storyID)
        #acquires the contribution to be made to the story
        contrib = request.form["content"]
        #fetches the userid of current user in session
        userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
        #edits story
        dbtools.edit_story(c,storyID,contrib,userID)
        db.commit()
        db.close()
        flash("Successfully added to story")
        return redirect(url_for('userHome'))
    #checks if the user is not logged in
    if "user" not in session:
        #flashes error messsage below if they are not logged in
        flash("You tried to access the edit page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    #in case of a user typing localhost:5000/edit, displays the error below
    flash("You tried to access /edit. If you wish to edit a story, please click on Add to an existing story if you wish to add to a storym")
    return redirect(url_for('userHome'))

@app.route("/editPage", methods=["POST","GET"])
def editPage():
    '''This page also facilitates editing a story'''
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    if request.method == "POST":
        storyID = request.form["storyID"]
        #fetches the title of the story using title_story
        storyTitle = dbtools.title_story(c,storyID)
        #fetches the last made contribution using last_story
        prevContrib = dbtools.last_story(c,storyID)
        #renders template using the title and last made contribution
        return render_template("edit_story.html",title=storyTitle,contrib = prevContrib,id=storyID)
    #checks if the user is not logged in
    if "user" not in session:
        #flashes error messsage below if they are not logged in
        flash("You tried to access the edit page without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    #in case of a user typing localhost:5000/editPage, displays the error below
    flash("You tried to access edit page directly, if you wish to edit a story please do so through the home page")
    return redirect(url_for('userHome'))

@app.route("/view/<int:storyid>")
def view(storyid):
    '''This function facilitates viewing stories'''
    #checks if the user is not logged in
    if "user" not in session:
        #flashes the error messsage below if they are not logged in
        flash("You tried to view a story without being logged in! If you wish to access this feature, log in or register an account first!")
        return redirect(url_for('home'))
    db = sqlite3.connect("stories.db")
    c = db.cursor()
    userID = c.execute("SELECT userid FROM users WHERE username = ?",(session["user"],)).fetchone()[0]
    #fetches the entire story using hole_story
    wholeStory = dbtools.hole_story(c,storyid)
    #fetches the title of the story using title_story
    titleStory = dbtools.title_story(c,storyid)
    #in case of a user typing localhost:5000/view/storyID, checks if they can edit and if so, redirect them back to home page
    if dbtools.can_edit(c,storyid,userID):
        flash("You must contribute to the story titled " + titleStory + " before you can view it")
        return redirect(url_for('userHome'))
    return render_template("view_story.html",story = wholeStory,title = titleStory)

@app.route("/logout")
def logout():
    '''This function logs out the user'''
    #removes the user from the session
    session.pop("user")
    #redirects back to the home page
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.debug = True
    app.run()
