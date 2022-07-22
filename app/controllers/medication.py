import json
from flask_restful import Resource, request

from app.schemas import MedicationSchema
from app.models.medication import Medication
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


class MedicationView(Resource):

    def post(self):
        """
        Creating a Medication Entry
        """
        medication_schema = MedicationSchema()

        medication_data = request.get_json()

        validated_medication_data, errors = medication_schema.load(medication_data)

        if errors:
            return dict(status='fail', message=errors), 400

        medication = Medication(**validated_medication_data)

        saved_medication = medication.save()

        if not saved_medication:
            return dict(status='fail', message='Internal Server Error'), 500

        new_medication_data, errors = medication_schema.dumps(medication)

        return dict(status='success', data=dict(medication=json.loads(new_medication_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All medications
        """
        medication_schema = MedicationSchema(many=True)

        medications = Medication.find_all(user_id=user_id)

        medications_data, errors = medication_schema.dumps(medications)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(medications=json.loads(medications_data))), 200


class MedicationDetailView(Resource):

    @jwt_required
    def get(self, medication_id):
        """
        Getting individual medication
        """
        schema = MedicationSchema()

        medication = Medication.get_by_id(medication_id)

        if not medication:
            return dict(status="fail", message=f"Medication with id {medication_id} not found"), 404

        medication_data, errors = schema.dumps(medication)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(medication=json.loads(medication_data))), 200




