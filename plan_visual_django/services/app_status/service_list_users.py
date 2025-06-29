from django.contrib.auth import get_user_model

User = get_user_model()

def service_list_users():
    users = User.objects.all()

    user_data = []

    for user in users:
        user_record = {
            'username': user.username,
            'superuser_flag': " [SUPERUSER]" if user.is_superuser else "",
            'is_staff_flag': " [STAFF]" if user.is_staff else "",
        }
        user_data.append(user_record)
    return user_data
