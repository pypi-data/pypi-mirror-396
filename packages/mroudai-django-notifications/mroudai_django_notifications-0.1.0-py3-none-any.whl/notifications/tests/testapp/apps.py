from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = "notifications.tests.testapp"
    label = "notifications_testapp"
    verbose_name = "Notifications Test App"
