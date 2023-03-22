import json
from flask_restful import Resource, request

from app.schemas import GratefulSchema
from app.models.gratefuls import Grateful
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask_bcrypt import Bcrypt
from app.helpers.admin import is_owner_or_admin


class GratefulsView(Resource):
    @jwt_required
    def post(self):
        """
        Creating a Grateful Entry
        """
        gratefuls_schema = GratefulSchema()

        grateful_data = request.get_json()

        validated_grateful_data, errors = gratefuls_schema.load(grateful_data)

        if errors:
            return dict(status='fail', message=errors), 400

        grateful = Grateful(**validated_grateful_data)

        saved_grateful = grateful.save()

        if not saved_grateful:
            return dict(status='fail', message='Internal Server Error'), 500

        new_grateful_data, errors = gratefuls_schema.dumps(grateful)

        return dict(status='success', data=dict(grateful=json.loads(new_grateful_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All gratefuls
        """
        grateful_schema = GratefulSchema(many=True)

        gratefuls = Grateful.find_all(user_id=user_id)
        if not gratefuls:
            return dict(
                status='fail',
                message=f'No Grateful data found'
            ), 404

        gratefuls_data, errors = grateful_schema.dumps(gratefuls)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(gratefuls=json.loads(gratefuls_data))), 200

class GratefulsDetailView(Resource):
    @jwt_required
    def get(self, grateful_id):
        """
        Getting a particular grateful
        """
        grateful_schema = GratefulSchema(many=False)

        grateful = Grateful.get_by_id(grateful_id)

        if not grateful:
            return dict(status='fail', message=f'No grateful data'), 404
        
        grateful_data, errors = grateful_schema.dumps(grateful)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500
        
        return dict(status="success", data=dict(grateful=json.loads(grateful_data)))

    @jwt_required
    def patch(self, grateful_id):
        """
        Update user grateful
        """
        current_user_id = get_jwt_identity()
        current_user_roles = get_jwt_claims()['roles'] 
        grateful_schema = GratefulSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = grateful_schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        grateful = Grateful.get_by_id(grateful_id)

        if not grateful:
            return dict(
                status="fail",
                message=f"Grateful with id {grateful_id} not found"
            ), 404
        
        if not is_owner_or_admin(grateful, current_user_id, current_user_roles):
            return dict(status='fail', message='unauthorised'), 403

        updated_grateful = Grateful.update(grateful, **validated_update_data)

        if not updated_grateful:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(
            status="success",
            message=f"Grateful updated successfully"
        ), 200

    @jwt_required
    def delete(self, grateful_id):
        """
        Delete a user grateful
        """
        current_user_id = get_jwt_identity()
        current_user_roles = get_jwt_claims()['roles']  
        grateful = Grateful.get_by_id(grateful_id)

        if not grateful:
            return dict(
                status="fail",
                message=f"Grateful with id {grateful_id} not found"
            ), 404
        
        if not is_owner_or_admin(grateful, current_user_id, current_user_roles):
            return dict(status='fail', message='unauthorised'), 403

        deleted_grateful = grateful.delete()

        if not deleted_grateful:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200