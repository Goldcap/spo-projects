import hashlib
import datetime

from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, login, authenticate
from django.db import IntegrityError
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.forms import USStateField
from django.utils.timezone import now

from spo_app.widgets import SpoCheckboxSelectMultiple
from spo_app.models import *

class UserForm(forms.Form):
    UserName = forms.CharField(max_length=10)

    Password1 = forms.CharField(max_length=10)
    password2 = forms.EmailField(max_length=10)

    def clean(self):
        data = self.cleaned_data
        if "password1" in data and "password2" in data and data["password1"] != data["password2"]:
            raise forms.ValudationError("Passwords must be same")

class VendorForm(forms.ModelForm):
    FirstName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True, error_messages = {'invalid': 'Your First Name is required'})
    LastName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=True)
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}), required=False)  
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your Personal Number'}), required=False)
    BusinessTelephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your Business Number'}), required=False)
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company', 'width': '100%'}), required=True)
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    Password = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Password'}), required=True) 
    PasswordConfirm = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Confirm Password'}), required=False) 
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), required=False, queryset=ProductCategory.objects.filter(ForProfile=True))
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), required=False, queryset=ProductFeature.objects.filter(ForProfile=True))
    SelectedMarket = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), required=False, queryset=Market.objects.filter())
    SelectedMailingLists = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), required=False, queryset=MailingListSource.objects.filter())
    ShortDecs = forms.CharField(widget = forms.Textarea, required=False)
    user = None
    
    class Meta:
        model = VendorProfile
        fields = ['Company', 'FirstName', 'LastName', 'Telephone', "BusinessTelephone"]

    def __init__(self, *args, **kw):
        super(VendorForm, self).__init__(*args, **kw)
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName
        self.fields['Website'].initial = self.instance.Website 
        self.fields['Telephone'].initial = self.instance.Telephone 
        self.fields['BusinessTelephone'].initial = self.instance.BusinessTelephone 
        self.fields['Company'].initial = self.instance.Company
        self.fields['ShortDecs'].initial = self.instance.ShortDecs
        if self.instance.user:
            self.fields['Email'].initial = self.instance.user.email
        try:
            self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
            self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
            self.fields['SelectedMarket'].initial = self.instance.SelectedMarket.values_list('pk',flat=True)
            self.fields['SelectedMailingLists'].initial = self.instance.SelectedMailingLists.values_list('pk',flat=True)
        except:
            pass
        
        
    def save(self):
        """
        vendor signup
        """
        self.user = User.objects.create_user(self.data['Email'].strip(), self.data['Email'].strip(), self.data['Password'].strip())
        #self.user.is_active = False
        self.user.save()
        
        rec = VendorProfile()
        
        rec.user = self.user
        rec.Company = self.data['Company']
        rec.FirstName = self.data['FirstName']
        print "1"
        rec.LastName = self.data['LastName']
        print "2"
        rec.Email = self.data['Email']
        print "3"
        #rec.Telephone = self.data['Telephone']
        #rec.BusinessTelephone = self.data['BusinessTelephone']
        rec.Approved = 1
        #rec.Password = hashlib.md5(self.data['Password']).hexdigest()
        
        print "5"
        rec.save()
        print "6"
        self._errors = ErrorList(['Successfully submitted!'])

    def save_vendor_home(self, request):
        """
        vendor home page
        """
        #try:
        self.user = User.objects.get(email=self.data['Email'].strip())
        self.user.email = self.data['Email'].strip()
        self.user.username = self.data['Email'].strip()
        self.user.save()

        rec = VendorProfile.objects.get(user__email=self.data['Email'])
        rec.Company = self.data['Company']
        rec.FirstName = self.data['FirstName']
        rec.LastName = self.data['LastName']
        rec.Website = self.data['Website']
        rec.Telephone = self.data['Telephone']
        rec.BusinessTelephone = self.data['BusinessTelephone']
        rec.ShortDecs = self.data['ShortDecs']
        rec.save()
            
        #except User.DoesNotExist:
        #    pass

        for c in request.POST.getlist('SelectedCategory'):
            try:
                rec.SelectedCategory.add(c)
            except IntegrityError:
                pass
        for f in request.POST.getlist('SelectedFeature'):
            try:
                rec.SelectedFeature.add(f)
            except IntegrityError:
                pass
        for m in request.POST.getlist('SelectedMarket'):
            try:
                rec.SelectedMarket.add(m)
            except IntegrityError:
                pass
        for l in request.POST.getlist('SelectedMailingLists'):
            try:
                rec.SelectedMailingLists.add(l)
            except IntegrityError:
                pass
        
        self._errors = ErrorList(['Your form uccessfully submitted!'])
    
    def is_valid(self):
        if len(VendorProfile.objects.filter(user__email=self.data['Email'])) > 0:
            self.add_error('Email', 'Email already exists.')
            #self._errors = ErrorList(['Email already exists.'])
            valid = False
        else:
            valid = True
        
        if ((len(self.data['Password']) == 0) or (len(self.data['PasswordConfirm']) == 0) or (self.data['PasswordConfirm'] != self.data['Password'])):
            self.add_error('Password', 'There was a problem with your password, please try again.')
            #self._errors = ErrorList(['There was a problem with your password, please try again.'])
            valid = False
        
        #print valid
        return valid
        
        

