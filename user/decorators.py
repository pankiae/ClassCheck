from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def teacher_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_teacher(),
        login_url='login',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def student_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_student(),
        login_url='login',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_admin(),
        login_url='login',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
