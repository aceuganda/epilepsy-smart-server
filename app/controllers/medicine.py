import json
from flask_restful import Resource, request

from app.schemas import MedicineSchema
from app.models.medicine import Medicine
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask_bcrypt import Bcrypt
from app.helpers.admin import is_owner_or_admin


class MedicineView(Resource):
    @jwt_required
    def post(self):
        """
        Creating a Medicine Entry
        """
        medicine_schema = MedicineSchema()

        medicine_data = request.get_json()

        validated_medicine_data, errors = medicine_schema.load(medicine_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_medicine = Medicine.find_first(name=validated_medicine_data["name"], user_id=validated_medicine_data["user_id"])

        if existing_medicine:
            return dict(status='fail',
                        message=f'Medicine {validated_medicine_data["name"]} already exists for this user'), 409

        medicine = Medicine(**validated_medicine_data)

        saved_medicine = medicine.save()

        if not saved_medicine:
            return dict(status='fail', message='Internal Server Error'), 500

        new_medicine_data, errors = medicine_schema.dumps(medicine)

        return dict(status='success', data=dict(medicine=json.loads(new_medicine_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All medicines
        """
        medicine_schema = MedicineSchema(many=True)

        medicines = Medicine.find_all(user_id=user_id)
        if not medicines:
            return dict(
                status='fail',
                message=f'No Medicine data found'
            ), 404

        medicines_data, errors = medicine_schema.dumps(medicines)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(medicines=json.loads(medicines_data))), 200


class MedicineDetailView(Resource):

    @jwt_required
    def get(self, medicine_id):
        """
        Getting individual medicine
        """
        schema = MedicineSchema()

        medicine = Medicine.get_by_id(medicine_id)

        if not medicine:
            return dict(status="fail", message=f"Medicine with id {medicine_id} not found"), 404

        medicine_data, errors = schema.dumps(medicine)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(medicine=json.loads(medicine_data))), 200
    
    @jwt_required
    def delete(self, medicine_id):
        """
        Delete a user medicine
        """
        current_user_id = get_jwt_identity()
        current_user_roles = get_jwt_claims()['roles']
        medicine = Medicine.get_by_id(medicine_id)

        if not medicine:
            return dict(
                status="fail",
                message=f"Grateful with id {medicine_id} not found"
            ), 404
        
        if not is_owner_or_admin(medicine, current_user_id, current_user_roles):
            return dict(status='fail', message='unauthorised'), 403

        deleted_medicine = medicine.delete()

        if not deleted_medicine:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200