class VendorProfileForm(forms.ModelForm):
    FirstName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True, error_messages = {'invalid': 'Your First Name is required'})
    LastName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=True)
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}), required=True)  
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}), required=True)
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    #Password = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Password'}), required=True) 
    #PasswordConfirm = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Confirm Password'}), required=True) 
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductCategory.objects.filter(ForProfile=True))
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductFeature.objects.filter(ForProfile=True))
    SelectedMarket = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=Market.objects.filter())
    ShortDecs = forms.CharField(widget = forms.Textarea, required=False)
    user = None
    
    class Meta:
        model = VendorProfile
        fields = ['Company', 'FirstName', 'LastName', 'Website','SelectedCategory','SelectedFeature','SelectedMarket','ShortDecs',]

    def __init__(self, *args, **kw):
        super(VendorProfileForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName  
        self.fields['Website'].initial = self.instance.Website
        self.fields['ShortDecs'].initial = self.instance.ShortDecs
        self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
        self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
        self.fields['SelectedMarket'].initial = self.instance.SelectedMarket.values_list('pk',flat=True)
        
    def save(self):
        """
        vendor signup
        """
        try:
            self.user, created = User.objects.get_or_create(email=self.cleaned_data['Email'],
                                                   username=self.cleaned_data['Email'],
                                                   is_active=False,)
        except:
            self._errors = ErrorList(['An account with that email already exists.'])
            return 
            
        rec, created = VendorProfile.objects.get_or_create(Company=self.cleaned_data['Company'])
        rec.user = self.user
        rec.FirstName = self.cleaned_data['FirstName']
        rec.LastName = self.cleaned_data['LastName']
        rec.Website = self.cleaned_data['Website']
        rec.save()
        
        for c in request.POST.getlist('SelectedCategory'):
            try:
                rec.SelectedCategory.add(c)
            except IntegrityError:
                pass
        for f in request.POST.getlist('SelectedFeature'):
            try:
                rec.SelectedFeature.add(f)
            except IntegrityError:
                pass
        for m in request.POST.getlist('SelectedMarket'):
            try:
                rec.SelectedMarket.add(m)
            except IntegrityError:
                pass
                                        
        self._errors = ErrorList(['Successfully submitted!'])

class VendorLoginForm(forms.Form):
    Email = models.EmailField()
    Password = models.CharField(max_length=300)

    def login(self):
        """ use awebers client lib to obtain an authorization url
            limit to one auth record...
        """
        user = authenticate(username=self.data['Email'].strip(), password=self.data['Password'].strip())
        if user:
            self._errors = ErrorList(['Successfully logged in!'])
            return True
        else:
            self._errors = ErrorList(['Login failed !'])
            return False

class VendorImageForm(forms.Form):
    ImgFile = models.ImageField()
    caption = models.CharField(max_length=100)
    user = None
    def clean_image(self):
        ' reject large images. '
        max_size = 10**5
        if len(self.cleaned_data['ImgFile'].content) > max_size:
            raise forms.ValidationError(
             'Image must be less then %d bytes.' % max_size
            )
        else:
            return self.cleaned_data['ImgFile']

class MarketContractFormOne(forms.ModelForm):
    
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}))
    FirstName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    LastName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    DBA_BoothName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'DBA/Booth Name'}))
    Address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    Address1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    City = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}))
    State = USStateField(widget=forms.Select(choices=STATE_CHOICES))
    Zip = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Zip'}))
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone'}))
    Fax = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fax'}))
    Cell = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell'}))
    Email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}))
    Facebook = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Facebook'}))
    Twitter = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Twitter'}))
    FirstNameAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name (Alt)'}))
    LastNameAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name (Alt)'}))
    TelephoneAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone (Alt)'}))
    FaxAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fax (Alt)'}))
    CellAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell (Alt)'}))
    EmailAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email (Alt)'}))
    MarketFeesSingleBooth = forms.IntegerField()
    MarketFeesDoubleBooth = forms.IntegerField()
    MarketFeesHalfBooth = forms.IntegerField()
    MarketFeesPPF = forms.IntegerField()
    RequiredID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Vendor EIN, SSN, or NY Sales Tax ID'}))
    IsCompleted = forms.IntegerField()

    
    class Meta:
        model = MarketContract
        fields = ['Company', 'FirstName', 'LastName', 'DBA_BoothName',
                  'Address', 'Address1', 'City', 'State', 'Zip', 'Telephone', 
                  'Fax', 'Cell', 'Email', 'Website', 'Facebook', 'Twitter', 
                  'FirstNameAlt', 'LastNameAlt',
                  'TelephoneAlt', 'FaxAlt', 'CellAlt', 'EmailAlt',
                  'MarketFeesSingleBooth', 'MarketFeesDoubleBooth', 
                  'MarketFeesHalfBooth', 'MarketFeesPPF',
                  'RequiredID', 'IsCompleted',]

    def __init__(self, *args, **kw):
        
        if 'vendor' in kw:
            self.vendor = kw.pop('vendor')
        
        super(MarketContractFormOne, self).__init__(*args, **kw)
        
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName
        self.fields['DBA_BoothName'].initial = self.instance.DBA_BoothName
        self.fields['Address'].initial = self.instance.Address
        self.fields['Address1'].initial = self.instance.Address1
        self.fields['City'].initial = self.instance.City
        self.fields['State'].initial = self.instance.State
        self.fields['Zip'].initial = self.instance.Zip
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['Fax'].initial = self.instance.Fax
        self.fields['Cell'].initial = self.instance.Cell
        self.fields['Email'].initial = self.instance.Email
        self.fields['Website'].initial = self.instance.Website
        self.fields['Facebook'].initial = self.instance.Facebook
        self.fields['Twitter'].initial = self.instance.Twitter
        self.fields['FirstNameAlt'].initial = self.instance.FirstNameAlt
        self.fields['LastNameAlt'].initial = self.instance.LastNameAlt
        self.fields['TelephoneAlt'].initial = self.instance.TelephoneAlt
        self.fields['FaxAlt'].initial = self.instance.FaxAlt
        self.fields['CellAlt'].initial = self.instance.CellAlt
        self.fields['EmailAlt'].initial = self.instance.EmailAlt
        self.fields['MarketFeesSingleBooth'].initial = self.instance.MarketFeesSingleBooth
        self.fields['MarketFeesDoubleBooth'].initial = self.instance.MarketFeesDoubleBooth
        self.fields['MarketFeesHalfBooth'].initial = self.instance.MarketFeesHalfBooth
        self.fields['MarketFeesPPF'].initial = self.instance.MarketFeesPPF
        self.fields['RequiredID'].initial = self.instance.RequiredID
        self.fields['IsCompleted'].initial = self.instance.IsCompleted
        
        if self.vendor and (not self.instance.Company or self.instance.Company==''):
            self.fields['Company'].initial = self.vendor.Company
        if self.vendor and (not self.instance.FirstName or self.instance.FirstName==''):
            self.fields['FirstName'].initial = self.vendor.FirstName
        if self.vendor and (not self.instance.LastName or self.instance.LastName==''):
            self.fields['LastName'].initial = self.vendor.LastName
        if self.vendor and (not self.instance.Website or self.instance.Website==''):
            self.fields['Website'].initial = self.vendor.Website
        if self.vendor and (not self.instance.Email or self.instance.Email==''):
            self.fields['Email'].initial = self.vendor.user.email
        
    def save(self, user, market):
        """
        vendor home page
        """
        try:
            
            self.instance.Company = self.data['Company']
            self.instance.FirstName = self.data['FirstName']
            self.instance.LastName = self.data['LastName']
            self.instance.DBA_BoothName = self.data['DBA_BoothName']
            self.instance.Address = self.data['Address']
            self.instance.Address1 = self.data['Address1']
            self.instance.City = self.data['City']
            self.instance.State = self.data['State']
            self.instance.Zip= self.data['Zip']
            self.instance.Telephone = self.data['Telephone']
            self.instance.Fax = self.data['Fax']
            self.instance.Cell = self.data['Cell']
            self.instance.Email = self.data['Email']
            self.instance.Website = self.data['Website']
            self.instance.Facebook = self.data['Facebook']
            self.instance.Twitter = self.data['Twitter']
            self.instance.FirstNameAlt = self.data['FirstNameAlt']
            self.instance.LastNameAlt = self.data['LastNameAlt']
            self.instance.TelephoneAlt = self.data['TelephoneAlt']
            self.instance.FaxAlt = self.data['FaxAlt']
            self.instance.CellAlt = self.data['CellAlt']
            self.instance.EmailAlt = self.data['EmailAlt']
            self.instance.MarketFeesSingleBooth = self.data['MarketFeesSingleBooth']
            self.instance.MarketFeesDoubleBooth = self.data['MarketFeesDoubleBooth']
            self.instance.MarketFeesHalfBooth = self.data['MarketFeesHalfBooth']
            self.instance.MarketFeesPPF = self.data['MarketFeesPPF']
            self.instance.RequiredID = self.data['RequiredID']

            self.instance.save()
                        
        except MarketContract.DoesNotExist:
            pass

        self._errors = ErrorList(['Successfully submitted!'])

