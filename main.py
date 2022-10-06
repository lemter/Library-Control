from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/books")
def books():
    return render_template("books.html")

@app.route("/readers")
def readers():
    return render_template("readers.html")

@app.route("/borrows")
def borrows():
    return render_template("borrows.html")