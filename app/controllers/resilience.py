import json
from flask_restful import Resource, request

from app.schemas import ResilienceSchema
from app.models.resilience import Resilience
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


class ResilienceView(Resource):

    def post(self):
        """
        Creating a Resilience Entry
        """
        resilience_schema = ResilienceSchema()

        resilience_data = request.get_json()

        validated_resilience_data, errors = resilience_schema.load(resilience_data)

        if errors:
            return dict(status='fail', message=errors), 400

        resilience = Resilience(**validated_resilience_data)

        saved_resilience = resilience.save()

        if not saved_resilience:
            return dict(status='fail', message='Internal Server Error'), 500

        new_resilience_data, errors = resilience_schema.dumps(resilience)

        return dict(status='success', data=dict(resilience=json.loads(new_resilience_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All resiliences
        """
        resilience_schema = ResilienceSchema(many=True)

        resiliences = Resilience.find_all(user_id=user_id)

        resiliences_data, errors = resilience_schema.dumps(resiliences)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(resiliences=json.loads(resiliences_data))), 200


class ResilienceDetailView(Resource):

    @jwt_required
    def get(self, resilience_id):
        """
        Getting individual resilience
        """
        schema = ResilienceSchema()

        resilience = Resilience.get_by_id(resilience_id)

        if not resilience:
            return dict(status="fail", message=f"Resilience with id {resilience_id} not found"), 404

        resilience_data, errors = schema.dumps(resilience)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(resilience=json.loads(resilience_data))), 200