class MarketContractFormTwo(forms.ModelForm):
    
    class Meta:
        model = MarketContract
        fields = []

    def __init__(self, *args, **kw):
        super(MarketContractFormTwo, self).__init__(*args, **kw)
        
    def save(self,request):
        """
        vendor home page
        """
        
        product, created = Product.objects.get_or_create(user=request.user,Name=request.POST["ProductTitle"])
        product.Description=request.POST["ProductDescription"]
        product.Price=request.POST["ProductPrice"]
        product.save()
        self.instance.SelectedProducts.add(product)
        
        self._errors = ErrorList(['Successfully submitted!'])

class MarketContractFormThree(forms.ModelForm):
    
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(attrs={'size':'three-up'}), queryset=ProductCategory.objects.filter(ForProfile=False))
    FoodVendorsOnsiteCooking = forms.CharField() # FOOD VENDORS
    FoodVendorsEquipment = forms.CharField() # Will you require additional Electrical circuits then the two twenty amps that we provide for equipment?
    AboutYou = forms.CharField(widget = forms.Textarea, required=False)
    SelectedBusinessType = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(attrs={'size':'two-up'}), queryset=BusinessType.objects.all())
    
    #BusinessLogo = models.ImageField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/', blank=True)
   
    class Meta:
        model = MarketContract
        fields = [ 'SelectedCategory', 'FoodVendorsOnsiteCooking', 'FoodVendorsEquipment', 'AboutYou', 'SelectedBusinessType',]

    def __init__(self, *args, **kw):
        super(MarketContractFormThree, self).__init__(*args, **kw)
        
        self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
        self.fields['FoodVendorsOnsiteCooking'].initial = self.instance.FoodVendorsOnsiteCooking
        self.fields['FoodVendorsEquipment'].initial = self.instance.FoodVendorsEquipment
        self.fields['AboutYou'].initial = self.instance.AboutYou
        self.fields['SelectedBusinessType'].initial = self.instance.SelectedBusinessType.values_list('pk',flat=True)
        
    def save(self, request, market):
        """
        vendor home page
        """
        try:
            self.instance.FoodVendorsOnsiteCooking = self.data['FoodVendorsOnsiteCooking']
            self.instance.FoodVendorsEquipment = self.data['FoodVendorsEquipment']
            self.instance.AboutYou = self.data['AboutYou']
            
            self.instance.save()
        except MarketContract.DoesNotExist:
            pass
        
        
        for c in request.POST.getlist('SelectedCategory'):
            try:
                self.instance.SelectedCategory.add(c)
            except IntegrityError:
                pass
        for m in request.POST.getlist('SelectedBusinessType'):
            try:
                self.instance.SelectedBusinessType.add(m)
            except IntegrityError:
                pass
                    
        self._errors = ErrorList(['Successfully submitted!'])

class MarketContractFormFour(forms.ModelForm):
    
    YourExperience = forms.CharField(widget = forms.Textarea, required=False)
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductFeature.objects.filter(ForProfile=True))
    
    class Meta:
        model = MarketContract
        fields = ['YourExperience','SelectedFeature']

    def __init__(self, *args, **kw):
        super(MarketContractFormFour, self).__init__(*args, **kw)
        
        self.fields['YourExperience'].initial = self.instance.YourExperience
        self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
        
    def save(self, request):
        """
        vendor home page
        """
        try:
            self.instance.YourExperience = self.data['YourExperience']
            self.instance.save()
        except MarketContract.DoesNotExist:
            pass

        for c in request.POST.getlist('SelectedFeature'):
            try:
                self.instance.SelectedFeature.add(c)
            except IntegrityError:
                pass
        
        self._errors = ErrorList(['Successfully submitted!'])

class PaymentPromiseForm(forms.ModelForm):

    PaymentAmount = forms.FloatField(label='Payment Amount', widget=forms.TextInput(attrs={'placeholder': 'Payment Amount'}))
    Invoice = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Invoice Number'}))
    
    class Meta:
        model = Payment
        fields = ['PaymentAmount','Invoice']

    def __init__(self, *args, **kw):
        super(PaymentPromiseForm, self).__init__(*args, **kw)
        self.fields['PaymentAmount'].initial = self.instance.PaymentAmount
        self.fields['Invoice'].initial = self.instance.Invoice

        
class PaymentInfoForm(forms.ModelForm):
    user = None
    market = None
    PaymentVia = forms.IntegerField()
    
    class Meta:
        model = MarketContract
        fields = ['PaymentVia']

    def __init__(self, *args, **kw):
        super(PaymentInfoForm, self).__init__(*args, **kw)
        if self.instance.accounting:
            self.fields['PaymentVia'].initial = self.instance.accounting.PaymentVia

    def save(self, request):
        """
        vendor home page
        """
        try:
            pass
        except MarketContract.DoesNotExist:
            pass

        self._errors = ErrorList(['Successfully submitted!'])

class CheckForm(forms.ModelForm):
    
    BankName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Bank Name'}))
    RoutingNumber = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Routing Number'}))
    CheckNumber = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Check Number'}))
    
    class Meta:
        model = AccountingInfo
        fields = ['BankName', 'RoutingNumber', 'CheckNumber']

    def __init__(self, *args, **kw):
        super(CheckForm, self).__init__(*args, **kw)
        
        self.fields['BankName'].initial = self.instance.BankName
        self.fields['RoutingNumber'].initial = self.instance.RoutingNumber
        self.fields['CheckNumber'].initial = self.instance.CheckNumber
        
    def save(self):
        """
        vendor home page
        """
        try:
            self.instance.BankName = self.data['BankName']
            self.instance.RoutingNumber = self.data['RoutingNumber']
            self.instance.CheckNumber = self.data['CheckNumber']
            self.instance.save()
        except AccountingInfo.DoesNotExist:
            pass


################################
#   Administrative Versions    #
################################
        
