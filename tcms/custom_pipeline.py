from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from tcms.utils.permissions import initiate_user_with_default_setups


def email_required(strategy, details, backend, user=None, *args, **kwargs):
    if not details.get('email'):
        messages.error(
            strategy.request or backend.strategy.request,
            _("Email address is required")
        )
        return HttpResponseRedirect(reverse('tcms-login'))


def check_unique_email(strategy, details, backend, user=None, *args, **kwargs):
    try:
        User.objects.get(email=details.get('email'))

        messages.error(
            strategy.request or backend.strategy.request,
            _("A user with address %(email)s already exists") % {'email': details['email']}
        )
        return HttpResponseRedirect(reverse('tcms-login'))
    except User.DoesNotExist:
        pass


def initiate_defaults(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        initiate_user_with_default_setups(user)
