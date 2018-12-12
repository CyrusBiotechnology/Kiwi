"""
This file is deprecated until the issue between docker and Django base signals is resolved
"""

from tcms.testruns.models import TestCaseRun
import django_slack
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('django')


@receiver(post_save, sender=TestCaseRun)
def handle_slack_notifications_post_testcaserun_save(sender, *args, **kwargs):
    """
    Send a slack notification after a TestCaseRun has been updated
    :param sender:
    :param args:
    :param kwargs:
    :return:
    """
    logger.info('Signal Received')
    template = None
    if not kwargs.get('created'):
        """
        Filter out test runs when the are first created
        TODO: Make receiving notifications on creation optional
        """
        template = 'slack/updated_testcaserun_assignee.slack'

    if template:
        django_slack.slack_message(template, {'tc_run': kwargs.get('instance')})