class AdminMarketContractFormOne(forms.ModelForm):
    
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}))
    FirstName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    LastName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    DBA_BoothName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'DBA/Booth Name'}))
    Address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    Address1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}))
    City = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}))
    State = USStateField(widget=forms.Select(choices=STATE_CHOICES))
    Zip = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Zip'}))
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone'}))
    Fax = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fax'}))
    Cell = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell'}))
    Email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}))
    Facebook = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Facebook'}))
    Twitter = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Twitter'}))
    FirstNameAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name (Alt)'}))
    LastNameAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name (Alt)'}))
    TelephoneAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone (Alt)'}))
    FaxAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Fax (Alt)'}))
    CellAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell (Alt)'}))
    EmailAlt = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email (Alt)'}))
    MarketFeesSingleBooth = forms.IntegerField()
    MarketFeesDoubleBooth = forms.IntegerField()
    MarketFeesHalfBooth = forms.IntegerField()
    MarketFeesPPF = forms.IntegerField()
    RequiredID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Vendor EIN, SSN, or NY Sales Tax ID'}))
    IsCompleted = forms.IntegerField()
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(attrs={'size':'three-up'}), queryset=ProductCategory.objects.filter(ForProfile=False))
    FoodVendorsOnsiteCooking = forms.CharField() # FOOD VENDORS
    FoodVendorsEquipment = forms.CharField() # Will you require additional Electrical circuits then the two twenty amps that we provide for equipment?
    AboutYou = forms.CharField(widget = forms.Textarea, required=False)
    
    class Meta:
        model = MarketContract
        fields = ['Company', 'FirstName', 'LastName', 'DBA_BoothName',
                  'Address', 'Address1', 'City', 'State', 'Zip', 'Telephone', 
                  'Fax', 'Cell', 'Email', 'Website', 'Facebook', 'Twitter', 
                  'FirstNameAlt', 'LastNameAlt',
                  'TelephoneAlt', 'FaxAlt', 'CellAlt', 'EmailAlt',
                  'MarketFeesSingleBooth', 'MarketFeesDoubleBooth', 
                  'MarketFeesHalfBooth', 'MarketFeesPPF',
                  'RequiredID', 'IsCompleted',]

    def __init__(self, *args, **kw):
        
        if 'vendor' in kw:
            self.vendor = kw.pop('vendor')
        
        super(AdminMarketContractFormOne, self).__init__(*args, **kw)
        
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName
        self.fields['DBA_BoothName'].initial = self.instance.DBA_BoothName
        self.fields['Address'].initial = self.instance.Address
        self.fields['Address1'].initial = self.instance.Address1
        self.fields['City'].initial = self.instance.City
        self.fields['State'].initial = self.instance.State
        self.fields['Zip'].initial = self.instance.Zip
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['Fax'].initial = self.instance.Fax
        self.fields['Cell'].initial = self.instance.Cell
        self.fields['Email'].initial = self.instance.Email
        self.fields['Website'].initial = self.instance.Website
        self.fields['Facebook'].initial = self.instance.Facebook
        self.fields['Twitter'].initial = self.instance.Twitter
        self.fields['FirstNameAlt'].initial = self.instance.FirstNameAlt
        self.fields['LastNameAlt'].initial = self.instance.LastNameAlt
        self.fields['TelephoneAlt'].initial = self.instance.TelephoneAlt
        self.fields['FaxAlt'].initial = self.instance.FaxAlt
        self.fields['CellAlt'].initial = self.instance.CellAlt
        self.fields['EmailAlt'].initial = self.instance.EmailAlt
        self.fields['MarketFeesSingleBooth'].initial = self.instance.MarketFeesSingleBooth
        self.fields['MarketFeesDoubleBooth'].initial = self.instance.MarketFeesDoubleBooth
        self.fields['MarketFeesHalfBooth'].initial = self.instance.MarketFeesHalfBooth
        self.fields['MarketFeesPPF'].initial = self.instance.MarketFeesPPF
        self.fields['RequiredID'].initial = self.instance.RequiredID
        self.fields['IsCompleted'].initial = self.instance.IsCompleted
        self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
        self.fields['FoodVendorsOnsiteCooking'].initial = self.instance.FoodVendorsOnsiteCooking
        self.fields['FoodVendorsEquipment'].initial = self.instance.FoodVendorsEquipment
        self.fields['AboutYou'].initial = self.instance.AboutYou
        
        if self.vendor and (not self.instance.Company or self.instance.Company==''):
            self.fields['Company'].initial = self.vendor.Company
        if self.vendor and (not self.instance.FirstName or self.instance.FirstName==''):
            self.fields['FirstName'].initial = self.vendor.FirstName
        if self.vendor and (not self.instance.LastName or self.instance.LastName==''):
            self.fields['LastName'].initial = self.vendor.LastName
        if self.vendor and (not self.instance.Website or self.instance.Website==''):
            self.fields['Website'].initial = self.vendor.Website
        if self.vendor and (not self.instance.Email or self.instance.Email==''):
            self.fields['Email'].initial = self.vendor.user.email
        
    def save(self, request, user, market):
        """
        vendor home page
        """
        try:
            
            self.instance.Company = self.data['Company']
            self.instance.FirstName = self.data['FirstName']
            self.instance.LastName = self.data['LastName']
            self.instance.DBA_BoothName = self.data['DBA_BoothName']
            self.instance.Address = self.data['Address']
            self.instance.Address1 = self.data['Address1']
            self.instance.City = self.data['City']
            self.instance.State = self.data['State']
            self.instance.Zip= self.data['Zip']
            self.instance.Telephone = self.data['Telephone']
            self.instance.Fax = self.data['Fax']
            self.instance.Cell = self.data['Cell']
            self.instance.Email = self.data['Email']
            self.instance.Website = self.data['Website']
            self.instance.Facebook = self.data['Facebook']
            self.instance.Twitter = self.data['Twitter']
            self.instance.FirstNameAlt = self.data['FirstNameAlt']
            self.instance.LastNameAlt = self.data['LastNameAlt']
            self.instance.TelephoneAlt = self.data['TelephoneAlt']
            self.instance.FaxAlt = self.data['FaxAlt']
            self.instance.CellAlt = self.data['CellAlt']
            self.instance.EmailAlt = self.data['EmailAlt']
            self.instance.MarketFeesSingleBooth = self.data['MarketFeesSingleBooth']
            self.instance.MarketFeesDoubleBooth = self.data['MarketFeesDoubleBooth']
            self.instance.MarketFeesHalfBooth = self.data['MarketFeesHalfBooth']
            self.instance.MarketFeesPPF = self.data['MarketFeesPPF']
            self.instance.RequiredID = self.data['RequiredID']
            self.instance.SelectedCategory.clear()
            for c in request.POST.getlist('SelectedCategory'):
                try:
                    self.instance.SelectedCategory.add(c)
                except IntegrityError:
                    pass
            self.instance.FoodVendorsOnsiteCooking = self.data['FoodVendorsOnsiteCooking']
            self.instance.FoodVendorsEquipment = self.data['FoodVendorsEquipment']
            self.instance.AboutYou = self.data['AboutYou']
                
            self.instance.save()
                        
        except MarketContract.DoesNotExist:
            pass

        self._errors = ErrorList(['Successfully submitted!'])

class AdminMarketContractFormTwo(forms.ModelForm):
    
    class Meta:
        model = MarketContract
        fields = []

    def __init__(self, *args, **kw):
        super(AdminMarketContractFormTwo, self).__init__(*args, **kw)
        
    def save(self,request):
        """
        vendor home page
        """
        
        product, created = Product.objects.get_or_create(user=request.user,Name=request.POST["ProductTitle"])
        product.Description=request.POST["ProductDescription"]
        product.Price=request.POST["ProductPrice"]
        product.save()
        self.instance.SelectedProducts.add(product)
        
        self._errors = ErrorList(['Successfully submitted!'])

