from celery import shared_task
from models import db, QuizAttempt, User, Quiz, ist_format
from utils import format_report
from mail import send_email
from datetime import datetime, timedelta
import requests
import csv
import os
from time import sleep


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def getResultStatus(percentage):
      result_status = "Needs Improvement"
      if (percentage >= 90):
          result_status = "Outstanding"
      elif (percentage >= 80):
          result_status = "Excellent"
      elif (percentage >= 70):
          result_status = "Very Good"
      elif (percentage >= 60):
          result_status = "Good"
      elif (percentage >= 50):
          result_status = "Average"
      else:
          result_status = "Needs Improvement"
      return result_status

@shared_task(bind = True, ignore_results=False, name="admin_csv_report")
def generate_admin_report(self, period):
    try:
        # Create temp directory if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_dir = os.path.join(current_dir, 'static', 'csv_exports')
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir, exist_ok=True)
        csv_file_name = f"admin_report_{datetime.now().strftime('%f')}.csv"
        file_path = os.path.join(csv_dir, csv_file_name)

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            sr_no = 1

            # Write headers
            writer.writerow([
                'Sr No',
                'Attempt ID',
                'User ID',
                'Username',
                'Email',
                'Quiz ID',
                'Quiz Name',
                'Quiz Difficulty',
                'Quiz Type',
                'Chapter',
                'Subject',
                'Started At',
                'Submitted At',
                'Time Taken',
                'User Score',
                'Total Marks',
                'Percentage',
                'Result Status',
                'Submission Status'
            ])
            
            if period == 'last_30_days':
                thirty_days_ago = datetime.now() - timedelta(days=30)
                attempts = QuizAttempt.query.filter(
                    QuizAttempt.started_at >= thirty_days_ago
                ).order_by(QuizAttempt.started_at.desc()).all()
            else:  # 'all_time'
                attempts = QuizAttempt.query.order_by(QuizAttempt.started_at.desc()).all()
            
            
            # Write data rows
            for attempt in attempts:
                time_taken = format_time(attempt.time_taken_seconds) if attempt.time_taken_seconds else "00:00:00"
                percentage = round((attempt.user_score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0

                writer.writerow([
                    sr_no,
                    attempt.id,
                    attempt.user_id,
                    attempt.user.username,
                    attempt.user.email,
                    attempt.quiz_id,
                    attempt.quiz.name,
                    attempt.quiz.difficulty.value,
                    attempt.quiz.quiz_type.value,
                    attempt.quiz.chapter.name,
                    attempt.quiz.chapter.subject.name,
                    ist_format(attempt.started_at),
                    ist_format(attempt.submitted_at) if attempt.submitted_at else "Not Submitted",
                    time_taken,
                    attempt.user_score,
                    attempt.total_marks,
                    percentage,
                    getResultStatus(percentage),
                    attempt.status
                ])
                sr_no += 1
        
        return {"status": "completed", "file_path": file_path}
        
    except Exception as exc:
        print(f"CSV generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    


@shared_task(ignore_results = False, name = "monthly_report")
def monthly_report():
    users = User.query.all()
    for user in users[1:]:
        user_data = {}
        user_data['username'] = user.username if user.username else "not found"
        user_data['email'] = user.email if user.email else "not provided"
        user_performance = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        user_attempts = QuizAttempt.query.filter(QuizAttempt.started_at >= thirty_days_ago, 
                                                 QuizAttempt.user_id == user.id
                                                ).order_by(QuizAttempt.started_at.desc()).all()
        serial_no = 1
        for attempt in user_attempts:
            this_attempt = {}
            time_taken = format_time(attempt.time_taken_seconds) if attempt.time_taken_seconds else "00:00:00"
            percentage = round((attempt.user_score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0
            this_attempt["serial_no"] = serial_no
            this_attempt["quiz_name"] = attempt.quiz.name
            this_attempt["quiz_difficulty"] = attempt.quiz.difficulty.value
            this_attempt["quiz_type"] = attempt.quiz.quiz_type.value
            this_attempt["quiz_chapter"] = attempt.quiz.chapter.name
            this_attempt["quiz_subject"] = attempt.quiz.chapter.subject.name
            this_attempt["started_at"] = ist_format(attempt.started_at)
            this_attempt["submitted_at"] = ist_format(attempt.submitted_at) if attempt.submitted_at else "Not Submitted"
            this_attempt["time_taken"] = time_taken
            this_attempt["user_score"] = attempt.user_score
            this_attempt["total_marks"] = attempt.total_marks
            this_attempt["percentage"] = percentage
            this_attempt["result_status"] = getResultStatus(percentage)
            this_attempt["status"] = attempt.status
            serial_no += 1
            user_performance.append(this_attempt)
        user_data['performance'] = user_performance
        message = format_report('templates/mail_template_css.html', user_data)
        send_email(user.email, subject = "Monthly Performance Report - QuizDeck", message = message)
    return "Monthly reports sent"


@shared_task(ignore_results = False, name = "daily_reminder")
def daily_reminder():
    key = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"
    token = "O1AFV34l1DuvGi4DfTk89Vqe5Rgn5RfyxwAa0pKeuIA"
    url = f"https://chat.googleapis.com/v1/spaces/AAQA7RvR5EM/messages?key={key}&token={token}"
    
    users = User.query.all()
    quizzes = Quiz.query.all()
    for user in users[1:]:
        attempted_quizzes = [attempt.quiz_id for attempt in user.quiz_attempts]
        quiz_string = ""
        for quiz in quizzes:
            if quiz.id not in attempted_quizzes and quiz.check_status() != "Ended":
                quiz_string += f"🔵{quiz.name} -> 📌{quiz.check_status()}\n"

        text = (
                    f"Hi {user.username} 👋\n"
                    f"You have some quizzes waiting for you:\n\n"
                    f"{quiz_string}"
                    f"Start now 👉 http://localhost:8080/"
                )

        response = requests.post(url, json = {"text": text})
        sleep(10)  # To avoid hitting rate limits
        if response.status_code == 200:
            print("Daily reminders sent successfully")
        else:
            print(f"Failed to send daily reminder: {response.status_code} - {response.text}")
    # Return a message indicating success or failure
    return "Daily reminders sent."


# Automatic Quiz Unlocking Task
@shared_task(ignore_results = False, name = "unlock_quiz_task")
def unlock_quiz_task(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
   
    if not quiz:
        print(f"Quiz with ID {quiz_id} not found.")
        return "Quiz not found."
    
    if quiz.quiz_type.value == "Practice":
        return "Practice quizzes do not require unlocking."
    
    if quiz and quiz.is_locked and not quiz.is_unlocked_by_celery:
        quiz.is_locked = False
        quiz.is_unlocked_by_celery = True
        db.session.commit()
        print(f"Quiz {quiz.name} with ID {quiz.id} has been unlocked by Celery task.")
    else:
        print(f"Quiz with ID {quiz_id} is either not found or already unlocked.")
    return f"Quiz unlock task completed."