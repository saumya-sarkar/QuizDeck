from flask_security import auth_required, roles_accepted
from flask_restful import Resource, reqparse
from models import db, Chapter, Quiz, Question, ist_format
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
from dateutil import parser



quiz_create_fields = reqparse.RequestParser()
quiz_create_fields.add_argument('name', type=str, required=True, location='json')
quiz_create_fields.add_argument('duration_mins', type=int, required=False, location='json')
quiz_create_fields.add_argument('difficulty', type=str, required=False, location='json')
quiz_create_fields.add_argument('quiz_type', type=str, required=True, location='json')
quiz_create_fields.add_argument('chapter_id', type=int, required=True, location='json')
quiz_create_fields.add_argument('start_time', type=str, required=False, location='json')
quiz_create_fields.add_argument('end_time', type=str, required=False, location='json')


quiz_read_fields = reqparse.RequestParser()
quiz_read_fields.add_argument('id', type=int, required=True, location='json')



quiz_update_fields = reqparse.RequestParser()
quiz_update_fields.add_argument('id', type=int, required=True, location='json')
quiz_update_fields.add_argument('name', type=str, required=False, location='json')
quiz_update_fields.add_argument('duration_mins', type=int, required=False, location='json')
quiz_update_fields.add_argument('difficulty', type=str, required=False, location='json')
quiz_update_fields.add_argument('quiz_type', type=str, required=False, location='json')
quiz_update_fields.add_argument('chapter_id', type=int, required=False, location='json')
quiz_update_fields.add_argument('start_time', type=str, required=False, location='json')
quiz_update_fields.add_argument('end_time', type=str, required=False, location='json')



quiz_delete_fields = reqparse.RequestParser()
quiz_delete_fields.add_argument('id', type=int, required=True, location='json', help='ID of the quiz is required for deletion')


class GetAllQuizzes(Resource):
    
    @auth_required('token')
    def get(self):
        all_quizzes = Quiz.query.filter_by(deleted=False).all()
        if not all_quizzes:
            return {"code": 404, "error_message": "No quizzes have been added yet."}, 404
        return [
            {
                "id": quiz.id,
                "name": quiz.name,
                "duration_mins": quiz.duration_mins,
                "difficulty": quiz.difficulty.value,
                "quiz_type": quiz.quiz_type.value,
                "chapter_id": quiz.chapter_id,
                "chapter_name": quiz.chapter.name,
                "start_time": ist_format(quiz.start_time) if quiz.start_time else None,
                "end_time": ist_format(quiz.end_time) if quiz.end_time else None,
                "is_locked": quiz.is_locked,
                "created_at": ist_format(quiz.created_at),
                "updated_at": ist_format(quiz.updated_at) if quiz.updated_at else None
            }
            for quiz in all_quizzes
        ], 200

    @auth_required('token')  # This endpoint is for users
    def get(self):
        args = quiz_read_fields.parse_args()
        id = args.get('id')
        quiz = Quiz.query.filter_by(id=id, deleted=False).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404
        return {
            "id": quiz.id,
            "name": quiz.name,
            "description": quiz.description,
            "duration_mins": quiz.duration_mins,
            "one_time_attempt": quiz.one_time_attempt,
            "difficulty": quiz.difficulty.value,
            "chapter_id": quiz.chapter_id,
            "chapter_name": quiz.chapter.name,
            "created_at": quiz.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }, 200

    @auth_required('token')  # This endpoint is for admin
    @roles_accepted('admin')
    def post(self):
        args = quiz_read_fields.parse_args()
        id = args.get('id')
        quiz = Quiz.query.filter_by(id=id, deleted=False).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404

        all_questions = quiz.questions.filter_by(deleted=False).all()
        if not all_questions:
            return {"code": 200, "error_message": "No questions found for this quiz"}, 200

        questions = [
            {
                "id": question.id,
                "question_statement": question.question_statement,
                "marks": question.marks,
                "options": [
                    {
                        "id": option.id,
                        "option_text": option.option_text,
                        "is_correct": option.is_correct
                    }
                    for option in question.options
                ],
                "explanation": question.explanation,
                "quiz_id": question.quiz_id,
                "quiz_name": question.quiz.name
            }
            for question in all_questions
        ]
        return {
            "id": quiz.id,
            "name": quiz.name,
            "chapter_name": quiz.chapter.name,
            "subject_name": quiz.chapter.subject.name,
            "questions": questions
        }, 200



