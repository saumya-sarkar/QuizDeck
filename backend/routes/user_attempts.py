from flask_security import auth_required
from flask_restful import Resource, reqparse
from models import QuizAttempt, ist_format
from sqlalchemy import desc
from caching import cache
from datetime import timedelta


user_quiz_attempt_fields = reqparse.RequestParser()
user_quiz_attempt_fields.add_argument('user_id', type=int, required=True, location='json')

class UserQuizAttempts(Resource):
    @auth_required('token')
    def post(self):

        args = user_quiz_attempt_fields.parse_args()
        user_id = args.get('user_id')

        cache_key = f"user_quiz_attempts_{user_id}" # Cache key for user attempts

        # Check if cached data exists
        cached_attempts = cache.get(cache_key)
        if cached_attempts:
            print(f"Cache hit for user {user_id}")
            return cached_attempts, 200
        else:
            print(f"Cache miss for user {user_id}")
        
        # If no cache, fetch from database
        # Fetch all attempts for the current user, ordered by most recent first
        attempts = QuizAttempt.query.filter_by(
            user_id=user_id
        ).filter(
            QuizAttempt.status.in_(['completed', 'auto_submitted'])
        ).order_by(desc(QuizAttempt.submitted_at)).all()
        
        if not attempts:
            return {
                "code": 404, 
                "message": "No quiz attempts found",
                "attempts": []
            }, 200
        
        attempts_data = []
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter
            subject = chapter.subject
            
            attempts_data.append({
                "id": attempt.id,
                "quiz_id": quiz.id,
                "quiz_name": quiz.name,
                "subject_name": subject.name,
                "chapter_name": chapter.name,
                "difficulty": quiz.difficulty.value,
                "quiz_type": quiz.quiz_type.value,
                "started_at": ist_format(attempt.started_at),
                "submitted_at": ist_format(attempt.submitted_at),
                "time_taken_seconds": attempt.time_taken_seconds,
                "user_score": attempt.user_score,
                "total_marks": attempt.total_marks,
                "percentage": round((attempt.user_score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0,
                "status": attempt.status,
                "total_questions": quiz.get_total_questions()
            })

        # Cache the result
        response_data = {
            "code": 200,
            "message": "Quiz attempts retrieved successfully",
            "attempts": attempts_data,
            "total_attempts": len(attempts_data)
        }
        cache_timeout = int(timedelta(days=7).total_seconds())  # Cache for 7 days
        # Store in cache
        cache.set(cache_key, response_data, timeout=cache_timeout)
        print(f"Cache set for user {user_id} with timeout {cache_timeout} seconds")

        return response_data, 200