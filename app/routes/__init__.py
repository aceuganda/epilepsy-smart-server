from flask_restful import Api
from app.controllers import (
    IndexView, UserView, UserDetailView, UserLoginView, ResetPassword, SiezureView, SeizureDetailView)


api = Api()

# Index route
api.add_resource(IndexView, '/')

# User routes
api.add_resource(UserView, '/users', endpoint='users')
api.add_resource(UserDetailView, '/users/<string:user_id>',
                 endpoint='user')
api.add_resource(UserLoginView, '/users/login', endpoint='user_login')
api.add_resource(ResetPassword, '/users/reset_password',
                 endpoint='reset_password')

#Seizure routes
api.add_resource(SiezureView, '/seizures', endpoint='seizures')
api.add_resource(SiezureView, '/seizures/<string:user_id>')
api.add_resource(SeizureDetailView, '/seizures/<string:seizure_id>', endpoint='seizure')