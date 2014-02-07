from django.contrib import admin
from spo_app.models import ProductCategory, ProductFeature, Market,\
                                    BusinessType, FAQQuestion, FAQGroup, \
                                    MarketPaymentAccount, Payment, MailingListSource

admin.site.register(ProductCategory)
admin.site.register(ProductFeature)   
admin.site.register(MarketPaymentAccount)
admin.site.register(Market)
admin.site.register(MailingListSource)
admin.site.register(BusinessType)  
admin.site.register(FAQGroup)
admin.site.register(FAQQuestion)
admin.site.register(Payment)