from dacc.webhooks import register
from django.http import HttpResponse
from dateutil import parser
from .models import Issue, Project, IssueType
import logging

logger = logging.getLogger('django')


def create_issue(data):
    logger.error(data)
    issue = data['issue']
    project = Project.objects.get(key=issue['fields']['project']['key'])
    if project:
        issue_type = IssueType.objects.get(
            jid=issue['fields']['issuetype']['id'],
            project=project.id,
        )
        Issue.objects.create(
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
        )
    return HttpResponse('OK')


def update_issue(data):
    logger.error(data)
    issue = data['issue']
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
    return HttpResponse('OK')


def delete_issue(data):
    logger.error(data)
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

    return HttpResponse('OK')


register(create_issue, 'jira:issue_created')
register(update_issue,'jira:issue_updated')
register(delete_issue, 'jira:issue_deleted')
