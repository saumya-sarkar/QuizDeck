from flask import Flask
from flask_security import Security
from models import db, user_datastore
from flask_restful import Api
from flask_cors import CORS
from celery import Celery
from celery_init import celery_init_app
from celery.schedules import crontab
from tasks import generate_admin_report, monthly_report, daily_reminder
from caching import cache




def create_app():
    
    init_app = Flask(__name__)
    
    from config_file import localDev
    init_app.config.from_object(localDev)
    
    db.init_app(init_app)
    
    Security(init_app, user_datastore)

    CORS(init_app)

    init_api = Api(init_app, prefix='/api')

    cache.init_app(init_app)
    
    return init_app, init_api


app, api = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()
celery.conf.beat_schedule = {
    'send_monthly_report_task': {
        'task': 'monthly_report',
        'schedule': crontab(day_of_month='1', hour=19, minute=0),  # Run at 19:00 on the first day of every month
    },
    'send_daily_reminder_task': {
        'task': 'daily_reminder',
        'schedule': crontab(hour=19, minute=30),  # Every day at 19:30
    }
}
# 30 # Every 30 seconds
# crontab(minute='*/5'),  # Every 5 minutes
# crontab(hour=4, minute=30)  # Every day at 4:30 AM

from routes.user import UserRegister, UserLogin, qualificationList, checkUsername, checkEmail, userDetails
api.add_resource(UserRegister, '/register')  # localhost:5000/api/register
api.add_resource(UserLogin, '/login')  # localhost:5000/api/login
api.add_resource(qualificationList, '/qualifications')
api.add_resource(checkUsername, '/check-username')  # localhost:5000/api/check-username
api.add_resource(checkEmail, '/check-email')  # localhost:5000/api/check-email
api.add_resource(userDetails, '/user-details')  # localhost:5000/api/user-details

from routes.subject import GetAllSubs, UpdateSub, DeleteSub
api.add_resource(GetAllSubs, '/subject')  # localhost:5000/api/subject
api.add_resource(UpdateSub, '/subject/update')  # localhost:5000/api/subject/update
api.add_resource(DeleteSub, '/subject/delete')  # localhost:5000/api/subject/delete


from routes.chapter import GetAllChapters, UpdateChapter, DeleteChapter
api.add_resource(GetAllChapters, '/chapter')  # localhost:5000/api/chapter
api.add_resource(UpdateChapter, '/chapter/update')  # localhost:5000/api/chapter/update
api.add_resource(DeleteChapter, '/chapter/delete')  # localhost:5000/api/chapter/delete


from routes.quiz import GetAllQuizzes, UpdateQuiz, DeleteQuiz
api.add_resource(GetAllQuizzes, '/quiz')  # localhost:5000/api/quiz
api.add_resource(UpdateQuiz, '/quiz/update')  # localhost:5000/api/quiz/update
api.add_resource(DeleteQuiz, '/quiz/delete')  # localhost:5000/api/quiz/delete


from routes.question import get_all_questions, update_question, delete_question
api.add_resource(get_all_questions, '/question')  # localhost:5000/api/question
api.add_resource(update_question, '/question/update')  # localhost:5000/api/question/update
api.add_resource(delete_question, '/question/delete')  # localhost:5000/api/question/delete

from routes.user_quiz import StartQuiz, GetQuizData, SaveAnswer, SubmitQuiz, GetQuizResult
api.add_resource(StartQuiz, '/quiz/start')  # localhost:5000/api/quiz/start
api.add_resource(GetQuizData, '/quiz/data')  # localhost:5000/api/quiz/data
api.add_resource(SaveAnswer, '/quiz/save-answer')  # localhost:5000/api/quiz/save-answer
api.add_resource(SubmitQuiz, '/quiz/submit')  # localhost:5000/api/quiz/submit
api.add_resource(GetQuizResult, '/quiz/result')  # localhost:5000/api/quiz/result

# User Quiz Attempts API
from routes.user_attempts import UserQuizAttempts
api.add_resource(UserQuizAttempts, '/user/quiz-attempts')  # localhost:5000/api/user/quiz-attempts

# Admin Users Management Routes
from routes.admin_users import GetAllUsers, GetUserDetails, ToggleUserStatus
api.add_resource(GetAllUsers, '/admin/users')  # localhost:5000/api/admin/users
api.add_resource(GetUserDetails, '/admin/users/details')  # localhost:5000/api/admin/users/details
api.add_resource(ToggleUserStatus, '/admin/users/toggle-status')  # localhost:5000/api/admin/users/toggle-status

from routes.analytics import AdminAnalytics, UserAnalytics

# Add these API endpoints after your existing routes
api.add_resource(AdminAnalytics, '/admin/analytics')  # localhost:5000/api/admin/analytics
api.add_resource(UserAnalytics, '/user/analytics')   # localhost:5000/api/user/analytics


# Dashboard Stats API
from routes.admin_users import AdminDashboardStats

api.add_resource(AdminDashboardStats, '/admin/dashboard/stats')



from routes.csv_export import UserAttemptsCSVExport, CSVExportStatus, CSVExportDownload

# Add to your existing API routes:
api.add_resource(UserAttemptsCSVExport, '/csv-export/generate')
api.add_resource(CSVExportStatus, '/csv-export/status')
api.add_resource(CSVExportDownload, '/csv-export/download/<string:task_id>')  # localhost:5000/api/csv-export/download/<task_id>


if __name__ == '__main__':
    app.run(port=5000)  # 5000 is the default port for Flask