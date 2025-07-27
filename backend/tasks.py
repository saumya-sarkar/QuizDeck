from celery import shared_task
from models import QuizAttempt, ist_format
# from utils import format_report
# from mail import send_email
from datetime import datetime, timedelta
# import requests #plural
import csv
import os


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