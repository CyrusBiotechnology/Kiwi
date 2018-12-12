# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from mock import patch
from dateutil import parser

from django.conf import settings
from django.contrib.auth.models import User

from tcms.core.history import history_email_for
from tcms.testcases.models import BugSystem
from tcms.testcases.helpers.email import get_case_notification_recipients
from tcms.tests import BasePlanCase
from tcms.tests.factories import ComponentFactory
from tcms.tests.factories import BuildFactory
from tcms.tests.factories import TestCaseComponentFactory
from tcms.tests.factories import TestCaseEmailSettingsFactory
from tcms.tests.factories import TestCaseFactory
from tcms.tests.factories import TestCaseRunFactory
from tcms.tests.factories import TestCaseTagFactory
from tcms.tests.factories import TestRunFactory
from tcms.tests.factories import TagFactory


class TestCaseRemoveBug(BasePlanCase):
    """Test TestCase.remove_bug"""

    @classmethod
    def setUpTestData(cls):
        super(TestCaseRemoveBug, cls).setUpTestData()
        cls.build = BuildFactory(product=cls.product)
        cls.test_run = TestRunFactory(product_version=cls.version, plan=cls.plan,
                                      manager=cls.tester, default_tester=cls.tester)
        cls.case_run = TestCaseRunFactory(assignee=cls.tester, tested_by=cls.tester,
                                          case=cls.case, run=cls.test_run, build=cls.build)
        cls.bug_system = BugSystem.objects.get(name='Bugzilla')

    def setUp(self):
        self.bug_id_1 = '12345678'
        self.case.add_bug(self.bug_id_1, self.bug_system.pk,
                          summary='error when add a bug to a case')
        self.bug_id_2 = '10000'
        self.case.add_bug(self.bug_id_2, self.bug_system.pk, case_run=self.case_run)

    def tearDown(self):
        self.case.case_bug.all().delete()

    def test_remove_case_bug(self):
        self.case.remove_bug(self.bug_id_1)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_1).exists()
        self.assertFalse(bug_found)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_2).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_2))

    def test_case_bug_not_removed_by_passing_case_run(self):
        self.case.remove_bug(self.bug_id_1, run_id=self.case_run.pk)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_1).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_1))

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_2).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_2))

    def test_remove_case_run_bug(self):
        self.case.remove_bug(self.bug_id_2, run_id=self.case_run.pk)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_2).exists()
        self.assertFalse(bug_found)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_1).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_1))

    def test_case_run_bug_not_removed_by_missing_case_run(self):
        self.case.remove_bug(self.bug_id_2)

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_1).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_1))

        bug_found = self.case.case_bug.filter(bug_id=self.bug_id_2).exists()
        self.assertTrue(bug_found,
                        'Bug {0} does not exist. It should not be deleted.'.format(self.bug_id_2))


class TestCaseRemoveIssue(BasePlanCase):
    """Test TestCase.remove_issue"""

    @classmethod
    def setUpTestData(cls):
        super(TestCaseRemoveIssue, cls).setUpTestData()

        cls.build = BuildFactory(product=cls.product)
        cls.test_run = TestRunFactory(product_version=cls.version, plan=cls.plan,
                                      manager=cls.tester, default_tester=cls.tester)
        cls.case_run = TestCaseRunFactory(assignee=cls.tester, tested_by=cls.tester,
                                          case=cls.case, run=cls.test_run, build=cls.build)

    def setUp(self):
        from tcms.issues.models import Issue, IssueType, Project
        project = Project.objects.create(jid='10001', key='TEST', name='TEST')
        issue_type = IssueType.objects.create(project=project, name='Bug', jid='10001', icon_url='img.com')
        self.issue_1 = Issue.objects.create(
            jid='10001',
            link='foo.com',
            jira_key='TEST-1',
            fixVersions=[],
            summary="Issue 1",
            assignee="not me",
            iss_updated=parser.parse('2018-11-14T06:02:07.411+0000'),
            iss_created=parser.parse('2018-11-14T06:02:07.411+0000'),
            issue_type=issue_type,
            project=project
        )
        self.case.add_issues([self.issue_1.jira_key])
        self.issue_2 = Issue.objects.create(
            jid='10002',
            link='foo.com',
            jira_key='TEST-2',
            fixVersions=[],
            summary="Issue 2",
            assignee="not me",
            iss_updated=parser.parse('2018-11-14T06:02:07.411+0000'),
            iss_created=parser.parse('2018-11-14T06:02:07.411+0000'),
            issue_type=issue_type,
            project=project
        )
        self.case.add_issues([self.issue_2.jira_key])

    def tearDown(self):
        self.case.issue_set.all().delete()

    def test_remove_case_bug(self):
        self.case.remove_issue(self.issue_1.jid)

        issue_found = self.case.issue_set.filter(id=self.issue_1.id).exists()
        self.assertFalse(issue_found)

        issue_found = self.case.issue_set.filter(id=self.issue_2.id).exists()
        self.assertTrue(issue_found,
                        'Issue {0} does not exist. It should not be deleted.'.format(self.issue_2.id))


