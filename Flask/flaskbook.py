from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskbook_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

# Initialize db with the Flask app
db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)  
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

# Define the Friendship model directly in flask08.py
class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    users = db.relationship('users', backref=db.backref('friendships', lazy=True))

    def __init__(self, name, gender, description, user_id):
        self.name = name
        self.gender = gender
        self.description = description
        self.user_id = user_id

@app.route("/admin")
def admin():
    if "admin" in session:
        return render_template("admin.html")
    else:
        flash("You must be logged in as an admin to access this page.", "error")
        return redirect(url_for("admin_login"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        if username and email:
            existing_user = users.query.filter_by(name=username).first()
            if existing_user:
                flash("Username already exists. Try a different one.", "error")
            else:
                new_user = users(name=username, email=email)
                db.session.add(new_user)
                db.session.commit()
                flash("Your account has been registered!", "success")
                return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "admin" in session:
        user_to_delete = users.query.filter_by(_id=user_id).first()

        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()

            flash(f"User {user_to_delete.name} has been deleted successfully.", "success")
        else:
            flash("User not found.", "error")

        return redirect(url_for("view"))
    else:
        flash("You must be logged in as an admin to perform this action.", "error")
        return redirect(url_for("admin_login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        email = request.form["email"]

        if not user or not email:
            flash("Please enter both your name and email", "error")
            return redirect(url_for("login"))

        found_user = users.query.filter_by(name=user, email=email).first()
        if found_user:
            session.permanent = True
            session["user"] = user
            flash("Login Successful!", "success")
            return redirect(url_for("user"))
        else:
            flash("Error: Account not found. Please register first.", "error")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            flash("Already Logged In!", "info")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(name=user).first()

        if found_user:
            page = request.args.get('page', 1, type=int)
            per_page = 3

            friends_paginated = Friendship.query.filter_by(user_id=found_user._id).paginate(page=page, per_page=per_page)

            if request.method == "POST":
                email = request.form["email"]
                session["email"] = email
                found_user.email = email
                db.session.commit()
                flash("Email was saved!", "success")
            else:
                if "email" in session:
                    email = session["email"]

            return render_template("user.html", email=email, user=user, friends=friends_paginated)
        else:
            flash("User not found.", "error")
            return redirect(url_for("login"))
    else:
        flash("You are not logged in!", "error")
        return redirect(url_for("login"))

@app.route("/add_friend", methods=["POST"])
def add_friend():
    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(name=user).first()

        if found_user:
            friend_name = request.form["friend_name"]
            friend_gender = request.form["friend_gender"]
            friend_description = request.form["friend_description"]

            if friend_name and friend_gender and friend_description:
                new_friend = Friendship(name=friend_name, gender=friend_gender, description=friend_description, user_id=found_user._id)
                db.session.add(new_friend)
                db.session.commit()

                flash(f"Friend {friend_name} added successfully!", "success")
            else:
                flash("Please fill all the fields to add a friend.", "error")
        else:
            flash("User not found.", "error")

        return redirect(url_for("user"))
    else:
        flash("You must be logged in to add friends.", "error")
        return redirect(url_for("login"))

@app.route("/delete_friend/<int:friend_id>", methods=["POST"])
def delete_friend(friend_id):
    if "user" in session:
        user = session["user"]
        found_user = users.query.filter_by(name=user).first()

        if found_user:
            friend_to_delete = Friendship.query.filter_by(id=friend_id, user_id=found_user._id).first()

            if friend_to_delete:
                db.session.delete(friend_to_delete)
                db.session.commit()
                flash(f"Friend {friend_to_delete.name} has been deleted.", "success")
            else:
                flash("Friend not found or not associated with you.", "error")
        else:
            flash("User not found.", "error")

        return redirect(url_for("user"))
    else:
        flash("You are not logged in!", "error")
        return redirect(url_for("login"))
    
@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():

    admin_code_name = "marc2250"
    admin_password = "marc22500522cram"

    if request.method == "POST":
        code_name = request.form["code_name"]
        password = request.form["password"]

        if code_name == admin_code_name and password == admin_password:
            session["admin"] = code_name
            flash("Admin login successful!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid Code Name or Password.", "error")
            return redirect(url_for("admin_login"))

    return render_template("admin_login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates all tables (users and friendship) if they do not exist
    app.run(debug=True)
