from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .alchemy_models import SoloUser


# class SoloUserCreationForm(UserCreationForm):
#
#     class Meta(UserCreationForm.Meta):
#         model = SoloUser
#         # fields = UserCreationForm.Meta.fields + ('custom_field',)
#
#
# class SoloAuthenticationForm(AuthenticationForm):
#     def confirm_login_allowed(self, user):
#         pass
