import json
from flask_restful import Resource, request
import os
from app.schemas import UserSchema, UserLoginSchema, ClinicianSchema, UserPasswordSchema
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from app.models.role import Role 
from app.helpers.decorators import admin_required
from app.helpers.confirmation import send_verification
from flask import current_app
from app.helpers.token import validate_token

class UserView(Resource):

    def post(self):
        """
        Creating a User Account
        """
        user_schema = UserSchema()

        user_data = request.get_json()

        validated_user_data, errors = user_schema.load(user_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_user = User.find_first(email=validated_user_data["email"])

        if existing_user:
            return dict(status='fail',
                        message=f'User email {validated_user_data["email"]} already exists'), 409

        user = User(**validated_user_data)

        # get the customer role
        user_role = Role.find_first(name='app_user')

        if user_role:
            user.roles.append(user_role)

        saved_user = user.save()

        if not saved_user:
            return dict(status='fail', message='Internal Server Error'), 500
        
        email = validated_user_data.get('email', None)
        client_base_url = os.getenv(
            'CLIENT_BASE_URL',
            'https://smartapp.aceuganda.org/'
        )

        # To do change to a frontend url
        verification_url = f"{client_base_url}/verify/"
        secret_key = current_app.config["SECRET_KEY"]
        password_salt = current_app.config["VERIFICATION_SALT"]
        sender = current_app.config["MAIL_DEFAULT_SENDER"]
        template = "verify.html"
        subject = "Please confirm your email"

        if errors:
            return dict(status="fail", message=errors), 400

        # send verification
        send_verification(
            email,
            user.username,
            verification_url,
            secret_key,
            password_salt,
            sender,
            current_app._get_current_object(),
            template,
            subject
        )


        new_user_data, errors = user_schema.dumps(user)

        return dict(status='success', data=dict(user=json.loads(new_user_data))), 201

    @admin_required
    def get(self):
        """
        Getting All users
        """
        user_schema = UserSchema(many=True)

        users = User.find_all()
        if not users:
            return dict(
                status='fail',
                message=f'No user data found'
            ), 404

        users_data, errors = user_schema.dumps(users)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500
            
        v_total_users = json.loads(users_data)
        total_users = len(v_total_users)

        return dict(status="success", data=dict(total_users=total_users, users=v_total_users)), 200


class UserDetailView(Resource):

    @jwt_required
    def get(self, user_id):
        """
        Getting individual user
        """
        schema = UserSchema()

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        user_data, errors = schema.dumps(user)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(user=json.loads(user_data))), 200

    @jwt_required
    def patch(self, user_id):
        """
        Update a single user
        """

        # To do check if user is admin
        schema = UserSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        updated_user = User.update(user, **validated_update_data)

        if not updated_user:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="User updated successfully"), 200

    @jwt_required
    def patch(self, user_id):
        """
        Change a single users password
        """
        schema = UserPasswordSchema()

        change_password_data = request.get_json()

        validated_change_password_data, errors = schema.load(change_password_data)

        if errors:
            return dict(status="fail", message=errors), 400

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404
    
        current_password = validated_change_password_data['current_password']
        new_password = validated_change_password_data['new_password']

        if user.password_is_valid(current_password):
            password_hash = Bcrypt().generate_password_hash(new_password).decode()

            updated_user = User.update(user, password=password_hash)

            if not updated_user:
                return dict(status='fail', message='Internal Server Error'), 500
        else:
            return dict(status='fail', message="current password is wrong"), 401

        return dict(status="success", message="Password updated successfully"), 200

    @admin_required
    def delete(self, user_id):
        """
        Delete a single user
        """

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        deleted_user = user.delete()

        if not deleted_user:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200


class UserLoginView(Resource):

    def post(self):
        """
        """
        user_schema = UserLoginSchema()
        token_schema = UserSchema()

        login_data = request.get_json()

        validated_user_data, errors = user_schema.load(login_data)

        if errors:
            return dict(status='fail', message=errors), 400

        email = validated_user_data.get('email', None)
        password = validated_user_data.get('password', None)

        user = User.find_first(email=email)

        if not user:
            return dict(status='fail', message="login failed"), 401

        user_dict, errors = token_schema.dump(user)

        if user and user.password_is_valid(password):

            access_token = user.generate_token(user_dict)

            if not access_token:
                return dict(
                    status="fail",
                    message="Internal Server Error"
                ), 500

            return dict(
                status='success',
                data=dict(
                    access_token=access_token,
                    email=user.email,
                    username=user.username,
                    verified=user.verified,
                    id=str(user.id),
                )), 200

        return dict(status='fail', message="login failed"), 401


class ResetPasswordView(Resource):

    def post(self, token):

        password_schema = UserSchema(only=("password",))

        secret = current_app.config["SECRET_KEY"]
        salt = current_app.config["PASSWORD_SALT"]

        request_data = request.get_json()
        validated_data, errors = password_schema.load(request_data)

        if errors:
            return dict(status='fail', message=errors), 400

        password = validated_data['password']

        hashed_password = Bcrypt().generate_password_hash(password).decode()

        email = validate_token(token, secret, salt)

        if not email:
            return dict(status='fail', message="invalid token"), 401

        user = User.find_first(**{'email': email})

        if not user:
            return dict(
                status="fail",
                message=f'user with email {email} not found'
            ), 404

        if not user.verified:
            return dict(
                status='fail', message=f'email {email} is not verified'), 400
        user.password = hashed_password

        user_saved = user.save()

        if not user_saved:
            return dict(status='fail', message='internal server error'), 500

        return dict(
            status='success', message='password reset successfully'), 200



