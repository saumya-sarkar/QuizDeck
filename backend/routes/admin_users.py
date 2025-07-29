from flask_security import auth_required, roles_accepted, current_user
from flask_restful import Resource, reqparse
from models import db, User, QuizAttempt, Subject, Chapter, Quiz, ist_format
from sqlalchemy import desc
from collections import defaultdict
from caching import cache

user_read_fields = reqparse.RequestParser()
user_read_fields.add_argument('id', type=int, required=True, location='json')

class GetAllUsers(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):

        all_users = User.query.filter(User.roles.any(name='user')).all()

        if not all_users:
            return {"code": 404, "error_message": "No users found"}, 404
        
        users_data = []
        for user in all_users:
            # Calculate user statistics
            total_attempts = QuizAttempt.query.filter_by(user_id=user.id).filter(
                QuizAttempt.status.in_(['completed', 'auto_submitted'])
            )
            total_attempts_count = total_attempts.count()
            # Calculate average score
            total_user_score = 0
            total_quiz_marks = 0
            for attempt in total_attempts:
                total_user_score += attempt.user_score
                total_quiz_marks += attempt.total_marks
            score_percentage = round( (total_user_score/total_quiz_marks)*100, 2) if total_quiz_marks > 0 else 0

            # Get last login info
            last_login = ist_format(user.current_login_at) if user.current_login_at else 'Never'
            
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "qualification": user.qualification.value if user.qualification else None,
                "is_active": user.active,
                "total_attempts": total_attempts_count,
                "average_score": score_percentage,
                "last_login": last_login,
                "login_count": user.login_count or 0
            })
        
        return {
            "code": 200,
            "users": users_data,
            "total_users": len(users_data)
        }, 200

class GetUserDetails(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = user_read_fields.parse_args()
        user_id = args.get('id')
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"code": 404, "error_message": "User not found"}, 404
    
        
        # Get detailed quiz attempts
        quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        
        # Calculate statistics
        total_attempts = len(quiz_attempts)
        completed_attempts = len([a for a in quiz_attempts if a.status in ['completed', 'auto_submitted']])
        in_progress_attempts = len([a for a in quiz_attempts if a.status == 'in_progress'])
        
        # Calculate scores
        completed_quiz_attempts = [a for a in quiz_attempts if a.status in ['completed', 'auto_submitted']]
        if completed_quiz_attempts:
            total_score = sum(a.user_score for a in completed_quiz_attempts)
            total_possible = sum(a.total_marks for a in completed_quiz_attempts)
            avg_score = round(total_score / len(completed_quiz_attempts), 2) if completed_quiz_attempts else 0
            avg_percentage = round((total_score / total_possible) * 100, 2) if total_possible > 0 else 0
        else:
            avg_score = 0
            avg_percentage = 0
        
        # Subject-wise performance
        subject_performance = defaultdict(lambda: {'attempts': 0, 'total_score': 0, 'total_possible': 0})
        
        for attempt in completed_quiz_attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter
            subject = chapter.subject
            
            subject_performance[subject.name]['attempts'] += 1
            subject_performance[subject.name]['total_score'] += attempt.user_score
            subject_performance[subject.name]['total_possible'] += attempt.total_marks
        
        # Convert to list with percentages
        subject_stats = []
        for subject_name, stats in subject_performance.items():
            percentage = round((stats['total_score'] / stats['total_possible']) * 100, 2) if stats['total_possible'] > 0 else 0
            subject_stats.append({
                'subject_name': subject_name,
                'attempts': stats['attempts'],
                'average_score': round(stats['total_score'] / stats['attempts'], 2) if stats['attempts'] > 0 else 0,
                'percentage': percentage
            })
        
        # Recent quiz attempts (last 10)
        recent_attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(desc(QuizAttempt.started_at)).limit(10).all()
        recent_attempts_data = []
        
        for attempt in recent_attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter
            subject = chapter.subject
            
        
        # User activity timeline
        activity_data = {
            'first_login': ist_format(user.current_login_at) if user.current_login_at else None,
            'last_login': ist_format(user.current_login_at) if user.current_login_at else None,
            'total_login_count': user.login_count or 0,
            'registration_date': ist_format(user.registration_date) if user.registration_date else None
        }
        
        user_details = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "qualification": user.qualification.value if user.qualification else None,
            "date_of_birth": user.dob.strftime("%Y-%m-%d") if user.dob else None,
            "is_active": user.active,
            "current_login_ip": user.current_login_ip,
            "last_login_ip": user.last_login_ip,
            
            # Quiz Statistics
            "quiz_stats": {
                "total_attempts": total_attempts,
                "completed_attempts": completed_attempts,
                "in_progress_attempts": in_progress_attempts,
                "average_score": avg_score,
                "average_percentage": avg_percentage
            },
            
            # Subject-wise performance
            "subject_performance": subject_stats,
            
            # Activity data
            "activity": activity_data
        }
        
        return {
            "code": 200,
            "user_details": user_details
        }, 200

class ToggleUserStatus(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    def patch(self):
        args = user_read_fields.parse_args()
        user_id = args.get('id')
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"code": 404, "error_message": "User not found"}, 404
        
        # Check if user is admin
        if any(role.name == 'admin' for role in user.roles):
            return {"code": 403, "error_message": "Cannot modify admin user status"}, 403
        
        # Toggle active status
        user.active = not user.active
        db.session.commit()
        
        status_text = "activated" if user.active else "deactivated"
        
        return {
            "code": 200,
            "message": f"User {user.username} has been {status_text} successfully",
            "is_active": user.active
        }, 200

class AdminDashboardStats(Resource):
    @auth_required('token')
    @roles_accepted('admin')
    @cache.cached(timeout=30, key_prefix='admin_dashboard_stats')
    def get(self):
        # This endpoint can be used to fetch overall admin statistics
        total_users = User.query.filter(User.roles.any(name='user')).filter_by(active=True).count()
        total_quizzes = Quiz.query.filter_by(deleted=False).count()
        total_chapters = Chapter.query.filter_by(deleted=False).count()
        total_subjects = Subject.query.filter_by(deleted=False).count()

        return {
            "code": 200,
            "total_users": total_users,
            "total_quizzes": total_quizzes,
            "total_chapters": total_chapters,
            "total_subjects": total_subjects
        }, 200

class UserDashboardStats(Resource):
    @auth_required('token')
    def get(self):
        # This endpoint can be used to fetch overall user statistics
        user_id = current_user.id
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"code": 404, "error_message": "User not found"}, 404
        
        username = user.username
        totalQuizzesTaken = len(set(attempt.quiz_id for attempt in user.quiz_attempts))
        totalScore = sum(attempt.user_score for attempt in user.quiz_attempts)
        totalMarks = sum(attempt.total_marks for attempt in user.quiz_attempts)
        averageScore = round((totalScore / totalMarks) * 100, 2) if totalMarks > 0 else 0
        subjectsExplored = len(set(attempt.quiz.chapter.subject_id for attempt in user.quiz_attempts))
        currentStreak = 7 # Placeholder for current streak logic, can be implemented later
        return {
            "code": 200,
            "username": username,
            "totalQuizzesTaken": totalQuizzesTaken,
            "averageScore": averageScore,
            "subjectsExplored": subjectsExplored,
            "currentStreak": currentStreak
        }, 200