# populate_db.py
from app import db, User, Subject, Question

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