# Contains Database configurations
import os


class Base:
    """ base config """
    # main
    SECRET_KEY = os.getenv("FLASK_APP_SECRET")
    PASSWORD_SALT = os.getenv("FLASK_APP_SALT")
    VERIFICATION_SALT = os.getenv("FLASK_VERIFY_SALT")

    # mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.getenv("APP_MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("APP_MAIL_PASSWORD")

    # mail accounts
    MAIL_DEFAULT_SENDER = "epilepsy.smartapp@gmail.com"
    
    # EXCEPTIONS
    PROPAGATE_EXCEPTIONS = True

class Development(Base):
    """ development config """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    # SQLALCHEMY_DATABASE_URI = "postgresql:///epilepsy_smart_db"


class Testing(Base):
    """ test environment config """

    TESTING = True
    DEBUG = True
    # use a separate db
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_TEST_URI")
    # SQLALCHEMY_DATABASE_URI = "postgresql:///flask_app_test_db"


class Production(Base):
    """ production config """

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


app_config = {"development": Development,
              "testing": Testing, "production": Production}
