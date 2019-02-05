from dacc.webhooks import register
from django.http import HttpResponse
from dateutil import parser
from .models import Issue, Project, IssueType
import logging

logger = logging.getLogger('django')


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


def create_issue(data):
    issue = data['issue']
    project_key = issue['fields']['project']['key']
    # Use filter because we don't want the exception if get fails
    project = Project.objects.filter(key=project_key).first()
    if project:
        issue_type = _get_issue_type(issue, project)
        if not issue_type:
            logger.info("%s not configured to save IssueType %s",
                        project_key, issue['fields']['issuetype']['name'])
            return HttpResponse('OK')
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
        logger.info("Created issue %s", created_issue.jira_key)
    else:
        logger.info("No configuration for project %s, skipping issue %s",
                    project_key, issue['fields']['issuetype']['id'])
    return HttpResponse('OK')


def update_issue(data):
    issue = data['issue']
    project_key = issue['fields']['project']['key']
    # Use filter because we don't want the exception if get fails
    project = Project.objects.filter(key=issue['fields']['project']['key']).first()
    if project:
        issue_type = _get_issue_type(issue, project)
        if not issue_type:
            logger.info("%s not configured to save IssueType %s",
                        project_key, issue['fields']['issuetype']['name'])
            return HttpResponse('OK')
        # Create the issue if the create webhook missed it.  This can happen in the case of an issue
        # changing from a type we don't care about to one we do.
        issue_qs = Issue.objects.filter(jid=issue['id'], project=project)
        if len(issue_qs) == 0:
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
            logger.info("Issue %s created", issue['key'])
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
    return HttpResponse('OK')


def delete_issue(data):
    issue = data['issue']
    # Use filter because we don't want the exception if get fails
    project = Project.objects.filter(key=issue['fields']['project']['key']).first()
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
register(update_issue, 'jira:issue_updated')
register(delete_issue, 'jira:issue_deleted')
