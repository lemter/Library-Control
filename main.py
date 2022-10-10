import re
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
class LibControl:
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

    def addReader(self, f_name, l_name):
        if f_name and l_name:
            cursor.execute(f"INSERT INTO readers (reader_f_name, reader_l_name) VALUES ('{f_name}', '{l_name}')")
            connection.commit()
            self.js.window.location.reload()
        else:
            self.js.alert("All text fields must be filled.")

    def changeReaderName(self, reader_id, new_name):
        cursor.execute(f"UPDATE readers SET reader_f_name = '{new_name}' WHERE reader_id = {reader_id}")
        connection.commit()
        self.js.window.location.reload()

    def changeReaderLastName(self, reader_id, new_lastname):
        cursor.execute(f"UPDATE readers SET reader_l_name = '{new_lastname}' WHERE reader_id = {reader_id}")
        connection.commit()
        self.js.window.location.reload()

    def deleteReader(self, reader_id):
        cursor.execute(f"DELETE FROM readers WHERE reader_id = {reader_id}")
        connection.commit()
        self.js.window.location.replace("/readers")

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/books", methods=['POST', 'GET'])
def books():
    if request.method == 'GET':
        cursor.execute('SELECT * FROM books ORDER BY book_id ASC')
        books = cursor.fetchall()
        return LibControl.render(render_template("books/books.html", books = books))

@app.route("/books/<book_id>", methods=['POST', 'GET'])
def bookSettings(book_id):
    if request.method == 'GET':
        cursor.execute(f"SELECT book_name, book_author FROM books WHERE book_id = {book_id}")
        book = cursor.fetchone()
        book_name = book[0]
        book_author = book[1]
        return LibControl.render(render_template("books/book_settings.html", book_id = book_id, book_name = book_name, book_author = book_author))

@app.route("/readers", methods=['POST', 'GET'])
def readers():
    if request.method == 'GET':
        cursor.execute('SELECT * FROM readers ORDER BY reader_f_name, reader_l_name ASC')
        readers = cursor.fetchall()
        return LibControl.render(render_template("readers/readers.html", readers = readers))

@app.route("/readers/<reader_id>", methods=['POST', 'GET'])
def readerSettings(reader_id):
    if request.method == 'GET':
        cursor.execute(f"SELECT reader_f_name, reader_l_name FROM readers WHERE reader_id = {reader_id}")
        reader = cursor.fetchone()
        reader_name = reader[0]
        reader_lastname = reader[1]
        return LibControl.render(render_template("readers/reader_settings.html", reader_id = reader_id, reader_name = reader_name, reader_lastname = reader_lastname))


@app.route("/borrows")
def borrows():
    return render_template("borrows.html")

if __name__ == '__main__':
    app.run()