class AdminMarketContractFormThree(forms.ModelForm):
    
    SelectedBusinessType = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(attrs={'size':'two-up'}), queryset=BusinessType.objects.all())
    YourExperience = forms.CharField(widget = forms.Textarea, required=False)
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductFeature.objects.filter(ForProfile=True))
    
    #BusinessLogo = models.ImageField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/', blank=True)
   
    class Meta:
        model = MarketContract
        fields = [ 'SelectedCategory', 'FoodVendorsOnsiteCooking', 'FoodVendorsEquipment', 'AboutYou', 'SelectedBusinessType',]

    def __init__(self, *args, **kw):
        super(AdminMarketContractFormThree, self).__init__(*args, **kw)
        
        self.fields['SelectedBusinessType'].initial = self.instance.SelectedBusinessType.values_list('pk',flat=True)
        self.fields['YourExperience'].initial = self.instance.YourExperience
        self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
        
    def save(self, request, market):
        """
        vendor home page
        """
        self.instance.SelectedBusinessType.clear()
        for m in request.POST.getlist('SelectedBusinessType'):
            try:
                self.instance.SelectedBusinessType.add(m)
            except IntegrityError:
                pass
        self.instance.SelectedFeature.clear()
        for c in request.POST.getlist('SelectedFeature'):
            try:
                self.instance.SelectedFeature.add(c)
            except IntegrityError:
                pass
       
        try:
            self.instance.YourExperience = self.data['YourExperience']
            self.instance.save()
        except MarketContract.DoesNotExist:
            pass

                             
        self._errors = ErrorList(['Successfully submitted!'])

class AdminPaymentInfoForm(forms.ModelForm):
    user = None
    market = None
    PaymentVia = models.IntegerField(default=0, blank=True, null=True)   # PAYMENT INFO - Check
    
    class Meta:
        model = AccountingInfo
        fields = ['PaymentVia']

    def __init__(self, *args, **kw):
        super(AdminPaymentInfoForm, self).__init__(*args, **kw)
        self.fields['PaymentVia'].initial = self.instance.accounting.PaymentVia

    def save_market_contract(self):
        """
        vendor home page
        """
        try:
            if 'PaymentVia' in self.data:
                self.instance.accounting.PaymentVia = self.data['PaymentVia']

            self.instance.save()
        except MarketContract.DoesNotExist:
            pass

        self._errors = ErrorList(['Successfully submitted!'])
        
