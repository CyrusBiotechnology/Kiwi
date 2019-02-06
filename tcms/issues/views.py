from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.sites.models import Site
from dacc.authentication.auth import atlassian_authenticated
from global_login_required import login_not_required
from .models import Issue
import logging

logger = logging.getLogger('django')


@xframe_options_exempt
@atlassian_authenticated
@login_not_required
def issue_linked_test_cases(request):
    """
    View that gets rendered in the Jira issues page.  Displays a table of all test cases for a given Jira issue.
    :param request:
    :return:
    """
    jira_key = request.GET.get('issueKey')
    issue = Issue.objects.filter(jira_key=jira_key).first()
    if not issue:
        return render(request, 'issues/issue_not_found.html')
    else:
        site_url = Site.objects.get_current().domain
        context = {'cases': [], 'site_url': site_url}
        cases = issue.test_cases.all()
        for case in cases:
            try:
                last_run = case.case_run.latest('case_run_id')
            except Exception:
                # Quick fix in the event there is no case run
                last_run = {'case_run_id': 'None', 'case_run_status': 'N/A'}
            case_data = {
                'case': case,
                'run': last_run,
            }
            context['cases'].append(case_data)

    return render(request, 'issues/testcase_table.html', context=context)
