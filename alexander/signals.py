# from django.contrib.auth.signals import user_logged_in, user_logged_out
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import UserLoginRecord,User

# @receiver(user_logged_in)
# def log_user_login(sender, request, user, **kwargs):
#     try:
#         user_instance = User.objects.get(Username=user.Username)
#         UserLoginRecord.objects.create(user=user_instance)
#     except User.DoesNotExist:
#         print('User does not exist')
#         pass

# @receiver(user_logged_out)
# def log_user_logout(sender, request, user, **kwargs):
#     try:
#         user_instance = User.objects.get(Username=user.Username)
#         record = UserLoginRecord.objects.filter(user=user_instance).latest('login_time')
#         record.logout_time = timezone.now()
#         record.session_duration = record.logout_time - record.login_time
#         record.save()
#     except (User.DoesNotExist, UserLoginRecord.DoesNotExist):
#         pass

