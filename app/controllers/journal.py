import json
from flask_restful import Resource, request

from app.schemas import JournalSchema
from app.models.journal import Journal
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


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

