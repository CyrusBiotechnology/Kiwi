from tcms.testruns.models import TestCaseRun
import django_slack
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('slack')


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
    if kwargs.get('created'):
        template = 'slack/new_testcaserun.slack'
    elif 'assignee' in kwargs.get('updated_fields', []):
        template = 'slack/updated_testcaserun_assignee.slack'

    if template:
        django_slack.slack_message(template, {'tc_run': kwargs.get('instance')})

    try:
        django_slack.slack_message('slack/simple.slack', {})
    except Exception as err:
        logger.error('Error sending slack message {0}'.format(err))

