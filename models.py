from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class SoloUser(models.Model):

    user_id = models.IntegerField(unique=True, null=True)
    # email = models.EmailField(_('email address'), blank=True)

    is_solo_user = models.BooleanField(
        _('solo staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this solo tables site.'),
    )
    is_solo_admin = models.BooleanField(default=False)
