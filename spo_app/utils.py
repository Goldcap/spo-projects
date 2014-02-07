import datetime
import shortuuid
import datetime
import pytz

from django_mandrill.mail.mandrillmail import MandrillTemplateMail
from django.conf import settings

def generate_app_id(length=5):
    """
    Generate a short ID for this model.
    """
    id = shortuuid.uuid()[:length]
    date = datetime.datetime.now().strftime('%d%I%M%p%y-')
    return date + id
    
def isComplete(marketcontract):
    #FROM MARKET CONTRACT
    completed = 1
    #Market Form One
    
    errors = []
    fields = ['Company',
            'FirstName',
            'LastName',
            'DBA_BoothName',
            'Address',
            'Address1',
            'City',
            'State',
            'Zip',
            'Telephone',
            'Fax',
            'Cell',
            'Email',
            'Website',
            'Facebook',
            'Twitter',
            'FirstNameAlt',
            'LastNameAlt',
            'TelephoneAlt',
            'FaxAlt',
            'CellAlt',
            'EmailAlt',
            'RequiredID',
            'AboutYou',
            'YourExperience',
            ]          

    for key in fields:
        print "CHECKING " + str(key)
    
        val = getattr(marketcontract,key)
        print "VALUE IS " + str(val)
        if not val or val == '':
            completed = 0
            errors.append(key)
    
    if marketcontract.MarketFeesSingleBooth == 0 and \
        marketcontract.MarketFeesDoubleBooth == 0 and \
        marketcontract.MarketFeesHalfBooth == 0:
        errors.append('Booth Size')
        completed = 0
    
    if marketcontract.SelectedProducts.count() == 0:
        completed = 0
        errors.append('Products')
    
    if marketcontract.SelectedCategory.count() == 0:
        completed = 0
        errors.append('Categories')
    
    if marketcontract.SelectedBusinessType.count() == 0:
        completed = 0
        errors.append('Primary Business')
    
    if marketcontract.SelectedFeature.count() == 0:
        completed = 0
        errors.append('Product Pledge')
    
    if marketcontract.SelectedBusinessLogos.count() == 0:
        completed = 0
        errors.append('Business Logos')
    
    if marketcontract.SelectedDisplayImages.count() == 0:
        completed = 0
        errors.append('Display Images')
    
    if marketcontract.SelectedFeaturedMerchandise.count() == 0:
        completed = 0
        errors.append('Featured Merchandise')
    
    if marketcontract.accounting and marketcontract.accounting.Deposit == 0:
        completed = 0
        errors.append('Deposit Payment')
    
    marketcontract.IsCompleted = completed
    marketcontract.DateSubmitted = datetime.datetime.now() 
    marketcontract.save()
    return True
    
def sendAnEmail(subject,to,template,vars):
    template_content = []
    message = {
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'from_name': settings.DEFAULT_FROM_NAME,
        'subject': subject,
        'to': [{'email': to,}],
        'global_merge_vars': vars,
    }
    
    mail = MandrillTemplateMail(template, template_content, message)
    result = mail.send()
    
def sendAdminEmail(subject,user,profile,template,dtz=False,body=''):
    fmt = '%Y-%m-%d %H:%M:%S %Z'
    d = datetime.datetime.now(pytz.timezone("America/New_York"))
    dtz_string = d.strftime(fmt) + ' ' + "America/New_York"
    if dtz:
        subject = subject + ' at ' + dtz_string
    
    recips = []
    map(lambda x: recips.append({'email':x}), settings.ADMINISTRATOR_EMAIL)
    template_content = []
    message = {
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'from_name': settings.DEFAULT_FROM_NAME,
        'subject': subject,
        'to': recips,
        'global_merge_vars': [
            {'name':'SUBJECT', 'content': subject},
            {'name':'FIRST_NAME', 'content': profile.FirstName},
            {'name':'LAST_NAME', 'content': profile.LastName},
            {'name':'COMPANY', 'content': profile.Company},  
            {'name':'EMAIL', 'content': user.email},
            {'name':'CURRENT_DATE', 'content': dtz_string},
            {'name':'BODY', 'content': body}
        ],
    }
    
    mail = MandrillTemplateMail(template, template_content, message)
    result = mail.send()
    