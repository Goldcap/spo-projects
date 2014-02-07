import datetime
import pytz
import urllib

from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404, \
                             redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
    
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models import Max
from django.db.models import Count
from django.utils import simplejson as json
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.uploadedfile import UploadedFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils.timezone import make_aware, get_default_timezone, utc

from django.contrib.auth.views import password_reset
from django.contrib.auth.views import password_change
from django.shortcuts import render

from sorl.thumbnail import get_thumbnail

import StringIO
import xlsxwriter

from forms import *
from models import VendorProfile
from utils import isComplete, sendAnEmail, sendAdminEmail

def forgot_password(request):
    if request.method == 'POST':
        return password_reset(request, 
            from_email=request.POST.get('email'))
    else:
        return render(request, 'forgot_password.html')

def home(request):
    """
    page index
    """
    
    return render_to_response('home.html', {
    }, context_instance=RequestContext(request))
     
def index(request):
    """
    site index
    """
    return render_to_response('index.html', {
    }, context_instance=RequestContext(request))


######################
#  Public Features   #
######################

def profile_form(request):
    """
    New Vendor Profile
    """
    vendor = None
    if request.method == 'POST':
        form = VendorProfileForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            pass
            #form._errors = ErrorList(['All fields are required, please check your data.'])
    else:
        form = VendorProfileForm()
        
    return render_to_response('profile-form.html', 
    {'vendor':vendor,'form':form},
    context_instance=RequestContext(request))
    #return render_to_response('profile-form.html', {
    #}, context_instance=RequestContext(request))

def vendor_login(request):
    """
    """
    form_values = request.POST
    if request.method == 'POST':
        #form = VendorLoginForm(request.POST)
        user = authenticate(username=request.POST['Email'].strip(), password=request.POST['Password'].strip())
        try:
            profile = VendorProfile.objects.get(user=user)
            if user and user.is_active and profile.Approved == 1:
                login(request, user)
                ActivityLog.objects.create(user=user,activity="Login")
                #subject = 'Urban Space Holdings Vendor Login'
                #sendAdminEmail(subject,user,profile,"Vendor Login Market Director Notification",True)
            
                if ('next' in request.GET):
                    return redirect(request.GET['next'])
                else:
                    return redirect('/vendor_home/')
            elif user:
                return redirect('/vendor_pending/')
        except:
            pass
        
        form = VendorLoginForm()
        form._errors = ErrorList(['Invalid Email or Password.'])
        return render_to_response('vendor-login.html', {'form': form,'form_values':form_values
        }, context_instance=RequestContext(request))
                    
        
    else:
        form = VendorLoginForm()
        return render_to_response('vendor-login.html', {'form': form,'form_values':form_values
        }, context_instance=RequestContext(request))

def vendor_signup(request):
    """
    """
    form_values = request.POST
    if request.method == 'POST':
        form = VendorForm(request.POST)

        try:
            if form.is_valid():
                form.save()
                user = authenticate(username=request.POST['Email'].strip(), password=request.POST['Password'].strip())
                profile = VendorProfile.objects.get(user=user)
                
                subject = 'Urban Space Holdings Vendor Signup'
                sendAdminEmail(subject,user,profile,"Vendor Signup Market Director Notification",True)
                
                if user and profile.Approved == 1:
                    login(request, user)
                    if ('next' in request.GET):
                        return redirect(request.GET['next'])
                    else:
                        return redirect('/vendor_home/')
                else:
                    return redirect('/vendor_pending/')
        except:
            pass
            
        return render_to_response('vendor-signup.html', {'form': form,'form_values':form_values
        }, context_instance=RequestContext(request))
    else:
        form = VendorForm()
        return render_to_response('vendor-signup.html', {'form': form,'form_values':form_values
        }, context_instance=RequestContext(request))

