import json
from flask_restful import Resource, request

from app.schemas import JournalSchema
from app.models.journal import Journal
from flask_bcrypt import Bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from app.helpers.admin import is_owner_or_admin

class JournalsView(Resource):
    @jwt_required
    def post(self):
        """
        Creating a Journal Entry
        """
        journals_schema = JournalSchema()

        journal_data = request.get_json()

        validated_journal_data, errors = journals_schema.load(journal_data)

        if errors:
            return dict(status='fail', message=errors), 400

        journal = Journal(**validated_journal_data)

        saved_journal = journal.save()

        if not saved_journal:
            return dict(status='fail', message='Internal Server Error'), 500

        new_journal_data, errors = journals_schema.dumps(journal)

        return dict(status='success', data=dict(journal=json.loads(new_journal_data))), 201

    @jwt_required
    def get(self, user_id):
        """
        Getting All journals
        """
        journal_schema = JournalSchema(many=True)

        journals = Journal.find_all(user_id=user_id)
        if not journals:
            return dict(
                status='fail',
                message=f'No Journal data found'
            ), 404

        journals_data, errors = journal_schema.dumps(journals)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(journals=json.loads(journals_data))), 200


class JournalsDetailView(Resource):
    @jwt_required
    def get(self, journal_id):
        """
        Getting a particular journal
        """
        journal_schema = JournalSchema(many=False)

        journal = Journal.get_by_id(journal_id)

        if not journal:
            return dict(status='fail', message=f'No journal data'), 404
        
        journal_data, errors = journal_schema.dumps(journal)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500
        
        return dict(status="success", data=dict(journal=json.loads(journal_data)))
    
    @jwt_required
    def patch(self, journal_id):
        """
        Update user journal
        """
        current_user_id = get_jwt_identity()
        current_user_roles = get_jwt_claims()['roles'] 
        journal_schema = JournalSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = journal_schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        journal = Journal.get_by_id(journal_id)

        if not journal:
            return dict(
                status="fail",
                message=f"Journal with id {journal_id} not found"
            ), 404

        if not is_owner_or_admin(journal, current_user_id, current_user_roles):
            return dict(status='fail', message='unauthorised'), 403

        updated_journal = Journal.update(journal, **validated_update_data)

        if not updated_journal:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(
            status="success",
            message=f"Journal updated successfully"
        ), 200



    @jwt_required
    def delete(self, journal_id):
        """
        Delete a user journal
        """
        current_user_id = get_jwt_identity()
        current_user_roles = get_jwt_claims()['roles']        
        journal = Journal.get_by_id(journal_id)

        if not journal:
            return dict(
                status="fail",
                message=f"Journal with id {journal_id} not found"
            ), 404

        if not is_owner_or_admin(journal, current_user_id, current_user_roles):
            return dict(status='fail', message='unauthorised'), 403

        deleted_journal = journal.delete()

        if not deleted_journal:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200