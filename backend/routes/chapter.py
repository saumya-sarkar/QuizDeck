from flask_security import auth_required, roles_accepted
from flask_restful import Resource, reqparse
from models import db, Subject, Chapter, ist_format


chapter_create_fields = reqparse.RequestParser()
chapter_create_fields.add_argument('name', type=str, required=True, location='json', help='Name of the chapter is required')
chapter_create_fields.add_argument('description', type=str, required=True, location='json', help='Description of the chapter is required')
chapter_create_fields.add_argument('subject_id', type=int, required=True, location='json', help='ID of the subject is required for creating a chapter')

chapter_read_fields = reqparse.RequestParser()
chapter_read_fields.add_argument('id', type=int, required=True, location='json', help='ID of the chapter is required for reading')

chapter_update_fields = reqparse.RequestParser()
chapter_update_fields.add_argument('id', type=int, required=True, location='json', help='ID of the chapter is required')
chapter_update_fields.add_argument('name', type=str, required=False, location='json', help='Name of the chapter is optional')
chapter_update_fields.add_argument('description', type=str, required=False, location='json', help='Description of the chapter is optional')
chapter_update_fields.add_argument('subject_id', type=int, required=False, location='json', help='ID of the subject is optional for updating a chapter')

chapter_delete_fields = reqparse.RequestParser()
chapter_delete_fields.add_argument('id', type=int, required=True, location='json', help='ID of the chapter is required for deletion')


class GetAllChapters(Resource):
    
    @auth_required('token')
    def get(self):
        all_chapters = Chapter.query.filter_by(deleted=False).all()
        if not all_chapters:
            return {"code": 404, "error_message": "No chapters have been added yet."}, 404
        return [
            {
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "subject_id": chapter.subject_id,
                "subject_name": chapter.subject.name,
                "created_at": ist_format(chapter.created_at),
                "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None
            }
            for chapter in all_chapters
        ], 200
    
    @auth_required('token')
    def post(self):
        args = chapter_read_fields.parse_args()
        id = args.get('id')
        chapter = Chapter.query.filter_by(id=id, deleted=False).first()
        if not chapter:
            return {"code": 404, "error_message": "Chapter not found"}, 404
        
        all_quizzes = chapter.quizzes.filter_by(deleted=False).all()
        
        if not all_quizzes:
            return {
            "id": chapter.id,
            "name": chapter.name,
            "subject_name": chapter.subject.name,
            "quizzes": []
        }, 200
        
        for quiz in all_quizzes:
            quiz.check_locked()
        
        quizzes = [
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
                "updated_at": ist_format(quiz.updated_at) if quiz.updated_at else None,
                "quiz_status": quiz.check_status(),
                "available_for": quiz.check_available_for(),
                "total_questions": quiz.get_total_questions(),
                "total_marks": quiz.get_total_marks()
            }
            for quiz in all_quizzes
        ]
        return {
            "id": chapter.id,
            "name": chapter.name,
            "subject_name": chapter.subject.name,
            "quizzes": quizzes
        }, 200


