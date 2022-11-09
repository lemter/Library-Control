from flask import Flask, render_template, request, session, redirect
import jyserver.Flask as jsf
import psycopg2
from datetime import datetime

connection = psycopg2.connect(
    user = "postgres",
    password = "pass",
    host = "localhost",
    port = "5432",
    database = "library_db"
)

cursor = connection.cursor()

app = Flask(__name__)

app.secret_key = "libcontrol_secretkey"

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

    def addReader(self, f_name, l_name, username, passw):
        if f_name and l_name and username and passw:
            cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
            user = cursor.fetchone()
            if not user:
                cursor.execute(f"INSERT INTO readers (reader_f_name, reader_l_name) VALUES ('{f_name}', '{l_name}') RETURNING reader_id")
                reader_id = cursor.fetchone()[0]
                connection.commit()
                cursor.execute(f"INSERT INTO users VALUES('{username}', '{passw}', 0, {reader_id})")
                connection.commit()
                self.js.window.location.reload()
            else:
                self.js.alrt("Username is taken.")
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

    def addBorrow(self, reader_id, book_id):
        if reader_id and book_id:
            cursor.execute(f"INSERT INTO borrows (reader_id, book_id, taking_date, taking_time) VALUES ({reader_id}, {book_id}, '{datetime.now().strftime('%m/%d/%Y')}', '{datetime.now().strftime('%H:%M')}')")
            connection.commit()
            self.js.window.location.reload()
        else:
            self.js.alert("All text fields must be filled.")

    def new_b_reader(self, borrow_id, reader_id):
        print(borrow_id, reader_id)
        if reader_id:
            cursor.execute(f"UPDATE borrows SET reader_id = {reader_id} WHERE borrow_id = {borrow_id}")
            connection.commit()
            self.js.window.location.reload()
        else:
            self.js.alert("You need to write new reader id.")

    def new_b_book(self, borrow_id, book_id):
        if book_id:
            cursor.execute(f"UPDATE borrows SET book_id = {book_id} WHERE borrow_id = {borrow_id}")
            connection.commit()
            self.js.window.location.reload()
        else:
            self.js.alert("You need to write new book id.")

    def new_b_takingtime(self, borrow_id, takingdate, takingtime):
        if takingdate and takingtime:
            try:
                cursor.execute(f"UPDATE borrows SET taking_date = {takingdate}, taking_time = {takingtime} WHERE borrow_id = {borrow_id}")
                connection.commit()
            except: self.js.alert("Date or time format writed incorrect.")
            self.js.window.location.reload()
        else:
            self.js.alert("You need to fill taking date and time fields.")

    def submite_borrow(self, borrow_id):
        cursor.execute(f"UPDATE borrows SET return_date = '{datetime.now().strftime('%m/%d/%Y')}', return_time = '{datetime.now().strftime('%H:%M')}' WHERE borrow_id = {borrow_id}")
        connection.commit()
        self.js.window.location.reload()

    def deleteBorrow(self, borrow_id):
        cursor.execute(f"DELETE FROM borrows WHERE borrow_id = {borrow_id}")
        connection.commit()
        self.js.window.location.replace("/borrows")

    def mainpage(self, reader_id):
        self.js.window.location.replace(f"/home?reader_id={reader_id}")

    def login(self, login, passw):
        cursor.execute(f"SELECT * FROM users WHERE username = '{login}' AND password = '{passw}'")
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['username'] = login
            session['password'] = passw
            session['level'] = user[2]
            session['reader_id'] = user[3]
            self.js.window.location.replace('/')
        else:
            self.js.alert("Incorrect login or password!")

    def deauth(self):
        session.pop('loggedin')
        session.pop('username')
        session.pop('password')
        session.pop('level')
        session.pop('reader_id')
        self.js.window.location.replace('/')

    def regist(self, login, passw, reader_id):
        cursor.execute(f"INSERT INTO users VALUES('{login}', '{passw}', 0, {reader_id})")
        connection.commit()
        self.js.window.location.replace('/')