class TestCaseRemoveComponent(BasePlanCase):
    """Test TestCase.remove_component"""

    @classmethod
    def setUpTestData(cls):
        super(TestCaseRemoveComponent, cls).setUpTestData()

        cls.component_1 = ComponentFactory(name='Application',
                                           product=cls.product,
                                           initial_owner=cls.tester,
                                           initial_qa_contact=cls.tester)
        cls.component_2 = ComponentFactory(name='Database',
                                           product=cls.product,
                                           initial_owner=cls.tester,
                                           initial_qa_contact=cls.tester)

        cls.cc_rel_1 = TestCaseComponentFactory(case=cls.case,
                                                component=cls.component_1)
        cls.cc_rel_2 = TestCaseComponentFactory(case=cls.case,
                                                component=cls.component_2)

    def test_remove_a_component(self):
        self.case.remove_component(self.component_1)

        found = self.case.component.filter(pk=self.component_1.pk).exists()
        self.assertFalse(
            found,
            'Component {0} exists. But, it should be removed.'.format(
                self.component_1.pk))
        found = self.case.component.filter(pk=self.component_2.pk).exists()
        self.assertTrue(
            found,
            'Component {0} does not exist. It should not be removed.'.format(
                self.component_2.pk))


class TestCaseRemovePlan(BasePlanCase):
    """Test TestCase.remove_plan"""

    @classmethod
    def setUpTestData(cls):
        super(TestCaseRemovePlan, cls).setUpTestData()

        cls.new_case = TestCaseFactory(author=cls.tester, default_tester=None, reviewer=cls.tester,
                                       plan=[cls.plan])

    def test_remove_plan(self):
        self.new_case.remove_plan(self.plan)

        found = self.plan.case.filter(pk=self.new_case.pk).exists()
        self.assertFalse(
            found, 'Case {0} should has no relationship to plan {1} now.'.format(self.new_case.pk,
                                                                                 self.plan.pk))


class TestCaseRemoveTag(BasePlanCase):
    """Test TestCase.remove_tag"""

    @classmethod
    def setUpTestData(cls):
        super(TestCaseRemoveTag, cls).setUpTestData()

        cls.tag_rhel = TagFactory(name='rhel')
        cls.tag_fedora = TagFactory(name='fedora')
        TestCaseTagFactory(case=cls.case, tag=cls.tag_rhel, user=cls.tester.pk)
        TestCaseTagFactory(case=cls.case, tag=cls.tag_fedora, user=cls.tester.pk)

    def test_remove_tag(self):
        self.case.remove_tag(self.tag_rhel)

        tag_pks = list(self.case.tag.all().values_list('pk', flat=True))
        self.assertEqual([self.tag_fedora.pk], tag_pks)


class TestSendMailOnCaseIsUpdated(BasePlanCase):
    """Test send mail on case post_save signal is triggered"""
    @classmethod
    def setUpTestData(cls):
        super(TestSendMailOnCaseIsUpdated, cls).setUpTestData()

        cls.case.add_text('action', 'effect', 'setup', 'breakdown')

        cls.email_setting = TestCaseEmailSettingsFactory(
            case=cls.case,
            notify_on_case_update=True,
            auto_to_case_author=True)

        cls.case_editor = User.objects.create_user(username='editor')
        # This is actually done when update a case. Setting current_user
        # explicitly here aims to mock that behavior.
        cls.case.current_user = cls.case_editor

    @patch('tcms.core.utils.mailto.send_mail')
    def test_send_mail_to_case_author(self, send_mail):
        self.case.summary = 'New summary for running test'
        self.case.save()

        expected_subject, expected_body = history_email_for(self.case, self.case.summary)
        recipients = get_case_notification_recipients(self.case)

        # Verify notification mail
        send_mail.assert_called_once_with(settings.EMAIL_SUBJECT_PREFIX + expected_subject,
                                          expected_body,
                                          settings.DEFAULT_FROM_EMAIL,
                                          recipients,
                                          fail_silently=False)
