from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "notifications_testapp"

    def __str__(self):
        return self.name
