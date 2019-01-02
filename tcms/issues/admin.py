import ast
import json
from django.contrib import admin
from django.shortcuts import render, redirect
import django_rq
from dacc.authentication import AtlassianRequests
from dacc.authentication.models import Organization
from .models import Project, IssueType, Issue
from .forms import IssueTypeForm
from .lib import sync_issues


# Register your models here.
admin.site.register(Issue)
admin.site.register(Project)


@admin.site.register_view('config/', urlname='project-list', name='Project List')
def list_config(request):
    '''
    Provide a view to Select projects and configure which project you want to sync with.
    :param request:
    :return:
    '''
    #  Punting on multi- tenant support since Kiwi doesn't have this concept anyway
    tenant_info_obj = Organization.objects.first()
    if tenant_info_obj:
        tenant_info = tenant_info_obj.__dict__
    else:
        context = dict(admin.site.each_context(request))
        return render(request, 'issues/project_list.html', context)
    requests = AtlassianRequests(tenant_info)
    projects = requests.get_paginated('/rest/api/2/project/search')
    # TODO: Fix this to either use pagination in the template or use the generator in the template
    configured_projects = Project.objects.all()
    configured_projects_keys = Project.objects.values_list('key', flat=True).all()
    projects = [project for project in projects if project['key'] not in configured_projects_keys]

    context = dict(
        admin.site.each_context(request),
        configured=configured_projects,
        projects=projects,
    )

    return render(request, 'issues/project_list.html', context)


@admin.site.register_view('config/get/(?P<key>\w+)/$', urlname='jira-config', name='Jira Config', visible=False)
def create_config(request, key):
    """
    Configures the Issuetypes you want to sync with in the project
    :param request:
    :param key:
    :return:
    """
    tenant_info = Organization.objects.first().__dict__
    requests = AtlassianRequests(tenant_info)
    resp = requests.get(f'/rest/api/2/project/{key}').json()
    form = IssueTypeForm(issue_types=resp['issueTypes'], project=resp)
    context = {
        'project': resp,
        'project_name': resp['name'],
        'description': resp['description'],
        'form': form
    }

    return render(request, 'issues/project_config.html', context)


@admin.site.register_view('config/save/(?P<key>\w+)/$', urlname='save-config', name='Jira Config Save', visible=False)
def save_config(request, key):
    """
    Saves the issue configuration per project.  Will delete all existing issues types for the project and repopulate them.
    :param request: HttpRequest
    :param key: Jira key for the project
    :return:
    """
    project_json = json.loads(request.POST.get('project'))
    issue_types_json = request.POST.getlist('issue_types')
    project, created = Project.objects.get_or_create(
            jid=project_json['id'],
            key=key,
            name=project_json['name'],
    )

    # Clean the projects issue types before we re-create them
    IssueType.deactivate_project_issues(project=project)

    for issue in issue_types_json:
        issue = ast.literal_eval(issue)
        issue, created = IssueType.objects.get_or_create(
            project=project,
            name=issue['name'],
            jid=issue['id'],
            icon_url=issue['iconUrl']
        )
        issue.active = True
        issue.save()

    queue = django_rq.get_queue('default', is_async=True, autocommit=True, default_timeout=1200)
    queue.enqueue(sync_issues, project)
    return redirect('admin:project-list')
