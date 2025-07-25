from flask_security import auth_required, roles_accepted
from flask_restful import Resource, reqparse
from models import db, Subject, ist_format
from flask import url_for, current_app as app
from werkzeug.utils import secure_filename
import werkzeug
import os
import uuid # For unique filenames


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_cover_url(uploaded_file):
    # Generate a unique filename
    filename = secure_filename(uploaded_file.filename)
    # Ensure the filename is unique by appending a UUID
    unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    uploaded_file.save(filepath)

    # Store the relative URL in the database
    created_cover_url = url_for('static', filename='uploads/' + unique_filename, _external=True)
    return created_cover_url


subject_create_fields = reqparse.RequestParser()
subject_create_fields.add_argument('name', type=str, required=True, location='form')
subject_create_fields.add_argument('description', type=str, required=True, location='form')
subject_create_fields.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=False)

subject_read_fields = reqparse.RequestParser()
subject_read_fields.add_argument('id', type=int, required=True, location='json')

subject_update_fields = reqparse.RequestParser()
subject_update_fields.add_argument('id', type=int, required=True, location='form')
subject_update_fields.add_argument('name', type=str, required=False, location='form')
subject_update_fields.add_argument('description', type=str, required=False, location='form')
subject_update_fields.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=False)

subject_delete_fields = reqparse.RequestParser()
subject_delete_fields.add_argument('id', type=int, required=True, location='json')


class GetAllSubs(Resource):
    
    @auth_required('token')
    def get(self):
        all_subjects = Subject.query.filter_by(deleted=False).all()
        if not all_subjects:
            return {"code": 404, "error_message": "No subjects found"}, 404
        return [
            {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "cover_url": subject.cover_url,
                "totalUsers": 0,
                "totalChapters": 0,
                "totalQuizzes": 0,
                "badge": 'New',
                "created_at": ist_format(subject.created_at),
                "updated_at": ist_format(subject.updated_at) if subject.updated_at else None
            }
            for subject in all_subjects
        ], 200


    @auth_required('token')
    def post(self):
        args = subject_read_fields.parse_args()
        id = args.get('id')
        subject = Subject.query.filter_by(id=id, deleted=False).first()     
        
        if not subject:
            return {"code": 404, "error_message": "Subject not found"}, 404
        chapters = [
            {
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "created_at": ist_format(chapter.created_at),
                "updated_at": ist_format(chapter.updated_at) if chapter.updated_at else None,
                "quizCount": chapter.quizzes.filter_by(deleted=False).count() if chapter.quizzes else 0,
                "isCompleted": True  # Placeholder, implement logic if needed
            }
            for chapter in subject.chapters.filter_by(deleted=False).all()
        ]
        return {
            "id": subject.id,
            "name": subject.name,
            "chapters": chapters
        }, 200


class UpdateSub(Resource):
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = subject_create_fields.parse_args()
        name = args.get('name')
        description = args.get('description')
        uploaded_file = args.get('file')
        cover_url = None

        if uploaded_file and allowed_file(uploaded_file.filename):
            cover_url = create_cover_url(uploaded_file)
        elif uploaded_file and not allowed_file(uploaded_file.filename):
            return {"code": 400, "error_message": "Invalid image format for cover photo."}, 400
        
        if Subject.query.filter_by(name=name).first():
            return {"code": 409, "error_message": "Subject already exists"}, 409
        elif name == "" or name is None:
            return {"code": 400, "error_message": "Name of the subject is required"}, 400
        elif description == "" or description is None:
            return {"code": 400, "error_message": "Description of the subject is required"}, 400
        
        else:
            subject = Subject(name=name, description=description, cover_url=cover_url)
            db.session.add(subject)
            db.session.commit()
            
            return {
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "cover_url": subject.cover_url,
            "totalUsers": 0,
            "totalChapters": 0,
            "totalQuizzes": 0,
            "badge": 'New',
            "created_at": ist_format(subject.created_at),
            "updated_at": ist_format(subject.updated_at) if subject.updated_at else None
        }, 201

    @auth_required('token')
    @roles_accepted('admin')
    def put(self):
        data = subject_update_fields.parse_args()
        id = data.get('id')
        name = data.get('name')
        description = data.get('description')
        uploaded_file = data.get('file')
        cover_url = None
    
        subject = Subject.query.filter_by(id=id, deleted=False).first()
        
        if not subject:
            return {"code": 404, "error_message": "Subject not found"}, 404
        elif Subject.query.filter(Subject.name == name, Subject.id != id).first():
            return {"code": 409, "error_message": "Subject name already exists. Please choose a different name."}, 409
        
        if uploaded_file and allowed_file(uploaded_file.filename):
            cover_url = create_cover_url(uploaded_file)
        elif uploaded_file and not allowed_file(uploaded_file.filename):
            return {"code": 400, "error_message": "Invalid file format for cover URL"}, 400

        # Update the subject fields
        subject.name = name if name else subject.name
        subject.description = description if description else subject.description
        subject.cover_url = cover_url if cover_url else subject.cover_url
        
        db.session.commit()
        return {
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "cover_url": subject.cover_url,
            "created_at": ist_format(subject.created_at),
            "updated_at": ist_format(subject.updated_at) if subject.updated_at else None
        }, 200

    

class DeleteSub(Resource):
    
    # Soft delete a subject, marking it as deleted without removing it from the database
    @auth_required('token')
    @roles_accepted('admin')
    def patch(self):
        args = subject_delete_fields.parse_args()
        id = args.get('id')
        subject = Subject.query.filter_by(id=id, deleted=False).first()
        if not subject:
            return {"code": 404, "error_message": "Subject not found"}, 404
        
        subject.deleted = True
        db.session.commit()
        return {"code": 200, "message": "Subject has been soft deleted successfully, can be restored."}, 200
    

    # Permanently delete a subject, removing it from the database
    @auth_required('token')
    @roles_accepted('admin')
    def delete(self):
        args = subject_delete_fields.parse_args()
        id = args.get('id')
        subject = Subject.query.filter_by(id=id, deleted=True).first()
        
        if not subject:
            return {"code": 404, "error_message": "Subject not found in the recycle basket."}, 404
        
        if subject.cover_url:
            try:
                # Get the filename from the URL
                filename = subject.cover_url.split('/')[-1]
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Delete the file if it exists
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as error:
                app.logger.warning(f"Failed to delete cover image: {error}")


        db.session.delete(subject)
        db.session.commit()
        return {"code": 200, "message": "Subject has been permanently deleted, can not be restored anymore."}, 200
    
    
    
    @auth_required('token')
    @roles_accepted('admin')
    def get(self):
        deleted_subjects = Subject.query.filter_by(deleted=True).all()
        if not deleted_subjects:
            return {"code": 404, "error_message": "No deleted subjects found"}, 404
        return [
            {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "cover_url": subject.cover_url,
                "created_at": ist_format(subject.created_at),
                "updated_at": ist_format(subject.updated_at) if subject.updated_at else None
            }
            for subject in deleted_subjects
        ], 200
    
    @auth_required('token')
    @roles_accepted('admin')
    def post(self):
        args = subject_delete_fields.parse_args()
        id = args.get('id')
        subject = Subject.query.filter_by(id=id, deleted=True).first()
        if not subject:
            return {"code": 404, "error_message": "Subject not found"}, 404
        
        subject.deleted = False
        db.session.commit()
        
        return {
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "cover_url": subject.cover_url,
            "created_at": ist_format(subject.created_at),
            "updated_at": ist_format(subject.updated_at) if subject.updated_at else None,
        }, 200


    



