from flask import Flask, request, render_template, session, redirect, url_for
from os import urandom

app = Flask(__name__)
# sets the secret_key to a random string of bytes
app.secret_key = urandom(32

def __init__(self):

@app.route('/')
def home():
    if "username" not in session.keys():
        return redirect(url_for("login"))
    return render_template("")

@app.route("/login")
def login():
