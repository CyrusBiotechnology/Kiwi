# -*- coding: utf-8 -*-
from django import http
from django.template import loader
from django.shortcuts import render
from django.db.models import Count, Q
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import requires_csrf_token

from tcms.testplans.models import TestPlan
from tcms.testruns.models import TestRun, TestCaseRun


@require_GET
@login_required
def dashboard(request):
    """List all recent TestPlans and TestRuns"""
    test_plans = TestPlan.objects.filter(
        Q(author=request.user) | Q(owner=request.user)
    ).order_by(
        '-plan_id'
    ).select_related(
        'product', 'type'
    ).annotate(
        num_runs=Count('run', distinct=True)
    )
    test_plans_disable_count = test_plans.filter(is_active=False).count()

    test_runs = TestRun.objects.filter(
        stop_date__isnull=True,
    ).order_by('-run_id')

    # my_active_tc_runs = TestCaseRun.objects.filter(
    #     Q(assignee=request.user) and Q(run__in=active_test_runs)
    # )
    active_tc_runs = TestRun.objects.filter(
        Q(case_run__assignee=request.user) | Q(manager=request.user),
        stop_date__isnull=True,
    ).order_by('-run_id')

    context_data = {
        'test_plans_count': test_plans.count(),
        'test_plans_disable_count': test_plans_disable_count,
        'last_15_test_plans': test_plans.filter(is_active=True)[:15],

        'last_15_test_runs': test_runs[:15],
        'active_tc_runs': active_tc_runs,

        'test_runs_count': test_runs.count(),
    }
    return render(request, 'dashboard.html', context_data)


def navigation(request):
    """
    iframe navigation workaround until we migrate everything to patternfly
    """
    return render(request, 'navigation.html')


@requires_csrf_token
def server_error(request):
    """
        Render the error page with request object which supports
        static URLs so we can load a nice picture.
    """
    template = loader.get_template('500.html')
    return http.HttpResponseServerError(template.render({}, request))
