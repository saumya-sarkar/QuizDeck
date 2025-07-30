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

            userAttempts = QuizAttempt.query.filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.status.in_(['completed', 'auto_submitted'])
            ).order_by(desc(QuizAttempt.started_at)).all()
            
            # Chart 1: User Performance by Subject
            
            subject_performance = []
            subjectSet = [subject.name for subject in Subject.query.filter(Subject.deleted == False).all()]
            for subject in subjectSet:
                user_score = sum(attempt.user_score for attempt in userAttempts if attempt.quiz.chapter.subject.name == subject)
                total_marks = sum(attempt.total_marks for attempt in userAttempts if attempt.quiz.chapter.subject.name == subject)
                avg_percentage = ((user_score / total_marks) * 100) if total_marks > 0 else 0
                attempts = sum(1 for attempt in userAttempts if attempt.quiz.chapter.subject.name == subject)

                subject_performance.append({
                    "subject_name": subject,
                    "avg_percentage": round(avg_percentage, 2),
                    "attempts": attempts if attempts > 0 else 0
                })
            
            # Chart 2: Weekly Quiz Activity (Last 4 weeks)
            activity_dict = {}
            cur_week = datetime.now(ZoneInfo("Asia/Kolkata"))
            for i in range(4):
                activity_dict[(cur_week-timedelta(weeks=i)).strftime("%Y Week-%W")] = {"attempts": 0, "user_score": 0, "total_marks": 0}
            for attempt in userAttempts:
                week = attempt.started_at.strftime("%Y Week-%W")
                if week in activity_dict:
                    activity_dict[week]["attempts"] += 1
                    if attempt.total_marks > 0:
                        activity_dict[week]["user_score"] += attempt.user_score
                        activity_dict[week]["total_marks"] += attempt.total_marks
            
            weekly_activity = []
            for week, data in activity_dict.items():
                avg_score = (data["user_score"] / data["total_marks"] * 100) if data["total_marks"] > 0 else 0
                weekly_activity.append({
                    "week": week,
                    "attempts": data["attempts"],
                    "avg_score": round(avg_score, 2) if avg_score else 0
                })
            
            # Sort by week in descending order
            weekly_activity.reverse()
            
            # # Chart 3: Score Distribution
            score_dict = {
                "90-100%": 0,
                "80-89%": 0,
                "70-79%": 0,
                "60-69%": 0,
                "50-59%": 0,
                "Below 50%": 0
            }
            for attempt in userAttempts:
                score = attempt.user_score * 100.0 / attempt.total_marks if attempt.total_marks > 0 else 0
                if score >= 90:
                    score_dict["90-100%"] += 1
                elif score >= 80:
                    score_dict["80-89%"] += 1
                elif score >= 70:
                    score_dict["70-79%"] += 1
                elif score >= 60:
                    score_dict["60-69%"] += 1
                elif score >= 50:
                    score_dict["50-59%"] += 1
                else:
                    score_dict["Below 50%"] += 1

            score_distribution = [
                {"range": score_range, "count": count}
                for score_range, count in score_dict.items()
            ]

            # Chart 4: Recent Quiz Trends (Last 10 attempts)
            recent_trends = []
            recent_attempts = userAttempts[:10]  # Get the last 10 attempts
            for attempt in recent_attempts:
                score_percentage = (attempt.user_score * 100.0 / attempt.total_marks) if attempt.total_marks > 0 else 0
                quiz_name = attempt.quiz.name
                attempt_date = attempt.started_at.strftime('%Y-%m-%d')
                recent_trends.append({
                    "quiz": quiz_name,
                    "score": round(score_percentage, 2),
                    "date": attempt_date
                })

            recent_trends.reverse()  # Reverse to show the most recent first
            
            return {
                "code": 200,
                "data": {
                    "subject_performance": subject_performance,
                    "weekly_activity": weekly_activity,
                    "score_distribution": score_distribution,
                    "recent_trends": recent_trends
                }
            }, 200
            
        except Exception as error:
            return {"code": 500, "error_message": f"An error occurred: {str(error)}"}, 500