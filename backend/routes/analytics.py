from flask_security import auth_required, roles_accepted
from flask_restful import Resource
from models import db, User, Subject, Quiz, QuizAttempt, Question
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class AdminAnalytics(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        try:
            # Chart 1: User Registration Trend (Last 12 months)
            end_date = datetime.now(ZoneInfo("Asia/Kolkata"))
            start_date = end_date - timedelta(days=365)
            
            # Get monthly user registrations
            monthly_registrations = db.session.query(
                func.strftime('%Y-%m', User.registration_date).label('month'),
                func.count(User.id).label('count')
            ).filter(
                User.registration_date >= start_date,
                User.roles.any(name='user')
            ).group_by(func.strftime('%Y-%m', User.registration_date)).all()
            
            # Chart 2: Quiz Attempts by Subject
            subject_attempts = db.session.query(
                Subject.name.label('subject_name'),
                func.count(QuizAttempt.id).label('attempts')
            ).join(
                Quiz, Subject.id == Quiz.chapter_id
            ).join(
                QuizAttempt, Quiz.id == QuizAttempt.quiz_id
            ).filter(
                Subject.deleted == False,
                Quiz.deleted == False
            ).group_by(Subject.name).all()
            
            # Chart 3: Average Quiz Scores by Difficulty
            difficulty_scores = db.session.query(
                Quiz.difficulty.label('difficulty'),
                func.avg(QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks).label('avg_percentage')
            ).join(
                QuizAttempt, Quiz.id == QuizAttempt.quiz_id
            ).filter(
                Quiz.deleted == False,
                QuizAttempt.status.in_(['completed', 'auto_submitted']),
                QuizAttempt.total_marks > 0
            ).group_by(Quiz.difficulty).all()
            
            # Chart 4: Monthly Quiz Activity (Attempts vs Completions)
            monthly_activity = db.session.query(
                func.strftime('%Y-%m', QuizAttempt.started_at).label('month'),
                func.count(QuizAttempt.id).label('total_attempts'),
                func.sum(
                    func.case(
                        (QuizAttempt.status.in_(['completed', 'auto_submitted']), 1),
                        else_=0
                    )
                ).label('completed_attempts')
            ).filter(
                QuizAttempt.started_at >= start_date
            ).group_by(func.strftime('%Y-%m', QuizAttempt.started_at)).all()
            
            return {
                "code": 200,
                "data": {
                    "user_registrations": [
                        {"month": reg.month, "count": reg.count}
                        for reg in monthly_registrations
                    ],
                    "subject_attempts": [
                        {"subject": attempt.subject_name, "attempts": attempt.attempts}
                        for attempt in subject_attempts
                    ],
                    "difficulty_scores": [
                        {"difficulty": score.difficulty.value, "avg_score": round(score.avg_percentage, 1)}
                        for score in difficulty_scores if score.avg_percentage
                    ],
                    "monthly_activity": [
                        {
                            "month": activity.month,
                            "total_attempts": activity.total_attempts,
                            "completed_attempts": activity.completed_attempts
                        }
                        for activity in monthly_activity
                    ]
                }
            }, 200
            
        except Exception as error:
            return {"code": 500, "error_message": f"An error occurred: {str(error)}"}, 500

class UserAnalytics(Resource):
    @auth_required('token')
    def get(self):
        from flask_security import current_user
        
        try:
            user_id = current_user.id
            
            # Chart 1: User's Performance by Subject (Last 6 months)
            end_date = datetime.now(ZoneInfo("Asia/Kolkata"))
            start_date = end_date - timedelta(days=180)
            
            subject_performance = db.session.query(
                Subject.name.label('subject_name'),
                func.avg(QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks).label('avg_percentage'),
                func.count(QuizAttempt.id).label('attempts')
            ).join(
                Quiz, Subject.id == Quiz.chapter_id
            ).join(
                QuizAttempt, Quiz.id == QuizAttempt.quiz_id
            ).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.started_at >= start_date,
                QuizAttempt.status.in_(['completed', 'auto_submitted']),
                QuizAttempt.total_marks > 0,
                Subject.deleted == False,
                Quiz.deleted == False
            ).group_by(Subject.name).all()
            
            # Chart 2: Weekly Quiz Activity (Last 8 weeks)
            weekly_activity = db.session.query(
                func.strftime('%Y-W%W', QuizAttempt.started_at).label('week'),
                func.count(QuizAttempt.id).label('attempts'),
                func.avg(QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks).label('avg_score')
            ).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.started_at >= start_date,
                QuizAttempt.status.in_(['completed', 'auto_submitted']),
                QuizAttempt.total_marks > 0
            ).group_by(func.strftime('%Y-W%W', QuizAttempt.started_at)).all()
            
            # Chart 3: Score Distribution
            score_ranges = db.session.query(
                func.case(
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 90, '90-100%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 80, '80-89%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 70, '70-79%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 60, '60-69%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 50, '50-59%'),
                    else_='Below 50%'
                ).label('score_range'),
                func.count(QuizAttempt.id).label('count')
            ).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.status.in_(['completed', 'auto_submitted']),
                QuizAttempt.total_marks > 0
            ).group_by(
                func.case(
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 90, '90-100%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 80, '80-89%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 70, '70-79%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 60, '60-69%'),
                    (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks >= 50, '50-59%'),
                    else_='Below 50%'
                )
            ).all()
            
            # Chart 4: Recent Quiz Trends (Last 10 attempts)
            recent_attempts = db.session.query(
                Quiz.name.label('quiz_name'),
                (QuizAttempt.user_score * 100.0 / QuizAttempt.total_marks).label('percentage'),
                QuizAttempt.started_at
            ).join(
                Quiz, QuizAttempt.quiz_id == Quiz.id
            ).filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.status.in_(['completed', 'auto_submitted']),
                QuizAttempt.total_marks > 0
            ).order_by(desc(QuizAttempt.started_at)).limit(10).all()
            
            return {
                "code": 200,
                "data": {
                    "subject_performance": [
                        {
                            "subject": perf.subject_name,
                            "avg_score": round(perf.avg_percentage, 1),
                            "attempts": perf.attempts
                        }
                        for perf in subject_performance
                    ],
                    "weekly_activity": [
                        {
                            "week": activity.week,
                            "attempts": activity.attempts,
                            "avg_score": round(activity.avg_score, 1) if activity.avg_score else 0
                        }
                        for activity in weekly_activity
                    ],
                    "score_distribution": [
                        {"range": score.score_range, "count": score.count}
                        for score in score_ranges
                    ],
                    "recent_trends": [
                        {
                            "quiz": attempt.quiz_name,
                            "score": round(attempt.percentage, 1),
                            "date": attempt.started_at.strftime('%Y-%m-%d')
                        }
                        for attempt in reversed(recent_attempts)
                    ]
                }
            }, 200
            
        except Exception as error:
            return {"code": 500, "error_message": f"An error occurred: {str(error)}"}, 500