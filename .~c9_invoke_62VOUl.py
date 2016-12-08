from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import datetime, timedelta

from helpers import *

# configure application
app = Flask(__name__)

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

# things to be done always when rendering
def render(*args, **kwargs):
    # get current group and groups
    group = "None"
    groups = []
    if session.get("user_id") is not None:
        row = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = session["user_id"])
        
        # groups the user is in 
        groups = db.execute("SELECT b.group_name, b.group_id FROM group_users AS a JOIN groups AS b ON \
        a.group_id = b.group_id WHERE a.user_id = :user_id ORDER BY b.group_name ASC", user_id = session["user_id"])
        
        # current group
        if len(row) == 1:
            group_id = row[0]["group_id"]
            if group_id is not None:
                group = db.execute("SELECT group_name FROM groups WHERE group_id = :group_id", group_id=group_id)[0]["group_name"]
    return render_template(*args, cur_group=group, groups=groups, **kwargs)


@app.route("/")
@login_required
def index():
    """Display index."""
    row = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
    group_id = row[0]["group_id"]
    if group_id is not None:
        group = db.execute("SELECT * FROM groups WHERE group_id = :group_id", group_id = group_id)[0]
        
        # get all users in the group
        users = db.execute("SELECT * FROM group_users as a join users as b on a.user_id = b.user_id WHERE a.group_id = :gid", gid = group_id)
        return render("index.html", group = group, users = users);
    else:
        return render("join-group.html")
    

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
        return render("change_password.html")

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
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password_hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render("login.html")

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
        elif not request.form.get("name"):
            return apology("must enter name")
        
        # ensure username not taken, and if so, create user
        if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 1:
            db.execute("INSERT INTO users (username, password_hash, name) VALUES (:username, :hash, :name)",\
            username = request.form.get("username"), hash = pwd_context.encrypt(request.form.get("password1")), name = request.form.get("name"))
            return redirect(url_for("index"))
        else:
            return apology("That username is already taken")    
    
    # user trying to register (reached via GET)    
    else:
        return render("register.html")
        

@app.route("/switch-group", methods=["GET", "POST"])
@login_required
def switch_group():
    """switch the current group someone is in"""
    
    # ensure parameters are present
    if not request.args.get("gid"):
        return apology("missing gid")
    
    # check user is in new group   
    row = db.execute("SELECT * FROM group_users WHERE group_id=:gid AND user_id=:uid",\
        gid=int(request.args.get("gid")), uid=session["user_id"])
    
    # update database
    if len(row) == 1:
        db.execute("UPDATE users SET group_id=:gid where user_id=:uid", \
            gid=int(request.args.get("gid")), uid=session["user_id"])
    
    # homepage
    return(redirect(url_for("index")))
        
@app.route("/add-user", methods=["GET", "POST"])
@login_required
def add_user():
    """Make a join code for a user"""
    
    # user making join code (reached via POST)
    if request.method == "POST":
        
        # make sure join code submitted
        if not request.form.get("join_code"):
            return apology("must provide join code")
        
        # make sure user is in grouop
        rows = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = rows[0]["group_id"]
        if group_id is None: 
            return redirect(url_for("join_group"))
        
        # hash join code and store
        join_hash = pwd_context.encrypt(request.form.get("join_code"))
        join_end_time = datetime.now() + timedelta(hours=int(request.form.get("time")))
        # safe to use .format because we are using a datetime object (no possibility of SQL injection)
        db.execute("UPDATE groups SET join_hash = :join_hash, join_end_time = '{}' WHERE group_id = :group_id".format(join_end_time), \
        join_hash = join_hash, group_id = group_id)
        
        return redirect(url_for("index"))
        
    # user trying to make a join code (reached via GET)
    else:
        return render("add-user.html")
        
        

@app.route("/create-group", methods=["GET", "POST"])
@login_required
def create_group():
    """Create a group"""
    
    # user creating group (reached via POST)
    if request.method == "POST":
        
        # make sure group name and username submitted
        if not request.form.get("group_name"):
            return apology("must provide group_name")
        if not request.form.get("group_code"):
            return apology("must provide group_code")
        
        if len(db.execute("SELECT * FROM groups WHERE group_code = :group_code", group_code = request.form.get("group_code"))) == 1:
            return apology("group code already exists")
            
        # create group in database
        group_id = db.execute("INSERT INTO groups (group_name, group_code) VALUES(:group_name, :group_code)",\
        group_name = request.form.get("group_name"), group_code = request.form.get("group_code"))
        
        # insert user into group_users
        db.execute("INSERT INTO group_users (user_id, group_id) VALUES(:user_id, :group_id)",\
        user_id = int(session["user_id"]), group_id = group_id)
        
        # update current group for user
        db.execute("UPDATE users SET group_id = :group_id WHERE user_id = :user_id", \
        user_id = int(session["user_id"]), group_id = group_id)
        
        return redirect(url_for("index"))
        
    # user trying to create a group (reached via GET)
    else:
        return render("create-group.html")
        
