from flask import Flask, request, render_template, session, redirect, url_for
from os import urandom

app = Flask(__name__)
# sets the secret_key to a random string of bytes

@app.route("/")
def home():
    if "username" not in session.keys():
        return redirect(url_for("login/"))
    return render_template("add_story.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/register")
def new():
    return render_template("add_story.html")

@app.route("/PreviousWork")

@app.route("/NewStory")

@app.route("/AddToStory")


if __name__ == "__main__":
    app.debug = True
    app.run()
