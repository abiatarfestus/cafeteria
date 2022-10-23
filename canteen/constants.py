from django.db.models import F, Q
from django.contrib.auth.models import User

staff_and_admins = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
STAFF_EMAILS = [staff.email for staff in staff_and_admins if staff.is_staff and not staff.is_superuser]
ADMIN_EMAILS = [admin.email for admin in staff_and_admins if admin.is_superuser]

# print(f"STAFF AND ADMINS: {staff_and_admins}")
# print(f"STAFF EMAILS: {STAFF_EMAILS}")
# print(f"ADMINS EMAILS: {ADMIN_EMAILS}")