class AdminVendorProfileForm(forms.ModelForm):
    
    FirstName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}), required=True, error_messages = {'invalid': 'Your First Name is required'})
    LastName = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}), required=True)
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}), required=True)  
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}), required=True)
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your Personal Number'}), required=True)
    BusinessTelephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your Business Number'}), required=True)
    #Password = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Password'}), required=True) 
    #PasswordConfirm = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Confirm Password'}), required=True) 
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductCategory.objects.filter(ForProfile=True))
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductFeature.objects.filter(ForProfile=True))
    SelectedMarket = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=Market.objects.filter())
    ShortDecs = forms.CharField(widget = forms.Textarea, required=False)
    Approved = forms.IntegerField()
    user = None
    
    class Meta:
        model = VendorProfile
        fields = ['Company', 'FirstName', 'LastName', 'Website','SelectedCategory','SelectedFeature','SelectedMarket','ShortDecs',]

    def __init__(self, *args, **kw):
        super(AdminVendorProfileForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName  
        self.fields['Website'].initial = self.instance.Website
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['BusinessTelephone'].initial = self.instance.BusinessTelephone
        self.fields['ShortDecs'].initial = self.instance.ShortDecs
        self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
        self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
        self.fields['SelectedMarket'].initial = self.instance.SelectedMarket.values_list('pk',flat=True)
        self.fields['Email'].initial = self.instance.user.email
        self.fields['Approved'].initial = self.instance.Approved
            
    def save(self, request):
        """
        vendor signup
        """
        try:
            self.user = self.instance.user
        except:
            self._errors = ErrorList(['An account with that email already exists.'])
            return 
           
        self.instance.user.email = self.cleaned_data['Email']   
        self.instance.Company = self.cleaned_data['Company']
        self.instance.FirstName = self.cleaned_data['FirstName']
        self.instance.LastName = self.cleaned_data['LastName']
        self.instance.Website = self.cleaned_data['Website']
        self.instance.Telephone = self.cleaned_data['Telephone']
        self.instance.BusinessTelephone = self.cleaned_data['BusinessTelephone']
        self.instance.Approved = self.cleaned_data['Approved']
        self.instance.save()
        
        self.instance.SelectedCategory.clear()
        for c in request.POST.getlist('SelectedCategory'):
            try:
                self.instance.SelectedCategory.add(c)
            except IntegrityError:
                pass
        self.instance.SelectedFeature.clear()
        for f in request.POST.getlist('SelectedFeature'):
            try:
                self.instance.SelectedFeature.add(f)
            except IntegrityError:
                pass
        self.instance.SelectedMarket.clear()
        for m in request.POST.getlist('SelectedMarket'):
            try:
                self.instance.SelectedMarket.add(m)
            except IntegrityError:
                pass
                                        
        self._errors = ErrorList(['Successfully submitted!'])
    
    def render_row(self):
        if self.instance.Approved == 1:
            status = '<label class="complete">Approved</label>'
        elif self.instance.Approved == 0:
            status = '<label class="error">Declined</label>'
        elif self.instance.Approved == -1:
            status = '<label class="unknown">New</label>'
        return """
                <td><a href="#" class="doReveal" data-id="%s" id="profile_%s">%s</a></td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                %s
                </td>
                """ % (self.instance.id,
                        self.instance.id,
                        self.instance.Company,
                        self.instance.user.email,
                        self.instance.FirstName,
                        self.instance.LastName,
                        self.instance.Website,
                        self.instance.DateSubmitted, 
                        status)

class AdminMarketForm(forms.ModelForm):
    
    Name = models.CharField(max_length=100)
    Date = forms.DateField(initial=datetime.today)
    StartDate = forms.DateField(initial=datetime.today)
    EndDate = forms.DateField(initial=datetime.today)  
    SubmissionDate = forms.DateField(initial=datetime.today)
    
    class Meta:
        model = Market
        fields = ['Name', 'Date', 'StartDate', 'EndDate', 'SubmissionDate', ]

    def __init__(self, *args, **kw):
        super(AdminMarketForm, self).__init__(*args, **kw)
        self.fields['Name'].initial = self.instance.Name
        self.fields['Date'].initial = self.instance.Date
        self.fields['StartDate'].initial = self.instance.StartDate  
        self.fields['EndDate'].initial = self.instance.EndDate
        self.fields['SubmissionDate'].initial = self.instance.SubmissionDate
            
    def save(self, request):
        """
        vendor signup
        """
        self.instance.Name = self.cleaned_data['Name']
        self.instance.Date = self.cleaned_data['Date']
        self.instance.StartDate = self.cleaned_data['StartDate']
        self.instance.EndDate = self.cleaned_data['EndDate']
        self.instance.SubmissionDate = self.cleaned_data['SubmissionDate']
        self.instance.save()
                                        
        self._errors = ErrorList(['Successfully submitted!'])
    
    def render_row(self):
        return """
                <td><a href="#" class="doReveal" data-id="%s" id="profile_%s">%s %s</a>
                    <br />
                    <p class="textIndent"><a href="/vendor_profile_report/?market=%s&status=All&term=">View Profiles</a> | 
                    <a href="/vendor_accounts_report/?market=%s&status=All&term=">View Vendors</a></p></td>
                <td>%s - %s</td>
                <td>%s</td>
                <td><label class="complete">%s</label></td>
                <td><label class="incomplete">%s</label></td>
                <td><label class="waiting">%s</label></td>
                """ % (self.instance.id,
                        self.instance.id,
                        self.instance.Name,
                        self.instance.Date.strftime('%Y'),
                        self.instance.id,
                        self.instance.id,
                        self.instance.StartDate.strftime('%m/%d/%Y'),
                        self.instance.EndDate.strftime('%m/%d/%Y'),
                        self.instance.total,
                        self.instance.accepted,
                        self.instance.rejected,
                        self.instance.waitlisted)
                                                
class AdminVendorApplicationForm(forms.ModelForm):
    
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}), required=True)
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}), required=True)  
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone'}), required=True)
    CellPhone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell Phone'}), required=True)
    AppID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Application ID'}), required=True)
    ContractID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Contract ID'}), required=True)
    Twitter = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Twitter'}), required=False)
    Facebook = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Facebook'}), required=False)
    Status = forms.CharField(required=False)
    
    BoothApplied = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Booth Applied'}), required=True)
    BoothApproved = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Booth Approved'}), required=True)
    Notes = forms.CharField(widget = forms.Textarea, required=False)
    Deposit = forms.CharField(required=False)
    PaymentInfo = forms.CharField(widget = forms.CheckboxInput, required=False)
    AdditionalElectric = forms.CharField(required=False)
    #models.CharField(max_length=50, blank=True, null=True)
    
    SelectedCategory = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductCategory.objects.filter(ForProfile=False))
    SelectedFeature = forms.ModelMultipleChoiceField(widget=UsmCheckboxSelectMultiple(), queryset=ProductFeature.objects.filter(ForProfile=True))
    
    class Meta:
        model = MarketContract
        fields = ['Company', 'Website','SelectedCategory','SelectedFeature',]

    def __init__(self, *args, **kw):
        super(AdminVendorApplicationForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['Website'].initial = self.instance.Website
        self.fields['Email'].initial = self.instance.user.email
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['CellPhone'].initial = self.instance.Cell
        self.fields['AppID'].initial = self.instance.AppId
        self.fields['ContractID'].initial = self.instance.ContractId
        if not self.instance.accounting:
            accounting,created  = AccountingInfo.objects.get_or_create(Notes='Created')
            self.instance.accounting = accounting
            self.instance.save()
        self.fields['Twitter'].initial = self.instance.Twitter
        self.fields['Facebook'].initial = self.instance.Facebook
        self.fields['Status'].initial = self.instance.Status
        
        self.fields['BoothApplied'].initial = self.instance.accounting.BoothApplied
        self.fields['BoothApproved'].initial = self.instance.accounting.BoothApproved
        self.fields['Notes'].initial = self.instance.accounting.Notes
        self.fields['Deposit'].initial = self.instance.accounting.Deposit
        self.fields['PaymentInfo'].initial = self.instance.accounting.PaymentInfo
        self.fields['AdditionalElectric'].initial = self.instance.accounting.AdditionalElectric
        
        self.fields['SelectedCategory'].initial = self.instance.SelectedCategory.values_list('pk',flat=True)
        self.fields['SelectedFeature'].initial = self.instance.SelectedFeature.values_list('pk',flat=True)
            
    def save(self, request):
        """
        vendor signup
        """
        try:
            self.user = self.instance.user
        except:
            self._errors = ErrorList(['An account with that email already exists.'])
            return 
              
        self.instance.Company = self.cleaned_data['Company']
        self.instance.Website = self.cleaned_data['Website']
        self.instance.user.email = self.cleaned_data['Email']
        self.instance.Telephone = self.cleaned_data['Telephone']
        self.instance.Cell = self.cleaned_data['CellPhone']
        self.instance.AppId = self.cleaned_data['AppID']
        self.instance.ContractId = self.cleaned_data['ContractID']
        self.instance.Twitter = self.cleaned_data['Twitter']
        self.instance.Facebook = self.cleaned_data['Facebook']
        self.instance.Status = self.cleaned_data['Status']
        self.instance.save()
        
        self.instance.accounting.BoothApplied = self.cleaned_data['BoothApplied']
        self.instance.accounting.BoothApproved = self.cleaned_data['BoothApproved']
        self.instance.accounting.Notes = self.cleaned_data['Notes']
        if (self.cleaned_data['Deposit'] == "False"):
            self.instance.accounting.Deposit = False
        else:                                        
            self.instance.accounting.Deposit = True
        if (self.cleaned_data['PaymentInfo'] == "False"):
            self.instance.accounting.PaymentInfo = False
        else:
            self.instance.accounting.PaymentInfo = True
        if (self.cleaned_data['AdditionalElectric'] == "False"):
            self.instance.accounting.AdditionalElectric = False
        else:
            self.instance.accounting.AdditionalElectric = True
        self.instance.accounting.save()
        
        self.instance.SelectedCategory.clear()
        for c in request.POST.getlist('SelectedCategory'):
            try:
                self.instance.SelectedCategory.add(c)
            except IntegrityError:
                pass
        self.instance.SelectedFeature.clear()
        for f in request.POST.getlist('SelectedFeature'):
            try:
                self.instance.SelectedFeature.add(f)
            except IntegrityError:
                pass
                         
        self._errors = ErrorList(['Successfully submitted!'])
    
    def render_row(self):
        
        if self.instance.Status == "Accepted":
            status = '<label class="complete">Accepted</label>'
        elif self.instance.Status == "Rejected":
            status = '<label class="error">Rejected</label>'
        elif self.instance.Status == "Waitlist":
            status = '<label class="incomplete">Waitlist</label>'
        elif self.instance.Status != "Accepted" and self.instance.Status != "Rejected" and self.instance.Status != "Waitlist":
            status = '<label class="unknown">New</label>'
        
        if self.instance.accounting.PaymentStatus:
            ps = "Submitted"
        else:
            ps = "Not Submitted"
            
        return """
                <td><a href="#" class="doReveal" data-id="%s" id="profile_%s">%s</a></td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>
                %s
               </td>
               <td>
                %s
               </td>
                """ % (self.instance.id,
                        self.instance.id,
                        self.instance.Company,
                        self.instance.ContractId,
                        self.instance.AppId,     
                        self.instance.Website,
                        self.instance.user.email,
                        self.instance.Telephone,
                        status,
                        ps
                        )
                        
    def render_row_two(self):
        if self.instance.accounting.BoothApplied:
            bappl = self.instance.accounting.BoothApplied
        else:
            bappl = "None"
        
        if self.instance.accounting.BoothApplied:
            bappr = self.instance.accounting.BoothApproved
        else:
            bappr = "None"
        
        if self.instance.accounting.Deposit == True:
            deposit = "Paid"
        else:
            deposit = "Not Paid"
        
        if self.instance.accounting.PaymentInfo:
            paymentinfo = "Yes"
        else:
            paymentinfo = "No"
        
        if self.instance.accounting.AdditionalElectric == 1:
            additionalelectric = "Yes"
        else:
            additionalelectric = "No"
            
        return """
                <td colspan="8">
                	<div class="row">
                        <div class="three columns">
                         <strong>%s, %s %s</strong>
                        </div>
                         <div class="three columns">
                         <strong>Cell:</strong> %s
                        </div>
                         <div class="three columns">
                         <strong>Booth Applied:</strong> %s
                        </div>
                        <div class="three columns">
                         <strong>Booth Approved:</strong> %s
                        </div> 
                    </div>
                    <div class="row">
                        <div class="three columns">
                         <strong>Alt Phone:</strong> %s
                        </div>
                         <div class="three columns">
                         <strong>Deposit:</strong> %s
                        </div>
                        <div class="three columns">
                         <strong>Payment Info:</strong> <span class="cappie">%s</span>
                        </div>
                         <div class="three columns">
                         <strong>Addl Electric:</strong> <span class="cappie">%s</span>
                        </div>
                    </div>
                    <div class="row">
                        <div class="three columns">
                         <strong>Twitter:</strong> %s
                        </div>
                         <div class="three columns">
                         <strong>Facebook:</strong> %s
                        </div>
                         <div class="six columns">
                         <a href="/vendor_application_detail_one/%s/" class="button tiny">View Application</a>
                        </div>
                  
                    </div>
                    <div class="row">
                    	<div class="twelve columns">
                        	<p><strong>Notes:</strong> %s</p>
                        </div>
                    </div>
                    
                   <div class="row">
                    	<div class="twelve columns">
                        	<p>&nbsp;</p>
                        </div>
                    </div>
                </td>""" % ( self.instance.Address,
                  self.instance.City,
                  self.instance.State,
                  self.instance.Cell,
                  bappl,
                  bappr,
                  self.instance.TelephoneAlt,
                  deposit,
                  paymentinfo,
                  additionalelectric,
                  self.instance.Twitter,
                  self.instance.Facebook,
                  self.instance.id,
                  self.instance.accounting.Notes
                )
                        
class AdminVendorAccountingForm(forms.ModelForm):
    
    Company = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company'}), required=True)
    Website = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Website'}), required=True)  
    Email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}), required=True)
    Telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone'}), required=True)
    CellPhone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cell Phone'}), required=True)
    AppID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Application ID'}), required=True)
    ContractID = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Contract ID'}), required=True)
    Twitter = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Twitter'}), required=False)
    Facebook = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Facebook'}), required=False)
    Status = forms.CharField(required=False)
    
    BoothApplied = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Booth Applied'}), required=True)
    BoothApproved = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Booth Approved'}), required=True)
    Notes = forms.CharField(widget = forms.Textarea, required=False)
    Deposit = forms.CharField(required=False)
    PaymentInfo = forms.CharField(widget = forms.CheckboxInput, required=False)
    AdditionalElectric = forms.CharField(required=False)
    InvoiceId = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Invoice ID'}), required=False)
    InvoiceDate = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Invoice Date'}), required=False)
    DepositAmount = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Deposit Amount'}), required=False)
    PaymentVia = forms.IntegerField(required=False)
    TransactionId = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Transaction ID'}), required=False)
    RentAdjustments = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Rent Adjustments'}), required=False)
    PlacementFee = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'PlacementFee'}), required=False)
    PaidInFullDate = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Paid In Full Date'}), required=False)
    RejectedDate = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Rejected Date'}), required=False)
    #models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        model = MarketContract
        fields = ['Company', 'Website']

    def __init__(self, *args, **kw):
        super(AdminVendorAccountingForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['Website'].initial = self.instance.Website
        self.fields['Email'].initial = self.instance.user.email
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['CellPhone'].initial = self.instance.Cell
        self.fields['AppID'].initial = self.instance.AppId
        self.fields['ContractID'].initial = self.instance.ContractId
        if not self.instance.accounting:
            accounting,created  = AccountingInfo.objects.get_or_create(Notes='Created')
            self.instance.accounting = accounting
            self.instance.save()
        self.fields['Twitter'].initial = self.instance.Twitter
        self.fields['Facebook'].initial = self.instance.Facebook
        self.fields['Status'].initial = self.instance.Status
        
        self.fields['BoothApplied'].initial = self.instance.accounting.BoothApplied
        self.fields['BoothApproved'].initial = self.instance.accounting.BoothApproved
        self.fields['Notes'].initial = self.instance.accounting.Notes
        self.fields['Deposit'].initial = self.instance.accounting.Deposit
        self.fields['PaymentInfo'].initial = self.instance.accounting.PaymentInfo
        self.fields['AdditionalElectric'].initial = self.instance.accounting.AdditionalElectric
        
        self.fields['InvoiceId'].initial = self.instance.accounting.Invoice
        if self.instance.accounting.InvoiceDate:
            self.fields['InvoiceDate'].initial = self.instance.accounting.InvoiceDate.strftime('%Y-%m-%d')
        else:
            self.fields['InvoiceDate'].initial = now().strftime('%Y-%m-%d')
        if self.instance.accounting.DepositAmount > 0:
            self.fields['DepositAmount'].initial = self.instance.accounting.DepositAmount
        self.fields['PaymentVia'].initial = self.instance.accounting.PaymentVia
        self.fields['TransactionId'].initial = self.instance.accounting.Transaction
        if self.instance.accounting.RentAdjustments > 0:
            self.fields['RentAdjustments'].initial = self.instance.accounting.RentAdjustments
        if self.instance.accounting.PlacementFee > 0:
            self.fields['PlacementFee'].initial = self.instance.accounting.PlacementFee
        if self.instance.accounting.PaidInFullDate:
            self.fields['PaidInFullDate'].initial = self.instance.accounting.PaidInFullDate.strftime('%Y-%m-%d')
        else:
            self.fields['PaidInFullDate'].initial = now().strftime('%Y-%m-%d')
        
        if self.instance.accounting.RejectedDate:
            self.fields['RejectedDate'].initial = self.instance.accounting.RejectedDate.strftime('%Y-%m-%d')
        else:
            self.fields['RejectedDate'].initial = now().strftime('%Y-%m-%d')
        
    def save(self, request):
        """
        vendor signup
        """
        try:
            self.user = self.instance.user
        except:
            self._errors = ErrorList(['An account with that email already exists.'])
            return 
              
        self.instance.Company = self.cleaned_data['Company']
        self.instance.Website = self.cleaned_data['Website']
        self.instance.user.email = self.cleaned_data['Email']
        self.instance.Telephone = self.cleaned_data['Telephone']
        self.instance.Cell = self.cleaned_data['CellPhone']
        self.instance.AppId = self.cleaned_data['AppID']
        self.instance.ContractId = self.cleaned_data['ContractID']
        self.instance.Twitter = self.cleaned_data['Twitter']
        self.instance.Facebook = self.cleaned_data['Facebook']
        self.instance.Status = self.cleaned_data['Status']
        self.instance.save()
        
        self.instance.accounting.BoothApplied = self.cleaned_data['BoothApplied']
        self.instance.accounting.BoothApproved = self.cleaned_data['BoothApproved']
        self.instance.accounting.Notes = self.cleaned_data['Notes']
        if (self.cleaned_data['Deposit'] == "False"):
            self.instance.accounting.Deposit = False
        else:                                        
            self.instance.accounting.Deposit = True
        if (self.cleaned_data['PaymentInfo'] == "False"):
            self.instance.accounting.PaymentInfo = False
        else:
            self.instance.accounting.PaymentInfo = True
        if (self.cleaned_data['AdditionalElectric'] == "False"):
            self.instance.accounting.AdditionalElectric = False
        else:
            self.instance.accounting.AdditionalElectric = True
        self.instance.accounting.Invoice = self.cleaned_data['InvoiceId']
        self.instance.accounting.InvoiceDate = self.cleaned_data['InvoiceDate']
        if self.cleaned_data['DepositAmount']:
            self.instance.accounting.DepositAmount = self.cleaned_data['DepositAmount']
        self.instance.accounting.PaymentVia = self.cleaned_data['PaymentVia']
        self.instance.accounting.Transaction = self.cleaned_data['TransactionId']
        if self.cleaned_data['RentAdjustments']:
            self.instance.accounting.RentAdjustments = self.cleaned_data['RentAdjustments']
        if self.cleaned_data['PlacementFee']:
            self.instance.accounting.PlacementFee = self.cleaned_data['PlacementFee']
        self.instance.accounting.PaidInFullDate = self.cleaned_data['PaidInFullDate']
        self.instance.accounting.RejectedDate = self.cleaned_data['RejectedDate']
        
        self.instance.accounting.save()
        
        self._errors = ErrorList(['Successfully submitted!'])
    
    def render_row(self):
        
        if self.instance.Status == "Accepted":
            status = '<label class="complete">Accepted</label>'
        elif self.instance.Status == "Rejected":
            status = '<label class="error">Rejected</label>'
        elif self.instance.Status == "Waitlist":
            status = '<label class="incomplete">Waitlist</label>'
        elif self.instance.Status != "Accepted" and self.instance.Status != "Rejected" and self.instance.Status != "Waitlist":
            status = '<label class="unknown">New</label>'
        
        if self.instance.accounting.PaymentStatus:
            ps = "Submitted"
        else:
            ps = "Not Submitted"
            
        return """
                <td><a href="#" class="doReveal" data-id="%s" id="profile_%s">%s</a></td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>%s</td>
               <td>
                %s
               </td>
               <td>
                %s
               </td>
                """ % (self.instance.id,
                        self.instance.id,
                        self.instance.Company,
                        self.instance.ContractId,
                        self.instance.AppId,     
                        self.instance.Website,
                        self.instance.user.email,
                        self.instance.Telephone,
                        status,
                        ps
                        )
                        
    def render_row_two(self):
        if self.instance.accounting.BoothApplied:
            bappl = self.instance.accounting.BoothApplied
        else:
            bappl = "None"
        
        if self.instance.accounting.BoothApplied:
            bappr = self.instance.accounting.BoothApproved
        else:
            bappr = "None"
        
        if self.instance.accounting.Deposit == True:
            deposit = "Paid"
        else:
            deposit = "Not Paid"
        
        if self.instance.accounting.PaymentInfo:
            paymentinfo = "Yes"
        else:
            paymentinfo = "No"
        
        if self.instance.accounting.AdditionalElectric == 1:
            additionalelectric = "Yes"
        else:
            additionalelectric = "No"
        
        if self.instance.accounting.DepositAmount:
            depositAmount = "$" + str(self.instance.accounting.DepositAmount)
        else:
            depositAmount = "$0.00"
            
        if self.instance.accounting.PaymentVia == 0:
            paymentVia = "Paypal"
        elif self.instance.accounting.PaymentVia == 1:
            paymentVia = "Check"
        else:
            paymentVia = "None"
        
        if self.instance.accounting.DepositAmount:
            depositAmount = "$" + str(self.instance.accounting.DepositAmount)
        else:
            depositAmount = "$0.00"
            
        if self.instance.accounting.RentAdjustments:
            rentAdjustments = "$" + str(self.instance.accounting.RentAdjustments)
        else:
            rentAdjustments = "$0.00"
        
        if self.instance.accounting.PlacementFee:
            placementFee = "$" + str(self.instance.accounting.PlacementFee)
        else:
            placementFee = "$0.00"
            
            
        return """
                <td colspan="8">
                	<div class="row">
                        <div class="three columns">
                         <strong>%s, %s %s</strong>
                        </div>
                         <div class="three columns">
                         <strong>Cell:</strong> %s
                        </div>
                         <div class="three columns">
                         <strong>Booth Applied:</strong> %s
                        </div>
                        <div class="three columns">
                         <strong>Booth Approved:</strong> %s
                        </div> 
                    </div>
                    <div class="row">
                        <div class="three columns">
                         <strong>Alt Phone:</strong> %s
                        </div>
                         <div class="three columns">
                         <strong>Deposit:</strong> %s
                        </div>
                        <div class="three columns">
                         <strong>Payment Info:</strong> <span class="cappie">%s</span>
                        </div>
                         <div class="three columns">
                         <strong>Addl Electric:</strong> <span class="cappie">%s</span>
                        </div>
                    </div>
                    
                    <div class="row">
                     
                        <div class="three columns">
                         <strong>Invoice:</strong> %s
                        </div>
                        <div class="three columns left">
                         <strong>Invoice Date:</strong> %s
                        </div>
                        <div class="three columns">
                        	<strong>Deposit Amount:</strong> %s
                        </div>
                        <div class="three columns">
                        	<strong>Payment:</strong> %s
                        </div>
                    </div>
                    <div class="row">
                     
                        <div class="three columns">
                        	<strong>Transaction:</strong> %s
                        </div>
                        <div class="three columns">
                         <strong>Rent Adjustments:</strong> %s
                        </div>
                         <div class="three columns left">
                         <strong>Placement Fee:</strong> %s
                        </div>
                       
                    </div>
            
                    
                    <div class="row">
                        
                        <div class="three columns">
                        	<strong>Paid in Full Date:</strong> %s
                        </div>
                        <div class="eight columns left">
                        	<strong>Rejected Date:</strong> %s
                        </div>
                  
                    </div>
                    
                    <div class="row">
                    	<div class="twelve columns">
                        	<p><strong>Notes:</strong> %s</p>
                        </div>
                    </div>
                    
                   <div class="row">
                    	<div class="twelve columns">
                        	<p>&nbsp;</p>
                        </div>
                    </div>
                </td>""" % ( self.instance.Address,
                  self.instance.City,
                  self.instance.State,
                  self.instance.Cell,
                  bappl,
                  bappr,
                  self.instance.TelephoneAlt,
                  deposit,
                  paymentinfo,
                  additionalelectric,
                  self.instance.accounting.Invoice,
                  self.instance.accounting.InvoiceDate,
                  depositAmount,
                  paymentVia,
                  self.instance.accounting.Transaction,
                  rentAdjustments,
                  placementFee,
                  self.instance.accounting.PaidInFullDate,
                  self.instance.accounting.RejectedDate,
                  self.instance.accounting.Notes
                )