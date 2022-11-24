from flask_restful import Api
from app.controllers import (
    IndexView, UserView, UserDetailView, UserLoginView, ResetPassword, SiezureView, SeizureDetailView, MedicationView, MedicationDetailView, MedicineView, MedicineDetailView
    , ResilienceView, ResilienceDetailView, RolesView, RolesDetailView, UserRolesView, ClinicianView)


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
api.add_resource(ClinicianView, '/users/register_clinician', endpoint='clinicians')

#Seizure routes
api.add_resource(SiezureView, '/seizures', endpoint='seizures')
api.add_resource(SiezureView, '/seizures/<string:user_id>')
api.add_resource(SeizureDetailView, '/seizure/<string:seizure_id>', endpoint='seizure')

#Medicine routes
api.add_resource(MedicineView, '/medicines', endpoint='medicine')
api.add_resource(MedicineView, '/medicines/<string:user_id>')
api.add_resource(MedicineDetailView, '/medicine/<string:medicine_id>')

#Medication routes
api.add_resource(MedicationView, '/medications', endpoint='medication_records')
api.add_resource(MedicationView, '/medications/<string:user_id>')
api.add_resource(MedicationDetailView, '/medication/<string:medication_id>')

#Resilience routes
api.add_resource(ResilienceView, '/resilience', endpoint='resilience_tracking')
api.add_resource(ResilienceView, '/resiliences/<string:user_id>')
api.add_resource(ResilienceDetailView, '/resilience/<string:resilience_id>')

# Roles routes
api.add_resource(RolesView, '/roles', endpoint='roles')
api.add_resource(RolesDetailView, '/roles/<string:role_id>',
                 endpoint='roles_detail')

# User_Roles routes
api.add_resource(UserRolesView, '/user/<string:user_id>/roles',
                 endpoint='user_roles')
