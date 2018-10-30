from django.apps import AppConfig as DjangoAppConfig


class KiwiSlackConfig(DjangoAppConfig):
    name = 'tcms.slack'

    def ready(self):
        import tcms.slack.signals  # noqa