class ClinicianView(Resource):

    def post(self):
        """
        Creating a User Account
        """
        user_schema = ClinicianSchema()

        user_data = request.get_json()

        validated_user_data, errors = user_schema.load(user_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_user = User.find_first(email=validated_user_data["email"])

        if existing_user:
            return dict(status='fail',
                        message=f'User email {validated_user_data["email"]} already exists'), 409

        validated_user_data["username"] = None
        validated_user_data["age"] = None
        validated_user_data["gender"] = None
        validated_user_data["age_of_onset"] = None
        validated_user_data["seizure_type"] = None
        validated_user_data["caregiver_name"] = None
        validated_user_data["caregiver_contact"] = None
        validated_user_data["institution"] = None
        validated_user_data["profileImage"] = None

        user = User(**validated_user_data)

        # get the customer role
        user_role = Role.find_first(name='clinician')

        if user_role:
            user.roles.append(user_role)

        saved_user = user.save()

        if not saved_user:
            return dict(status='fail', message='Internal Server Error'), 500

        new_user_data, errors = user_schema.dumps(user)

        return dict(status='success', data=dict(user=json.loads(new_user_data))), 201
    
class UserEmailVerificationView(Resource):

    def get(self, token):
        """
        """

        user_schema = UserSchema()

        secret = current_app.config["SECRET_KEY"]
        salt = current_app.config["VERIFICATION_SALT"]

        email = validate_token(token, secret, salt)

        if not email:
            return dict(status="fail", message="invalid token"), 401

        user = User.find_first(**{'email': email})

        if not user:
            return dict(
                status='fail',
                message=f'User with email {email} not found'
            ), 404

        if user.verified:
            return dict(
                status='fail', message='Email is already verified'), 400

        user.verified = True

        user_saved = user.save()

        user_dict, _ = user_schema.dump(user)

        if user_saved:

            # generate access token
            access_token = user.generate_token(user_dict)

            if not access_token:
                return dict(
                    status='fail', message='Internal Server Error'), 500

            return dict(
                status='success',
                message='Email verified successfully',
                data=dict(
                    access_token=access_token,
                    email=user.email,
                    username=user.username,
                    verified=user.verified,
                    id=str(user.id),
                )), 200

        return dict(status='fail', message='Internal Server Error'), 500


class EmailVerificationRequest(Resource):

    def post(self):
        """
        """
        email_schema = UserSchema(only=("email",))

        request_data = request.get_json()

        validated_data, errors = email_schema.load(request_data)

        if errors:
            return dict(status='fail', message=errors), 400

        email = validated_data.get('email', None)
        client_base_url = os.getenv(
            'CLIENT_BASE_URL',
            'https://smartapp.aceuganda.org/'
        )

        # To do, change to a frontend url
        verification_url = f"{client_base_url}/account/verify/"
        secret_key = current_app.config["SECRET_KEY"]
        password_salt = current_app.config["VERIFICATION_SALT"]
        sender = current_app.config["MAIL_DEFAULT_SENDER"]
        template = "verify.html"
        subject = "Please confirm your email"

        user = User.find_first(**{'email': email})

        if not user:
            return dict(
                status='fail',
                message=f'User with email {email} not found'
            ), 404

        # send verification
        send_verification(
            email,
            user.username,
            verification_url,
            secret_key,
            password_salt,
            sender,
            current_app._get_current_object(),
            template,
            subject
        )

        return dict(
            status='success',
            message=f'Verification link sent to {email}'
        ), 200


class ForgotPasswordView(Resource):

    def post(self):
        """
        """

        email_schema = UserSchema(only=("email",))

        request_data = request.get_json()
        validated_data, errors = email_schema.load(request_data)

        if errors:
            return dict(status='fail', message=errors), 400

        email = validated_data.get('email', None)
        client_base_url = os.getenv(
            'CLIENT_BASE_URL',
            'https://smartapp.aceuganda.org/'
        )

        verification_url = f"{client_base_url}/reset-password/"
        secret_key = current_app.config["SECRET_KEY"]
        password_salt = current_app.config["PASSWORD_SALT"]
        sender = current_app.config["MAIL_DEFAULT_SENDER"]
        template = "reset.html"
        subject = "Password reset"

        user = User.find_first(**{'email': email})

        if not user:
            return dict(
                status='fail',
                message=f'User with email {email} not found'
            ), 404

        # send password reset link
        send_verification(
            email,
            user.username,
            verification_url,
            secret_key,
            password_salt,
            sender,
            current_app._get_current_object(),
            template,
            subject
        )

        return dict(
            status='success',
            message=f'Password reset link sent to {email}'
        ), 200
