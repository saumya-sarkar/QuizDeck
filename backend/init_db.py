from models import db, user_datastore, Question
# from app import app
# from flask import current_app as app
from app import create_app
from flask_security import hash_password
from datetime import date
import os
from sqlalchemy import text

app, _ = create_app()


def create_roles():
    user_datastore.find_or_create_role(name='admin')
    user_datastore.find_or_create_role(name='user')
    db.session.commit()
    print("Roles created or already exist.")


def create_admin():
    if not user_datastore.find_user(email='admin@quizapp.com') and user_datastore.find_role("admin"):
        user_datastore.create_user(email='admin@quizapp.com', username='admin', password_hash=hash_password('admin'), 
                                   full_name= "Saumya Sarkar", qualification= "PG", dob=date(2000, 1, 1), roles=['admin'])
        db.session.commit()
        print("Admin created.")
    else:
        print("Admin already exists.")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

with app.app_context():
    
    db.create_all() # Create tables 
    create_roles() # Create roles
    create_admin() # Create admin

    # tests = Question.query.filter(Question.question_statement.like('%Test%')).all()
    tests = Question.query.filter(Question.id.in_(range(7,8))).all()
    for test in tests:
        db.session.delete(test)
        db.session.commit()  # Commit changes to the database
        print(f"Deleted test: {test.id}")

    # Example of dropping a table (uncomment if needed)
    
    # # Define the table name you want to drop
    # table_name = 'quiz'
    # # column_name = 'updated_at'

    # # Create a SQL DROP TABLE statement
    # drop_table = text(f"DROP TABLE IF EXISTS {table_name};")

    # # sql_statement = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} DATETIME;")
    # # sql_statement = text(f"ALTER TABLE {table_name} DROP COLUMN {column_name};")

    # # Execute the SQL statement
    # with db.engine.connect() as connection:
    #     connection.execute(drop_table)
print("Database initialized and roles created.")


# from models import qualification_list
# print([str(i.value) for i in qualification_list.__members__.values()])