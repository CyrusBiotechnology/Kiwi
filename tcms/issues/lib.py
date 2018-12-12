from dacc.authentication import AtlassianRequests
from dacc.authentication.models import Organization
from .models import Project, IssueType, Issue
from dateutil import parser
import logging

logger = logging.getLogger('django')


def sync_issues(project):
    tenant_info = Organization.objects.first().__dict__
    requests = AtlassianRequests(tenant_info)
    key = project.key
    issue_types = IssueType.objects.filter(project=project)
    issue_types = ','.join([issue_type.name for issue_type in issue_types])
    jql = f'(project={key} AND issueType in ({issue_types}))'

    payload = {
        "jql": jql,
        "fields": [
            '*all'
        ],
        "startAt": 0,
        "maxResults": 20,
        "fieldsByKeys": False
    }
    logger.debug(payload)
    issues = requests.post_paginated('/rest/api/2/search', json=payload)

    for issue in issues:
        logger.debug(issue)
        project = Project.objects.get(key=issue['fields']['project']['key'])
        issue_type = IssueType.objects.get(
            jid=issue['fields']['issuetype']['id'],
            project=project.id,
        )
        req, _ = Issue.objects.get_or_create(
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
