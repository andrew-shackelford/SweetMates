"""
This is the main back end for the SweetMates website
We used the code from CS50 Finance as a Framework, including flask and cs50

Eric Bornstein
ebornstein@college.harvard.edu

Andrew Shackelford
ashackelford@college.harvard.edu

Catherine Tu
catherinetu@college.harvard.edu

December 7, 2016

"""
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from datetime import datetime, timedelta, date
from random import randint

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
   
    # error handling
    if request.args.get("error"):
        error = request.args.get("error")
    else:
        error = None
    return render_template(*args, cur_group=group, groups=groups, error=error, **kwargs)

# what to do in an error
def error(address, new_error):
    return(redirect(url_for(address)+"?error="+new_error))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    
    # if user reached route via GET (regular index request)
    if request.method == "GET":
        """Display index."""
        # get group_id
        row = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = row[0]["group_id"]
        
        # if group_id exists
        if group_id is not None:
            group = db.execute("SELECT * FROM groups WHERE group_id = :group_id", group_id = group_id)[0]
            user_name = row[0]["name"]
            # get all users in the group
            users = db.execute("SELECT * FROM group_users as a join users as b on a.user_id = b.user_id WHERE a.group_id = :gid", gid = group_id)
            return render("index.html", group = group, users = users, user_name = user_name);
        else:
            return render("join-group.html")
            
    # if user reached route via POST (trying to leave a group)
    if request.method == "POST":
        """Leave the current group"""
        
        # get group_id
        row = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = row[0]["group_id"]
        
        if group_id is None:
            # something weird happened, go to index
            return redirect(url_for("index"))
            
        group_users = db.execute("SELECT * FROM group_users where group_id = :group_id", group_id = group_id)
        
        if len(group_users) == 1:
            # number of users in group is 1, so kill the group on exit
            
            # remove user from group
            db.execute("DELETE FROM group_users WHERE group_id = :group_id AND user_id = :user_id", \
            group_id = group_id, user_id = int(session["user_id"]))
            # kill the join code
            db.execute("UPDATE groups SET join_hash = NULL WHERE group_id = :group_id", group_id = group_id)
            # set current group to null
            db.execute("UPDATE users SET group_id = NULL WHERE user_id = :user_id", user_id = int(session["user_id"]))
            
            return redirect(url_for("index"))
            

        # remove user from group
        group = db.execute("DELETE FROM group_users WHERE group_id = :group_id AND user_id = :user_id", \
        group_id = group_id, user_id = int(session["user_id"]))
        # set current group to null
        db.execute("UPDATE users SET group_id = NULL WHERE user_id = :user_id", user_id = int(session["user_id"]))
            
        # reassign chores this user had
        
        # get group_members
        group_members = db.execute("SELECT * FROM group_users WHERE group_id = :group_id", group_id = group_id)
        
        # get chores
        chores = db.execute("SELECT * FROM chores WHERE group_id = :group_id and user_id = :user_id", group_id = group_id, \
        user_id = int(session["user_id"]))
        
        # loop through each chore
        for chore in chores:
            new_due_date = datetime.now() + timedelta(days=int(chore["days_to_do"]))
            new_user = group_members[randint(0, len(group_members) - 1)]["user_id"]
            
            # update chore
            # safe to use .format for datetime object
            db.execute("UPDATE chores SET due_date = '{}', user_id = :user_id WHERE id = :chore_id".format(new_due_date), \
            user_id = new_user, chore_id = chore["id"])
            
            # update chore history
            db.execute("INSERT INTO chore_history (chore_id, user_id) VALUES(:chore_id, :user_id)", chore_id = chore["id"], \
            user_id = int(session["user_id"]))
            
            
        return redirect(url_for("index"))
    

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Allow the user to change their password."""
    
    # if user reached route via POST (attempting to change their password)
    if request.method == "POST":
        
        # ensure username and passwords submitted and match
        if not request.form.get("old_password"):
            return error("change_password", "must provide old password")
        elif not request.form.get("password1"):
            return error("change_password", "must provide new password")
        elif not request.form.get("password2"):
            return error("change_password", "must re-enter new password")
        elif request.form.get("password1") != request.form.get("password2"):
            return error("change_password", "new passwords do not match")
        elif request.form.get("old_password") == request.form.get("password1"):
            return error("change_password", "new password must be different")
        
        # ensure old password correct, change password if so
        user = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=int(session["user_id"]))
        if pwd_context.verify(request.form.get("old_password"), user[0]["password_hash"]):
            db.execute("UPDATE users SET password_hash = :password_hash WHERE user_id = :user_id", \
            password_hash = pwd_context.encrypt(request.form.get("password1")), user_id = int(session["user_id"]))
            return redirect(url_for("index"))
        else:
            return error("change_password", "incorrect old password")    
    
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
            return error("login", "must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return error("login", "must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password_hash"]):
            return error("login", "invalid username and/or password")

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
            return error("register", "must provide username")
        elif not request.form.get("password1"):
            return error("register", "must provide password")
        elif not request.form.get("password2"):
            return error("register", "must re-enter password")
        elif request.form.get("password1") != request.form.get("password2"):
            return error("register", "passwords do not match")
        elif not request.form.get("name"):
            return error("register", "must enter name")
        
        # ensure username not taken, and if so, create user
        if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 1:
            session["user_id"] = db.execute("INSERT INTO users (username, password_hash, name) \
            VALUES (:username, :hash, :name)",\
            username = request.form.get("username"), hash = pwd_context.encrypt(request.form.get("password1")), name = request.form.get("name"))
            return redirect(url_for("index"))
        else:
            return error("register", "That username is already taken")    
    
    # user trying to register (reached via GET)    
    else:
        return render("register.html")
        

@app.route("/switch-group", methods=["GET", "POST"])
@login_required
def switch_group():
    """switch the current group someone is in"""
    
    # ensure parameters are present
    if not request.args.get("gid"):
        return(error("index", "Missing Group"))
    
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
            return error("add_user", "must provide join code")
        
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
        
        rows = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = rows[0]["group_id"]
        if group_id is None: 
            return redirect(url_for("join_group"))
            
        return render("add-user.html")
        
        

@app.route("/create-group", methods=["GET", "POST"])
@login_required
def create_group():
    """Create a group"""
    
    # user creating group (reached via POST)
    if request.method == "POST":
        
        # make sure group name and username submitted
        if not request.form.get("group_name"):
            return error("add_user", "must provide group_name")
        if not request.form.get("group_code"):
            return error("add_user", "must provide group_code")
        
        # make sure group code is unique
        if len(db.execute("SELECT * FROM groups WHERE group_code = :group_code", group_code = request.form.get("group_code"))) == 1:
            return error("create_group", "group code already exists")
            
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
            return error("join_group", "must provide group ID")
        elif not request.form.get("join_code"):
            return error("join_group", "must provide join code")
    
        # query database for group
        rows = db.execute("SELECT * FROM groups WHERE group_code = :group_code", group_code=request.form.get("group_code"))
        
        # if group does not exist
        if len(rows) == 0:
            return error("join_group", "group does not exist")
        
        # check if group has excepted users
        if rows[0]["join_hash"] is None: 
            return(error("join_group", "join code is incorrect"))
        
        # ensure group_code exists and join_code is correct
        if not pwd_context.verify(request.form.get("join_code"), rows[0]["join_hash"]):
            return error("join_group", "invalid join code")
        
        # check if code is expired
        if datetime.now() > datetime.strptime(rows[0]["join_end_time"],'%Y-%m-%d %H:%M:%S.%f'):
            return error("join_group", "join code is expired")
        
    

        # add user & group into group_users
        group = db.execute("SELECT group_id FROM groups WHERE group_code = :group_code", group_code = request.form.get("group_code"))
        group_id = group[0]["group_id"]
        row = db.execute("SELECT * FROM group_users WHERE group_id=:gid AND user_id=:uid",\
            gid=group_id, uid=int(session["user_id"]))
        if len(row) != 0:
            return error("join_group", "already in this group")
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
            return error("chat", "must enter message text")
        
        # add chat to database
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = group[0]["group_id"]
        
        # ensure group_id exists
        if group_id is None:
            return(redirect(url_for("index")))
        
        # insert chat into database
        db.execute("INSERT INTO chats (chat_text, group_id) VALUES (:chat_text, :group_id)", \
        chat_text = request.form["message"], group_id = group_id)
        
        # render chat page
        return redirect(url_for("chat"))
        
    else:
        # reached via GET
        
        # get group
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        
        # make sure user is in a group
        group_id = group[0]["group_id"]
        if group_id is None:
            return(redirect(url_for("index")))
            
        # load correct page 
        if not request.args.get("p"):
            page = 1
        else:
            page = request.args.get("p")
            try:
                page = int(page)
            except ValueError:
                page = 1
        
        # get number of pages from database
        row = db.execute("SELECT count(*) from chats WHERE group_id = :group_id", group_id=group_id)    
        num_pages = (row[0]["count(*)"] + 9) // 10
        if page > num_pages:
            page = num_pages
        
        # get correct chats from database
        chats = db.execute("SELECT * from chats WHERE group_id = :group_id ORDER BY chat_time DESC \
         LIMIT 10 OFFSET :off", group_id = group_id, off=((page - 1) * 10))
        
        
        for chat in chats:
            # get time, offset for EST and clean it up
            chat_time = datetime.strptime(chat["chat_time"],'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
            chat_time_string = chat_time.strftime('%A, %B %-d at %-I:%M:%S %p')
            chat["chat_time"] = chat_time_string
        
        # return page
        return render("chat.html", chats=chats, page=page, num_pages=num_pages)
        
        
@app.route("/chores", methods=["GET", "POST"])
@login_required
def chores():
    
    # reached via POST
    if request.method == "POST":
        
        if request.form.get("type") == "completed" or request.form.get("type") == "delete":
            # completing / deleting chore
            if request.form.get("type") == "completed":
                # chore completed
                # affirm current group to work within
                group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
                group_id = group[0]["group_id"]
                
                # ensure group_id exists
                if group_id is None:
                    return(redirect(url_for("index")))
                    
                # ensure chore_id exists
                chore_id = request.form.get("chore")
                if chore_id is None:
                    return(redirect(url_for("chores")))
                    
                # get chore
                chore = db.execute("SELECT * FROM chores WHERE id = :chore_id", chore_id = chore_id)
                
                # get group_members
                group_members = db.execute("SELECT * FROM group_users WHERE group_id = :group_id", group_id = group_id)
                
                new_due_date = datetime.now() + timedelta(days=int(chore[0]["days_to_do"]))
                new_user = group_members[randint(0, len(group_members) - 1)]["user_id"]
                
                # update chore
                # safe to use .format for datetime object
                db.execute("UPDATE chores SET due_date = '{}', user_id = :user_id WHERE id = :chore_id".format(new_due_date), \
                user_id = new_user, chore_id = chore_id)
                
                # update chore history
                db.execute("INSERT INTO chore_history (chore_id, user_id) VALUES(:chore_id, :user_id)", chore_id = chore_id, \
                user_id = int(session["user_id"]))
                
                # return page
                return redirect(url_for("chores"))
                
            else:
                # delete chore
                # affirm current group to work within
                group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
                group_id = group[0]["group_id"]
                
                # ensure group_id exists
                if group_id is None:
                    return(redirect(url_for("index")))
                    
                # ensure chore_id exists
                chore_id = request.form.get("chore")
                if chore_id is None:
                    return(redirect(url_for("chores")))
                    
                # get chore
                chore = db.execute("SELECT * from chores where id = :chore_id", chore_id = chore_id)
                
                new_chore_name = chore[0]["name"] + " deleted"
                
                # delete chore
                db.execute("UPDATE chores SET user_id = NULL, name = :name WHERE id = :chore_id",\
                chore_id = chore_id, name = new_chore_name)
                
                # delete chore history
                db.execute("DELETE FROM chore_history WHERE chore_id = :chore_id", chore_id = chore_id)
                
                # update chore history
                db.execute("INSERT INTO chore_history (chore_id, user_id) VALUES (:chore_id, :user_id)", \
                chore_id = chore_id, user_id = int(session["user_id"]))
                
                # return page
                return redirect(url_for("chores"))
        
        else:
            # adding chore
            # make sure new chore is added
            if not request.form.get("new chore"):
                return error("chores", "please enter chore title")
            if not request.form.get("time"):
                return error("chores", "please enter chore due date")
    
            # affirm current group to work within
            group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
            group_id = group[0]["group_id"]
            
            # ensure group_id exists
            if group_id is None:
                return(redirect(url_for("index")))
            
            # random selection of group member for chore assignment
            group_members = db.execute("SELECT * FROM group_users WHERE group_id = :group_id", group_id = group_id)
            
            # insert chore into database & assign to person
            # safe to use .format for due_date due to input being a datetime object
            db.execute("INSERT INTO chores (group_id, name, due_date, days_to_do, user_id) VALUES (:group_id, :name, \
                        '{}', :days_to_do, :user_id)".format(datetime.now() + timedelta(days=int(request.form["time"]))),\
                        group_id = group_id, name = request.form["new chore"], days_to_do = request.form["time"], \
                        user_id = group_members[randint(0, len(group_members) - 1)]["user_id"])
            
            # render chore page
            return redirect(url_for("chores"))
        
    else:
        # reached through GET
        
        # get group
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        
        # make sure user is in a group
        group_id = group[0]["group_id"]
        if group_id is None:
            return(redirect(url_for("index")))
        
        # get current user chores
        self_chores = db.execute("SELECT name, due_date, id, \
        ROUND(julianday(DATE(due_date)) - julianday(DATE('now'))) AS time_left \
        FROM chores WHERE user_id = :user_id AND group_id=:gid",\
        user_id = int(session["user_id"]), gid=group_id)
        
        for chore in self_chores:
            # get time, offset for EST and clean it up
            chore_time = datetime.strptime(chore["due_date"],'%Y-%m-%d %H:%M:%S.%f') - timedelta(hours=5)
            chore_time_string = chore_time.strftime('%A, %B %-d')
            chore["due_date"] = chore_time_string
            chore["time_left"] = int(chore["time_left"])
        
        # chores others should do
        others_chores = db.execute("SELECT a.name, a.due_date, b.name AS person, \
        ROUND(julianday(DATE(a.due_date)) - julianday(DATE('now'))) as time_left FROM chores AS a \
        LEFT JOIN users AS b \
        ON a.user_id = b.user_id WHERE b.user_id != :user_id AND a.group_id=:gid",\
        user_id = int(session["user_id"]), gid=group_id)
        
        for chore in others_chores:
            # get time, offset for EST and clean it up
            chore_time = datetime.strptime(chore["due_date"],'%Y-%m-%d %H:%M:%S.%f') - timedelta(hours=5)
            chore_time_string = chore_time.strftime('%A, %B %-d')
            chore["due_date"] = chore_time_string
            chore["time_left"] = int(chore["time_left"])
        
        # load correct page 
        if not request.args.get("p"):
            page = 1
        else:
            page = request.args.get("p")
            try:
                page = int(page)
            except ValueError:
                page = 1
        
        # get number of pages from database
        row = db.execute("SELECT count(*) from chore_history AS a LEFT JOIN chores AS b \
        ON a.chore_id = b.id WHERE b.group_id = :group_id ORDER BY a.time ASC", group_id=group_id)    
        num_pages = (row[0]["count(*)"] + 4) // 5
        if page > num_pages:
            page = num_pages
        
        # get correct history from database
        history = db.execute("SELECT b.name, a.time, c.name AS person from chore_history AS a \
        LEFT JOIN chores AS b ON a.chore_id = b.id  LEFT JOIN users AS c on a.user_id=c.user_id \
        WHERE b.group_id = :group_id ORDER BY a.time DESC \
         LIMIT 5 OFFSET :off", group_id = group_id, off=((page - 1) * 5))
        
        
        
        for chore in history:
            # get time, offset for EST and clean it up
            chore_time = datetime.strptime(chore["time"],'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
            chore_time_string = chore_time.strftime('%A, %B %-d at %-I:%M:%S %p')
            chore["time"] = chore_time_string
            
        
        # get other user chores
        return render("chores.html", self_chores = self_chores, others_chores=others_chores,\
            chore_history=history, page=page, num_pages=num_pages)
        
@app.route("/choose", methods=["GET", "POST"])
@login_required
def choose():  
    """Vote on Topics"""
    # reached via POST
    if request.method == "POST":
        
        # check if user entered group ID
        if not request.form.get("form"):
            return(redirect(url_for("choose")))
            
        if request.form.get("form") == "choice":
            if not request.form.get("choice"):
                return(redirect(url_for("choose")))
            if not request.form.get("yes"):
                return(redirect(url_for("choose")))
            answer = request.form.get("yes")
            if answer != "no" and answer != "yes":
                return(redirect(url_for("choose")))
                
            choice = request.form.get("choice")
            print(request.form.get("form"))
            # choice exists
            row = db.execute("SELECT group_id FROM choose WHERE id=:cid", cid=int(choice))
            
            if len(row) != 1:
                return(redirect(url_for("choose")))
            
            # user in group
            group_id = row[0]["group_id"]
            
            row = db.execute("SELECT * FROM group_users WHERE group_id=:gid AND user_id=:uid",\
                gid=group_id, uid=int(session["user_id"]))
            
            if len(row) != 1:
                return(redirect(url_for("choose")))
                
            # already answered
            row = db.execute("SELECT * FROM choose_users WHERE choose_id=:cid AND user_id=:uid",\
                cid=choice, uid=int(session["user_id"]))
            
            if len(row) != 0:
                return(redirect(url_for("choose")))
            
            # answer
            db.execute("INSERT into choose_users (choose_id, user_id) values(:cid, :uid)",\
                cid=choice, uid=int(session["user_id"]))
            
            if answer == "yes":
                db.execute("UPDATE choose SET yes=yes+1 WHERE id=:cid", cid=choice)
            else:
                db.execute("UPDATE choose SET no=no+1 WHERE id=:cid", cid=choice)
        elif request.form.get("form") == "new_choice":
            # check for group
            group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
            group_id = group[0]["group_id"]
            
            # ensure group_id exists
            if group_id is None:
                return(redirect(url_for("index")))
            
            if not request.form.get("choice"):
                return error("choose", "must enter question")
            
            a = db.execute("INSERT INTO choose (text, group_id) VALUES (:q, :gid)",\
                q=request.form.get("choice"), gid=int(group_id))

        return(redirect(url_for("choose")))
    else:
        # check for group
        group = db.execute("SELECT group_id FROM users WHERE user_id = :user_id", user_id = int(session["user_id"]))
        group_id = group[0]["group_id"]
        
        # ensure group_id exists
        if group_id is None:
            return(redirect(url_for("index")))
            
        # load correct page 
        if not request.args.get("p1"):
            page1 = 1
        else:
            page1 = request.args.get("p1")
            try:
                page1 = int(page1)
            except ValueError:
                page1 = 1
        # load correct page 
        if not request.args.get("p2"):
            page2 = 1
        else:
            page2 = request.args.get("p2")
            try:
                page2 = int(page2)
            except ValueError:
                page2 = 1
        
        # get number of pages from database
        row = db.execute("SELECT count(*) from choose AS a LEFT JOIN \
            (SELECT * FROM choose_users WHERE user_id=:uid) AS b \
            ON a.id=b.choose_id \
            WHERE group_id=:gid AND b.id IS NULL", gid=group_id, uid=int(session["user_id"]))    
        num_pages1 = (row[0]["count(*)"] + 4) // 5
        if page1 > num_pages1:
            page1 = num_pages1
        
        my_choices = db.execute("SELECT a.date_asked, a.text, a.id FROM choose AS a LEFT JOIN \
            (SELECT * FROM choose_users WHERE user_id=:uid) AS b \
            ON a.id=b.choose_id WHERE group_id=:gid AND b.id IS NULL \
            ORDER BY a.date_asked DESC LIMIT 5 OFFSET :off",\
                gid=group_id,off=((page1 - 1) * 5), uid=int(session["user_id"]))
        
        for choice in my_choices:
            # get time, offset for EST and clean it up
            choice_time = datetime.strptime(choice["date_asked"],'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
            choice_time_string = choice_time.strftime('%A, %B %-d at %-I:%M:%S %p')
            choice["date_asked"] = choice_time_string
         
        # get answerred quesions      
        row = db.execute("SELECT count(*) from choose AS a INNER JOIN \
            (SELECT * FROM choose_users WHERE user_id=:uid) AS b \
            ON a.id=b.choose_id \
            WHERE group_id=:gid", gid=group_id, uid=int(session["user_id"]))
        num_pages2 = (row[0]["count(*)"] + 4) // 5
        if page2 > num_pages2:
            page2 = num_pages2
        
        chosen = db.execute("SELECT * FROM choose AS a INNER JOIN \
            (SELECT * FROM choose_users WHERE user_id=:uid) AS b \
            ON a.id=b.choose_id WHERE group_id=:gid  ORDER BY a.date_asked DESC LIMIT 5 OFFSET :off",\
            gid=group_id,off=((page2 - 1) * 5), uid=int(session["user_id"]))
         
        for choice in chosen:
            # get time, offset for EST and clean it up
            choice_time = datetime.strptime(choice["date_asked"],'%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
            choice_time_string = choice_time.strftime('%A, %B %-d at %-I:%M:%S %p')
            choice["date_asked"] = choice_time_string

        return(render("choose.html",my_choices=my_choices, page1=page1, num_pages1=num_pages1, \
            page2=page2, num_pages2=num_pages2, chosen=chosen))