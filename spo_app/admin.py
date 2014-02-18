from django.contrib import admin
from spo_app.models import FAQQuestion, FAQGroup, VendorProfile, VendorImage

admin.site.register(FAQGroup)
admin.site.register(FAQQuestion)
admin.site.register(VendorProfile)
admin.site.register(VendorImage)
