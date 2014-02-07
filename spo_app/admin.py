from django.contrib import admin
from spo_app.models import FAQQuestion, FAQGroup

admin.site.register(FAQGroup)
admin.site.register(FAQQuestion)