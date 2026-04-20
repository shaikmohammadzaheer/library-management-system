from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------------------
# MODELS
# --------------------

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(100))
    quantity = db.Column(db.Integer)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    roll = db.Column(db.String(50))


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    book_id = db.Column(db.Integer)
# --------------------
# ROUTES
# --------------------

@app.route('/')
def home():
    return render_template('home.html')


# 📚 BOOKS PAGE
@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@app.route('/admin')
def admin():
    total_books = Book.query.count()
    total_students = Student.query.count()
    total_issued = Issue.query.count()

    return render_template('admin.html',
                           books=total_books,
                           students=total_students,
                           issued=total_issued)

# ➕ ADD BOOK
@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    quantity = request.form['quantity']

    new_book = Book(title=title, author=author, quantity=quantity)
    db.session.add(new_book)
    db.session.commit()

    return redirect('/books')


# ❌ DELETE BOOK
@app.route('/delete_student/<int:id>')
def delete_student(id):
    student = Student.query.get(id)

    if student:
        db.session.delete(student)
        db.session.commit()

    return redirect('/student')


# ✏️ EDIT BOOK
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.roll = request.form['roll']

        db.session.commit()
        return redirect('/student')

    return render_template('edit_student.html', student=student)


# 👨‍🎓 STUDENT PAGE
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']

        new_student = Student(name=name, roll=roll)
        db.session.add(new_student)
        db.session.commit()

    students = Student.query.all()   # ✅ THIS IS IMPORTANT

    return render_template('student.html', students=students)


# 📖 ISSUE BOOK (FIXED)
@app.route('/issue/<int:id>', methods=['GET', 'POST'])
def issue_book(id):
    book = Book.query.get(id)
    students = Student.query.all()

    if request.method == 'POST':
        student = request.form['student']

        if book.quantity > 0:
            book.quantity -= 1

            new_issue = Issue(student_name=student, book_id=id)
            db.session.add(new_issue)

            db.session.commit()

        return redirect('/books')

    return render_template('issue.html', book=book, students=students)


# 📜 ISSUED BOOKS PAGE
@app.route('/issued')
def issued_books():
    records = Issue.query.all()

    data = []
    for r in records:
        book = Book.query.get(r.book_id)

        data.append({
            'student': r.student_name,   # make sure this exists
            'book': book.title if book else "Unknown",
            'id': r.id
        })

    return render_template('issued.html', records=data)


# 🔄 RETURN BOOK
@app.route('/return/<int:id>')
def return_book(id):
    issue = Issue.query.get(id)

    if issue:
        book = Book.query.get(issue.book_id)
        book.quantity += 1

        db.session.delete(issue)
        db.session.commit()

    return redirect('/issued')


@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.roll = request.form['roll']

        db.session.commit()
        return redirect('/student')

    return render_template('edit_student.html', student=student)

# -------------------
# CREATE TABLES
# -------------------
with app.app_context():
    db.create_all()

# -------------------
# RUN APP
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
