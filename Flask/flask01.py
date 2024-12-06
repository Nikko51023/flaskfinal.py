from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello! I have a question... <h1>Nigahi Na?<h1>"

@app.route("/<name>")
def user(name):
    return f"Eyy wazzup {name}!"

@app.route("/admin")
def admin():
    return redirect(url_for("home"))
if __name__ == "__main__":
    app.run()