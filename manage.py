from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.models import db
from server import app

# import models
from app.models.user import User
from app.models.seizure import Seizure
from app.models.medication import Medication
from app.models.medicine import Medicine


# register app and db with migration class
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

