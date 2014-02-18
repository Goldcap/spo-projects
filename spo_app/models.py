from datetime import datetime
from django.utils.timezone import utc

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
    DateAdded = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=utc), blank=True, null=True)
    
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
    status = models.IntegerField(default=0)
    dateAdded = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=utc), blank=True, null=True)

    @property
    def thumbnail(self):
        im = get_thumbnail(self.ImgFile, "160x160", quality=50)
        return "/static/media/" + im.url

    @property
    def current_status(self):
        if (self.status == 1):
            return '<span style="color:green">Public</span>'
        return '<span style="color:red">Private</span>'

#http://stackoverflow.com/questions/1760421/how-can-i-render-a-manytomanyfield-as-checkboxes
class VendorProfile(models.Model):
    """
    """
    user = models.ForeignKey(User, blank=True, null=True, unique=True)
    FirstName = models.CharField(max_length=100)
    LastName = models.CharField(max_length=100)
    Company = models.CharField(max_length=100)
    DateSubmitted = models.DateTimeField(default=datetime.now(), blank=True, null=True)
    Address = models.CharField(max_length=300,blank=True, null=True)
    Address1 = models.CharField(max_length=300, blank=True, null=True)
    City = models.CharField(max_length=300, blank=True, null=True)
    State = models.CharField(max_length=300, blank=True, null=True)
    Zip = models.CharField(max_length=300, blank=True, null=True)
    Telephone = models.CharField(max_length=50, blank=True, null=True)
    BusinessTelephone = models.CharField(max_length=50, blank=True, null=True)
    Fax = models.CharField(max_length=50, blank=True, null=True)
    Cell = models.CharField(max_length=50, blank=True, null=True)
    Email = models.CharField(max_length=300, blank=True, null=True)
    Website = models.CharField(max_length=300, blank=True, null=True)
    Facebook = models.CharField(max_length=300, blank=True, null=True)
    Twitter = models.CharField(max_length=300, blank=True, null=True)
    Password = models.CharField(max_length=300, blank=True, null=True)
    SelectedMailingLists = models.ManyToManyField(MailingListSource, blank=True, null=True)
    ShortDecs = models.TextField(blank=True, null=True)
    Approved = models.IntegerField(default=-1)
    SelectedImages = models.ManyToManyField(VendorImage, blank=True, null=True)
    
    def __str__(self):
        return "%s %s" % (self.FirstName, self.LastName)
    
    def __unicode__(self):
        return "%s %s" % (self.FirstName, self.LastName)
        
    @property
    def last_login(self):
        try:
            al = ActivityLog.objects.filter(user=self.user,activity='Login').order_by('-DateAdded')[0]
            return al.DateAdded
        except:
            return None
        
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
    DateAdded = models.DateTimeField(default=datetime.utcnow().replace(tzinfo=utc), blank=True, null=True)

class ActivityLog(models.Model):
    """
    Activity Log
    """
    
    user = models.ForeignKey(User)
    activity =  models.CharField(choices=USER_ACTIVITY_CHOICES, max_length=20, default='Login')
    DateAdded = models.DateTimeField(auto_now_add=True)
    