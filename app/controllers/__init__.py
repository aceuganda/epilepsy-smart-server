from .index import IndexView
from .user import (UserView, UserDetailView, UserLoginView, ResetPassword, ClinicianView)
from .seizure import (SiezureView, SeizureDetailView, SeizureOverview)
from .medicine import(MedicineDetailView, MedicineView)
from .medication import(MedicationDetailView, MedicationView)
from .resilience import(ResilienceView, ResilienceDetailView)
from .roles import RolesView, RolesDetailView
from .user_role import UserRolesView