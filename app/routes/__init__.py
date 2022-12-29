from flask_restful import Api
from app.controllers import (
    IndexView, UserView, UserDetailView, UserLoginView, ResetPassword, SiezureView, SeizureDetailView, SeizureOverview, SeizureDetailOverview, MedicationView, MedicationDetailView, MedicationOverview, MedicationDetailOverview, MedicineView, MedicineDetailView
    , ResilienceView, ResilienceDetailView, RolesView, RolesDetailView, UserRolesView, ClinicianView, ResilienceFeelingsOverview, ResilienceFeelingsDetailedOverview, ResilienceSocialEngagementDetailedOverview, ResilienceTreatmentScaleDetailedOverview)


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
api.add_resource(SeizureOverview, '/seizure/overview')
api.add_resource(SeizureDetailOverview, '/seizure/<string:user_id>/overview')

#Medicine routes
api.add_resource(MedicineView, '/medicines', endpoint='medicine')
api.add_resource(MedicineView, '/medicines/<string:user_id>')
api.add_resource(MedicineDetailView, '/medicine/<string:medicine_id>')

#Medication routes
api.add_resource(MedicationView, '/medications', endpoint='medication_records')
api.add_resource(MedicationView, '/medications/<string:user_id>')
api.add_resource(MedicationDetailView, '/medication/<string:medication_id>')
api.add_resource(MedicationOverview, '/medication/overview')
api.add_resource(MedicationDetailOverview, '/medication/<string:user_id>/overview')

#Resilience routes
api.add_resource(ResilienceView, '/resilience', endpoint='resilience_tracking')
api.add_resource(ResilienceView, '/resiliences/<string:user_id>')
api.add_resource(ResilienceDetailView, '/resilience/<string:resilience_id>')
api.add_resource(ResilienceFeelingsOverview, '/resilience/feelings_overview')
api.add_resource(ResilienceFeelingsDetailedOverview, '/resilience/<string:user_id>/feelings_overview')
api.add_resource(ResilienceSocialEngagementDetailedOverview, '/resilience/<string:user_id>/social_engagement')
api.add_resource(ResilienceTreatmentScaleDetailedOverview, '/resilience/<string:user_id>/peer_treatment')

# Roles routes
api.add_resource(RolesView, '/roles', endpoint='roles')
api.add_resource(RolesDetailView, '/roles/<string:role_id>',
                 endpoint='roles_detail')

# User_Roles routes
api.add_resource(UserRolesView, '/user/<string:user_id>/roles',
                 endpoint='user_roles')