class UpdateQuiz(Resource):
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = quiz_create_fields.parse_args()
        name = args.get('name')
        duration_mins = args.get('duration_mins')
        difficulty = args.get('difficulty')
        quiz_type = args.get('quiz_type')
        chapter_id = args.get('chapter_id')
        start_time = args.get('start_time')
        end_time = args.get('end_time')
        

        if name == "" or name is None:
            return {"code": 400, "error_message": "Name of the quiz is required"}, 400
        if chapter_id == "" or chapter_id is None:
            return {"code": 400, "error_message": "ID of the chapter is required for creating a quiz"}, 400
        
        if Quiz.query.filter_by(name=name).first():
            return {"code": 409, "error_message": "Quiz already exists"}, 409
        if Chapter.query.filter_by(id=chapter_id, deleted=False).first() is None:
            return {"code": 404, "error_message": "Chapter not found for the given chapter_id"}, 404
        
        if duration_mins and duration_mins <= 0:
            return {"code": 400, "error_message": "Invalid duration. Must be a positive integer"}, 400
        
        if difficulty not in ["Easy", "Medium", "Hard"]:
            return {"code": 400, "error_message": "Invalid difficulty. Must be one of: Easy, Medium, Hard"}, 400

        if quiz_type == "" or quiz_type is None:
            return {"code": 400, "error_message": "Type of the quiz is required"}, 400
        if quiz_type not in ["Practice", "Mock", "Exam"]:
            return {"code": 400, "error_message": "Invalid quiz type. Must be one of: Practice, Mock, Exam"}, 400
        
        
        if quiz_type == "Exam":
            if start_time is None or start_time == "":
                return {"code": 400, "error_message": "Start time is required for Exam type quiz"}, 400
            else: 
                start_time = parser.parse(start_time).astimezone(ZoneInfo("Asia/Kolkata"))
                if start_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "Start time cannot be in the past"}, 400
                else:
                    end_time = None  # End time is not used for Exam type quiz
                    duration_mins = duration_mins if duration_mins else 60
                    end_time = start_time + timedelta(minutes=duration_mins)

                    if datetime.now(ZoneInfo("Asia/Kolkata")) < start_time or datetime.now(ZoneInfo("Asia/Kolkata")) > end_time:
                        is_locked = True
                    else:
                        is_locked = False
        
        elif quiz_type == "Mock":
            if start_time is None or start_time == "":
                return {"code": 400, "error_message": "Start time is required for Mock type quiz"}, 400
            elif end_time is None or end_time == "":
                return {"code": 400, "error_message": "End time is required for Mock type quiz"}, 400
            else:
                start_time = parser.parse(start_time).astimezone(ZoneInfo("Asia/Kolkata"))
                end_time = parser.parse(end_time).astimezone(ZoneInfo("Asia/Kolkata"))
                if start_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "Start time cannot be in the past"}, 400
                elif end_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "End time cannot be in the past"}, 400
                elif end_time <= start_time:
                    return {"code": 400, "error_message": "End time cannot be before start time"}, 400
                else:
                    if datetime.now(ZoneInfo("Asia/Kolkata")) < start_time or datetime.now(ZoneInfo("Asia/Kolkata")) > end_time:
                        is_locked = True
                    else:
                        is_locked = False
        
        elif quiz_type == "Practice":
            start_time = None  # Start time is not used for Practice type quiz
            end_time = None  # End time is not used for Practice type quiz
            is_locked = False

        quiz = Quiz(name=name, duration_mins=duration_mins, difficulty=difficulty, quiz_type=quiz_type, start_time=start_time,
                    end_time=end_time, is_locked=is_locked, chapter_id=chapter_id)

        db.session.add(quiz)
        db.session.commit()
            
        return {
                "id": quiz.id,
                "name": quiz.name,
                "duration_mins": quiz.duration_mins,
                "difficulty": quiz.difficulty.value,
                "quiz_type": quiz.quiz_type.value,
                "chapter_id": quiz.chapter_id,
                "chapter_name": quiz.chapter.name,
                "start_time": ist_format(quiz.start_time) if quiz.start_time else None,
                "end_time": ist_format(quiz.end_time) if quiz.end_time else None,
                "is_locked": quiz.is_locked,
                "created_at": ist_format(quiz.created_at),
                "updated_at": ist_format(quiz.updated_at) if quiz.updated_at else None,
                "quiz_status": quiz.check_status(),
                "available_for": quiz.check_available_for(),
                "total_questions": quiz.get_total_questions(),
                "total_marks": quiz.get_total_marks()
            }, 201

    
    @auth_required('token')
    @roles_accepted('admin')
    def put(self):
        args = quiz_update_fields.parse_args()
        id = args.get('id')
        name = args.get('name')
        duration_mins = args.get('duration_mins')
        difficulty = args.get('difficulty')
        quiz_type = args.get('quiz_type')
        chapter_id = args.get('chapter_id')
        start_time = args.get('start_time')
        end_time = args.get('end_time')

        if name == "" or name is None:
            return {"code": 400, "error_message": "Name of the quiz is required"}, 400
        if chapter_id == "" or chapter_id is None:
            return {"code": 400, "error_message": "ID of the chapter is required"}, 400
        
        quiz = Quiz.query.filter_by(id=id, deleted=False).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404
        if Quiz.query.filter(Quiz.id != id, Quiz.name == name).first():
            return {"code": 409, "error_message": "Quiz with this name already exists"}, 409
        if Chapter.query.filter_by(id=chapter_id, deleted=False).first() is None:
            return {"code": 404, "error_message": "Chapter not found for the given chapter_id"}, 404
        
        if duration_mins and duration_mins <= 0:
            return {"code": 400, "error_message": "Invalid duration. Must be a positive integer"}, 400
        
        if difficulty not in ["Easy", "Medium", "Hard"]:
            return {"code": 400, "error_message": "Invalid difficulty. Must be one of: Easy, Medium, Hard"}, 400

        if quiz_type == "" or quiz_type is None:
            return {"code": 400, "error_message": "Type of the quiz is required"}, 400
        if quiz_type not in ["Practice", "Mock", "Exam"]:
            return {"code": 400, "error_message": "Invalid quiz type. Must be one of: Practice, Mock, Exam"}, 400
        
        
        if quiz_type == "Exam":
            if start_time is None or start_time == "":
                return {"code": 400, "error_message": "Start time is required for Exam type quiz"}, 400
            else: 
                start_time = parser.parse(start_time).astimezone(ZoneInfo("Asia/Kolkata"))
                if start_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "Start time cannot be in the past"}, 400
                else:
                    end_time = None  # End time is not used for Exam type quiz
                    duration_mins = duration_mins if duration_mins else 60
                    end_time = start_time + timedelta(minutes=duration_mins)

                    if datetime.now(ZoneInfo("Asia/Kolkata")) < start_time or datetime.now(ZoneInfo("Asia/Kolkata")) > end_time:
                        is_locked = True
                    else:
                        is_locked = False
        elif quiz_type == "Mock":
            if start_time is None or start_time == "":
                return {"code": 400, "error_message": "Start time is required for Mock type quiz"}, 400
            elif end_time is None or end_time == "":
                return {"code": 400, "error_message": "End time is required for Mock type quiz"}, 400
            else:
                start_time = parser.parse(start_time).astimezone(ZoneInfo("Asia/Kolkata"))
                end_time = parser.parse(end_time).astimezone(ZoneInfo("Asia/Kolkata"))
                if start_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "Start time cannot be in the past"}, 400
                elif end_time < datetime.now(ZoneInfo("Asia/Kolkata")):
                    return {"code": 400, "error_message": "End time cannot be in the past"}, 400
                elif end_time <= start_time:
                    return {"code": 400, "error_message": "End time cannot be before start time"}, 400
                else:
                    if datetime.now(ZoneInfo("Asia/Kolkata")) < start_time or datetime.now(ZoneInfo("Asia/Kolkata")) > end_time:
                        is_locked = True
                    else:
                        is_locked = False
        elif quiz_type == "Practice":
            start_time = None  # Start time is not used for Practice type quiz
            end_time = None  # End time is not used for Practice type quiz
            is_locked = False
        
        quiz.name = name if name else quiz.name
        quiz.duration_mins = duration_mins if duration_mins else quiz.duration_mins
        quiz.difficulty = difficulty if difficulty else quiz.difficulty
        quiz.quiz_type = quiz_type if quiz_type else quiz.quiz_type
        quiz.chapter_id = chapter_id if chapter_id else quiz.chapter_id
        quiz.start_time = start_time if start_time else quiz.start_time
        quiz.end_time = end_time if end_time else quiz.end_time
        quiz.is_locked = is_locked

        db.session.commit()
        return {
                "id": quiz.id,
                "name": quiz.name,
                "duration_mins": quiz.duration_mins,
                "difficulty": quiz.difficulty.value,
                "quiz_type": quiz.quiz_type.value,
                "chapter_id": quiz.chapter_id,
                "chapter_name": quiz.chapter.name,
                "start_time": ist_format(quiz.start_time) if quiz.start_time else None,
                "end_time": ist_format(quiz.end_time) if quiz.end_time else None,
                "is_locked": quiz.is_locked,
                "created_at": ist_format(quiz.created_at),
                "updated_at": ist_format(quiz.updated_at) if quiz.updated_at else None,
                "quiz_status": quiz.check_status(),
                "available_for": quiz.check_available_for(),
                "total_questions": quiz.get_total_questions(),
                "total_marks": quiz.get_total_marks()
            }, 200


