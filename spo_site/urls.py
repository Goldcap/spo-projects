from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'spo_app.views.index', name='index'),
    url(r'^gallery/', 'spo_app.views.home', name='home'),
    url(r'^account/',include('django.contrib.auth.urls')),
    url(r'^forgot-password/$','spo_app.views.forgot_password',name="forgot-password"),
            
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #SECTION 1: Public Pages
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile_form/', 'spo_app.views.profile_form'),
    url(r'^faq/', 'spo_app.views.faq'),
    url(r'^mailing_list/', 'spo_app.views.mailing_list'), 
    
    #SECTION 2: Vendor Pages
    url(r'^faq/(?P<pageno>\d+)/', 'spo_app.views.vendor_faq', name='vendor_faq_with_pageno'),
    url(r'^faq/', 'spo_app.views.vendor_faq', name='vendor_faq'),
    url(r'^profile/', 'spo_app.views.vendor_home'),
    url(r'^login/', 'spo_app.views.vendor_login', name="vendor_login"),
    url(r'^signup/', 'spo_app.views.vendor_signup', name="vendor_signup"),
    url(r'^my_images/', 'spo_app.views.vendor_images', name="vendor_images"),
    url(r'^pending/', 'spo_app.views.vendor_pending', name="vendor_pending"),
    url(r'^image_manager/(?P<vendor_id>\d+)/', 'spo_app.views.market_contract_image'),
    url(r'^image_manager/delete/', 'spo_app.views.market_contract_image_delete'),
    url(r'^image_manager/info/', 'spo_app.views.market_contract_image_info'),
   
    #SECTION 3: Admin Pages
    url(r'^admin_login/', 'spo_app.views.admin_login'),
    url(r'^profile_report/export/', 'spo_app.views.export_report', {'source': 'vendor_profile_report'}),
    url(r'^profile_report/', 'spo_app.views.vendor_profile_report'),
    url(r'^profile_form/(?P<profile_id>\d+)/', 'spo_app.views.vendor_profile_form'),
    url(r'^login_activity/export/', 'spo_app.views.export_report', {'source': 'vendor_login_activity'}),
    url(r'^login_activity/', 'spo_app.views.vendor_login_activity'),
    url(r'^images_report/', 'spo_app.views.vendor_images_report'),
    
    #GLOBALS
    url(r'^logout/$', 'django.contrib.auth.views.logout',
    {'next_page': '/login/'}),
    
)
