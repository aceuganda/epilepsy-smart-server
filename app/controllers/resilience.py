import json
from flask_restful import Resource, request

from app.schemas import ResilienceSchema
from app.models.resilience import Resilience
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
# from app.models.activities import Activity
# from app.models.feelings import Feeling
from datetime import datetime, timedelta
from sqlalchemy import and_
from math import ceil
import calendar
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
        filter_after = datetime.today() - timedelta(days = 3)
        print(filter_after)
        resiliences = Resilience.query.filter(Resilience.timestamp>=filter_after, Resilience.user_id==user_id).all()   
        if not resiliences:
            return dict(
                status='fail',
                message=f'No resilience data found'
            ), 404

        resiliences_data, errors = resilience_schema.dumps(resiliences)
        print(resiliences_data)



        
        resiliences_data_list = json.loads(resiliences_data)
        print(resiliences_data_list)
        print(resiliences_data_list[0]["treatment_scale_by_other"])

        #count social engagement activities for 3 days
        total =0
        treatment_total= 0
        counter =0
        total_positive_feelings = 0
        total_negative_feelings = 0
        overall_positive_feelings_list = []
        overall_negative_feelings_list = []
        for engagement in resiliences_data_list:
            deserialized_social_engagement = json.loads(engagement["engagement_activities"][0])
            day_social_activity_count = len(deserialized_social_engagement)
            total = total + day_social_activity_count

            # count treatement by others
            treatment_total = treatment_total + engagement["treatment_scale_by_other"]
            counter+=1

            #count the feelings 
            if engagement["type_of_feelings"] == "Positive" or engagement["type_of_feelings"] == "positive":
                deserialized_positive_feelings = json.loads(engagement["feelings_experienced"][0])
                day_positive_feelings_count = len(deserialized_positive_feelings)
                total_positive_feelings = total_positive_feelings + day_positive_feelings_count
                overall_positive_feelings_list = overall_positive_feelings_list+ deserialized_positive_feelings

            elif engagement["type_of_feelings"] == "Negative" or engagement["type_of_feelings"] == "negative":
                deserialized_negative_feelings = json.loads(engagement["feelings_experienced"][0])
                day_negative_feelings_count = len(deserialized_negative_feelings)
                total_negative_feelings = total_negative_feelings + day_negative_feelings_count
                overall_negative_feelings_list = overall_negative_feelings_list + deserialized_negative_feelings

        
        three_day_social_activity_count = total
        
        if three_day_social_activity_count >0 and three_day_social_activity_count <=5:
            resiliences_data_list.append(dict(three_day_social_activity_count=three_day_social_activity_count))
            resiliences_data_list.append(dict(three_day_social_activity_comment="Low social engagement"))
        elif three_day_social_activity_count >5 and three_day_social_activity_count <=9:
            resiliences_data_list.append(dict(three_day_social_activity_count=three_day_social_activity_count))
            resiliences_data_list.append(dict(three_day_social_activity_comment="Medium social engagement"))
        elif three_day_social_activity_count >=10:
            resiliences_data_list.append(dict(three_day_social_activity_count=three_day_social_activity_count))
            resiliences_data_list.append(dict(three_day_social_activity_comment="High social engagement"))



        #average treatment by others value over 3 days
        av_treatment_by_others = treatment_total/counter
        if av_treatment_by_others >= 65:
            resiliences_data_list.append(dict(three_day_av_treatment=av_treatment_by_others))
            resiliences_data_list.append(dict(three_day_av_treatment_comment="Oh no! Seems you have not been treated well lately"))
        elif av_treatment_by_others <65:
            resiliences_data_list.append(dict(three_day_av_treatment=av_treatment_by_others))
            resiliences_data_list.append(dict(three_day_av_treatment_comment="Positive! You're being treated well lately"))

        #feelings feedback calculation
        percentage_positive_feelings = ((total_positive_feelings)/(total_positive_feelings+total_negative_feelings))*100
        resiliences_data_list.append(dict(three_day_av_positive_feeling_percentage=percentage_positive_feelings))

        feelings_occurrence = {}
        if percentage_positive_feelings >= 60:
            feelings_occurrence = {item: overall_positive_feelings_list.count(item) for item in overall_positive_feelings_list}
            good_feeling_count = feelings_occurrence.get("happy",0) + feelings_occurrence.get("joyful",0)+ feelings_occurrence.get("appreciated",0)+feelings_occurrence.get("cheerful",0)
            positive_feeling_count = feelings_occurrence.get("encouraged",0)+ feelings_occurrence.get("hopeful",0)+ feelings_occurrence.get("confident",0)+ feelings_occurrence.get("inspired",0)
            grateful_feeling_count = feelings_occurrence.get("grateful",0)

            if good_feeling_count > positive_feeling_count and good_feeling_count > grateful_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling good lately"))

            elif positive_feeling_count > good_feeling_count and positive_feeling_count > grateful_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling positive lately"))
            
            elif grateful_feeling_count > positive_feeling_count and good_feeling_count > good_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling grateful lately"))
            else:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling positive lately"))

        elif percentage_positive_feelings <60:
            feelings_occurrence = {item: overall_negative_feelings_list.count(item) for item in overall_negative_feelings_list}
            down_feeling_count = feelings_occurrence.get("sad",0)+feelings_occurrence.get("discouraged",0)+feelings_occurrence.get("lonely",0)+feelings_occurrence.get("hopeless",0)
            distressed_feeling_count = feelings_occurrence.get("angry",0)+ feelings_occurrence.get("irritable",0)+feelings_occurrence.get("impatient",0)
            anxious = feelings_occurrence.get("worried",0)+ feelings_occurrence.get("fearful",0)
            confused_feeling_count = feelings_occurrence.get("confused",0)
            envious_feeling_count = feelings_occurrence.get("envious",0)

            if down_feeling_count> distressed_feeling_count and down_feeling_count >anxious and down_feeling_count >confused_feeling_count and down_feeling_count > envious_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling down lately"))

            elif distressed_feeling_count>down_feeling_count  and distressed_feeling_count >anxious and distressed_feeling_count >confused_feeling_count and distressed_feeling_count > envious_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling distressed lately"))

            elif anxious> distressed_feeling_count and anxious >down_feeling_count and anxious >confused_feeling_count and anxious > envious_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling anxious lately"))

            elif confused_feeling_count> distressed_feeling_count and confused_feeling_count >down_feeling_count and confused_feeling_count >anxious and confused_feeling_count > envious_feeling_count:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling abit confused lately"))

            elif envious_feeling_count> distressed_feeling_count and envious_feeling_count >down_feeling_count and envious_feeling_count >confused_feeling_count and envious_feeling_count > anxious:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling envious lately"))
            else:
                resiliences_data_list.append(dict(three_day_av_feeling_comment="It seems you have been feeling abit negative lately"))



        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(resiliences=resiliences_data_list)), 200


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


