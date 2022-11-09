from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.models import db
from server import app
from dotenv import load_dotenv
from os.path import join, dirname

# import models
from app.models.user import User
from app.models.seizure import Seizure
from app.models.medication import Medication
from app.models.medicine import Medicine
from app.models.resilience import Resilience
from app.models.feelings import Feeling
from app.models.activities import Activity
from app.models.role import Role
from app.models.user_role import UserRole
from app.helpers.admin import create_superuser, create_default_roles

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# register app and db with migration class
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.option('-e', '--email', dest='email')
@manager.option('-p', '--password', dest='password')
@manager.option('-c', '--confirm_password', dest='confirm_password')
def admin_user(email, password, confirm_password):
    create_superuser(email, password, confirm_password)


@manager.command
def create_roles():
    create_default_roles()


if __name__ == '__main__':
    manager.run()

