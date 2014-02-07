from datetime import datetime

from django.db import models
from django.contrib.auth.models import User, Group 

from utils import generate_app_id

from sorl.thumbnail import ImageField
from sorl.thumbnail import get_thumbnail

MARKET_CONTRACT_CHOICES = (('Accepted','Accepted'), ('Rejected','Rejected'), ('Waitlist','Waitlist'))
USER_ACTIVITY_CHOICES = (('Login','Login'), )
PAYMENT_CHOICES = ((0,'Paypal'),(1,'Check'),(2,'CreditCard'), )


class MailingListSource(models.Model):
    """
    Mailing List List
    """
    Name = models.CharField(max_length=100)
    DateAdded = models.DateTimeField(default=datetime.now(), blank=True, null=True)
    
    class Meta:
        verbose_name = "Mailing List"
        verbose_name_plural = "Mailing Lists"
        
    def __unicode__(self):
        return "%s" % (self.Name)
        
class VendorImage(models.Model):
    """
    """
    user = models.ForeignKey(User)
    ImgFile = models.ImageField(upload_to='uploads/vendor_images/', blank=True)
    filename = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    caption = models.CharField(max_length=100, blank=True)

    @property
    def thumbnail(self):
        im = get_thumbnail(self.ImgFile, "80x80", quality=50)
        return "/static/media/" + im.url
    

class FAQGroup(models.Model):
    """
    """
    class Meta:
        verbose_name = "FAQ Group"
        verbose_name_plural = "FAQ Groups"
    
    def __unicode__(self):
        return "%s" % (self.Name)

    Name = models.CharField(max_length=100, blank=True, null=True)

class FAQQuestion(models.Model):
    """
    """
    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __unicode__(self):
        return "%s" % (self.Question)
    
    Question = models.TextField(default='', blank=True)
    Answer = models.TextField(default='', blank=True, null=True)
    Group = models.ForeignKey(FAQGroup)
    for_vendor = models.BooleanField(default=False)
    
class MailingList(models.Model):
    """
    Mailing List Entry
    """
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    EmailAddress = models.CharField(max_length=300, blank=True, null=True)
    ZipCode = models.CharField(max_length=100, blank=True, null=True)
    DateAdded = models.DateTimeField(default=datetime.now(), blank=True, null=True)

class ActivityLog(models.Model):
    """
    Activity Log
    """
    
    user = models.ForeignKey(User)
    market = models.ForeignKey(Market, blank=True, null=True)
    activity =  models.CharField(choices=USER_ACTIVITY_CHOICES, max_length=20, default='Login')
    DateAdded = models.DateTimeField(auto_now_add=True)
    