class ResilienceFeelingsOverview(Resource):

    @jwt_required
    def get(self):
        """
        Get all resilience records
        """
        overview = []

        schema = ResilienceSchema(many=True)

        # weekly overview

        weekly_feelings_count = {
            "monday": {
               "positive":0,
                "negative":0
            },
            "tuesday": {
               "positive":0,
               "negative":0
            },
            "wednesday": {
               "positive":0,
                "negative":0
            },
            "thursday": {
               "positive":0,
                "negative":0
            },
            "friday": {
               "positive":0,
                "negative":0
            },
            "saturday": {
               "positive":0,
                "negative":0
            },
            "sunday": {
               "positive":0,
                "negative":0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_resiliences = Resilience.query.filter(Resilience.timestamp > weekly_filter).all()

        if not weekly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        weekly_resilience_data, weekly_errors = schema.dumps(weekly_resiliences)
        weekly_resilience_data_list = json.loads(weekly_resilience_data)

        for d in weekly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            feelings_count = d["type_of_feelings"].lower()
            weekly_feelings_count[day][feelings_count] +=1
        
        overview.append(dict(weekly_feelings_count=weekly_feelings_count))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview

        monthly_feelings_count = {
            "week1": {
               "positive":0,
                "negative":0
            },
            "week2": {
               "positive":0,
                "negative":0
            },
            "week3": {
               "positive":0,
                "negative":0
            },
            "week4": {
               "positive":0,
                "negative":0
            },
            "week5": {
               "positive":0,
                "negative":0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_resiliences = Resilience.query.filter(Resilience.timestamp > monthly_filter).all()

        if not monthly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        monthly_resilience_data, monthly_errors = schema.dumps(monthly_resiliences)
        monthly_resilience_data_list = json.loads(monthly_resilience_data)

        for d in monthly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            feelings_count = d["type_of_feelings"].lower()
            monthly_feelings_count[week][feelings_count] +=1
        
        overview.append(dict(monthly_feelings_count=monthly_feelings_count))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly feelings_count

        yearly_feelings_count = {
            "january": {
               "positive":0,
                "negative":0
            },
            "february": {
               "positive":0,
                "negative":0
            },
            "march": {
               "positive":0,
                "negative":0
            },
            "april": {
               "positive":0,
                "negative":0
            },
            "may": {
               "positive":0,
                "negative":0
            },
            "june": {
               "positive":0,
                "negative":0
            },
            "july": {
               "positive":0,
                "negative":0
            },
            "august": {
               "positive":0,
                "negative":0
            },
            "september": {
               "positive":0,
                "negative":0
            },
            "october": {
               "positive":0,
                "negative":0
            },
            "november": {
               "positive":0,
                "negative":0
            },
            "december": {
               "positive":0,
                "negative":0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_resiliences = Resilience.query.filter(Resilience.timestamp > yearly_filter).all()

        if not yearly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        yearly_resilience_data, yearly_errors = schema.dumps(yearly_resiliences)
        yearly_resilience_data_list = json.loads(yearly_resilience_data)

        for d in yearly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            feelings_count = d["type_of_feelings"].lower()
            yearly_feelings_count[month][feelings_count] +=1
        
        overview.append(dict(yearly_feelings_count=yearly_feelings_count))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=(overview))), 200



class ResilienceFeelingsDetailedOverview(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Get all user resilience records: feelings for a user.
        """
        overview = []

        schema = ResilienceSchema(many=True)

        # weekly overview

        weekly_feelings_count = {
            "monday": {
               "positive":0,
                "negative":0
            },
            "tuesday": {
               "positive":0,
               "negative":0
            },
            "wednesday": {
               "positive":0,
                "negative":0
            },
            "thursday": {
               "positive":0,
                "negative":0
            },
            "friday": {
               "positive":0,
                "negative":0
            },
            "saturday": {
               "positive":0,
                "negative":0
            },
            "sunday": {
               "positive":0,
                "negative":0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_resiliences = Resilience.query.filter(Resilience.timestamp > weekly_filter, Resilience.user_id==user_id).all()

        if not weekly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        weekly_resilience_data, weekly_errors = schema.dumps(weekly_resiliences)
        weekly_resilience_data_list = json.loads(weekly_resilience_data)

        for d in weekly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            feelings_count = d["type_of_feelings"].lower()
            weekly_feelings_count[day][feelings_count] +=1
        
        overview.append(dict(weekly_feelings_count=weekly_feelings_count))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview

        monthly_feelings_count = {
            "week1": {
               "positive":0,
                "negative":0
            },
            "week2": {
               "positive":0,
                "negative":0
            },
            "week3": {
               "positive":0,
                "negative":0
            },
            "week4": {
               "positive":0,
                "negative":0
            },
            "week5": {
               "positive":0,
                "negative":0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_resiliences = Resilience.query.filter(Resilience.timestamp > monthly_filter, Resilience.user_id==user_id).all()

        if not monthly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        monthly_resilience_data, monthly_errors = schema.dumps(monthly_resiliences)
        monthly_resilience_data_list = json.loads(monthly_resilience_data)

        for d in monthly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            feelings_count = d["type_of_feelings"].lower()
            monthly_feelings_count[week][feelings_count] +=1
        
        overview.append(dict(monthly_feelings_count=monthly_feelings_count))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly feelings_count

        yearly_feelings_count = {
            "january": {
               "positive":0,
                "negative":0
            },
            "february": {
               "positive":0,
                "negative":0
            },
            "march": {
               "positive":0,
                "negative":0
            },
            "april": {
               "positive":0,
                "negative":0
            },
            "may": {
               "positive":0,
                "negative":0
            },
            "june": {
               "positive":0,
                "negative":0
            },
            "july": {
               "positive":0,
                "negative":0
            },
            "august": {
               "positive":0,
                "negative":0
            },
            "september": {
               "positive":0,
                "negative":0
            },
            "october": {
               "positive":0,
                "negative":0
            },
            "november": {
               "positive":0,
                "negative":0
            },
            "december": {
               "positive":0,
                "negative":0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_resiliences = Resilience.query.filter(Resilience.timestamp > yearly_filter, Resilience.user_id==user_id).all()

        if not yearly_resiliences:
            return dict(status="fail", message="No resilience data found"), 404

        yearly_resilience_data, yearly_errors = schema.dumps(yearly_resiliences)
        yearly_resilience_data_list = json.loads(yearly_resilience_data)

        for d in yearly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            feelings_count = d["type_of_feelings"].lower()
            yearly_feelings_count[month][feelings_count] +=1
        
        overview.append(dict(yearly_feelings_count=yearly_feelings_count))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=(overview))), 200


class ResilienceSocialEngagementDetailedOverview(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Get all user resilience records: social engagement for a user
        """
        overview = []

        schema = ResilienceSchema(many=True)

        # weekly overview

        weekly_social_engagement_count = {
            "monday": {
                "true":0,
                "false":0
            },
            "tuesday": {
                "true":0,
                "false":0
            },
            "wednesday": {
                "true":0,
                "false":0
            },
            "thursday": {
                "true":0,
                "false":0
            },
            "friday": {
                "true":0,
                "false":0
            },
            "saturday": {
                "true":0,
                "false":0
            },
            "sunday": {
                "true":0,
                "false":0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_resiliences = Resilience.query.filter(Resilience.timestamp > weekly_filter, Resilience.user_id==user_id).all()

        if not weekly_resiliences:
            return dict(status="fail", message="No resilience: social engagement data found"), 404

        weekly_resilience_data, weekly_errors = schema.dumps(weekly_resiliences)
        weekly_resilience_data_list = json.loads(weekly_resilience_data)

        for d in weekly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            social_engagement_count = str(d["engaged_socially_today"]).lower()
            weekly_social_engagement_count[day][social_engagement_count] +=1
        
        overview.append(dict(weekly_social_engagement_count=weekly_social_engagement_count))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview

        monthly_social_engagement_count = {
            "week1": {
                "true":0,
                "false":0
            },
            "week2": {
                "true":0,
                "false":0
            },
            "week3": {
                "true":0,
                "false":0
            },
            "week4": {
                "true":0,
                "false":0
            },
            "week5": {
                "true":0,
                "false":0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_resiliences = Resilience.query.filter(Resilience.timestamp > monthly_filter, Resilience.user_id==user_id).all()

        if not monthly_resiliences:
            return dict(status="fail", message="No resilience: social engagement data found"), 404

        monthly_resilience_data, monthly_errors = schema.dumps(monthly_resiliences)
        monthly_resilience_data_list = json.loads(monthly_resilience_data)

        for d in monthly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            social_engagement_count = str(d["engaged_socially_today"]).lower()
            monthly_social_engagement_count[week][social_engagement_count] +=1
        
        overview.append(dict(monthly_social_engagement_count=monthly_social_engagement_count))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly social_engagement_count

        yearly_social_engagement_count = {
            "january": {
                "true":0,
                "false":0
            },
            "february": {
                "true":0,
                "false":0
            },
            "march": {
                "true":0,
                "false":0
            },
            "april": {
                "true":0,
                "false":0
            },
            "may": {
                "true":0,
                "false":0
            },
            "june": {
                "true":0,
                "false":0
            },
            "july": {
                "true":0,
                "false":0
            },
            "august": {
                "true":0,
                "false":0
            },
            "september": {
                "true":0,
                "false":0
            },
            "october": {
                "true":0,
                "false":0
            },
            "november": {
                "true":0,
                "false":0
            },
            "december": {
                "true":0,
                "false":0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_resiliences = Resilience.query.filter(Resilience.timestamp > yearly_filter, Resilience.user_id==user_id).all()

        if not yearly_resiliences:
            return dict(status="fail", message="No resilience:social engagement data found"), 404

        yearly_resilience_data, yearly_errors = schema.dumps(yearly_resiliences)
        yearly_resilience_data_list = json.loads(yearly_resilience_data)

        for d in yearly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            social_engagement_count = str(d["engaged_socially_today"]).lower()
            yearly_social_engagement_count[month][social_engagement_count] +=1
        
        overview.append(dict(yearly_social_engagement_count=yearly_social_engagement_count))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=(overview))), 200


class ResilienceTreatmentScaleDetailedOverview(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Get all user resilience records:treatment scale for a user
        """
        overview = []

        schema = ResilienceSchema(many=True)

        # weekly overview

        weekly_treatment_scale_count = {
            "monday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "tuesday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "wednesday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "thursday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "friday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "saturday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "sunday": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            }
        }

        weekly_filter = datetime.today() - timedelta(days = 7)

        weekly_resiliences = Resilience.query.filter(Resilience.timestamp > weekly_filter, Resilience.user_id==user_id).all()

        if not weekly_resiliences:
            return dict(status="fail", message="No resilience: social engagement data found"), 404

        weekly_resilience_data, weekly_errors = schema.dumps(weekly_resiliences)
        weekly_resilience_data_list = json.loads(weekly_resilience_data)

        for d in weekly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            day = calendar.day_name[dt.weekday()].lower()
            treatment_scale_count = int(d["treatment_scale_by_other"]/10)
            weekly_treatment_scale_count[day][treatment_scale_count] +=1
        
        overview.append(dict(weekly_treatment_scale_count=weekly_treatment_scale_count))

        if weekly_errors:
            return dict(status="fail", message=weekly_errors), 500

        # monthly overview

        monthly_treatment_scale_count = {
            "week1": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "week2": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "week3": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "week4": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "week5": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            }
        }

        def week_of_month(date):
            last_day_of_week_of_month = date.day + (7 - (1 + date.weekday()))
            return str(ceil(last_day_of_week_of_month/7.0))

        monthly_filter = datetime.today() - timedelta(days = 31)

        monthly_resiliences = Resilience.query.filter(Resilience.timestamp > monthly_filter, Resilience.user_id==user_id).all()

        if not monthly_resiliences:
            return dict(status="fail", message="No resilience: social engagement data found"), 404

        monthly_resilience_data, monthly_errors = schema.dumps(monthly_resiliences)
        monthly_resilience_data_list = json.loads(monthly_resilience_data)

        for d in monthly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            week = "week" + week_of_month(dt)
            treatment_scale_count = int(d["treatment_scale_by_other"]/10)
            monthly_treatment_scale_count[week][treatment_scale_count] +=1
        
        overview.append(dict(monthly_treatment_scale_count=monthly_treatment_scale_count))

        if monthly_errors:
            return dict(status="fail", message=monthly_errors), 500

        # yearly treatment_scale_count

        yearly_treatment_scale_count = {
            "january": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "february": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "march": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "april": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "may": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "june": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "july": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "august": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "september": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "october": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "november": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            },
            "december": {
                0:0,
                1:0,
                2:0,
                3:0,
                4:0,
                5:0,
                6:0,
                7:0,
                8:0,
                9:0,
                10:0
            }
        }

        yearly_filter = datetime.today() - timedelta(days = 365)

        yearly_resiliences = Resilience.query.filter(Resilience.timestamp > yearly_filter, Resilience.user_id==user_id).all()

        if not yearly_resiliences:
            return dict(status="fail", message="No resilience:social engagement data found"), 404

        yearly_resilience_data, yearly_errors = schema.dumps(yearly_resiliences)
        yearly_resilience_data_list = json.loads(yearly_resilience_data)

        for d in yearly_resilience_data_list:
            timestamp = d['timestamp']
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            month = calendar.month_name[dt.month].lower()
            treatment_scale_count = int(d["treatment_scale_by_other"]/10)
            yearly_treatment_scale_count[month][treatment_scale_count] +=1
        
        overview.append(dict(yearly_treatment_scale_count=yearly_treatment_scale_count))

        if yearly_errors:
            return dict(status="fail", message=yearly_errors), 500

        return dict(status='success', data=dict(overview=(overview))), 200