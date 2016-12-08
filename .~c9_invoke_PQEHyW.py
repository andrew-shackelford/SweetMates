from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import datetime, timedelta

from helpers import *

# configure application


# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///sweetMates.db")

@app.route("/")
@login_required
def index():
    """Display index."""
    
    return render_template(index.html);

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow the user to change their password."""
    
    # if user reached route via POST (attempting to change their password)
    if request.method == "POST":
        
        # ensure username and passwords submitted and match
        if not request.form.get("old_password"):
            return apology("must provide old password")
        elif not request.form.get("password1"):
            return apology("must provide new password")
        elif not request.form.get("password2"):
            return apology("must re-enter new password")
        elif request.form.get("password1") != request.form.get("password2"):
            return apology("new passwords do not match")
        elif request.form.get("old_password") == request.form.get("password1"):
            return apology("new password must be different")
        
        # ensure old password correct, change password if so
        user = db.execute("SELECT * FROM users WHERE id = :id", id=int(session["user_id"]))
        if pwd_context.verify(request.form.get("old_password"), user[0]["hash"]):
            db.execute("UPDATE users SET hash = :hash WHERE id = :id", \
            hash = pwd_context.encrypt(request.form.get("password1")), id = int(session["user_id"]))
            return redirect(url_for("index"))
        else:
            return apology("incorrect password")    
    
    # user trying to input a password change (reached via GET)    
    else:
        return render_template("change_password.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # user submitting registration (reached via POST)
    if request.method == "POST":
        
        # ensure username and passwords submitted and match
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password1"):
            return apology("must provide password")
        elif not request.form.get("password2"):
            return apology("must re-enter password")
        elif request.form.get("password1") != request.form.get("password2"):
            return apology("passwords do not match")
        
        # ensure username not taken, and if so, create user
        if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 1:
            db.execute("INSERT INTO users (username, passwordhash) VALUES(:username, :hash)",\
            username = request.form.get("username"), hash = pwd_context.encrypt(request.form.get("password1")))
            return redirect(url_for("index"))
        else:
            return apology("That username is already taken")    
    
    # user trying to register (reached via GET)    
    else:
        return render_template("register.html")
        
@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    """Make a join code for a user"""
    
    # user making join code (reached via POST)
    if request.method == "POST":
        
        # make sure join code submitted
        if not request.form.get("join_code"):
            return apology("must provide join code")
            
        # hash join code and store
        group_id = int(db.execute("SELECT group_id from users where user_id = :user_id", user_id = int(session["user_id"])))
        join_hash = pwd_context.encrypt(request.form.get("join_code"), id = group_id)
        join_end_time = datetime.now() + timedelta(days=1)
        db.execute("UPDATE groups SET join_hash = :join_hash AND join_end_time = :join_end_time AND group_id = :group_id", \
        join_hash = join_hash, join_end_time = join_end_time, group_id = group_id)
        
        return redirect(url_for("index"))
        
    # user trying to make a join code (reached via GET)
    else:
        return render_template("join-group.html")
        
        

@app.route("/create-group", methods=["GET", "POST"])
def create_group():
    """Create a group"""
    
    # user creating group (reached via POST)
    if request.method == "POST":
        
        # make sure group name and username submitted
        if not request.form.get("group_name"):
            return apology("must provide group_name")
        if not request.form.get("group_id"):
            return apology("must provide group_id")
        
        # create group in database
        db.execute("INSERT INTO groups (group_name, group_username) VALUES(:group_name, :group_username)",\
        group_name = request.form.get("group_name"), group_username = request.form.get("group_id"))
        
        return redirect(url_for("index"))
        
    # user trying to create a group (reached via GET)
    else:
        return render_template("create-group.html")
        
@app.route("/join-group", methods=["GET", "POST"])
def join_group():
    """Join a group"""
    
    # reached via POST
    if request.method == "POST":
        # check if user entered group ID
        if not request.form.get("group_id"):
            return apology("must provide group ID")
    
        # check if group id exists
        if not db.execute("SELECT * FROM groups WHERE group_id = :group_id", group_id=request.form.get("group_id")):
            return apology("that group doesn't exist")
                
        # add user & group into group_users
        else:
            db.execute("INSERT INTO group_users (user_id, group_id) VALUES (:user_id, :group_id)",\
                user_id = session["user_id"], group_id = request.form.get("group_id"))
                        
        return redirect(url_for("index"))
    
    # reach join group page through GET
    else:
        return render_template("join-group.html")