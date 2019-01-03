from dacc.authentication import AtlassianRequests
from dacc.authentication.models import Organization
from .models import Project, IssueType, Issue
from dateutil import parser
import logging

from django.db.utils import DataError

logger = logging.getLogger('django')


def sync_issues(project):
    """
    Generates a jql query based on the project and active issue types associated with the project.  Paginates through
    the Jira API and saves all issues to the database.
    :param project: Project
    :return: None
    """
    tenant_info = Organization.objects.first().__dict__
    requests = AtlassianRequests(tenant_info)
    key = project.key
    issue_types = IssueType.objects.filter(project=project, active=True)
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
    issues = requests.post_paginated('/rest/api/2/search', json=payload)

    total = 0
    saved = 0
    failed = 0
    for issue in issues:
        total += total
        issue_type = None
        try:
            issue_type = IssueType.objects.get(
                jid=issue['fields']['issuetype']['id'],
                project=project.id,
            )
        except DataError as err:
            logger.error('DataError: {0}'.format(err))

        try:
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
            logging.info('Issue {0} created'.format(req.jira_key))
            saved += saved
        except DataError as err:
            failed += failed
            logger.error('DataError: {0}'.format(err))
        logger.info('Processed {0} issues'.format(total))

    logger.info(
        f'Sync Completed on {total} issues for project {project.name}. {saved} were saved with {failed} failures'
    )
