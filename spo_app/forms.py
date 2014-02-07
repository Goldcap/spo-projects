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
    SelectedMailingLists = forms.ModelMultipleChoiceField(widget=SpoCheckboxSelectMultiple(), required=False, queryset=MailingListSource.objects.filter())
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
        rec.LastName = self.data['LastName']
        rec.Email = self.data['Email']
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
        #rec.Company = self.data['Company']
        rec.FirstName = self.data['FirstName']
        #rec.LastName = self.data['LastName']
        rec.Website = self.data['Website']
        #rec.Telephone = self.data['Telephone']
        #rec.BusinessTelephone = self.data['BusinessTelephone']
        if 'ShortDecs' in self.data:
            rec.ShortDecs = self.data['ShortDecs']
        rec.save()
            
        #except User.DoesNotExist:
        #    pass

        for l in request.POST.getlist('SelectedMailingLists'):
            try:
                rec.SelectedMailingLists.add(l)
            except IntegrityError:
                pass
        
        self._errors = ErrorList(['Your profile was successfully saved!'])
        
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
    ShortDecs = forms.CharField(widget = forms.Textarea, required=False)
    user = None
    
    class Meta:
        model = VendorProfile
        fields = ['Company', 'FirstName', 'LastName', 'Website', 'ShortDecs',]

    def __init__(self, *args, **kw):
        super(VendorProfileForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName  
        self.fields['Website'].initial = self.instance.Website
        self.fields['ShortDecs'].initial = self.instance.ShortDecs
        
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


################################
#   Administrative Versions    #
################################
        
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
    ShortDecs = forms.CharField(widget = forms.Textarea, required=False)
    Approved = forms.IntegerField()
    user = None
    
    class Meta:
        model = VendorProfile
        fields = ['Company', 'FirstName', 'LastName', 'Website','ShortDecs',]

    def __init__(self, *args, **kw):
        super(AdminVendorProfileForm, self).__init__(*args, **kw)
        self.fields['Company'].initial = self.instance.Company
        self.fields['FirstName'].initial = self.instance.FirstName
        self.fields['LastName'].initial = self.instance.LastName  
        self.fields['Website'].initial = self.instance.Website
        self.fields['Telephone'].initial = self.instance.Telephone
        self.fields['BusinessTelephone'].initial = self.instance.BusinessTelephone
        self.fields['ShortDecs'].initial = self.instance.ShortDecs
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
