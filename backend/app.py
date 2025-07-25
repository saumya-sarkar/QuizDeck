from flask import Flask
from flask_security import Security, auth_required, roles_accepted
from models import db, user_datastore
from flask_restful import Api
from flask_cors import CORS


def create_app():
    
    init_app = Flask(__name__)
    
    from config_file import localDev
    init_app.config.from_object(localDev)
    
    db.init_app(init_app)
    
    Security(init_app, user_datastore)

    CORS(init_app)

    init_api = Api(init_app, prefix='/api')
    
    return init_app, init_api


app, api = create_app()

from routes.user import UserRegister, UserLogin, qualificationList, checkUsername, checkEmail, userDetails
api.add_resource(UserRegister, '/register')  # localhost:5000/api/register
api.add_resource(UserLogin, '/login')  # localhost:5000/api/login
api.add_resource(qualificationList, '/qualifications')
api.add_resource(checkUsername, '/check-username')  # localhost:5000/api/check-username
api.add_resource(checkEmail, '/check-email')  # localhost:5000/api/check-email
api.add_resource(userDetails, '/user-details')  # localhost:5000/api/user-details

from routes.subject import GetAllSubs, UpdateSub, DeleteSub
api.add_resource(GetAllSubs, '/subject')  # localhost:5000/api/subject
api.add_resource(UpdateSub, '/subject/update')  # localhost:5000/api/subject/update
api.add_resource(DeleteSub, '/subject/delete')  # localhost:5000/api/subject/delete


from routes.chapter import GetAllChapters, UpdateChapter, DeleteChapter
api.add_resource(GetAllChapters, '/chapter')  # localhost:5000/api/chapter
api.add_resource(UpdateChapter, '/chapter/update')  # localhost:5000/api/chapter/update
api.add_resource(DeleteChapter, '/chapter/delete')  # localhost:5000/api/chapter/delete


from routes.quiz import GetAllQuizzes, UpdateQuiz, DeleteQuiz
api.add_resource(GetAllQuizzes, '/quiz')  # localhost:5000/api/quiz
api.add_resource(UpdateQuiz, '/quiz/update')  # localhost:5000/api/quiz/update
api.add_resource(DeleteQuiz, '/quiz/delete')  # localhost:5000/api/quiz/delete


from routes.question import get_all_questions, update_question, delete_question
api.add_resource(get_all_questions, '/question')  # localhost:5000/api/question
api.add_resource(update_question, '/question/update')  # localhost:5000/api/question/update
api.add_resource(delete_question, '/question/delete')  # localhost:5000/api/question/delete

from routes.user_quiz import StartQuiz, GetQuizData, SaveAnswer, SubmitQuiz, GetQuizResult
api.add_resource(StartQuiz, '/quiz/start')  # localhost:5000/api/quiz/start
api.add_resource(GetQuizData, '/quiz/data')  # localhost:5000/api/quiz/data
api.add_resource(SaveAnswer, '/quiz/save-answer')  # localhost:5000/api/quiz/save-answer
api.add_resource(SubmitQuiz, '/quiz/submit')  # localhost:5000/api/quiz/submit
api.add_resource(GetQuizResult, '/quiz/result')  # localhost:5000/api/quiz/result



@app.route('/test')
@auth_required('token')
@roles_accepted('admin')
def test():
    return {"message": "Test endpoint reached successfully"}, 200


if __name__ == '__main__':
    app.run()