@app.route("/join-group", methods=["GET", "POST"])
@login_required
def join_group():
    """Join a group"""
    
    # reached via POST
    if request.method == "POST":
        # check if user entered group ID
        if not request.form.get("group_code"):
            return apology("must provide group ID")
        elif not request.form.get("join_code"):
            return apology("must provide join code")
    
        # query database for group
        rows = db.execute("SELECT * FROM groups WHERE group_code = :group_code", group_code=request.form.get("group_code"))
        
        # if group does not exist
        if len(rows) == 0:
            return apology("group does not exist")
        
        # check if group has excepted users
        if rows[0]["join_hash"] is None: 
            return(apology("join code is incorrect"))
        
        # ensure group_code exists and join_code is correct
        if not pwd_context.verify(request.form.get("join_code"), rows[0]["join_hash"]):
            return apology("invalid join code")
        
        # check if code is expired
        if datetime.now() >  datetime.strptime(rows[0]["join_end_time"],'%Y-%m-%d %H:%M:%S.%f'):
            return apology("join code is expired")
        
    

        # add user & group into group_users
        group = db.execute("SELECT group_id FROM groups WHERE group_code = :group_code", group_code = request.form.get("group_code"))
        group_id = group[0]["group_id"]
        db.execute("INSERT INTO group_users (user_id, group_id) VALUES (:user_id, :group_id)",\
            user_id = int(session["user_id"]), group_id=group_id)
            
        # update current group for user
        db.execute("UPDATE users SET group_id = :group_id WHERE user_id = :user_id", \
        user_id = int(session["user_id"]), group_id = group_id)
                        
        return redirect(url_for("index"))
    
    # reach join group page through GET
    else:
        return render("join-group.html")
        
@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    """ View or send a chat"""
    
    # reached via POST
    if request.method == "POST":
        if not request.form["message"]:
            return apology("must enter message text")
        
        # add chat to database
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = group[0]["group_id"]
        
        if group_id is None:
            return(redirect(url_for("index")))
            
        db.execute("INSERT INTO chats (chat_text, group_id) VALUES (:chat_text, :group_id)", \
        chat_text = request.form["message"], group_id = group_id)
        
        return redirect(url_for("chat"))
        
        return render("chat.html", chats=recent_chats)
    else:
        # reached via GET
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        
        # make sure user is in a group
        group_id = group[0]["group_id"]
        if group_id is None:
            return(redirect(url_for("index")))
            
        # page 
        if not request.args.get("p"):
            page = 1
        else:
            page = request.args.get("p")
            try:
                page = int(page)
            except ValueError:
                page = 1
        
        row = db.execute("SELECT count(*) from chats WHERE group_id = :group_id", group_id=group_id)    
        num_pages = (row[0]["count(*)"] + 9) // 10
        if page > num_pages:
            page = num_pages
        
        chats = db.execute("SELECT * from chats WHERE group_id = :group_id ORDER BY chat_time DESC \
         LIMIT 10 OFFSET :off", group_id = group_id, off=((page - 1) * 10))
        
        return render("chat.html", chats=chats, page=page, num_pages=num_pages)
        
        
@app.route("/task-schedule", methods=["GET", "POST"])
@login_required
def task_schedule():
    # reached via POST
    if request.method == "POST":
        if not request.form["task schedule"]:
            return apology("must enter message text")
        
        # add chat to database
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = group[0]["group_id"]
        
        if group_id is None:
            return(redirect(url_for("index")))
            
        db.execute("INSERT INTO chats (chat_text, group_id) VALUES (:chat_text, :group_id)", \
        chat_text = request.form["message"], group_id = group_id)
        
        return redirect(url_for("chat"))
        
        return render("chat.html", chats=recent_chats)
    else:
        # reached via GET
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        
        # make sure user is in a group
        group_id = group[0]["group_id"]
        if group_id is None:
            return(redirect(url_for("index")))
            
        # page 
        if not request.args.get("p"):
            page = 1
        else:
            page = request.args.get("p")
            try:
                page = int(page)
            except ValueError:
                page = 1
        
        row = db.execute("SELECT count(*) from chats WHERE group_id = :group_id", group_id=group_id)    
        num_pages = (row[0]["count(*)"] + 9) // 10
        if page > num_pages:
            page = num_pages
        
        chats = db.execute("SELECT * from chats WHERE group_id = :group_id ORDER BY chat_time DESC \
         LIMIT 10 OFFSET :off", group_id = group_id, off=((page - 1) * 10))
        
        return render("chat.html", chats=chats, page=page, num_pages=num_pages)