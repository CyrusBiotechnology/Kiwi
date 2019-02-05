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
    # Use filter because we don't want the exception if get fails
    project = Project.objects.filter(key=issue['fields']['project']['key']).first()
    issue_type = _get_issue_type(issue, project)
    if issue_type:
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
        logger.info(f'Deleted issue %s', issue['key'])

    return HttpResponse('OK')


def _save_issue(issue):
    project_key = issue['fields']['project']['key']
    # Use filter because we don't want the exception if get fails
    project = Project.objects.filter(key=project_key).first()
    if project:
        issue_type = _get_issue_type(issue, project)
        if not issue_type:
            logger.info("%s not configured to save IssueType %s",
                        project_key, issue['fields']['issuetype']['name'])
            return
        # Create the issue if the create webhook missed it.  This can happen in the case of an issue
        # changing from a type we don't care about to one we do.
        issue_qs = Issue.objects.filter(jid=issue['id'], project=project)
        if len(issue_qs) == 0:
            created_issue = Issue.objects.create(
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
            logger.info("Issue %s created", created_issue.jira_key)
        else:
            Issue.objects.filter(jid=issue['id'], project=project).update(
                link=issue['self'],
                jira_key=issue['key'],
                fixVersions=issue['fields']['fixVersions'],
                summary=issue['fields']['summary'],
                assignee=issue['fields']['assignee'],
                issue_type=issue_type,
                iss_updated=parser.parse(issue['fields']['updated']),
                iss_created=parser.parse(issue['fields']['created']),
            )
            logger.info("Issue %s updated", issue['key'])
    else:
        logger.info("No configuration for project %s, skipping issue %s",
                    project_key, issue['fields']['issuetype']['id'])


def _get_issue_type(issue, project):
    # Use filter because we don't want the exception if get fails
    issue_type = IssueType.objects.filter(
        jid=issue['fields']['issuetype']['id'],
        project=project.id,
    ).first()
    if not issue_type:
        logger.info("Project %s not configured for IssueType %s, skipping %s",
                    project.name, issue['fields']['issuetype']['name'], issue['key'])
    return issue_type


register(create_issue, 'jira:issue_created')
register(update_issue, 'jira:issue_updated')
register(delete_issue, 'jira:issue_deleted')
