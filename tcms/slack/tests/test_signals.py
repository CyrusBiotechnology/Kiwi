from tcms.tests import BaseCaseRun
from django.test import TestCase
from unittest.mock import MagicMock
from tcms.slack.signals import django_slack
from django.db.models.signals import post_save
from django_slack.utils import get_backend
from django.urls import reverse
from django.shortcuts import get_object_or_404
from tcms.testruns.models import TestCaseRun
from django.contrib.auth.models import User
from django.test import Client


class TestTestcaserunNotification(BaseCaseRun):

    @classmethod
    def setUpTestData(cls):
        super(TestTestcaserunNotification, cls).setUpTestData()

    def test_should_send_signal_when_testcaserunsaves(self):
        self.signal_was_called = False
        django_slack.slack_message = MagicMock()

        def handler(sender, *args, **kwargs):
            self.signal_was_called = True

        post_save.connect(handler)

        self.case_run_1.notes = "Updated notes"
        self.case_run_1.save()

        self.assertTrue(self.signal_was_called)
        django_slack.slack_message.assert_called_with(
            'slack/updated_testcaserun_assignee.slack',
            {'tc_run': self.case_run_1}
        )


class TestTestcaserunNotificationNoMock(BaseCaseRun):

    @classmethod
    def setUpTestData(cls):
        super(TestTestcaserunNotificationNoMock, cls).setUpTestData()

    def test_should_send_signal_when_testcaserunsaves(self):
        self.signal_was_called = False

        def handler(sender, *args, **kwargs):
            self.signal_was_called = True

        post_save.connect(handler)

        self.case_run_1.notes = "Updating the test case"
        self.case_run_1.save()

        self.assertTrue(self.signal_was_called)


class TestDjangoSlack(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.backend = get_backend()
        # cls.backend.reset_messages()

    def test_django_slack(self):
        django_slack.slack_message('slack/simple.slack', {})


class TestAssigneeViewSignal(BaseCaseRun):

    @classmethod
    def setUpTestData(cls):
        super(TestAssigneeViewSignal, cls).setUpTestData()

    def test_update_assignee_view(self):
        # django_slack.slack_message = MagicMock()
        user = User.objects.get(username='User1')
        user.set_password('password')
        user.save()
        c = Client()
        c.force_login(user)
        c.post(
            reverse('testruns-update_assignee'),
            data={'id': 1, 'assignee': 'User2'}, follow=True)
        django_slack.slack_message.assert_called_with(
            'slack/updated_testcaserun_assignee.slack',
            {'tc_run': self.case_run_1}
        )

    def test_update_assigne_view_code(self):
        django_slack.slack_message = MagicMock()
        obj_id = self.case_run_1.pk
        test_case_run = get_object_or_404(TestCaseRun, pk=obj_id)
        user = User.objects.get(username='User2')
        test_case_run.assignee = user
        test_case_run.save()

        django_slack.slack_message.assert_called_with(
            'slack/updated_testcaserun_assignee.slack',
            {'tc_run': self.case_run_1}
        )


