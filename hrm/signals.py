from django.db.models.signals import post_save
from django.dispatch import receiver
from care.users.models import User
from hrm.models.employee_profile import Employee
from datetime import date
import threading

_employee_creation_context = threading.local()
_employee_creation_context.suppress_signal = False

def suppress_employee_signal():
    """
    Suppress the employee creation signal.
    This is useful when creating a User instance that should not trigger the employee creation logic.
    """
    class SuppressSignal:
        def __enter__(self):
            _employee_creation_context.suppress_signal = True

        def __exit__(self, exc_type, exc_val, exc_tb):
            _employee_creation_context.suppress_signal = False
        
    return SuppressSignal()


@receiver(post_save, sender=User)
def create_employee_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create an Employee profile for every new User (non-superuser).
    """
    if getattr(_employee_creation_context, "suppress_signal", False):
        return
    if instance.is_superuser:
        return
    Employee.objects.get_or_create(
        user=instance,
        defaults={
            "department": "unknown",
            "role": "unknown",
            "hire_date": date.today()
        }
    )