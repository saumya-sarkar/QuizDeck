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
            # Chart 1: Total Attempts by User
            user_attempts = []

            all_users = User.query.filter(User.roles.any(name='user')).all()

            for user in all_users:
                attempts_count = user.quiz_attempts.filter(
                    QuizAttempt.status.in_(['completed', 'auto_submitted'])
                ).count()
                user_attempts.append({
                    "username": user.username,
                    "attempts": attempts_count
                })
            
            # Sort by attempts in descending order
            user_attempts.sort(key=lambda x: x['attempts'], reverse=True)


            # Chart 2: Total Attempts by Subject

            subject_attempts = []

            all_subjects = Subject.query.filter(Subject.deleted == False).all()
            all_attempts = QuizAttempt.query.filter(
                QuizAttempt.status.in_(['completed', 'auto_submitted'])
            ).all()
            for subject in all_subjects:
                attempts_count = 0
                for attempt in all_attempts:
                    if attempt.quiz.chapter.subject_id == subject.id:
                        attempts_count += 1

                subject_attempts.append({
                    "subject": subject.name,
                    "attempts": attempts_count
                })
            # Sort by attempts in descending order
            subject_attempts.sort(key=lambda x: x['attempts'], reverse=True)

            # Chart 3: Average Quiz Scores by Difficulty
            e_score, m_score, h_score = 0, 0, 0
            e_marks, m_marks, h_marks = 0, 0, 0
            for attempt in all_attempts:
                if attempt.quiz.difficulty.value == 'Easy':
                    e_score += attempt.user_score
                    e_marks += attempt.total_marks
                elif attempt.quiz.difficulty.value == 'Medium':
                    m_score += attempt.user_score
                    m_marks += attempt.total_marks
                elif attempt.quiz.difficulty.value == 'Hard':
                    h_score += attempt.user_score
                    h_marks += attempt.total_marks

            difficulty_scores = [
                {"difficulty": "Easy", "avg_score": round((e_score / e_marks) * 100, 2) if e_marks > 0 else 0},
                {"difficulty": "Medium", "avg_score": round((m_score / m_marks) * 100, 2) if m_marks > 0 else 0},
                {"difficulty": "Hard", "avg_score": round((h_score / h_marks) * 100, 2) if h_marks > 0 else 0}
            ]

            # Chart 4: Monthly Quiz Activity
            attempts_by_month = {}
            for attempt in all_attempts:
                month = attempt.started_at.strftime('%Y-%m-%d')
                if month not in attempts_by_month:
                    attempts_by_month[month] = 1
                else:
                    attempts_by_month[month] += 1

            monthly_activity = [
                        {
                            "month": attempt,
                            "total_attempts": attempts_by_month[attempt]
                        }
                        for attempt in attempts_by_month
                    ]
            
            return {
                "code": 200,
                "data": {
                    "user_attempts": user_attempts,
                    "subject_attempts": subject_attempts,
                    "difficulty_scores": difficulty_scores,
                    "monthly_activity": monthly_activity
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