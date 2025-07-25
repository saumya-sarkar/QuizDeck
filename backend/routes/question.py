from flask_security import auth_required, roles_accepted
from flask_restful import Resource, reqparse
from models import db, Quiz, Question, Option, ist_format



question_create_fields = reqparse.RequestParser()
question_create_fields.add_argument('question_statement', type=str, required=True, location='json')
question_create_fields.add_argument('marks', type=int, required=False, location='json')
question_create_fields.add_argument('explanation', type=str, required=False, location='json')
question_create_fields.add_argument('quiz_id', type=int, required=True, location='json')
question_create_fields.add_argument('question_options', type=list, required=True, location='json')

question_read_fields = reqparse.RequestParser()
question_read_fields.add_argument('id', type=int, required=True, location='json')

question_update_fields = reqparse.RequestParser()
question_update_fields.add_argument('id', type=int, required=True, location='json')
question_update_fields.add_argument('question_statement', type=str, required=True, location='json')
question_update_fields.add_argument('marks', type=int, required=False, location='json')
question_update_fields.add_argument('explanation', type=str, required=False, location='json')
question_update_fields.add_argument('quiz_id', type=int, required=True, location='json')
question_update_fields.add_argument('options', type=list, required=True, location='json')

question_delete_fields = reqparse.RequestParser()
question_delete_fields.add_argument('id', type=int, required=True, location='json')


class get_all_questions(Resource):
    
    @auth_required('token')
    def get(self):
        all_questions = Question.query.filter_by(deleted=False).all()
        if not all_questions:
            return {"code": 404, "error_message": "No questions have been added yet."}, 404
        return [
            {
                "id": question.id,
                "question_statement": question.question_statement,
                "question_diagram_url": question.question_diagram_url,
                "marks": question.marks,
                "explanation": question.explanation,
                "quiz_id": question.quiz_id,
                "quiz_name": question.quiz.name
            }
            for question in all_questions
        ], 200
    
    @auth_required('token')
    def get(self):
        args = question_read_fields.parse_args()
        id = args.get('id')
        question = Question.query.filter_by(id=id, deleted=False).first()
        if not question:
            return {"code": 404, "error_message": "Question not found"}, 404
        return {
            "id": question.id,
            "question_statement": question.question_statement,
            "question_diagram_url": question.question_diagram_url,
            "marks": question.marks,
            "explanation": question.explanation,
            "quiz_id": question.quiz_id,
            "quiz_name": question.quiz.name,
        }, 200