def vendor_pending(request):
    """
    Vendor Acceptance Waiting Room
    """
    return render_to_response('vendor-pending.html', 
        context_instance=RequestContext(request))
        
def admin_login(request):
    """
    admin_login
    """
    if request.method == 'POST':
        #form = VendorLoginForm(request.POST)
        user = authenticate(username=request.POST['Email'].strip(), password=request.POST['Password'].strip())
                    
        if user and user.is_active and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('/vendor_profile_report/')
        else:
            form = VendorLoginForm()
            form._errors = ErrorList(['Invalid Email or Password.'])
            return render_to_response('admin-login.html', {'form': form,}, 
                context_instance=RequestContext(request))
    else:
        form = VendorLoginForm()
        return render_to_response('admin-login.html', {'form': form,}, 
            context_instance=RequestContext(request))

def faq(request, pageno='1'):
    """
    Public FAQ
    """
    faq_list = FAQQuestion.objects.filter(for_vendor=False)
    paginator = Paginator(faq_list, 4) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        faqs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        faqs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        faqs = paginator.page(paginator.num_pages)

    
    return render_to_response('faq.html', {'faqs':faqs,
    }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = AdminVendorApplicationForm(request.POST, instance=marketcontract)
        if form.is_valid():
            form.save( request )
            resp = {"message":"message","status":"success",
                "result":form.render_row(),
                "more": form.render_row_two()
            }
            return HttpResponse(json.dumps(resp),content_type="application/json")
        else:
            print form.errors
            resp = {"message":"message","status":"failure","result":""}
            return HttpResponse(json.dumps(resp),content_type="application/json")
            
def mailing_list(request):
    """
    Mailing List Form
    """
    
    error = False
    
    if request.method == 'POST':
        fields = {"fname","lname","email","zip_code"}
        for field in fields:
            if request.POST[field] == "":
                error = True
        
        try:
            validate_email( request.POST['email'] )
        except ValidationError:
            error = True
            
        if error:
            template ='mailing_list.html' 
        else:
            
            ml,created = MailingList.objects.get_or_create(EmailAddress=request.POST['email'])
            ml.FirstName = request.POST['fname']
            ml.LastName = request.POST['lname']
            ml.EmailAddress = request.POST['email']
            ml.ZipCode = request.POST['zip_code']
            ml.save()
            
            template ='mailing_list_embed.html'
             
        return render_to_response(template, {"error":error,
                                            "fname":request.POST['fname'],
                                            "lname":request.POST['lname'],
                                            "email":request.POST['email'],
                                            "zip_code":request.POST['zip_code']}, 
        context_instance=RequestContext(request))
    else:
        return render_to_response('mailing_list.html', {"error":error}, 
        context_instance=RequestContext(request))
    
######################
#  Vendor Features   #
######################

@login_required
def vendor_home(request):
    """
    My Profile
    """
    
    form_values = request.POST
    vendor_images = None
    if request.method == 'POST':
        vendor = VendorProfile.objects.get(user=request.user)
        form = VendorForm(request.POST, instance=vendor)
        form.save_vendor_home( request )
    else:
        vendor = VendorProfile.objects.get(user=request.user)
        form = VendorForm(instance=vendor)
        vendor_images = vendor.SelectedImages.all()
    
    return render_to_response('vendor-home.html', {'vendor':vendor,'form':form,'images':vendor_images},
    context_instance=RequestContext(request))

@login_required
def vendor_images(request):
    """
    My Photos
    """
    vendor = VendorProfile.objects.get(user=request.user)
    images = VendorImage.objects.filter(user=request.user)
    
    return render_to_response('vendor-images.html', 
        {'vendor':vendor,
        'images':images},
        context_instance=RequestContext(request))


@login_required
@csrf_exempt
def market_contract_image(request, vendor_id):
    """
    
    Market Contract Images 
    
    """
        
    if request.method == 'POST':
        
        atype = request.POST["atype"]
        
        profile = VendorProfile.objects.get(pk=vendor_id)
            
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        #getting file data for farther manipulations
        file = request.FILES[u'files[]']
        thefile = file.name
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size
        
        theimage = VendorImage()
        if ('title' in request.POST):
            theimage.caption = request.POST["title"]
        theimage.filename=str(thefile)
        theimage.ImgFile=file
        theimage.user = request.user
        theimage.save()
        filename = theimage.caption
        
        profile.SelectedImages.add(theimage)
        id = theimage.id
        im = get_thumbnail(theimage.ImgFile, "80x80", quality=50)
        thumb_url = "/static/media/" + im.url
        file_url = "/static/media/uploads/vendor_images/" + filename
            
        files = []
        files.append({ "id":id, 
                       "name":filename, 
                       "size":file_size, 
                       "url":file_url, 
                       "thumbnail_url":thumb_url,
                       "type":"image/jpg", })
        result = {"files":files}
        response_data = json.dumps(result)
    return HttpResponse(response_data, mimetype='application/json')
    
@login_required
@csrf_exempt
def market_contract_image_delete(request):
    """
    
    Market Contract Image Delete 
    
    """
    
    response_data = None    
    if request.method == 'POST':
        
        atype = request.POST["atype"]
        iid = request.POST["image"]
        
        theimage = VendorImage.objects.get(pk=iid)
        if theimage and theimage.user and (theimage.user == request.user):
            theimage.delete()
               
        result = {"response":True,
                  "image":iid}
        response_data = json.dumps(result)
        
    return HttpResponse(response_data, mimetype='application/json')
    
@login_required
def vendor_faq(request, pageno='1'):
    """
    Market FAQ
    """
    faq_list = FAQQuestion.objects.filter(for_vendor=True)
    paginator = Paginator(faq_list, 4) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        faqs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        faqs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        faqs = paginator.page(paginator.num_pages)

    
    return render_to_response('vendor-faq.html', {'faqs':faqs,
    }, context_instance=RequestContext(request))
    

######################
#   Admin Features   #
######################

@staff_member_required
def vendor_profile_report(request):
    """
    Profile Reports
    """
    
    query = Q()
    form = {}
    order_by = request.GET.get('order_by', 'DateSubmitted')
    
    if ("market" in request.GET) and (request.GET["market"] != "All"):
        query = query & Q(SelectedMarket=Market.objects.get(pk=request.GET["market"]))
        form["market"]=int(request.GET["market"])
    
    
    if ("status" in request.GET) and (request.GET["status"] != "All"):
        form["status"] = request.GET["status"]
        if request.GET["status"] == "Approved":
            query = query & Q(Approved=1)
        elif request.GET["status"] == "New":
            query = query & Q(Approved=-1)
        else:
            query = query & Q(Approved=0)
        
    if ("term" in request.GET):
        form["term"] = request.GET["term"]
        query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                            Q(LastName__icontains=request.GET["term"]) |
                            Q(user__email__icontains=request.GET["term"])|
                            Q(Website__icontains=request.GET["term"]) |
                            Q(Company__icontains=request.GET["term"]))
    
        
    if query:
        profile_list = VendorProfile.objects.filter(query).order_by(order_by)
    else:
        profile_list = VendorProfile.objects.filter().order_by(order_by)
    paginator = Paginator(profile_list, 25) # Show 25 contacts per page

    markets = Market.objects.all()
    
    page = request.GET.get('page')
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        profiles = paginator.page(paginator.num_pages)
    
    return render_to_response('vendor-profile-report.html', 
        {"profiles":profiles,"markets":markets,"form":form,"request":request}, 
        context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def vendor_profile_form(request, profile_id):
    """
    New Vendor Profile
    """
    vendor = VendorProfile.objects.get(pk=profile_id)
    if request.method == 'POST':
        form = AdminVendorProfileForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save( request )
            resp = {"message":"message","status":"success","result":form.render_row()}
            return HttpResponse(json.dumps(resp),content_type="application/json")
        else:
            resp = {"message":"message","status":"failuer","result":""}
            return HttpResponse(json.dumps(resp),content_type="application/json")
    else:
        form = AdminVendorProfileForm(instance=vendor)
        
    return render_to_response('vendor-profile-form.html', 
                    {'vendor':vendor,'form':form},
                    context_instance=RequestContext(request))


@staff_member_required
def customer_report(request):
    """
    Customer Report
    """
    query = Q()
    form = {}
    
    order_by = request.GET.get('order_by', 'FirstName')
    
    if ("term" in request.GET):
        form["term"] = request.GET["term"]
        query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                            Q(LastName__icontains=request.GET["term"]) |
                            Q(EmailAddress__icontains=request.GET["term"]) |
                            Q(ZipCode=request.GET["term"]))
    
    if query:
        profile_list = MailingList.objects.filter(query).order_by(order_by)
    else:
        profile_list = MailingList.objects.filter().order_by(order_by)
    paginator = Paginator(profile_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        profiles = paginator.page(paginator.num_pages)

    
    return render_to_response('customer-report.html', 
        {"profiles":profiles,"form":form,"request":request}, 
        context_instance=RequestContext(request))


@staff_member_required
def vendor_login_activity(request):
    """
    Vendor Login
    """
    query = Q()
    form = {}
    
    order_by = request.GET.get('order_by', 'llogin')
        
    if ("term" in request.GET):
        form["term"] = request.GET["term"]
        query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                            Q(LastName__icontains=request.GET["term"]) |
                            Q(user__email__icontains=request.GET["term"]) |
                            Q(Company__icontains=request.GET["term"]))
    
    if query:
        profile_list = VendorProfile.objects.filter(query).annotate(llogin=Max(
        'user__activitylog__DateAdded')).order_by(order_by)
    else:
        profile_list = VendorProfile.objects.filter(Approved=True).annotate(llogin=Max(
        'user__activitylog__DateAdded')).order_by(order_by)
    paginator = Paginator(profile_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        profiles = paginator.page(paginator.num_pages)
    
    return render_to_response('vendor-login-activity.html', 
        {"profiles": profiles,"form":form,"request":request},
        context_instance=RequestContext(request))

def export_report(request, source):
    
    # create a workbook in memory
    output = StringIO.StringIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(source)
    
    header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'blue'})

    query = Q()
    order_by = request.GET.get('order_by', 'DateSubmitted')
    
    if (source == 'vendor_profile_report'):
        
        headers = ['Company','Email','First Name','Last Name','Website','Date']
        
        if ("market" in request.GET) and (request.GET["market"] != "All"):
            query = query & Q(SelectedMarket=Market.objects.get(pk=request.GET["market"]))
            
        if ("status" in request.GET) and (request.GET["status"] != "All"):
            if request.GET["status"] == "Approved":
                query = query & Q(Approved=1)
            elif request.GET["status"] == "New":
                query = query & Q(Approved=-1)
            else:
                query = query & Q(Approved=0)
            
        if ("term" in request.GET):
            query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                                Q(LastName__icontains=request.GET["term"]) |
                                Q(user__email__icontains=request.GET["term"])|
                                Q(Website__icontains=request.GET["term"]) |
                                Q(Company__icontains=request.GET["term"]))
        
            
        if query:
            profile_list = VendorProfile.objects.filter(query).order_by(order_by)
        else:
            profile_list = VendorProfile.objects.filter().order_by(order_by)
        
        j=0
        for header in headers:
            worksheet.write(0, j, header, header_format)
            j=j+1
        
        i=1
        for profile in profile_list:
            worksheet.write(i, 0, profile.Company)
            worksheet.write(i, 1, profile.user.email)
            worksheet.write(i, 2, profile.FirstName)
            worksheet.write(i, 3, profile.LastName)
            worksheet.write(i, 4, profile.Website)
            if profile.DateSubmitted:
                adate = profile.DateSubmitted.strftime("%Y-%m-%d %H:%M:%S")
                #date_time = datetime.strptime(profile.DateSubmitted,'%Y-%m-%d %H:%M:%S.%f')
                worksheet.write(i, 5, adate)
            else:
                worksheet.write(i, 5, "None")
            i=i+1
    
    elif (source == 'customer_report'):
        
        headers = ['Email','First Name','Last Name','Zip Code','Date']
        
        query = Q()
        
        order_by = request.GET.get('order_by', 'FirstName')
        
        if ("term" in request.GET):
            form["term"] = request.GET["term"]
            query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                                Q(LastName__icontains=request.GET["term"]) |
                                Q(EmailAddress__icontains=request.GET["term"]) |
                                Q(ZipCode=request.GET["term"]))
        
        if query:
            profile_list = MailingList.objects.filter(query).order_by(order_by)
        else:
            profile_list = MailingList.objects.filter().order_by(order_by)   
        
        j=0
        for header in headers:
            worksheet.write(0, j, header, header_format)
            j=j+1
        
        i=1
        for profile in profile_list:
            worksheet.write(i, 0, profile.EmailAddress)
            worksheet.write(i, 1, profile.FirstName)
            worksheet.write(i, 2, profile.LastName)
            worksheet.write(i, 3, profile.ZipCode)
            if profile.DateAdded:
                adate = profile.DateAdded.strftime("%Y-%m-%d %H:%M:%S")
                #date_time = datetime.strptime(profile.DateSubmitted,'%Y-%m-%d %H:%M:%S.%f')
                worksheet.write(i, 4, adate)
            else:
                worksheet.write(i, 4, "None")
            i=i+1
            
    elif (source == 'vendor_login_activity'):
        
        headers = ['Company','Email','First Name','Last Name','Date Added','Last Login']
        
        query = Q()
        
        order_by = request.GET.get('order_by', 'llogin')
        
        if ("term" in request.GET):
            form["term"] = request.GET["term"]
            query = query & (Q(FirstName__icontains=request.GET["term"]) | 
                                Q(LastName__icontains=request.GET["term"]) |
                                Q(user__email__icontains=request.GET["term"]) |
                                Q(Company__icontains=request.GET["term"]))
        
        if query:
            profile_list = VendorProfile.objects.filter(query).annotate(llogin=Max(
            'user__activitylog__DateAdded')).order_by(order_by)
        else:
            profile_list = VendorProfile.objects.filter(Approved=True).annotate(llogin=Max(
            'user__activitylog__DateAdded')).order_by(order_by) 
        
        j=0
        for header in headers:
            worksheet.write(0, j, header, header_format)
            j=j+1
        
        i=1
        for profile in profile_list:
            worksheet.write(i, 0, profile.Company)
            worksheet.write(i, 1, profile.user.email)
            worksheet.write(i, 2, profile.FirstName)
            worksheet.write(i, 3, profile.LastName) 
            if profile.user.date_joined:
                adate = profile.user.date_joined.strftime("%Y-%m-%d %H:%M:%S")
                #date_time = datetime.strptime(profile.DateSubmitted,'%Y-%m-%d %H:%M:%S.%f')
                worksheet.write(i, 4, adate)
            else:
                worksheet.write(i, 4, "None")
            if profile.last_login:
                adate = profile.last_login.strftime("%Y-%m-%d %H:%M:%S")
                #date_time = datetime.strptime(profile.DateSubmitted,'%Y-%m-%d %H:%M:%S.%f')
                worksheet.write(i, 5, adate)
            else:
                worksheet.write(i, 5, "None")
            i=i+1
           
    workbook.close()

    # construct response
    output.seek(0)
    response = HttpResponse(output.read(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=test.xlsx"

    return response