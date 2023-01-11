import json
from flask_restful import Resource, request

from app.schemas import MedicationSchema
from app.models.medication import Medication
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from math import ceil
import calendar

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
        if not medications:
            return dict(
                status='fail',
                message=f'No Medication data found'
            ), 404

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

class MedicationMissedReasons(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Getting individual reasons for missing medication
        """
        reasons = []

        schema = MedicationSchema(many=True)

        medications = Medication.find_all(user_id=user_id)

        if not medications:
            return dict(
                status='fail',
                message=f'No Medication data found'
            ), 404
        
        medications, errors = schema.dumps(medications)
        medications_list = json.loads(medications)

        for entry in medications_list:
            reason_missed = entry["reason_missed_dose"]
            if reason_missed == "" or reason_missed == None:
                continue
            else:
                reasons.append(reason_missed)
        
        if errors:
            return dict(status="fail", message="Internal Server Error"), 500
        
        if len(reasons) <= 0:
            return dict(status='fail', message=f'No reasons for missing medication data found'), 404
        else:
            return dict(status="success", data=dict(reasons=reasons)), 200

class MedicationOverview(Resource):

    @jwt_required
    def get(self):
        """
        Getting all medication records
        """
        overview = []

        schema = MedicationSchema(many=True)

        # weekly overview
        weekly_medications = {
            "monday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "tuesday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "wednesday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "thursday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "friday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "saturday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "sunday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_medication = Medication.query.filter(Medication.timestamp > weekly_filter).all()
        
        if not weekly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        weekly_medication_data, weekly_errors = schema.dumps(weekly_medication)
        weekly_medication_data_list = json.loads(weekly_medication_data)
        print(weekly_medication_data_list)

        for data in weekly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            took_medicine = data["took_medicine"]
            weekly_medications[day][took_medicine] += 1
        
        overview.append(dict(weekly_medications=weekly_medications))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview
        monthly_medications = {
            "week1": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week2": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week3": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week4": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week5": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_medication = Medication.query.filter(Medication.timestamp > monthly_filter).all()
        
        if not monthly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        monthly_medication_data, monthly_errors = schema.dumps(monthly_medication)
        monthly_medication_data_list = json.loads(monthly_medication_data)
        print(monthly_medication_data_list)

        for data in monthly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            took_medicine = data["took_medicine"]
            monthly_medications[week][took_medicine] += 1
        
        overview.append(dict(monthly_medications=monthly_medications))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly overview
        yearly_medications = {
            "january": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "february": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "march": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "april": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "may": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "june": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "july": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "august": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "september": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "october": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "november": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "december": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_medication = Medication.query.filter(Medication.timestamp > yearly_filter).all()
        
        if not yearly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        yearly_medication_data, yearly_errors = schema.dumps(yearly_medication)
        yearly_medication_data_list = json.loads(yearly_medication_data)

        for data in yearly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            took_medicine = data["took_medicine"]
            yearly_medications[month][took_medicine] += 1
        
        overview.append(dict(yearly_medications=yearly_medications))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        return dict(status='success', data=dict(overview=overview))

class MedicationDetailOverview(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Getting all medication records
        """
        overview = []

        schema = MedicationSchema(many=True)

        # weekly overview
        weekly_medications = {
            "monday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "tuesday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "wednesday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "thursday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "friday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "saturday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "sunday": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_medication = Medication.query.filter(Medication.timestamp > weekly_filter, Medication.user_id==user_id).all()
        
        if not weekly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        weekly_medication_data, weekly_errors = schema.dumps(weekly_medication)
        weekly_medication_data_list = json.loads(weekly_medication_data)
        print(weekly_medication_data_list)

        for data in weekly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            took_medicine = data["took_medicine"]
            weekly_medications[day][took_medicine] += 1
        
        overview.append(dict(weekly_medications=weekly_medications))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview
        monthly_medications = {
            "week1": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week2": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week3": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week4": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "week5": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_medication = Medication.query.filter(Medication.timestamp > monthly_filter, Medication.user_id==user_id).all()
        
        if not monthly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        monthly_medication_data, monthly_errors = schema.dumps(monthly_medication)
        monthly_medication_data_list = json.loads(monthly_medication_data)

        for data in monthly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            took_medicine = data["took_medicine"]
            monthly_medications[week][took_medicine] += 1
        
        overview.append(dict(monthly_medications=monthly_medications))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly overview
        yearly_medications = {
            "january": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "february": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "march": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "april": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "may": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "june": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "july": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "august": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "september": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "october": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "november": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            },
            "december": {
                "all doses": 0,
                "some doses": 0,
                "no doses": 0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_medication = Medication.query.filter(Medication.timestamp > yearly_filter, Medication.user_id==user_id).all()
        
        if not yearly_medication:
            return dict(status="fail", message=f"No medication data found"), 404

        yearly_medication_data, yearly_errors = schema.dumps(yearly_medication)
        yearly_medication_data_list = json.loads(yearly_medication_data)

        for data in yearly_medication_data_list:
            timestamp = data['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            took_medicine = data["took_medicine"]
            yearly_medications[month][took_medicine] += 1
        
        overview.append(dict(yearly_medications=yearly_medications))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        return dict(status='success', data=dict(overview=overview))  

