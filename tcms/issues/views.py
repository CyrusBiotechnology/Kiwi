from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.sites.models import Site
from dacc.authentication.auth import atlassian_authenticated
from global_login_required import login_not_required
from .models import Issue


@xframe_options_exempt
@atlassian_authenticated
@login_not_required
def issue_linked_test_cases(request):
    jira_key = request.GET.get('issueKey')
    issue = Issue.objects.get(jira_key=jira_key)
    cases = issue.test_cases.all()
    site_url = Site.objects.get_current().domain
    context = {'cases': [], 'site_url': site_url}
    for case in cases:
        last_run = case.case_run.latest('case_run_id')
        case_data = {
            'case': case,
            'run': last_run,
        }
        context['cases'].append(case_data)

    return render(request, 'issues/testcase_table.html', context=context)
