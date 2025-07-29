from flask_security import auth_required, current_user
from flask_restful import Resource, reqparse
from models import db, Quiz, Question, Option, QuizAttempt, UserAnswer, ist_now, ist_format
from operator import itemgetter


from caching import cache

def invalidate_user_attempts_cache(user_id):
    cache_key = f"user_quiz_attempts_{user_id}"
    if cache.get(cache_key):
        # Invalidate cache for this user
        cache.delete(cache_key)
    print(f"Cache invalidated for user {user_id}")


quiz_start_parser = reqparse.RequestParser()
quiz_start_parser.add_argument('quiz_id', type=int, required=True, location='json')

get_quiz_parser = reqparse.RequestParser()
get_quiz_parser.add_argument('attempt_id', type=int, required=True, location='json')

save_answer_parser = reqparse.RequestParser()
save_answer_parser.add_argument('attempt_id', type=int, required=True, location='json')
save_answer_parser.add_argument('question_id', type=int, required=True, location='json')
save_answer_parser.add_argument('selected_option_id', type=int, required=False, location='json')

submit_quiz_parser = reqparse.RequestParser()
submit_quiz_parser.add_argument('attempt_id', type=int, required=True, location='json')
submit_quiz_parser.add_argument('answers', type=list, required=True, location='json')
submit_quiz_parser.add_argument('time_taken_seconds', type=int, required=True, location='json')
submit_quiz_parser.add_argument('is_auto_submit', type=bool, default=False, location='json')

get_result_parser = reqparse.RequestParser()
get_result_parser.add_argument('attempt_id', type=int, required=True, location='json')
get_result_parser.add_argument('user_id', type=int, required=True, location='json')


class StartQuiz(Resource):
    @auth_required('token')
    def post(self):
        args = quiz_start_parser.parse_args()
        quiz_id = args.get('quiz_id')
        
        # Get quiz details
        quiz = Quiz.query.filter_by(id=quiz_id, deleted=False).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404
        
        # Check if quiz is available for taking
        quiz.check_locked()
        
        if quiz.is_locked:
            return {"code": 403, "error_message": "Quiz is currently locked"}, 403
        
        # Check if user already has an active attempt for this quiz
        existing_attempt = QuizAttempt.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id,
            status='in_progress'
        ).first()
        
        if existing_attempt:
            # Return existing attempt
            return {
                "code": 200,
                "message": "Resuming existing quiz attempt",
                "attempt": {
                    "id": existing_attempt.id,
                    "quiz_id": quiz_id,
                    "started_at": ist_format(existing_attempt.started_at),
                    "duration_mins": quiz.duration_mins,
                    "status": existing_attempt.status
                }
            }, 200
        
        # Create new quiz attempt
        quiz_total_marks = quiz.get_total_marks()
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            status='in_progress',
            total_marks=quiz_total_marks,
        )
        
        db.session.add(attempt)
        db.session.commit()

        # Invalidate cache for user attempts
        invalidate_user_attempts_cache(current_user.id)

        return {
            "code": 201,
            "message": "Quiz started successfully",
            "attempt": {
                "id": attempt.id,
                "quiz_id": quiz_id,
                "started_at": ist_format(attempt.started_at),
                "duration_mins": quiz.duration_mins,
                "status": attempt.status,
                "total_marks": quiz_total_marks
            }
        }, 201

class GetQuizData(Resource):
    @auth_required('token')
    def post(self):
        args = get_quiz_parser.parse_args()
        attempt_id = args.get('attempt_id')

        attempt = QuizAttempt.query.filter_by(
            id=attempt_id,
            user_id=current_user.id
        ).first()
        
        if not attempt:
            return {"code": 404, "error_message": "Quiz attempt not found"}, 404
        
        if attempt.status != 'in_progress':
            return {"code": 403, "error_message": "Quiz attempt is no longer active"}, 403
        
        # Get quiz and questions
        quiz = attempt.quiz
        questions = Question.query.filter_by(quiz_id=quiz.id, deleted=False).all()
        
        # Get user's existing answers
        user_answers = {answer.question_id: answer.selected_option_id 
                       for answer in attempt.answers}
        
        quiz_data = {
            "attempt_id": attempt.id,
            "quiz": {
                "id": quiz.id,
                "name": quiz.name,
                "duration_mins": quiz.duration_mins,
                "chapter_name": quiz.chapter.name,
                "subject_name": quiz.chapter.subject.name
            },
            "started_at": ist_format(attempt.started_at),
            "questions": [
                {
                    "id": question.id,
                    "question_statement": question.question_statement,
                    "marks": question.marks,
                    "options": [
                        {
                            "id": option.id,
                            "option_text": option.option_text
                        }
                        for option in question.options
                    ],
                    "selected_option_id": user_answers.get(question.id)
                }
                for question in questions
            ]
        }
        
        return {"code": 200, "data": quiz_data}, 200

class SaveAnswer(Resource):
    @auth_required('token')
    def post(self):
        args = save_answer_parser.parse_args()
        attempt_id = args.get('attempt_id')
        question_id = args.get('question_id')
        selected_option_id = args.get('selected_option_id')
        
        # Verify attempt belongs to current user
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id,
            user_id=current_user.id,
            status='in_progress'
        ).first()
        
        if not attempt:
            return {"code": 404, "error_message": "Active quiz attempt not found"}, 404
        
        # Check if answer already exists
        existing_answer = UserAnswer.query.filter_by(
            quiz_attempt_id=attempt_id,
            question_id=question_id
        ).first()
        
        if existing_answer:
            # Update existing answer
            existing_answer.selected_option_id = selected_option_id
        else:
            # Create new answer
            answer = UserAnswer(
                quiz_attempt_id=attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                is_correct=False,  # Will be updated later when quiz is submitted
                marks_obtained=0  # Will be updated later when quiz is submitted
            )
            db.session.add(answer)
        
        db.session.commit()
        
        return {
            "code": 200,
            "message": "Answer saved successfully"
        }, 200