class DeleteQuiz(Resource):

    @auth_required('token')
    @roles_accepted('admin')
    def patch(self):
        args = quiz_delete_fields.parse_args()
        id = args.get('id')
        quiz = Quiz.query.filter_by(id=id, deleted=False).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404

        quiz.deleted = True
        db.session.commit()
        return {"code": 200, "message": "quiz has been soft deleted successfully, can be restored."}, 200

    @auth_required('token')
    @roles_accepted('admin')
    def delete(self):
        args = quiz_delete_fields.parse_args()
        id = args.get('id')
        quiz = Quiz.query.filter_by(id=id, deleted=True).first()
        if not quiz:
            return {"code": 404, "error_message": "quiz not found"}, 404

        db.session.delete(quiz)
        db.session.commit()
        return {"code": 200, "message": "quiz has been permanently deleted, can not be restored anymore."}, 200


    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        deleted_quizzes = Quiz.query.filter_by(deleted=True).all()
        if not deleted_quizzes:
            return {"code": 404, "error_message": "No deleted quizzes found"}, 404
        return [
            {
                "id": quiz.id,
                "name": quiz.name,
                "description": quiz.description,
                "duration_mins": quiz.duration_mins,
                "one_time_attempt": quiz.one_time_attempt,
                "difficulty": quiz.difficulty.value,
                "chapter_id": quiz.chapter_id,
                "chapter_name": quiz.chapter.name,
                "created_at": quiz.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for quiz in deleted_quizzes
        ], 200
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = quiz_delete_fields.parse_args()
        id = args.get('id')
        quiz = Quiz.query.filter_by(id=id, deleted=True).first()
        if not quiz:
            return {"code": 404, "error_message": "Quiz not found"}, 404

        quiz.deleted = False
        db.session.commit()
        return {
                "message": "quiz restored successfully.",
                "restored_quiz": {
                    "id": quiz.id,
                    "name": quiz.name,
                    "description": quiz.description,
                    "duration_mins": quiz.duration_mins,
                    "one_time_attempt": quiz.one_time_attempt,
                    "difficulty": quiz.difficulty.value,
                    "chapter_id": quiz.chapter_id,
                    "chapter_name": quiz.chapter.name,
                    "created_at": quiz.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, 200


    