class update_question(Resource):
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = question_create_fields.parse_args()
        question_statement = args.get('question_statement')
        marks = args.get('marks')
        explanation = args.get('explanation')
        quiz_id = args.get('quiz_id')
        question_options = args.get('question_options')


        if Question.query.filter_by(question_statement=question_statement, quiz_id=quiz_id).first():
            return {"code": 409, "error_message": "question already exists for the given quiz"}, 409
        if Quiz.query.filter_by(id=quiz_id, deleted=False).first() is None:
            return {"code": 404, "error_message": "quiz not found for the given quiz_id"}, 404
        if question_statement == "" or question_statement is None:
            return {"code": 400, "error_message": "question statement is required"}, 400
        if quiz_id == "" or quiz_id is None:
            return {"code": 400, "error_message": "quiz_id is required"}, 400
        if question_options is None or not isinstance(question_options, list) or len(question_options) < 2:
            return {"code": 400, "error_message": "At least two options are required"}, 400
        
        
        for option in question_options:
            if 'option_text' not in option or option['option_text'] == "":
                return {"code": 400, "error_message": "Each option must have a non-empty option_text"}, 400
            if 'is_correct' not in option:
                option['is_correct'] = False
        
        count_correct = sum(1 for option in question_options if option.get('is_correct') is True)
        if count_correct == 0:
            return {"code": 400, "error_message": "At least one option must be marked as correct"}, 400
        if count_correct > 1:
            return {"code": 400, "error_message": "Only one option can be marked as correct"}, 400
            
    
        try:
            # 1. Create the parent object
            question = Question(
            question_statement=question_statement,
            marks=marks,
            explanation=explanation,
            quiz_id=quiz_id
            )
            db.session.add(question)

            # 2. Flush to get the question.id generated by the database
            db.session.flush()

            # 3. Now question.id is available to use for child entities
            options_to_add = []
            for option_data in question_options: # list of dicts like {'option_text': 'A', 'is_correct': True}
                question_option = Option(
                    option_text=option_data.get('option_text'),
                    is_correct=option_data.get('is_correct', False),
                    question_id=question.id  # Use the flushed ID here
                )
                options_to_add.append(question_option)
        
            db.session.add_all(options_to_add)

            # 4. Commit the entire transaction (the question and all its options)
            db.session.commit()

            return {
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
            }, 201

        except Exception as error:
            db.session.rollback()  # Rollback the transaction if any error occurs
            return {"error_message": f"An error occurred: {str(error)}"}, 500



    @auth_required('token')
    @roles_accepted('admin')
    def put(self):
        args = question_update_fields.parse_args()
        
        id = args.get('id')
        question_statement = args.get('question_statement')
        marks = args.get('marks')
        explanation = args.get('explanation')
        quiz_id = args.get('quiz_id')
        question_options = args.get('options')

        question = Question.query.filter_by(id=id, deleted=False).first()
        
        if not question:
            return {"code": 404, "error_message": "question not found"}, 404
        if Quiz.query.filter_by(id=quiz_id, deleted=False).first() is None and quiz_id is not None:
            return {"code": 404, "error_message": "quiz not found for the given quiz_id"}, 404
        if Question.query.filter(Question.id != id, Question.question_statement == question_statement, Question.quiz_id == quiz_id).first():
            return {"code": 409, "error_message": "question already exists for the given quiz"}, 409
        
        if question_statement == "" or question_statement is None:
            return {"code": 400, "error_message": "question statement is required"}, 400
        if quiz_id == "" or quiz_id is None:
            return {"code": 400, "error_message": "quiz_id is required"}, 400
        if question_options is None or not isinstance(question_options, list) or len(question_options) < 2:
            return {"code": 400, "error_message": "At least two options are required"}, 400
        
        
        for option in question_options:
            if 'option_text' not in option or option['option_text'] == "":
                return {"code": 400, "error_message": "Each option must have a non-empty option_text"}, 400
            if 'is_correct' not in option:
                option['is_correct'] = False
        
        count_correct = sum(1 for option in question_options if option.get('is_correct') is True)
        if count_correct == 0:
            return {"code": 400, "error_message": "At least one option must be marked as correct"}, 400
        if count_correct > 1:
            return {"code": 400, "error_message": "Only one option can be marked as correct"}, 400
        
        question.question_statement = question_statement if question_statement else question.question_statement
        question.marks = marks if marks is not None else question.marks
        question.explanation = explanation if explanation is not None else question.explanation
        question.quiz_id = quiz_id if quiz_id is not None else question.quiz_id
        
        def option_update(option_data):
            option = Option.query.filter_by(id=option_data.get('id'), question_id=question.id).first()
            option.option_text = option_data.get('option_text', option.option_text)
            option.is_correct = option_data.get('is_correct', option.is_correct)
            db.session.commit()

        def option_add(option_data):
            new_option = Option(
                option_text=option_data.get('option_text'),
                is_correct=option_data.get('is_correct', False),
                question_id=question.id
            )
            db.session.add(new_option)
            db.session.commit()
        
        def option_delete(option_id):
            option = Option.query.filter_by(id=option_id, question_id=question.id).first()
            if option:
                db.session.delete(option)
                db.session.commit()

        current_option_id = [option.id for option in question.options] 
        
        for option in question_options:
            if 'id' not in option.keys():
                option_add(option)
            elif option['id'] and option.get('id') is not None:
                option_data = option
                option_update(option_data)
        
        for id in current_option_id:
            if id not in [option.get('id') for option in question_options if 'id' in option]:
                option_delete(id)
        
        db.session.commit()

        return {
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
        }, 201

class delete_question(Resource):

    @auth_required('token')
    @roles_accepted('admin')
    def patch(self):
        args = question_delete_fields.parse_args()
        id = args.get('id')
        question = Question.query.filter_by(id=id, deleted=False).first()
        if not question:
            return {"code": 404, "error_message": "question not found"}, 404

        question.deleted = True
        db.session.commit()
        return {"code": 200, "message": "question has been soft deleted successfully, can be restored."}, 200

    @auth_required('token')
    @roles_accepted('admin')
    def delete(self):
        args = question_delete_fields.parse_args()
        id = args.get('id')
        question = Question.query.filter_by(id=id, deleted=True).first()
        if not question:
            return {"code": 404, "error_message": "question not found"}, 404

        db.session.delete(question)
        db.session.commit()
        return {"code": 200, "message": "question has been permanently deleted, can not be restored anymore."}, 200


    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        deleted_questions = Question.query.filter_by(deleted=True).all()
        if not deleted_questions:
            return {"code": 404, "error_message": "No deleted questions found"}, 404
        return [
            {
                "id": question.id,
                "question_statement": question.question_statement,
                "question_diagram_url": question.question_diagram_url,
                "marks": question.marks,
                "explanation": question.explanation,
                "quiz_id": question.quiz_id,
                "quiz_name": question.quiz.name
            }
            for question in deleted_questions
        ], 200
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = question_delete_fields.parse_args()
        id = args.get('id')
        question = Question.query.filter_by(id=id, deleted=True).first()
        if not question:
            return {"code": 404, "error_message": "question not found"}, 404

        question.deleted = False
        db.session.commit()
        return {
                "message": "question restored successfully.",
                "restored_question": {
                    "id": question.id,
                    "question_statement": question.question_statement,
                    "question_diagram_url": question.question_diagram_url,
                    "marks": question.marks,
                    "explanation": question.explanation,
                    "quiz_id": question.quiz_id,
                    "quiz_name": question.quiz.name
                }
            }, 200


    



