from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, RoleMixin, UserMixin
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def ist_now():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

def ist_format(dt):
    if dt is not None:
        return dt.strftime("%Y-%m-%d %H:%M:%S") 
    else: 
        return None
    

db = SQLAlchemy()

import enum
from sqlalchemy import Enum
class qualification_list(enum.Enum):
    HS = "High School"
    DIP = "Diploma"
    UG = "Undergraduate"
    PG = "Postgraduate"
    PhD = "Doctorate"
    OTH = "Other"


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True) 

    email = db.Column(db.String(256), unique=True, nullable=False) 
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(256), nullable=True)
    qualification = db.Column(Enum(qualification_list), nullable=False, default=qualification_list.OTH)
    dob = db.Column(db.Date(), nullable=True)

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(128), unique=True, nullable=False)

    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    quiz_attempts = db.relationship('QuizAttempt', back_populates='user', lazy='dynamic')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)
    cover_url = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=ist_now)
    updated_at = db.Column(db.DateTime(), nullable=True, default=None, onupdate=ist_now)

    # This is used to mark the subject as deleted without actually removing it from the database.
    # This allows for easy restoration if needed
    deleted = db.Column(db.Boolean, default=False)
    
    #relationships
    chapters = db.relationship('Chapter', back_populates='subject', lazy='dynamic', cascade='all, delete-orphan')
    

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=ist_now)
    updated_at = db.Column(db.DateTime(), nullable=True, default=None, onupdate=ist_now)

    # This is used to mark the chapter as deleted without actually removing it from the database. 
    # This allows for easy restoration if needed
    deleted = db.Column(db.Boolean, default=False)
    
    #relationships
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter', lazy='dynamic', cascade='all, delete-orphan')



class difficulty_list(enum.Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

class quiz_types(enum.Enum):
    Practice = "Practice"
    Mock = "Mock"
    Exam = "Exam"

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    duration_mins = db.Column(db.Integer, nullable=False, default=60)  # Default duration is set to 60 minutes
    difficulty = db.Column(Enum(difficulty_list), nullable=False, default=difficulty_list.Easy)  # Default difficulty is set to Easy
    quiz_type = db.Column(Enum(quiz_types), nullable=False, default=quiz_types.Practice)  # Default quiz type is set to Practice

    start_time = db.Column(db.DateTime(), nullable=True)  # Date and Time when the quiz is scheduled
    end_time = db.Column(db.DateTime(), nullable=True)  # Date and Time when the quiz ends
    is_locked = db.Column(db.Boolean, nullable=False, default=False)  # Default flag indicates if the quiz is locked or not
    is_unlocked_by_celery = db.Column(db.Boolean, nullable=True, default=False)

    created_at = db.Column(db.DateTime(), nullable=False, default=ist_now)
    updated_at = db.Column(db.DateTime(), nullable=True, default=None, onupdate=ist_now)

    # This is used to mark the quiz as deleted without actually removing it from the database.
    # This allows for easy restoration if needed
    deleted = db.Column(db.Boolean, default=False)

    #relationships
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    chapter = db.relationship('Chapter', back_populates='quizzes')
    quiz_attempts = db.relationship('QuizAttempt', back_populates='quiz', lazy='dynamic')
    questions = db.relationship('Question', back_populates='quiz', lazy='dynamic', cascade='all, delete-orphan')


    def check_locked(self):
        if self.start_time and self.end_time:
            start_time = self.start_time.astimezone(ZoneInfo("Asia/Kolkata"))
            end_time = self.end_time.astimezone(ZoneInfo("Asia/Kolkata"))
            now = ist_now()
            if start_time <= now <= end_time:
                self.is_locked = False
                db.session.commit()  # Commit the change to the database
            else:
                self.is_locked = True
                db.session.commit()  # Commit the change to the database
    
    def check_status(self):
        if self.start_time and self.end_time:
            start_time = self.start_time.astimezone(ZoneInfo("Asia/Kolkata"))
            end_time = self.end_time.astimezone(ZoneInfo("Asia/Kolkata"))
            now = ist_now()
            if now < start_time:
                return "Upcoming"
            elif start_time <= now <= end_time:
                return "Active"
            else:
                return "Ended"
        return "Available"
    
    def check_available_for(self):
        start_time = self.start_time.astimezone(ZoneInfo("Asia/Kolkata")) if self.start_time else None
        end_time = self.end_time.astimezone(ZoneInfo("Asia/Kolkata")) if self.end_time else None
        if start_time is None or end_time is None:
            return None
        duration = end_time - start_time
        if duration is not None and isinstance(duration, timedelta):
            days = duration.days
            str_duration = str(duration)
            hours, minutes, seconds = str_duration.split(' ')[-1].split(':')
            if days > 0:
                return f"{days} days {hours} hours {minutes} minutes"
            elif int(hours) > 0:
                return f"{hours} hours {minutes} minutes"
            else:
                return f"{minutes} minutes"
        else:
            return None
    
    def get_total_marks(self):
        total_marks = 0
        for question in self.questions:
            if not question.deleted:
                    total_marks += question.marks
        return total_marks
    
    def get_total_questions(self):
        total_questions = 0
        for question in self.questions:
            if not question.deleted:
                total_questions += 1
        return total_questions
    
    def get_total_attempts(self):
        return self.quiz_attempts.count()
    
    def get_total_users(self):
        total_users = set()
        for attempt in self.quiz_attempts:
            if attempt.user_id is not None:
                total_users.add(attempt.user_id)
        return len(total_users)


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.Text, unique = True, nullable=False)  # Statement of the question
    marks = db.Column(db.Integer, nullable=False, default=1)  # Default marks for the question is set to 1
    explanation = db.Column(db.Text, nullable=True)  # Optional explanation for the question
    
    # This is used to mark the question as deleted without actually removing it from the database.
    # This allows for easy restoration if needed
    deleted = db.Column(db.Boolean, default=False)
    
    #relationships
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quiz = db.relationship('Quiz', back_populates='questions')
    options = db.relationship('Option', back_populates='question', lazy='dynamic', cascade='all, delete-orphan')

class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)

    option_text = db.Column(db.Text, nullable=False)  # Text of the option
    is_correct = db.Column(db.Boolean, default=False)

    #relationships
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question', back_populates='options')


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'
    id = db.Column(db.Integer, primary_key=True)
    
    started_at = db.Column(db.DateTime, nullable=False, default=ist_now)
    submitted_at = db.Column(db.DateTime, nullable=True)
    time_taken_seconds = db.Column(db.Integer, nullable=True)  # Total time taken in seconds
    
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, auto_submitted
    user_score = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=0)
    
    # relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user = db.relationship('User', back_populates = 'quiz_attempts')
    quiz = db.relationship('Quiz', back_populates = 'quiz_attempts')
    answers = db.relationship('UserAnswer', back_populates = 'quiz_attempt', cascade = 'all, delete-orphan')


class UserAnswer(db.Model):
    __tablename__ = 'user_answer'
    id = db.Column(db.Integer, primary_key=True)
    
    is_correct = db.Column(db.Boolean, default=False)
    marks_obtained = db.Column(db.Integer, default=0)

    # Relationships
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    quiz_attempt = db.relationship('QuizAttempt', back_populates='answers')
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.relationship('Question')
    selected_option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=True)
    selected_option = db.relationship('Option')