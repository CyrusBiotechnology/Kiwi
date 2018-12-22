from dacc.webhooks import register
from django.http import HttpResponse
from dateutil import parser
from .models import Issue, Project, IssueType
import logging

logger = logging.getLogger('django')


def create_issue(data):
    """
    Registered to the atlassian jira:issue_created webhook.  Saves all issues to the database if Kiwi has been
    configured to monitor that project. Otherwise ignore.
    :param data: Atlassian jira issue JSON
    :return: None
    """
    issue = data['issue']
    _save_issue(issue)
    return HttpResponse('OK')


def update_issue(data):
    """
    Registered to the atlassian jira:issue_updated webhook.  Saves all issues to the database if Kiwi has been
    configured to monitor that project. Otherwise ignore.
    :param data: Atlassian jira issue JSON
    :return: None
    """
    issue = data['issue']
    _save_issue(issue)
    return HttpResponse('OK')


def delete_issue(data):
    """
    Registered to the atlassian jira:issue_deleted webhook.  Deletes issue in the database if Kiwi has been
    configured to monitor that project. Otherwise ignore.
    :param data: Atlassian jira issue JSON
    :return: None
    """
    issue = data['issue']
    project = Project.objects.get(key=issue['fields']['project']['key'])
    if project:
        issue_type = IssueType.objects.get(
            jid=issue['fields']['issuetype']['id'],
            project=project.id,
        )
        Issue.objects.filter(
            jid=issue['id'],
            link=issue['self'],
            jira_key=issue['key'],
            fixVersions=issue['fields']['fixVersions'],
            summary=issue['fields']['summary'],
            assignee=issue['fields']['assignee'],
            issue_type=issue_type,
            project=project,
            iss_updated=parser.parse(issue['fields']['updated']),
            iss_created=parser.parse(issue['fields']['created']),
        ).delete()
        logger.info(f'Deleted issue {issue["key"]}')

    return HttpResponse('OK')


def _save_issue(issue):
    project = Project.objects.get(key=issue['fields']['project']['key'])
    if project:
        issue_type = IssueType.objects.get(
            jid=issue['fields']['issuetype']['id'],
            project=project.id,
        )
        Issue.objects.filter(
            jid=issue['id'],
            project=project,
        ).update(
            link=issue['self'],
            jira_key=issue['key'],
            fixVersions=issue['fields']['fixVersions'],
            summary=issue['fields']['summary'],
            assignee=issue['fields']['assignee'],
            issue_type=issue_type,
            iss_updated=parser.parse(issue['fields']['updated']),
            iss_created=parser.parse(issue['fields']['created']),
        )
        logger.info(f'Saved issue {issue["key"]}')
    else:
        logger.info(f'Ignoring issue {issue["key"]} for project {project.name}')


register(create_issue, 'jira:issue_created')
register(update_issue,'jira:issue_updated')
register(delete_issue, 'jira:issue_deleted')
