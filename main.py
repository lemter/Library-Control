from flask import Flask, render_template, request
import jyserver.Flask as jsf
import psycopg2

connection = psycopg2.connect(
    user = "postgres",
    password = "pass",
    host = "localhost",
    port = "5432",
    database = "library_db"
)

cursor = connection.cursor()

app = Flask(__name__)

@jsf.use(app)
class Books:
    def __init__(self):
        pass

    def addBook(self, book_name, book_author):
        if book_name and book_author:
            cursor.execute(f"INSERT INTO books (book_name, book_author) VALUES ('{book_name}', '{book_author}')")
            connection.commit()
            self.js.window.location.reload()
        else:
            self.js.alert("All text fields must be filled.")

    def changeBookName(self, book_id, new_name):
        cursor.execute(f"UPDATE books SET book_name = '{new_name}' WHERE book_id = {book_id}")
        connection.commit()
        self.js.window.location.reload()

    def changeAuthorName(self, book_id, new_author):
        cursor.execute(f"UPDATE books SET book_author = '{new_author}' WHERE book_id = {book_id}")
        connection.commit()
        self.js.window.location.reload()

    def deleteBook(self, book_id):
        cursor.execute(f"DELETE FROM books WHERE book_id = {book_id}")
        connection.commit()
        self.js.window.location.replace("/books")

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/books", methods=['POST', 'GET'])
def books():
    if request.method == 'GET':
        cursor.execute('SELECT * FROM books ORDER BY book_id ASC')
        books = cursor.fetchall()
        return Books.render(render_template("books/books.html", books = books))

@app.route("/books/<book_id>", methods=['POST', 'GET'])
def bookSetting(book_id):
    if request.method == 'GET':
        cursor.execute(f"SELECT book_name, book_author FROM books WHERE book_id = {book_id}")
        book = cursor.fetchone()
        book_name = book[0]
        book_author = book[1]
        return Books.render(render_template("books/book_settings.html", book_id = book_id, book_name = book_name, book_author = book_author))

@app.route("/readers")
def readers():
    return render_template("readers.html")

@app.route("/borrows")
def borrows():
    return render_template("borrows.html")

if __name__ == '__main__':
    app.run()