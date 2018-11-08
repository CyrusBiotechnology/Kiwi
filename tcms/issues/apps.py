from django.apps import AppConfig


class IssuesConfig(AppConfig):
    name = 'tcms.issues'

    def ready(self):
        from dacc.registration.descriptor import Descriptor
        from django.urls import reverse
        from tcms.issues import webhooks

        descriptor = Descriptor(
            'KiwiJira',
            'kiwi-jira',
            'Integration between Kiwi and Jira',
            'Cyrus Biotechnology',
            'https://cyrusbio.com/',
            ['read', 'write']
        )

        issue_test_panel = {
            "url": '{}?issueKey={{issue.key}}'.format(reverse('issue_linked_test_cases')),
            "key": 'kiwi-issue-panel',
            "location": "atl.jira.view.issue.left.context",
            "name": {
                "value": "Linked Kiwi Test Cases"
            },
            "layout": {
                "width": "100",
                "height": "200",
            },
            "weight": 500
        }

        descriptor.modules.add('webPanels', issue_test_panel)
