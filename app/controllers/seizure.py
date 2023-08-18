import json
from flask_restful import Resource, request

from app.schemas import SeizureSchema
from app.models.seizure import Seizure
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from math import ceil
import calendar


class SiezureView(Resource):
    @jwt_required
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

class SeizureOverview(Resource):

    @jwt_required
    def get(self):
        """
        Get all seizure records
        """
        overview = []

        schema = SeizureSchema(many=True)

        # weekly overview
        weekly_severity = {
            "monday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "tuesday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "wednesday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "thursday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "friday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "saturday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "sunday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # monthly overview
        monthly_severity = {
            "week1": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week2": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week3": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week4": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week5": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week6": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # yearly severity
        yearly_severity = {
            "january": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "february": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "march": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "april": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "may": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "june": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "july": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "august": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "september": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "october": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "november": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "december": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # get weekly data
        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_seizures = Seizure.query.filter(Seizure.timestamp > weekly_filter).all()

        # get monthly data
        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_seizures = Seizure.query.filter(Seizure.timestamp > monthly_filter).all()

        # get yearly data
        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_seizures = Seizure.query.filter(Seizure.timestamp > yearly_filter).all()

        if (not weekly_seizures and not monthly_seizures and not yearly_seizures):
            return dict(status="fail", message=f"No seizure data found"), 404

        # append weekly data to overview

        weekly_seizure_data, weekly_errors = schema.dumps(weekly_seizures)
        weekly_seizure_data_list = json.loads(weekly_seizure_data)

        for d in weekly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            weekly_severity[day][severity] +=1
        
        overview.append(dict(weekly_severity=weekly_severity))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # append monthly data to overview
        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_seizure_data, monthly_errors = schema.dumps(monthly_seizures)
        monthly_seizure_data_list = json.loads(monthly_seizure_data)

        for d in monthly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            monthly_severity[week][severity] +=1
        
        overview.append(dict(monthly_severity=monthly_severity))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # append yearly data to overview

        yearly_seizure_data, yearly_errors = schema.dumps(yearly_seizures)
        yearly_seizure_data_list = json.loads(yearly_seizure_data)

        for d in yearly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            yearly_severity[month][severity] +=1
        
        overview.append(dict(yearly_severity=yearly_severity))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=(overview))), 200

class SeizureDetailOverview(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Get all user seizure records 
        """
        overview = []

        schema = SeizureSchema(many=True)

        # weekly overview
        weekly_severity = {
            "monday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "tuesday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "wednesday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "thursday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "friday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "saturday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "sunday": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # monthly overview
        monthly_severity = {
            "week1": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week2": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week3": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week4": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week5": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "week6": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # yearly severity
        yearly_severity = {
            "january": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "february": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "march": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "april": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "may": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "june": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "july": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "august": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "september": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "october": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "november": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            },
            "december": {
                "mild": 0,
                "moderate": 0,
                "severe": 0
            }
        }

        # get weekly data
        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_seizures = Seizure.query.filter(Seizure.timestamp > weekly_filter, Seizure.user_id==user_id).all()

        # get monthly data
        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_seizures = Seizure.query.filter(Seizure.timestamp > monthly_filter, Seizure.user_id==user_id).all()

        # get yearly data
        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_seizures = Seizure.query.filter(Seizure.timestamp > yearly_filter, Seizure.user_id==user_id).all()

        if (not weekly_seizures and not monthly_seizures and not yearly_seizures):
            return dict(status="fail", message=f"No seizure data found"), 404

        # append weekly data to overview

        weekly_seizure_data, weekly_errors = schema.dumps(weekly_seizures)
        weekly_seizure_data_list = json.loads(weekly_seizure_data)

        for d in weekly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            weekly_severity[day][severity] +=1
        
        overview.append(dict(weekly_severity=weekly_severity))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # append monthly data to overview

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_seizure_data, monthly_errors = schema.dumps(monthly_seizures)
        monthly_seizure_data_list = json.loads(monthly_seizure_data)

        for d in monthly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            monthly_severity[week][severity] +=1
        
        overview.append(dict(monthly_severity=monthly_severity))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # append yearly data to overview
        
        yearly_seizure_data, yearly_errors = schema.dumps(yearly_seizures)
        yearly_seizure_data_list = json.loads(yearly_seizure_data)

        for d in yearly_seizure_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            severity = d["seizure_severity"]
            if severity != "mild" and severity != "moderate" and severity != "severe": 
                continue
            yearly_severity[month][severity] +=1
        
        overview.append(dict(yearly_severity=yearly_severity))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=overview)), 200    

class SeizureUserMetrics(Resource):
    @jwt_required
    def get(self, user_id):
        """
        Getting the number of user seizures overtime
        """
        seizure_metrics = []

        schema = SeizureSchema(many=True)

        # weekly seizures
        weekly_seizures = {
            "total_seizures": 0
        }

        # monthly seizures
        monthly_seizures = {
            "total_seizures": 0
        }

        # yearly seizures
        yearly_seizures = {
            "total_seizures": 0
        }

        # get weekly data
        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_seizure = Seizure.query.filter(Seizure.timestamp > weekly_filter, Seizure.user_id==user_id).all()

        # get monthly data
        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_seizure = Seizure.query.filter(Seizure.timestamp > monthly_filter, Seizure.user_id==user_id).all()

        # get annual data
        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_seizure = Seizure.query.filter(Seizure.timestamp > yearly_filter, Seizure.user_id==user_id).all()
        
        if (not weekly_seizure and not monthly_seizure and not yearly_seizure):
            return dict(status="fail", message=f"No seizure data found"), 404

        # append weekly data to seizure_metrics

        weekly_seizure_data, weekly_errors = schema.dumps(weekly_seizure)
        weekly_seizure_data_list = json.loads(weekly_seizure_data)

        for data in weekly_seizure_data_list:
            weekly_seizures["total_seizures"] += 1
        
        seizure_metrics.append(dict(weekly_seizures=weekly_seizures))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # append monthly data to seizure_metrics

        monthly_seizure_data, monthly_errors = schema.dumps(monthly_seizure)
        monthly_seizure_data_list = json.loads(monthly_seizure_data)

        for data in monthly_seizure_data_list:
            monthly_seizures["total_seizures"] += 1
        
        seizure_metrics.append(dict(monthly_seizures=monthly_seizures))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500
        
        # append yearly data to seizure_metrics

        yearly_seizure_data, yearly_errors = schema.dumps(yearly_seizure)
        yearly_seizure_data_list = json.loads(yearly_seizure_data)

        for data in yearly_seizure_data_list:
            yearly_seizures["total_seizures"] += 1
        
        seizure_metrics.append(dict(yearly_seizures=yearly_seizures))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(seizure_metrics=seizure_metrics))