from unittest import mock
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Project, IssueType, Issue, Organization
from .admin import AtlassianRequests
from .webhooks import *
from copy import deepcopy
import json


# Create your tests here.
class TestAdminViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        All the configuration to simulation calls to the JIRA api.  Since we did not implement multi-tenant
        we need to create and organization for the test to fetch
        :return:
        """
        Organization(
            key="MyOrg",
            clientKey='MyKeys111111',
            sharedSecret='shhhItsASecret',
            pluginsVersion='1',
            baseUrl='http://you.atlassian.net',
            productType='thebest',
            description='standard Org Stuff',
            serviceEntitlementNumber='1',
            eventType='install',
            publicKey='startheregoanywhere',
            serverVersion='7.8.10',
            installedBy='thisGuy'
        ).save()

        user = User.objects.create_superuser(username='testadmin', email='foo@bar.com', password='12345')
        user.set_password('12345')
        user.save()

        cls.project_search_results = {
                          "self": "http://you.atlassian.net/rest/api/2/project/paginated?startAt=0&maxResults=2",
                          "nextPage": "http://you.atlassian.net/rest/api/2/project/paginated?startAt=2&maxResults=2",
                          "maxResults": 2,
                          "startAt": 0,
                          "total": 7,
                          "isLast": False,
                          "values": [
                            {
                              "self": "http://you.atlassian.net/rest/api/2/project/EX",
                              "id": "10000",
                              "key": "EX",
                              "name": "Example",
                              "avatarUrls": {
                                "48x48": "http://you.atlassian.net/secure/projectavatar?size=large&pid=10000",
                                "24x24": "http://you.atlassian.net/secure/projectavatar?size=small&pid=10000",
                                "16x16": "http://you.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
                                "32x32": "http://you.atlassian.net/secure/projectavatar?size=medium&pid=10000"
                              },
                              "projectCategory": {
                                "self": "http://you.atlassian.net/rest/api/2/projectCategory/10000",
                                "id": "10000",
                                "name": "FIRST",
                                "description": "First Project Category"
                              },
                              "simplified": False,
                              "style": "classic"
                            },
                            {
                              "self": "http://your-domain.atlassian.net/rest/api/2/project/ABC",
                              "id": "10001",
                              "key": "ABC",
                              "name": "Alphabetical",
                              "avatarUrls": {
                                "48x48": "http://you.atlassian.net/secure/projectavatar?size=large&pid=10001",
                                "24x24": "http://you.atlassian.net/secure/projectavatar?size=small&pid=10001",
                                "16x16": "http://you.atlassian.net/secure/projectavatar?size=xsmall&pid=10001",
                                "32x32": "http://you.atlassian.net/secure/projectavatar?size=medium&pid=10001"
                              },
                              "projectCategory": {
                                "self": "http://you.atlassian.net/rest/api/2/projectCategory/10000",
                                "id": "10000",
                                "name": "FIRST",
                                "description": "First Project Category"
                              },
                              "simplified": False,
                              "style": "classic"
                            }
                          ]
                        }
        cls.project_result = {
          "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
          "id": "10000",
          "key": "EX",
          "description": "This project was created as an example for REST.",
          "lead": {
            "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
            "key": "mia",
            "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
            "name": "mia",
            "avatarUrls": {
              "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
              "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
              "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
              "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
            },
            "displayName": "Mia Krystof",
            "active": False
          },
          "components": [
            {
              "self": "http://your-domain.atlassian.net/rest/api/2/component/10000",
              "id": "10000",
              "name": "Component 1",
              "description": "This is a Jira component",
              "lead": {
                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                "key": "mia",
                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                "name": "mia",
                "avatarUrls": {
                  "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                  "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                  "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                  "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                },
                "displayName": "Mia Krystof",
                "active": False
              },
              "assigneeType": "PROJECT_LEAD",
              "assignee": {
                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                "key": "mia",
                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                "name": "mia",
                "avatarUrls": {
                  "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                  "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                  "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                  "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                },
                "displayName": "Mia Krystof",
                "active": False
              },
              "realAssigneeType": "PROJECT_LEAD",
              "realAssignee": {
                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                "key": "mia",
                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                "name": "mia",
                "avatarUrls": {
                  "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                  "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                  "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                  "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                },
                "displayName": "Mia Krystof",
                "active": False
              },
              "isAssigneeTypeValid": False,
              "project": "HSP",
              "projectId": 10000
            }
          ],
          "issueTypes": [
            {
              "self": "http://your-domain.atlassian.net/rest/api/2/issueType/3",
              "id": "3",
              "description": "A task that needs to be done.",
              "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
              "name": "Task",
              "subtask": False,
              "avatarId": 1
            },
            {
              "self": "http://your-domain.atlassian.net/rest/api/2/issueType/1",
              "id": "1",
              "description": "A problem with the software.",
              "iconUrl": "http://your-domain.atlassian.net/secure/viewavatar?size=xsmall&avatarId=10316&avatarType=issuetype\",",
              "name": "Bug",
              "subtask": False,
              "avatarId": 10002,
              "scope": {
                "type": "PROJECT",
                "project": {
                  "id": "10000"
                }
              }
            }
          ],
          "url": "http://your-domain.atlassian.net/browse/EX",
          "email": "from-jira@example.com",
          "assigneeType": "PROJECT_LEAD",
          "versions": [],
          "name": "Example",
          "roles": {
            "Developers": "http://your-domain.atlassian.net/rest/api/2/project/EX/role/10000"
          },
          "avatarUrls": {
            "48x48": "http://your-domain.atlassian.net/secure/projectavatar?size=large&pid=10000",
            "24x24": "http://your-domain.atlassian.net/secure/projectavatar?size=small&pid=10000",
            "16x16": "http://your-domain.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
            "32x32": "http://your-domain.atlassian.net/secure/projectavatar?size=medium&pid=10000"
          },
          "projectCategory": {
            "self": "http://your-domain.atlassian.net/rest/api/2/projectCategory/10000",
            "id": "10000",
            "name": "FIRST",
            "description": "First Project Category"
          },
          "simplified": False,
          "style": "classic"
        }

    def test_change_list_view(self):
        """
        Test that the configured and unconfigured projects return correctly
        :return:
        """
        # Create a project that is considered already configured
        project = Project.objects.create(jid='10001', key='TEST', name='TEST')
        user = User.objects.get(username='testadmin')

        with mock.patch.object(AtlassianRequests, 'get_paginated', return_value=self.project_search_results['values']):
            self.client.force_login(user)
            resp = self.client.get(reverse('admin:project-list'))
            self.assertEqual(resp.context['projects'], self.project_search_results['values'])
            self.assertEqual(resp.context['configured'].first(), project)

    def test_config_view(self):
        """
        Sine there is a complexity of 1, just ensure that the view works
        :return:
        """

        with mock.patch('tcms.issues.admin.AtlassianRequests.get') as mock_get:
            mock_get.return_value.json.return_value = self.project_result
            user = User.objects.get(username='testadmin')
            self.client.force_login(user)
            resp = self.client.get(reverse('admin:jira-config', args=['TEST']))
            self.assertEqual(resp.context['project_name'], self.project_result['name'])


class TestIssueSync(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project_search_results = {
            "self": "http://you.atlassian.net/rest/api/2/project/paginated?startAt=0&maxResults=2",
            "nextPage": "http://you.atlassian.net/rest/api/2/project/paginated?startAt=2&maxResults=2",
            "maxResults": 2,
            "startAt": 0,
            "total": 7,
            "isLast": False,
            "values": [
                {
                    "self": "http://you.atlassian.net/rest/api/2/project/EX",
                    "id": "10000",
                    "key": "EX",
                    "name": "Example",
                    "avatarUrls": {
                        "48x48": "http://you.atlassian.net/secure/projectavatar?size=large&pid=10000",
                        "24x24": "http://you.atlassian.net/secure/projectavatar?size=small&pid=10000",
                        "16x16": "http://you.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
                        "32x32": "http://you.atlassian.net/secure/projectavatar?size=medium&pid=10000"
                    },
                    "projectCategory": {
                        "self": "http://you.atlassian.net/rest/api/2/projectCategory/10000",
                        "id": "10000",
                        "name": "FIRST",
                        "description": "First Project Category"
                    },
                    "simplified": False,
                    "style": "classic",
                    "fields": {
                        "project": {
                            "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
                            "id": "10000",
                            "key": "EX",
                            "description": "This project was created as an example for REST.",
                            "lead": {
                                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                                "key": "mia",
                                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                                "name": "mia",
                                "avatarUrls": {
                                    "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                                    "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                                    "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                                    "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                                },
                                "displayName": "Mia Krystof",
                                "active": False
                            }
                        },
                        "issuetype": {
                          "self": "http://your-domain.atlassian.net/rest/api/2/issueType/3",
                          "id": "3",
                          "description": "A task that needs to be done.",
                          "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
                          "name": "Task",
                          "subtask": False,
                          "avatarId": 1
                        },
                        "fixVersions": ['1.2.3'],
                        "summary": "A test issue",
                        "assignee": "Matt Damon",
                        "updated":'2018-11-14T06:02:01.639+0000',
                        "created": '2018-11-14T06:02:01.639+0000',

                    },

                },
                {
                    "self": "http://your-domain.atlassian.net/rest/api/2/project/ABC",
                    "id": "10001",
                    "key": "ABC",
                    "name": "Alphabetical",
                    "avatarUrls": {
                        "48x48": "http://you.atlassian.net/secure/projectavatar?size=large&pid=10001",
                        "24x24": "http://you.atlassian.net/secure/projectavatar?size=small&pid=10001",
                        "16x16": "http://you.atlassian.net/secure/projectavatar?size=xsmall&pid=10001",
                        "32x32": "http://you.atlassian.net/secure/projectavatar?size=medium&pid=10001"
                    },
                    "projectCategory": {
                        "self": "http://you.atlassian.net/rest/api/2/projectCategory/10000",
                        "id": "10000",
                        "name": "FIRST",
                        "description": "First Project Category"
                    },
                    "simplified": False,
                    "style": "classic",
                    "fields": {
                        "project": {
                            "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
                            "id": "10000",
                            "key": "EX",
                            "description": "This project was created as an example for REST.",
                            "lead": {
                                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                                "key": "mia",
                                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                                "name": "mia",
                                "avatarUrls": {
                                    "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                                    "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                                    "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                                    "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                                },
                                "displayName": "Mia Krystof",
                                "active": False
                            }
                        },
                        "issuetype": {
                            "self": "http://your-domain.atlassian.net/rest/api/2/issueType/3",
                            "id": "3",
                            "description": "A task that needs to be done.",
                            "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
                            "name": "Task",
                            "subtask": False,
                            "avatarId": 1
                        },
                        "fixVersions": ['1.2.3'],
                        "summary": "A test issue",
                        "assignee": "Matt Damon",
                        "updated": '2018-11-14T06:02:01.639+0000',
                        "created": '2018-11-14T06:02:01.639+0000',

                    },
                }
            ]
        }

        Organization(
            key="MyOrg",
            clientKey='MyKeys111111',
            sharedSecret='shhhItsASecret',
            pluginsVersion='1',
            baseUrl='http://you.atlassian.net',
            productType='thebest',
            description='standard Org Stuff',
            serviceEntitlementNumber='1',
            eventType='install',
            publicKey='startheregoanywhere',
            serverVersion='7.8.10',
            installedBy='thisGuy'
        ).save()

    def test_sync_issues(self):
        from .lib import sync_issues
        project = Project.objects.create(jid='10000', key='EX', name='Example')
        IssueType.objects.create(
            project=project,
            name='Task',
            jid='3',
            icon_url="http://your-domain.atlassian.net/secure/viewavatar?&avatarId=10299&avatarType=issuetype")
        with mock.patch.object(AtlassianRequests, 'post_paginated', return_value=self.project_search_results['values']):
            sync_issues(project)
            issue1 = Issue.objects.get(jid=10000)
            issue2 = Issue.objects.get(jid=10001)
            self.assertEqual(issue1.jira_key, 'EX')
            self.assertEqual(issue2.jira_key, 'ABC')


class TestWebhooks(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create an existing project to save against
        project = Project(jid=10001, key="TEST", name="Test Project")
        project.save()
        # Project only takes the story issue type
        issue_type = IssueType(project=project, name="Story", jid=1, icon_url="http://notaurl.com/img")
        issue_type.save()
        # Create an existing issue for update cases
        cls.issue = Issue(
            jid=10001,
            link="https://atlassian.com/myissue",
            jira_key="TEST-1",
            fixVersions="[https://atlassian.com/fixversion]",
            summary="Summary of My Issue",
            assignee="tester1",
            issue_type=issue_type,
            project=project,
            iss_updated="2018-11-14T06:02:01.639+0000",
            iss_created="2018-11-14T06:02:01.639+0000",
        )
        cls.issue.save()

        cls.base_test_issue = {
            "issue": {
                    "self": "http://you.atlassian.net/rest/api/2/project/EX",
                    "id": "10001",
                    "key": "TEST-1",
                    "name": "Example",
                    "avatarUrls": {
                        "48x48": "http://you.atlassian.net/secure/projectavatar?size=large&pid=10000",
                        "24x24": "http://you.atlassian.net/secure/projectavatar?size=small&pid=10000",
                        "16x16": "http://you.atlassian.net/secure/projectavatar?size=xsmall&pid=10000",
                        "32x32": "http://you.atlassian.net/secure/projectavatar?size=medium&pid=10000"
                    },
                    "projectCategory": {
                        "self": "http://you.atlassian.net/rest/api/2/projectCategory/10000",
                        "id": "10000",
                        "name": "FIRST",
                        "description": "First Project Category"
                    },
                    "simplified": False,
                    "style": "classic",
                    "fields": {
                        "project": {
                            "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
                            "id": "10001",
                            "key": "TEST",
                            "description": "This project was created as an example for REST.",
                            "lead": {
                                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                                "key": "mia",
                                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                                "name": "mia",
                                "avatarUrls": {
                                    "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                                    "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                                    "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                                    "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                                },
                                "displayName": "Mia Krystof",
                                "active": False
                            }
                        },
                        "issuetype": {
                          "self": "http://your-domain.atlassian.net/rest/api/2/issueType/1",
                          "id": "1",
                          "description": "A task that needs to be done.",
                          "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
                          "name": "Story",
                          "subtask": False,
                          "avatarId": 1
                        },
                        "fixVersions": ['1.2.3'],
                        "summary": "A test issue",
                        "assignee": "Matt Damon",
                        "updated": '2018-11-14T06:02:01.639+0000',
                        "created": '2018-11-14T06:02:01.639+0000',

                    }
            }
        }

    def test_update_issue(self):
        data = deepcopy(self.base_test_issue)
        update_issue(data)
        updated_issue = Issue.objects.get(jid=10001)
        # Assert the issue has been updated
        self.assertEqual("A test issue", updated_issue.summary)

    def test_update_issue_no_exist(self):
        data = deepcopy(self.base_test_issue)
        data['issue']['id'] = "10002"
        update_issue(data)
        # Assert the issue was created
        self.assertTrue(Issue.objects.get(jid=10002))

    def test_update_issue_no_issue_type(self):
        data = deepcopy(self.base_test_issue)
        data['issue']['fields']['issuetype'] = {
                          "self": "http://your-domain.atlassian.net/rest/api/2/issueType/2",
                          "id": "2",
                          "description": "A task that needs to be done.",
                          "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
                          "name": "Task",
                          "subtask": False,
                          "avatarId": 1
                        }

        update_issue(data)
        # Assert the issue was not updated
        self.assertEqual(self.issue, Issue.objects.get(jid=10001))

    def test_update_issue_no_project(self):
        data = deepcopy(self.base_test_issue)
        data['issue']['fields']['project'] = {
                            "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
                            "id": "10002",
                            "key": "EX",
                            "description": "This project was created as an example for REST.",
                            "lead": {
                                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                                "key": "mia",
                                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                                "name": "mia",
                                "avatarUrls": {
                                    "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                                    "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                                    "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                                    "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                                },
                                "displayName": "Mia Krystof",
                                "active": False
                            }
                        }
        update_issue(data)
        # Assert the issue was not updated
        self.assertEqual(self.issue, Issue.objects.get(jid=10001))

    def test_create_issue(self):
        data = deepcopy(self.base_test_issue)
        data['issue']["id"] = "10023"
        create_issue(data)
        # Assert the issue has been updated
        self.assertTrue(Issue.objects.get(jid=10023))

    def test_create_issue_no_issue_type(self):
        data = deepcopy(self.base_test_issue)
        data['issue']['fields']['issuetype'] = {
            "self": "http://your-domain.atlassian.net/rest/api/2/issueType/2",
            "id": "2",
            "description": "A task that needs to be done.",
            "iconUrl": "http://your-domain.atlassian.net//secure/viewavatar?size=xsmall&avatarId=10299&avatarType=issuetype\",",
            "name": "Task",
            "subtask": False,
            "avatarId": 1
        }

        create_issue(data)
        # Assert the issue was not updated
        self.assertEqual(self.issue, Issue.objects.get(jid=10001))

    def test_create_issue_no_project(self):
        data = deepcopy(self.base_test_issue)
        data['issue']['fields']['project'] = {
            "self": "http://your-domain.atlassian.net/rest/api/2/project/EX",
            "id": "10002",
            "key": "EX",
            "description": "This project was created as an example for REST.",
            "lead": {
                "self": "http://your-domain.atlassian.net/rest/api/2/user?username=mia",
                "key": "mia",
                "accountId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
                "name": "mia",
                "avatarUrls": {
                    "48x48": "http://your-domain.atlassian.net/secure/useravatar?size=large&ownerId=mia",
                    "24x24": "http://your-domain.atlassian.net/secure/useravatar?size=small&ownerId=mia",
                    "16x16": "http://your-domain.atlassian.net/secure/useravatar?size=xsmall&ownerId=mia",
                    "32x32": "http://your-domain.atlassian.net/secure/useravatar?size=medium&ownerId=mia"
                },
                "displayName": "Mia Krystof",
                "active": False
            }
        }
        create_issue(data)
        # Assert the issue was not updated
        self.assertEqual(self.issue, Issue.objects.get(jid=10001))
