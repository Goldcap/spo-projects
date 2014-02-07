from django.contrib import admin
from spo_app.models import FAQQuestion, FAQGroup, VendorProfile

admin.site.register(FAQGroup)
admin.site.register(FAQQuestion)
admin.site.register(VendorProfile)