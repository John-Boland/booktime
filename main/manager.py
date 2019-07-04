from django.db import models

class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)
