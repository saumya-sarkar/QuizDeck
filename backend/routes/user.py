from flask import request
from flask_security import hash_password, verify_password, auth_required, roles_accepted, current_user
from flask_restful import Resource
from models import db, user_datastore, qualification_list, ist_now
from dateutil import parser
from datetime import datetime
from zoneinfo import ZoneInfo
from time import sleep


class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        qualification = data.get('qualification')
        dob = data.get('dob')

        if not email:
            return {"error": "Email is required"}, 400
        if not password:
            return {"error": "Password is required"}, 400
        
        if email and not username:
            username = email.split('@')[0]
        
        if user_datastore.find_user(email=email):
            return {"error": "User already exists"}, 400
        
        if not user_datastore.find_user(email=email) and user_datastore.find_user(username=username):
            return {"error": "A user with this username already exists, please change your username"}, 400
        
        from models import qualification_list
        if qualification and qualification not in qualification_list.__members__:
            return {"error": "Invalid qualification"}, 400
        
        if dob:
            try:
                dob = parser.parse(dob).date()
            except ValueError:
                return {"error": "Invalid date of birth format"}, 400
        
        if dob and dob > datetime.now(ZoneInfo("Asia/Kolkata")).date():
            return {"error": "Date of birth cannot be in the future"}, 400
        
        if dob == "":
            dob = None
        
        user_datastore.create_user(email=email, username=username, password_hash=hash_password(password), 
                                full_name=full_name, qualification=qualification, dob=dob, roles=['user'])
        db.session.commit()
        return {"message": "User registered successfully"}, 201
    
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        email_username = data.get('email_username')
        password = data.get('password')

        sleep(3) # Simulate a delay
        
        if not email_username:
            return {"error": "Email or username is required"}, 400

        if not password:
            return {"error": "Password is required"}, 400

        user = user_datastore.find_user(email=email_username) or user_datastore.find_user(username=email_username)
        if not user:
            return {"error": "User not found, register with us"}, 404

        if not verify_password(password, user.password_hash):
            return {"error": "Invalid password"}, 401
        
        if not user.is_active:
            return {"error": "User is inactive, contact admin"}, 403

        user.last_login_at = user.current_login_at
        user.current_login_at = ist_now()

        user.last_login_ip = user.current_login_ip
        user.current_login_ip = request.remote_addr

        user.login_count = (user.login_count or 0) + 1

        db.session.commit()

        
        return {
            "message": "Login successful",
            "authToken": user.get_auth_token(),
            "user": {"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name, "roles": [role.name for role in user.roles]}
        }, 200

class qualificationList(Resource):
    def get(self):
        qualifications = [
            {"name": q.name, "value": q.value}
            for q in qualification_list
        ]
        return qualifications, 200
    
class checkUsername(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        user = user_datastore.find_user(username=username)
        if user:
            return { "valid": False, "message": "This username is unavailable" }
        return { "valid": True, "message": "This username is available" }

class checkEmail(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        user = user_datastore.find_user(email=email)
        if user:
            return { "valid": False, "message": "This email is already registered" }
        return { "valid": True, "message": "This email is available for registration" }
    

class userDetails(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'user')
    def get(self):
        user = current_user
        
        if not user:
            return {"error": "User not found"}, 404

        user_data = {"id": user.id, "email": user.email, "username": user.username, "full_name": user.full_name, "roles": [role.name for role in user.roles]}

        return user_data, 200