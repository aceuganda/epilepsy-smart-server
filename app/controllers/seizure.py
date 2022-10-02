import json
from flask_restful import Resource, request

from app.schemas import SeizureSchema
from app.models.seizure import Seizure
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


class SiezureView(Resource):

    def post(self):
        """
        Creating a Seizure Entry
        """
        seizure_schema = SeizureSchema()

        seizure_data = request.get_json()

        validated_seizure_data, errors = seizure_schema.load(seizure_data)

        if errors:
            return dict(status='fail', message=errors), 400

        seizure = Seizure(**validated_seizure_data)

        saved_seizure = seizure.save()

        if not saved_seizure:
            return dict(status='fail', message='Internal Server Error'), 500

        new_seizure_data, errors = seizure_schema.dumps(seizure)

        return dict(status='success', data=dict(seizure=json.loads(new_seizure_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All seizures
        """
        seizure_schema = SeizureSchema(many=True)

        seizures = Seizure.find_all(user_id=user_id)
        if not seizures:
            return dict(
                status='fail',
                message=f'No seizure data found' 
            ), 404

        seizures_data, errors = seizure_schema.dumps(seizures)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(seizures=json.loads(seizures_data))), 200


class SeizureDetailView(Resource):

    @jwt_required
    def get(self, seizure_id):
        """
        Getting individual seizure
        """
        schema = SeizureSchema()

        seizure = Seizure.get_by_id(seizure_id)

        if not seizure:
            return dict(status="fail", message=f"Seizure with id {seizure_id} not found"), 404

        seizure_data, errors = schema.dumps(seizure)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(seizure=json.loads(seizure_data))), 200




