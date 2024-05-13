from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizzes.db'
db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    educator = db.relationship('User', backref=db.backref('subjects', lazy=True))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('questions', lazy=True))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'student':
            return render_template('student_dashboard.html', subjects=Subject.query.all())
        elif user.role == 'educator':
            return render_template('educator_dashboard.html', subjects=user.subjects)
        elif user.role == 'admin':
            return render_template('admin_dashboard.html', educators=User.query.filter_by(role='educator').all())
    else:
        flash('You need to login first!', 'warning')
        return redirect(url_for('login'))

@app.route('/quiz/<int:subject_id>', methods=['GET', 'POST'])
def quiz(subject_id):
    print("sjsbs",subject_id)
    if 'user_id' in session and session['role'] == 'student':
        if subject_id == 0:
            questions = Question.query.all()
        else:
            subject = Question.query.get(subject_id)
            print("Questionsa re=====>",subject)
            questions = subject
        if request.method == 'POST':
            score = 0
            for q in questions:
                answer = request.form.get(f'question_{q.id}')
                if answer == q.answer:
                    score += 1
            flash(f'Your score is {score} out of {len(questions)}', 'info')
            return redirect(url_for('dashboard'))
        return render_template('quiz.html', questions=questions)
    else:
        flash('You need to login as a student to take the quiz!', 'warning')
        return redirect(url_for('login'))

@app.route('/add_educator', methods=['GET', 'POST'])
def add_educator():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            if role == 'educator':
                user = User(username=username, password=password, role=role)
                db.session.add(user)
                db.session.commit()
                flash('Educator added successfully!', 'success')
            else:
                flash('Invalid role!', 'danger')
        return render_template('add_educator.html')
    else:
        flash('You need to login as an admin to add an educator!', 'warning')
        return redirect(url_for('login'))

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            educator_id = request.form['educator_id']
            subject = Subject(name=name, educator_id=educator_id)
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
        return render_template('add_subject.html', educators=User.query.filter_by(role='educator').all())
    else:
        flash('You need to login as an admin to add a subject!', 'warning')
        return redirect(url_for('login'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if 'user_id' in session and session['role'] == 'educator':
        if request.method == 'POST':
            question_text = request.form['question_text']
            options = request.form['options']
            answer = request.form['answer']
            subject_id = request.form['subject_id']
            question = Question(question_text=question_text, options=options, answer=answer, subject_id=subject_id)
            db.session.add(question)
            db.session.commit()
            flash('Question added successfully!', 'success')
        return render_template('add_question.html', subjects=Subject.query.all())
    else:
        flash('You need to login as an educator to add a question!', 'warning')
        return redirect(url_for('login'))
    
def add_migrate():
    # Create users
    admin_user = User(username='admin', password='password', role='admin')
    educator_user_1 = User(username='educator1', password='password', role='educator')
    educator_user_2 = User(username='educator2', password='password', role='educator')
    student_user = User(username='student', password='password', role='student')

# Create subjects and assign educators
    subject_1 = Subject(name='Math', educator=educator_user_1)
    subject_2 = Subject(name='Science', educator=educator_user_2)
    subject_3 = Subject(name='History', educator=educator_user_1)

# Create questions for each subject
    question_1 = Question(question_text='What is 2 + 2?', options='1, 2, 3, 4', answer='D', subject=subject_1)
    question_2 = Question(question_text='What is the capital of France?', options='Paris, London, Berlin, Madrid', answer='A', subject=subject_3)
    question_3 = Question(question_text='What is the symbol for sodium on the periodic table?', options='Na, K, Ca, Mg', answer='A', subject=subject_2)

# Add objects to the session and commit
    db.session.add_all([admin_user, educator_user_1, educator_user_2, student_user,
                    subject_1, subject_2, subject_3,
                    question_1, question_2, question_3])
    db.session.commit()

    print('Database populated successfully!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # add_migrate()
    app.run(debug=True)