class UpdateChapter(Resource):

    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = chapter_create_fields.parse_args()
        name = args.get('name')
        description = args.get('description')
        subject_id = args.get('subject_id')

        if Chapter.query.filter_by(name=name).first():
            return {"code": 409, "error_message": "Chapter already exists"}, 409
        
        elif Subject.query.filter_by(id=subject_id, deleted=False).first() is None:
            return {"code": 404, "error_message": "Subject not found for the given subject_id"}, 404
        
        elif name == "" or name is None:
            return {"code": 400, "error_message": "Name of the chapter is required"}, 400
        elif description == "" or description is None:
            return {"code": 400, "error_message": "Description of the chapter is required"}, 400
        elif subject_id == "" or subject_id is None:
            return {"code": 400, "error_message": "ID of the subject is required for creating a chapter"}, 400
        else:
            chapter = Chapter(name=name, description=description, subject_id=subject_id)
            db.session.add(chapter)
            db.session.commit()
            
            return {
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "subject_id": chapter.subject_id,
            "subject_name": chapter.subject.name,
            "created_at": ist_format(chapter.created_at),
            "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None,
            "quizCount": chapter.quizzes.filter_by(deleted=False).count() if chapter.quizzes else 0,
            "isCompleted": True  # Placeholder, implement logic if needed
            }, 201
    
    @auth_required('token')
    @roles_accepted('admin')
    def put(self):
        args = chapter_update_fields.parse_args()
        id = args.get('id')
        name = args.get('name')
        description = args.get('description')
        subject_id = args.get('subject_id')

        chapter = Chapter.query.filter_by(id=id, deleted=False).first()
        
        if not chapter:
            return {"code": 404, "error_message": "Chapter not found"}, 404
        
        if Subject.query.filter_by(id=subject_id, deleted=False).first() is None and subject_id is not None:
            return {"code": 404, "error_message": "Subject not found for the given subject_id"}, 404
        
        if Chapter.query.filter(Chapter.name == name, Chapter.id != id).first() is not None and name is not None:
            return {"code": 409, "error_message": "Chapter with this name already exists"}, 409
       
        chapter.name = name if name else chapter.name
        chapter.description = description if description else chapter.description
        chapter.subject_id = subject_id if subject_id else chapter.subject_id

        db.session.commit()
        return {
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "subject_id": chapter.subject_id,
            "subject_name": chapter.subject.name,
            "created_at": ist_format(chapter.created_at),
            "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None,
            "quizCount": chapter.quizzes.filter_by(deleted=False).count() if chapter.quizzes else 0,
            "isCompleted": True  # Placeholder, implement logic if needed
        }, 200

class DeleteChapter(Resource):

    @auth_required('token')
    @roles_accepted('admin')
    def patch(self):
        args = chapter_delete_fields.parse_args()
        id = args.get('id')
        chapter = Chapter.query.filter_by(id=id, deleted=False).first()
        
        if not chapter:
            return {"code": 404, "error_message": "Chapter not found"}, 404

        chapter.deleted = True
        db.session.commit()
        return {"code": 200, "message": "Chapter has been soft deleted successfully, can be restored."}, 200

    @auth_required('token')
    @roles_accepted('admin')
    def delete(self):
        
        args = chapter_delete_fields.parse_args()
        id = args.get('id')
        chapter = Chapter.query.filter_by(id=id, deleted=True).first()
        if not chapter:
            return {"code": 404, "error_message": "Chapter not found"}, 404

        db.session.delete(chapter)
        db.session.commit()
        return {"code": 200, "message": "Chapter has been permanently deleted, can not be restored anymore."}, 200


    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        deleted_chapters = Chapter.query.filter_by(deleted=True).all()
        if not deleted_chapters:
            return {"code": 404, "error_message": "No deleted chapters found"}, 404
        return [
            {
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "subject_id": chapter.subject_id,
                "subject_name": chapter.subject.name,
                "created_at": ist_format(chapter.created_at),
                "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None,
                "quizCount": chapter.quizzes.filter_by(deleted=False).count() if chapter.quizzes else 0,
                "isCompleted": True  # Placeholder, implement logic if needed
            }
            for chapter in deleted_chapters
        ], 200
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = chapter_delete_fields.parse_args()
        id = args.get('id')
        chapter = Chapter.query.filter_by(id=id, deleted=True).first()
        if not chapter:
            return {"code": 404, "error_message": "Chapter not found"}, 404

        chapter.deleted = False
        db.session.commit()
        return {
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "cover_url": chapter.cover_url,
            "created_at": ist_format(chapter.created_at),
            "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None,
            "quizCount": chapter.quizzes.filter_by(deleted=False).count() if chapter.quizzes else 0,
            "isCompleted": True  # Placeholder, implement logic if needed
        }, 200


    



