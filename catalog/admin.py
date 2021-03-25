from django.contrib import admin
from catalog import models

admin.site.register(models.Course)
admin.site.register(models.Section)
admin.site.register(models.Period)