@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def index():
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        cursor.execute(f"SELECT * FROM readers WHERE reader_id = {session['reader_id']}")
        userdata = cursor.fetchone()
        cursor.execute(f"""
        SELECT borrow_id,
               borrows.reader_id,
               CONCAT(reader_f_name, ' ', reader_l_name) AS "reader_name",
	           borrows.book_id,
	           books.book_name,
	           books.book_author,
	           borrows.taking_date,
	           borrows.taking_time,
	           borrows.return_date,
	           borrows.return_time,
	           CASE WHEN (return_date is null AND taking_date + interval '30 day' > CURRENT_DATE) THEN ('Expected')
	   		        WHEN (return_date is null AND taking_date + interval '30 day' <= CURRENT_DATE) THEN ('Overdue')
			        WHEN (return_date is not null) THEN ('Submitted')
			        END AS "status"
        FROM borrows
        JOIN readers ON (borrows.reader_id = readers.reader_id)
        JOIN books ON (borrows.book_id = books.book_id)
        WHERE borrows.reader_id = {session['reader_id']}
        ORDER BY borrows.taking_date DESC, taking_time DESC""")
        borrows = cursor.fetchall()
        return LibControl.render(render_template("reader_index.html", userdata = userdata, borrows = borrows))
    elif session["level"] == 1:
        return LibControl.render(render_template("index.html"))

@app.route("/books", methods=['POST', 'GET'])
def books():
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM books ORDER BY book_name, book_author ASC')
            books = cursor.fetchall()
            return LibControl.render(render_template("books/books.html", books = books))

@app.route("/books/<book_id>", methods=['POST', 'GET'])
def bookSettings(book_id):
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute(f"SELECT book_name, book_author FROM books WHERE book_id = {book_id}")
            book = cursor.fetchone()
            book_name = book[0]
            book_author = book[1]
            return LibControl.render(render_template("books/book_settings.html", book_id = book_id, book_name = book_name, book_author = book_author))

@app.route("/readers", methods=['POST', 'GET'])
def readers():
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM readers ORDER BY reader_f_name, reader_l_name ASC')
            readers = cursor.fetchall()
            return LibControl.render(render_template("readers/readers.html", readers = readers))

@app.route("/readers/<reader_id>", methods=['POST', 'GET'])
def readerSettings(reader_id):
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute(f"SELECT reader_f_name, reader_l_name FROM readers WHERE reader_id = {reader_id}")
            reader = cursor.fetchone()
            reader_name = reader[0]
            reader_lastname = reader[1]
            return LibControl.render(render_template("readers/reader_settings.html", reader_id = reader_id, reader_name = reader_name, reader_lastname = reader_lastname))


@app.route("/borrows", methods=['POST', 'GET'])
def borrows():
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute("""
            SELECT borrow_id,
               borrows.reader_id,
               CONCAT(reader_f_name, ' ', reader_l_name) AS "reader_name",
	           borrows.book_id,
	           books.book_name,
	           books.book_author,
	           borrows.taking_date,
	           borrows.taking_time,
	           borrows.return_date,
	           borrows.return_time,
	           CASE WHEN (return_date is null AND taking_date + interval '30 day' > CURRENT_DATE) THEN ('Expected')
	   		        WHEN (return_date is null AND taking_date + interval '30 day' <= CURRENT_DATE) THEN ('Overdue')
			        WHEN (return_date is not null) THEN ('Submitted')
			        END AS "status"
            FROM borrows
            JOIN readers ON (borrows.reader_id = readers.reader_id)
            JOIN books ON (borrows.book_id = books.book_id)""")
            borrows = cursor.fetchall()
            return LibControl.render(render_template("temp_pages/borrows.html", borrows = borrows))

@app.route("/borrows/<borrow_id>", methods=['POST', 'GET'])
def borrow_info(borrow_id):
    if not 'loggedin' in session: return redirect('/auth')
    if session["level"] == 0:
        return redirect('/')
    elif session["level"] == 1:
        if request.method == 'GET':
            cursor.execute(f"""
            SELECT borrow_id,
               borrows.reader_id,
               CONCAT(reader_f_name, ' ', reader_l_name) AS "reader_name",
	           borrows.book_id,
	           books.book_name,
	           books.book_author,
	           borrows.taking_date,
	           borrows.taking_time,
	           borrows.return_date,
	           borrows.return_time,
	           CASE WHEN (return_date is null AND taking_date + interval '30 day' > CURRENT_DATE) THEN ('Expected')
	   		        WHEN (return_date is null AND taking_date + interval '30 day' <= CURRENT_DATE) THEN ('Overdue')
			        WHEN (return_date is not null) THEN ('Submitted')
			        END AS "status"
            FROM borrows
            JOIN readers ON (borrows.reader_id = readers.reader_id)
            JOIN books ON (borrows.book_id = books.book_id)
            WHERE borrow_id = {borrow_id}""")
            borrow = cursor.fetchone()
            return LibControl.render(render_template("temp_pages/borrow_info.html", borrow = borrow))

@app.route("/auth")
def auth():
    return LibControl.render(render_template('auth.html'))

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)