class SubmitQuiz(Resource):
    @auth_required('token')
    def post(self):
        args = submit_quiz_parser.parse_args()
        attempt_id = args.get('attempt_id')
        answers = args.get('answers')  # List of {question_id, selected_option_id}
        time_taken_seconds = args.get('time_taken_seconds')
        is_auto_submit = args.get('is_auto_submit', False)
        
        # Verify attempt
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id,
            user_id=current_user.id,
            status='in_progress'
        ).first()
        
        if not attempt:
            return {"code": 404, "error_message": "Active quiz attempt not found"}, 404
        
        # Save all answers
        user_score = 0
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_option_id = answer_data.get('selected_option_id')
            
            if not selected_option_id:
                continue
                
            # Get question and check answer
            question = Question.query.get(question_id)
            if not question:
                continue
                
            correct_option = Option.query.filter_by(
                question_id=question_id,
                is_correct=True
            ).first()
            
            is_correct = correct_option and correct_option.id == selected_option_id
            marks_obtained = question.marks if is_correct else 0
            user_score += marks_obtained

            # Save or update answer
            existing_answer = UserAnswer.query.filter_by(
                quiz_attempt_id=attempt_id,
                question_id=question_id
            ).first()
            
            if existing_answer:
                existing_answer.selected_option_id = selected_option_id
                existing_answer.is_correct = is_correct
                existing_answer.marks_obtained = marks_obtained
            else:
                answer = UserAnswer(
                    quiz_attempt_id=attempt_id,
                    question_id=question_id,
                    selected_option_id=selected_option_id,
                    is_correct=is_correct,
                    marks_obtained=marks_obtained,
                )
                db.session.add(answer)
        
        # Update attempt
        attempt.submitted_at = ist_now()
        attempt.time_taken_seconds = time_taken_seconds
        attempt.user_score = user_score
        attempt.status = 'auto_submitted' if is_auto_submit else 'completed'
        
        db.session.commit()

        # Invalidate cache for user attempts
        invalidate_user_attempts_cache(current_user.id)
        
        return {
            "code": 200,
            "message": "Quiz submitted successfully",
            "result": {
                "user_score": user_score,
                "total_marks": attempt.total_marks,
                "percentage": round((user_score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0,
                "time_taken_seconds": time_taken_seconds,
                "status": attempt.status
            }
        }, 200

class GetQuizResult(Resource):
    @auth_required('token')
    def post(self):
        args = get_result_parser.parse_args()
        attempt_id = args.get('attempt_id')
        user_id = args.get('user_id', current_user.id)
        
        attempt = QuizAttempt.query.filter_by(
            id=attempt_id,
            user_id=user_id
        ).first()
        
        if not attempt:
            return {"code": 404, "error_message": "Quiz attempt not found"}, 404
        
        if attempt.status == 'in_progress':
            return {"code": 403, "error_message": "Quiz is still in progress"}, 403
        
        # Get detailed results
        questions_with_answers = []
        question_with_answers_ids = set()
        for answer in attempt.answers:
            question = answer.question
            correct_option = Option.query.filter_by(
                question_id=question.id,
                is_correct=True
            ).first()
            question_with_answers_ids.add(question.id)
            questions_with_answers.append({
                "question_id": question.id,
                "question_statement": question.question_statement,
                "marks": question.marks,
                "selected_option_id": answer.selected_option_id,
                "selected_option_text": answer.selected_option.option_text if answer.selected_option else None,
                "correct_option_id": correct_option.id if correct_option else None,
                "correct_option_text": correct_option.option_text if correct_option else None,
                "is_correct": answer.is_correct,
                "marks_obtained": answer.marks_obtained,
                "explanation": question.explanation
            })
        
        for question in attempt.quiz.questions:
            if question.id not in question_with_answers_ids and not question.deleted:
                # Add question without answer if not answered
                correct_option = Option.query.filter_by(
                    question_id=question.id,
                    is_correct=True
                ).first()
                questions_with_answers.append({
                    "question_id": question.id,
                    "question_statement": question.question_statement,
                    "marks": question.marks,
                    "selected_option_id": None,
                    "selected_option_text": None,
                    "correct_option_id": correct_option.id if correct_option else None,
                    "correct_option_text": correct_option.option_text if correct_option else None,
                    "is_correct": False,
                    "marks_obtained": 0,
                    "explanation": question.explanation
                })
        questions_with_answers = sorted(questions_with_answers, key=itemgetter("question_id"))
        result = {
            "attempt_id": attempt.id,
            "quiz_name": attempt.quiz.name,
            "chapter_name": attempt.quiz.chapter.name,
            "subject_name": attempt.quiz.chapter.subject.name,
            "started_at": ist_format(attempt.started_at),
            "submitted_at": ist_format(attempt.submitted_at) if attempt.submitted_at else None,
            "time_taken_seconds": attempt.time_taken_seconds,
            "user_score": attempt.user_score,
            "total_marks": attempt.total_marks,
            "percentage": round((attempt.user_score / attempt.total_marks) * 100, 2) if attempt.total_marks > 0 else 0,
            "status": attempt.status,
            "questions": questions_with_answers
        }
        
        return {"code": 200, "data": result}, 200