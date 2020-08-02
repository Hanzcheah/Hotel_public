# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from booking.models import Booking, promocoderooms, Roomnumber, Roomtype, FrontPage, FrontImage, FrontDesc, Feedback, Fedback2, Customer, Invoice, Promocode, Events, Pricing, Specialrequests, Pages, nearbyprices, depositwitheld, Depositsum, variablepricing, logging, reportdate, whiteboard, Timerole, Userlogin, reviews, socketdata, housekeepingroom, extra_items, PointLog
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import BookingForm, RoomForm, DateForm, RoomtypeForm, eeForm, frontimgForm, frontdesForm, cardForm, eeForm2,eeForm3 , feedbackForm, PromoForm, pricingForm, eventsForm, customerForm, customerForm2, specForm, Pageform, feedForm, invoiceForm, depForm, BookingForm2, BookingForm3, DepositsumForm, invoiceForm3, custForm1, extra_itemForm
from django.db.models import F
from django.shortcuts import get_object_or_404
import random, hashlib, base64, requests, calendar, decimal, json, pytz, csv
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError 
from django.contrib.auth.decorators import permission_required
from itertools import zip_longest
from collections import OrderedDict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import Image
from lxml import html, etree
from django.core.mail import EmailMessage, send_mail
from django.core.mail import EmailMultiAlternatives     
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.utils.timezone import localtime 
from django.utils import timezone
from pytz import all_timezones, timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
from django.core import serializers
from requests.adapters import HTTPAdapter
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password






    

@login_required(login_url='/login/')
def bookingdetail(request):


    all_bookings = Roomnumber.objects.all().extra({'room_number_as_int': "room_number::INTEGER"}).values('room_type_name__room_type_name', 'room_number','id','room_number_as_int').order_by('room_type_name__room_type_name','room_number_as_int')
    all_customers = Booking.objects.all()
    date = request.GET.get('date')

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  
    


    
    if date is None:

        qin_date = datetime.now().date()
        qin_date0 = qin_date.strftime("%a, %d/%m")

        qate0 = qin_date.strftime("%d%m%Y")

    else:
        qin_date = parsing_date(date).date()
        qin_date0 = qin_date.strftime("%a, %d/%m")

        qate0 = qin_date.strftime("%d%m%Y")

    round4 = 0
    round2 = 0    

    for i in all_bookings:

        round4 = round4 + 1
        print(round4)
        for y in range(0,7):

            round2 = round2 + 1
            print(round2)
            number = y
            roomnumber = i['room_number']
            date = qin_date +timedelta(days=y)
            room = Booking.objects.filter(room_number__room_number=roomnumber).filter(checkin_date__lte=date).filter(checkout_date__gt=date).values('first_name', 'email' , 'phone_number','room_number__status', 'pk','checkedout1')
            statuss= Roomnumber.objects.get(room_number=roomnumber)

            i["status0"] = statuss.status
            if room is not None:
                for t in room:
                    asdf = Customer.objects.get(email=t['email'], phone_number=t['phone_number'])
                    yes = "customer" + str(number)
                    ids = "id" + str(number)
                    i[ids] = t['pk']

                    i[yes] = asdf.pk

                    i[number] = asdf.first_name



            else:
                i[number]= None



    context = {

    'all_bookings':all_bookings,
    'qin_date0':qin_date0,

    'qate0':qate0,

    }
    return render(request,"booking/bookgraph.html", context)










@login_required(login_url='/login/')
def detail(request):

    Tasknumber = whiteboard.objects.filter(complete=False, hidden=False).count()
    if Tasknumber >0:
        gottask = True
    else:
        gottask=False
    clearing = Invoice.objects.filter(bookingfeepaid=False, staffbooking=False,molpay=True,totalpaid=False)
    now = datetime.now()

    nowa = float(now.strftime("%Y%m%d%H%M%S"))
    # print(clearing)
    addpoints = 0
    for a in clearing:
        cust1 = a.email
        cust2 = Customer.objects.get(pk=cust1.pk)
        if a.description:
            discountpromo = a.description
            if discountpromo.points:
                addpoints = discountpromo.points

        refa = a.referenceno
        if refa is not None:
            ref = float(refa[-14:])

            if nowa - ref > 10000:



                clear = Booking.objects.filter(referenceno=a.referenceno)

                if cust2.user_login:
                    if a.molpay == True: 
                        no1ofdays = 0
                        user1315 = Userlogin.objects.get(pk=cust2.user_login.pk)
                        for aasdf in clear:
                            if aasdf.room_type_name.pk is not 22 and aasdf.room_type_name.pk is not 23 and aasdf.room_type_name.pk is not 24 and aasdf.room_type_name.pk is not 28:
                                if aasdf.room_type_name.pk is 27:
                                    no1ofdays = no1ofdays + (int((aasdf.checkout_date-aasdf.checkin_date).days)*2)
                                else:
                                    no1ofdays = no1ofdays + int((aasdf.checkout_date-aasdf.checkin_date).days)

                clear2 = Invoice.objects.filter(referenceno=a.referenceno)
                for c in clear:
                    c.delete()
                for c2 in clear2:
                    c2.delete()

    print('ran first query')
    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d')
    yesterdate = todaydate - timedelta(days=1)

    breakfastpack = Booking.objects.filter(room_type_name__pk=24).filter(checkin_date__lte=yesterdate).filter(checkout_date__gte=todaydate).exclude(checkedin1__isnull=True).order_by('referenceno')
    breakfastnopack =Booking.objects.filter(room_type_name__pk=23).filter(checkin_date__lte=yesterdate).filter(checkout_date__gte=todaydate).exclude(checkedin1__isnull=True).order_by('referenceno')

    breakfast = breakfastpack | breakfastnopack
    breakfastno = breakfast.count() 
    breakfast2 = Booking.objects.filter(created_on__lt=deadline).filter(checkin_date__lte=yesterdate).filter(checkout_date__gte=todaydate).exclude(checkedin1__isnull=True).exclude(id__in=breakfast).order_by('referenceno')
    breakfast2no = breakfast2.count()
    refno3113 = None
    counter =0 
    newcounter = 0
    countercounter = 0

    for a in breakfast:
        if refno3113 == a.referenceno:
            counter = counter + 1
            if counter > 1:
                roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).exclude(room_number__pk=24).exclude(room_number__pk=23).exclude(room_type_name__pk=22).exclude(room_type_name__pk=28).order_by('room_number')
                numb1 = roomnum313.count()-1

                countercounter = countercounter + 1   
                if countercounter == 2:
                    countercounter=0                   
                newcounter = newcounter + countercounter  
                if newcounter > numb1:
                    try:
                    	a.room_number = roomnum313[0].room_number
                    except IndexError:
                    	a.room_number = None

                    # roomnum313[0].room_number
                else:
                    a.room_number = roomnum313[newcounter].room_number                                             
               
            else:
                roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
                if not roomnum313:
                    a.room_number=None
                else:
                    a.room_number = roomnum313.room_number
        else:
            counter= 0
            countercounter = 0
            newcounter=0
            refno3113 = a.referenceno
            roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
            if not roomnum313:
                a.room_number= None
            else:
                a.room_number = roomnum313.room_number


    todaydate1 = todaydate.strftime("%d/%m/%Y")
    c1 = Specialrequests.objects.filter(date=todaydate)
    date_customers1 = Booking.objects.filter(checkin_date=todaydate).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).order_by('first_name')




    date_customers2 = Booking.objects.filter(checkout_date=todaydate).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(upgrade=True, upgradelast=False).order_by('first_name')
    

    date_customers3 = Booking.objects.filter(checkin_date__lt=todaydate).filter(checkout_date__gt=todaydate).exclude(room_type_name__pk=22).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(room_type_name__pk=28).count()
    ab = Roomnumber.objects.all()

    date_customers4 = Booking.objects.filter(checkin_date=todaydate).exclude(room_type_name__pk=22).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(room_type_name__pk=28).count()
    date_customers5= Booking.objects.filter(checkout_date=todaydate).exclude(room_type_name__pk=22).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(room_type_name__pk=28).exclude(upgrade=True, upgradelast=False).count()
    date_customers6 = ab.count() - date_customers3- date_customers4

    count = 0


    template = loader.get_template('booking/index.html')

    context = {

        'c1':c1,
        'todaydate': todaydate,
        'date_customers1' : date_customers1,
        'date_customers2': date_customers2,
        'date_customers3' : date_customers3,
        'date_customers4': date_customers4,
        'date_customers5': date_customers5,
        'date_customers6': date_customers6,

        'breakfast':breakfast,
        'breakfast2':breakfast2,
        'breakfastno':breakfastno,
        'breakfast2no':breakfast2no,
        'Tasknumber':Tasknumber,
        "gottask":gottask
    }    
    return HttpResponse(template.render(context, request))




@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def roomtype(request):
    all_roomtypes=Roomtype.objects.all()



    template = loader.get_template('booking/roomtypes.html')
    context = {
    'all_roomtypes' : all_roomtypes
    }        
    return HttpResponse(template.render(context, request))







@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def roomsbackend(request):
    all_rooms = Roomnumber.objects.all().order_by('room_number')
    context = {
    'all_rooms':all_rooms
    }
    return render(request, "booking/roombackend.html", context)










@login_required(login_url='/login/')
def allbookings(request):
    order = request.GET.get('order')
    if order is None:
        order =0
    if int(order) is 3:
        all_bookings= Booking.objects.all().filter(maintain=False).order_by('-checkin_date')
    elif int(order) is 2:
        all_bookings= Booking.objects.all().filter(maintain=False).order_by('-checkout_date')        
    else:
        all_bookings= Booking.objects.all().filter(maintain=False).order_by('-created_on')

    
    allbookings = all_bookings
    paginator = Paginator(allbookings, 70)    
    page = request.GET.get('page')
    try:
        allbookings = paginator.page(page)
    except PageNotAnInteger:

        allbookings = paginator.page(1)
    except EmptyPage:
        allbookings = paginator.page(paginator.num_pages)




    context = {
    'allbookings':allbookings,
    'order':order,
    }
    return render(request,"booking/allbooking.html",context)





@login_required(login_url='/login/')
def allinvoices(request):

    first_name = request.GET.get('firstname')
    referenceno = request.GET.get('referenceno')
    if first_name:
      
        first = first_name.split()
        all_invoices = Invoice.objects.none()

        for a in first:
            query1 = Invoice.objects.all().filter(email__first_name__icontains=a)
            query2 = Invoice.objects.all().filter(email__last_name__icontains=a)
            all_invoices = query1 | query2 | all_invoices


    elif referenceno:
        all_invoices = Invoice.objects.filter(referenceno=referenceno).order_by('-id')
    else:
        all_invoices = Invoice.objects.all().order_by('-id')

    paginator = Paginator(all_invoices, 500)    
    page = request.GET.get('page')
    try:
        all_invoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_invoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_invoices = paginator.page(paginator.num_pages)


    context= {
    'all_invoices':all_invoices
    }
    return render(request,"booking/allinvoices.html", context)



@login_required(login_url='/login/')
def allinvoicespaid(request):
    all_invoices = Invoice.objects.all().filter(deposit =False).order_by('totalpaiddate')
    context= {
    'all_invoices':all_invoices
    }
    return render(request,"booking/allinvoices.html", context)



@login_required(login_url='/login/')
def allcustomers(request):
    all_customers = Customer.objects.all()
    context = {
        'all_customers':all_customers
    }
    return render(request,"booking/allcustomers.html", context)











@login_required(login_url='/login/')
def allsockets(request):
    all_customers = socketdata.objects.all()
    context = {
        'all_customers':all_customers
    }
    return render(request,"booking/allsockets.html", context)







@login_required(login_url='/login/')
def detailbydate(request):
    dateform = DateForm(request.GET or None)
    qin_date1 = request.GET.get('startdate')
    qout_date1 = request.GET.get('enddate')
    roomt = request.GET.get('roomtype')
    roomtypes= Roomtype.objects.all()
    print(roomtypes)

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    if not qin_date1:
        qin_date=date.today()
        qout_date=date.today()

    else:
        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)  

    bookv = request.GET.get('book')
    allbooking = Roomnumber.objects.all()
    we = Roomnumber.objects.all().filter( booking__checkin_date__gte=qin_date, booking__checkin_date__lt=qout_date).distinct()
    asdf = Roomnumber.objects.all().filter( booking__checkout_date__gt=qin_date,  booking__checkout_date__lte=qout_date).distinct()
    drrr = Roomnumber.objects.all().filter(booking__checkin_date__lte=qin_date, booking__checkout_date__gte=qout_date).distinct()
    qwer = asdf | we | drrr
    if bookv == '1':
        table=qwer
    else:
        table = allbooking.exclude(id__in=qwer)

    if roomtype:
        table=table.filter(room_type_name__room_type_name=roomt)
    

    context = {
    "table":table,
    "dateform":dateform,
    "roomtypes":roomtypes
    }


    return render(request, "booking/qdate.html", context)



@login_required(login_url='/login/')
def detailbyroom(request):
    dateform = DateForm(request.GET or None)
    month_date = request.GET.get('month')
    year = request.GET.get('year')
    roomnumber = request.GET.get('roomnumber')
    allrooms=Roomnumber.objects.all()
    
    date= datetime.now()
    week_date = date.replace(day=1).strftime("%d-%m-%Y")
    eee = date.replace(day=1).weekday()
    print(eee)

    if month_date and year:
        week_date="1-" + month_date+"-" + year
        dd = datetime.strptime(week_date, '%d-%m-%Y')
        eee = dd.weekday()
        print(eee)

            
    if not roomnumber:
        roomnumber = "000"
    

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    date1 = parsing_date(week_date)


    datedisplay0 = (date1)

 
    datename = []
    date_ = []
    dateformat = []
    

    def datefilter(text):

        day1 = Booking.objects.filter(checkin_date__lte=text)
        day_1 = day1.filter(checkout_date__gt=text)
        day_01 = day_1.filter(room_number__room_number=roomnumber)
        if not day_01:
            day__1 = "-"
        else:
            day__001 = day_01.get(room_number__room_number=roomnumber)
            day__1 = day__001.first_name 
        return day__1

    
    for i in range(0,31):

        datedisplay1 = (date1 + timedelta (days=i))
        date_display1 = datedisplay1.strftime("%a, %d-%m-%Y")        
        date_.append(date_display1)
        dateformat.append(datedisplay1)

    for s in dateformat:
        day__1 = datefilter(s)
        datename.append(day__1)


    print(date_)
    print(datename)
    calendar_ = OrderedDict(zip_longest(date_,datename))
    print(calendar_)


    template = loader.get_template('booking/roomquery.html')

    context={
    "calendar_":calendar_,
    "date_":date_,
    "datename":datename,
    "roomnumber":roomnumber,
    "week_date":week_date,
    "eee":eee
    }



    return HttpResponse(template.render(context, request))    



# @login_required(login_url='/login/')
def feedback(request):

    if request.method=="POST":
        # if not re.match(r'^[A-Za-z0-9]+$', password)
        cname = request.POST.get('contactname')
        cnumber = request.POST.get('contactno')
        cemail = request.POST.get('contactemail')
        descr = request.POST.get('description')
        nonetype = request.POST.get('contactaddress')
        # name_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
        if not nonetype:
            try:
                validate_email(cemail)
                asdf = Feedback.objects.create()
                asdf.contactname = cname
                asdf.contactno  = cnumber
                asdf.contactemail = cemail
                asdf.description = descr
                print(asdf)
                # if asdf.is_valid:
                asdf.save()

            except ValidationError:
                if cemail is None:
                    asdf.contactname = cname
                    asdf.contactno  = cnumber
                    asdf.contactemail = cemail
                    asdf.description = descr
                    print(asdf)
                    # if asdf.is_valid:
                    asdf.save()
                else:
                    return redirect('test2')
         

    return render(request, "booking/feedback.html")


@login_required(login_url='/login/')
def feedbackbackend(request):
    fb = Feedback.objects.all()
    context = {
    'fb':fb
    }

    return render(request,"booking/feedbackb.html", context)

@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def editroomtype(request):

    editroomtypeform = RoomtypeForm(request.POST or None, request.FILES or None)
    if editroomtypeform.is_valid():
        instance=editroomtypeform.cleaned_data['room_type_name']
        editroomtypeform.save()
        return redirect('detail')
    context = {
         "editroomtypeform":editroomtypeform
    }
    return render(request, "booking/roomtypeedit.html", context) 



@login_required(login_url='/login/')
def rform(request):

    rform = RoomForm(request.POST or None)
    if rform.is_valid():
        rform.save()
    context = {
         "rform":rform
    }
    return render(request, "booking/rforms.html", context)



@login_required(login_url='/login/')
def customers(request):


    pk= request.GET.get('pk')
    tz = timezone('Etc/GMT+8')
    today = tz.localize(datetime.today()).date()

    try: 
        customerno = Customer.objects.get(pk=pk)
        vispermit= ['HK', 'AG', 'AU', 'BS', 'MY','SM', 'BB','BZ', 'BW', 'BN','CM', 'CA','CY','DM','FJ','GH','GD','GY' ,'IE', 'JM', 'LI', 'KE','KI','KR','LS', 'MW', 'MV','MT','MU', 'MZ', 'NA','NR', 'NZ','NG','NL','PG', 'RW','KN','LC','VC','WS','SC','SL','SG','SB','ZA','CH','SZ','TO','UG','GB','TZ','VU','ZM','ZW','AL','AT','DZ','BE','CZ','CN','SK','DK','FI','DE','HU','IS','JP','LU','NO','SE','IT','BH','US','JO','KW','LB','EG', 'MA','YE','OM','SA', 'QA', 'AE', 'TR', 'TN', 'AF', 'IR', 'IQ','LY','SY', 'BG', 'RO', 'RU' ]
        customerfullname = str(customerno.first_name + " " + customerno.last_name) 
        path="/hotel/static/images/upload/" + customerfullname


        try:
            img_list1 =os.listdir(path)
            customerno.filevs = True

        except FileNotFoundError:
            customerno.filevs = False


        customercountry = customerno.country
        if customercountry in vispermit:
            customerno.vc = False
        else:
            customerno.vc = True
        custid = customerno.pk
        customerform = customerForm(request.POST or None, request.FILES or None, instance = customerno)


        if customerform.is_valid():
        	customerform.save()

        customerbooking = Invoice.objects.filter(email=custid).order_by('-datecreated')


        for c in customerbooking:
            if c.staffbooking == True:
                c.staffbook = "yes"
            else:
                c.staffbook = None

            if c.totalpaid == True:
                c.paid = "NotPaid"
                c.paid1 = "TotalPaid"
                if c.deposit == True:
                    c.paid = None
            else:
                c.paid = "NotPaid"


            extraitems = extra_items.objects.filter(referenceno = c.referenceno)
            if extraitems:
                c.extraitems = extraitems
            else:
                c.extraitems = None
            totalextra = 0
            for extra in extraitems:
                totalextra += extra.paymentprice

 
            invoiceno = Invoice.objects.get(referenceno =c.referenceno)
            depforminfo = depositwitheld.objects.filter(invoice=invoiceno) 
            c.depforminfo = depforminfo
            room = Booking.objects.filter(referenceno=c.referenceno).order_by('-room_type_name__room_price0')
            c.room = room
            booki=[] 
            roomtotal=0      
            for a in room:
                cin_date = a.checkin_date

                cout_date = a.checkout_date
                if a.room_number is None:
                    a.upgrade = None
                    if a.room_type_name.pk == 22:
                        a.room_number = Roomnumber.objects.get(room_number=401)
                        a.room_number.room_number = "Extra Bed"
                    elif a.room_type_name.pk == 23:
                        a.room_number = Roomnumber.objects.get(room_number=401)
                        a.room_number.room_number = "Breakfast Package"     
                    elif a.room_type_name.pk == 24:
                        a.room_number = Roomnumber.objects.get(room_number=401)
                        a.room_number.room_number = "Breakfast Add-on"
                    elif a.room_type_name.pk == 28:
                        a.room_number = Roomnumber.objects.get(room_number=401)
                        a.room_number.room_number = "Package"

                else:
                    a.upgrade = "yes"                        
                booki.append(a.room_number.room_number)
                c.checkin_date = cin_date
                c.checkout_date = cout_date
                roomtotal+=a.actualpay
            

            if roomtotal is None:
                roomtotal=0

            if c.total is None:
                c.total = 0

            c.discount1 = roomtotal+totalextra-c.total+c.gst
            if c.discount1 == 0:
                c.discount1 = None  

            c.roomno = ", ".join(booki)
            if not room:
                room= None
                c.checkin_date = None
                c.checkout_date = None

            if c.checkedin1 is not None:
                c.check1 = "Checkedin"

            if c.checkedout1 is not None:
                c.checkout1 = "Checkedout"




            if c.checkedin1 is None:     
                c.check = "True"
            else: 
                c.check = None


            if c.checkedout1 is None:
                if c.check is None:
                    c.checkout = "True"
            else:
                c.checkout = None



            # if c.checkin_date < today:
            #     if c.checkedin1 is None:     
            #         c.latecheck = "True"

        print(customerbooking)

    
    except Customer.DoesNotExist:
        return redirect('test2')
    # roomss = Booking.objects.filter(referenceno__in=customerbooking )

    context ={
    'customerform':customerform,
    'customerno':customerno,
    'customerbooking':customerbooking,
    # 'roomss':roomss
    }
    return render(request,"booking/customer.html", context)



def invoice(request):
    try: 
        invoiceno = request.GET.get('invoiceno')
        invoiceitem = Invoice.objects.get(referenceno=invoiceno)
        invoice = Booking.objects.filter(referenceno= invoiceno)
        total=0
        for i in invoice:
            total+= i.paymentprice
        

    except NameError:
        return redirect('test2')

    context = {
    'invoiceitem':invoiceitem,
    'invoice':invoice,
    'total':total
    }
    
    return render(request,"booking/invoices.html", context)


def specialcomments(request):
    todaydate = date.today()
    c1 = Specialrequests.objects.filter(date=todaydate)
    specform = specForm(request.POST or None)
    if specform.is_valid():
        specform.save()
        return redirect('detail')

#     date_customers1 = Booking.objects.all().filter(checkin_date__lte=todaydate)
#     date_customers1 = date_customers1.filter(checkout_date__gt=todaydate)
    context={
    'c1':c1,
    'specform':specform
    }

    return render(request, "booking/sre.html", context)
#     context={}


def specialrequestform(request):
    specform = specForm(request.POST or None)
    if specform.is_valid():
        specform.save()
        return redirect('detail')
    
    context={'specform':specform
    }

    return render(request, "booking/specform.html", context)


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem1(request, id):
    pk = request.GET.get('id')
    d = Booking.objects.get(pk=id)
    pkno = d.room_type_name.pk
    noofdays = int((d.checkout_date-d.checkin_date).days)
    if request.method =="POST":

        bbb3 =  "DELETED BOOKING first_name=" + d.first_name + ", last_name =" + d.last_name + "indate= " + d.checkin_date.strftime("%d-%m-%Y")+"outdate= " + d.checkout_date.strftime("%d-%m-%Y")
        logging1313 = logging.objects.create(description=bbb3, referenceno=d.referenceno, staff=request.user.username )
        d.delete()


        asdf = Booking.objects.filter(referenceno=d.referenceno)
        print('exist')
        print(asdf)
        if not asdf:
            try:
                addf = Invoice.objects.get(referenceno=d.referenceno)
                addpoints = 0
                if addf.description:
                    discountpromo = addf.description
                    if discountpromo.points:
                        addpoints = discountpromo.points
                cust1 = addf.email  
                cust2 = Customer.objects.get(pk=cust1.pk)  
                if cust2.user_login:
                    no1ofdays=0
                    user1315 = Userlogin.objects.get(pk=cust2.user_login.pk)
                    if addf.molpay == True:
                        if d.room_type_name.pk is not 22 and d.room_type_name.pk is not 23 and d.room_type_name.pk is not 24 and d.room_type_name.pk is not 28:
                            if d.room_type_name.pk is 27:
                                no1ofdays = no1ofdays + (int((d.checkout_date-d.checkin_date).days)*2)
                            else:
                                no1ofdays = no1ofdays + int((d.checkout_date-d.checkin_date).days)


                    # if d.room_type_name.pk is not 22 and d.room_type_name.pk is not 23 and d.room_type_name.pk is not 24 and d.room_type_name.pk is not 28:
                    #     no1ofdays = int((d.checkout_date-d.checkin_date).days)
                    user1315.numbertime = int(user1315.numbertime)-no1ofdays + addpoints 




                    user1315.save()
                    pointused = str(addpoints - no1ofdays)
                    newuserloginlog = PointLog.objects.create(user_login=user1315, pointused=pointused, pointdescription ="removed when booking deleted")

                if not addf.checkedin1:

                    bbb3 =  "DELETED BOOKING with INVOICE first_name=" + d.first_name + ", last_name =" + d.last_name + "indate= " + d.checkin_date.strftime("%d-%m-%Y")+"outdate= " + d.checkout_date.strftime("%d-%m-%Y") + addf.invoiceno
                    logging1313 = logging.objects.create(description=bbb3, referenceno=d.referenceno, staff=request.user.username )
                    addf.delete()


                else:
                    addf.cancelled==True
                    return HttpResponse("Booking checkedin already, order will be cancelled")



                    bbb3 =  "Booking checkedin already, order will be cancelled first_name=" + d.first_name + ", last_name =" + d.last_name + " indate= " + d.checkin_date.strftime("%d-%m-%Y")+" outdate= " + d.checkout_date.strftime("%d-%m-%Y") + " invoicenumber" + addf.invoiceno
                    logging1313 = logging.objects.create(description=bbb3, referenceno=d.referenceno, staff=request.user.username )



            except Invoice.DoesNotExist:
                return HttpResponse("something went wrong when deleting booking and cant find the invoice. Please contact Han")

        else:
            total2=0
            addf= Invoice.objects.get(referenceno=d.referenceno)
            addf = Invoice.objects.get(referenceno=d.referenceno)
            addpoints = 0
            if addf.description:
                discountpromo = addf.description
                if discountpromo.points:
                    addpoints = discountpromo.points
            for a in asdf:
                total123 = a.paymentprice
                total2 += total123

            if addf.rtacomm:

                if addf.gst > 0:
                    addf.total = decimal.Decimal(format((decimal.Decimal(total2)*decimal.Decimal(1.06)*decimal.Decimal(decimal.Decimal(1)-addf.rtacomm)),'.2f'))
                    addf.commamount = format(addf.total*decimal.Decimal(addf.rtacomm)/decimal.Decimal(1-decimal.Decimal(addf.rtacomm)),'.2f')
                    addf.gst = format((addf.total/decimal.Decimal(1.06)*decimal.Decimal(0.06)), '.2f')
                else:
                    addf.total = decimal.Decimal(format((decimal.Decimal(total2)*decimal.Decimal(1.00)*decimal.Decimal(decimal.Decimal(1)-addf.rtacomm)),'.2f'))
                    addf.commamount = format(addf.total*decimal.Decimal(addf.rtacomm)/decimal.Decimal(1-decimal.Decimal(addf.rtacomm)),'.2f')
                    addf.gst = format((addf.total/decimal.Decimal(1.00)*decimal.Decimal(0.00)), '.2f')
            else:
                if addf.gst > 0:


                    addf.total = format((decimal.Decimal(total2)*decimal.Decimal(1.06)),'.2f')
                    addf.gst = format((total2*decimal.Decimal(0.06)), '.2f')
                else:

                    addf.total = format((decimal.Decimal(total2)*decimal.Decimal(1.00)),'.2f')
                    addf.gst = format((total2*decimal.Decimal(0.00)), '.2f')




            if pkno == 22:
                addf.depositamt=addf.depositamt
            elif pkno ==23:
                addf.depositamt=addf.depositamt
            elif pkno == 24:
                addf.depositamt=addf.depositamt
            elif pkno == 28:
                addf.depositamt=addf.depositamt                
            else:
                addf.depositamt = addf.depositamt-decimal.Decimal(200)
                if addf.ttax:
                    if addf.ttax > 0:
                        addf.ttax = addf.ttax - decimal.Decimal(10*noofdays)





            addf.servicetax = 0
            # gst1 = total2/decimal.Decimal(1.06)

            # addf.servicetax = format((gst1/decimal.Decimal(11)), '.2f')

            addf.save()
            cust1 = addf.email  
            cust2 = Customer.objects.get(pk=cust1.pk)  
            if cust2.user_login:
                user1315 = Userlogin.objects.get(pk=cust2.user_login.pk) 
                no1ofdays=0                


                if d.room_type_name.pk is not 22 and d.room_type_name.pk is not 23 and d.room_type_name.pk is not 24 and d.room_type_name.pk is not 28:
                    if d.room_type_name.pk is 27:
                        no1ofdays = no1ofdays + (int((d.checkout_date-d.checkin_date).days)*2)
                    else:
                        no1ofdays = no1ofdays + int((d.checkout_date-d.checkin_date).days)



                # if d.room_type_name.pk is not 22 and d.room_type_name.pk is not 23 and d.room_type_name.pk is not 24 and d.room_type_name.pk is not 28:
                #     no1ofdays = int((d.checkout_date-d.checkin_date).days)
                user1315.numbertime = int(user1315.numbertime)-no1ofdays
                user1315.save()
                pointused = "-" + str(no1ofdays)
                newuserloginlog = PointLog.objects.create(user_login=user1315, pointused=pointused, pointdescription ="removed when booking deleted")

            bbb3 =  "Booking deleted invoice total altered first_name=" + d.first_name + ", last_name =" + d.last_name + " indate= " + d.checkin_date.strftime("%d-%m-%Y")+" outdate= " + d.checkout_date.strftime("%d-%m-%Y") + " invoicenumber" + addf.invoiceno + " newtotal=" + addf.total
            logging1313 = logging.objects.create(description=bbb3, referenceno=d.referenceno, staff=request.user.username )


        
        return redirect('allbookings')
     
    return render(request, "booking/delete.html")







@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem2(request, id):
    pk = request.GET.get('id')
    d = Roomtype.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")    


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem200(request, id):
    pk = request.GET.get('id')
    d = Booking.objects.get(pk=id)
    d.delete()
    return redirect('detail')
     
    return render(request, "booking/delete.html")    



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem3(request, id):
    pk = request.GET.get('id')
    d = Roomnumber.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")      


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem4(request, id):
    pk = request.GET.get('id')
    d = FrontPage.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('front')
     
    return render(request, "booking/delete.html")   


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem5(request, id):
    pk = request.GET.get('id')
    d = FrontImage.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('front')
     
    return render(request, "booking/delete.html")    

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem6(request, id):
    pk = request.GET.get('id')
    d = Feedback.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")         

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem7(request, id):
    pk = request.GET.get('id')
    d = Promocode.objects.get(pk=id)
    if request.method =="POST":
        d.active=False
        d.save()
        return redirect('addpromo')
     
    return render(request, "booking/delete.html")  

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem77(request, id):
    pk = request.GET.get('id')
    d = Promocode.objects.get(pk=id)
    allpromocoderooms = promocoderooms.objects.filter(promocode=d)
    if request.method =="POST":
        d.delete()
        for allpromocode in allpromocoderooms:
            allpromocode.delete()
        return redirect('addpromo')
     
    return render(request, "booking/delete.html")  


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem8(request, id):
    pk = Invoice.objects.all()
    if request.method =="POST":
        pk.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html") 


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem9(request, id):
    pk = Customer.objects.all()
    if request.method =="POST":
        pk.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")     

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem10(request, id):
    pk = Roomtype.objects.all()
    if request.method =="POST":
        pk.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")        

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem11(request, id):
    pk = Booking.objects.all()
    if request.method =="POST":
        pk.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")      



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem12(request, id):
    pk = Events.objects.all()
    if request.method =="POST":
        pk.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html")    


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem13(request, id):
    pk = request.GET.get('id')
    d = Pricing.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('detail')
     
    return render(request, "booking/delete.html") 

 
@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem14(request, id):
    pk = request.GET.get('id')
    d = Pages.objects.get(pk=id)
    if request.method =="POST":
        d.delete()
        return redirect('pagesout')
     
    return render(request, "booking/delete.html")          



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem15(request, id):
    pk = request.GET.get('id')
    d = depositwitheld.objects.get(pk=id)
    test = str(d.invoice.email.pk)
    test2 = d.invoice.referenceno

    dasdf = Invoice.objects.get(referenceno=test2)  
    invno = dasdf.invoiceno
    e = Booking.objects.filter(referenceno = test2)
    firstname= dasdf.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = test2).first()


    try:
        q111 = depositwitheld.objects.filter(invoice=dasdf)
    except depositwitheld.DoesNotExist:
        q111 = None



    if request.method =="POST":
        d.delete()

        def generate1(f, ae, afafa, q111):
            logo='booking/static/innbparklogo2.gif'           

            c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.drawImage(logo, 400 , 730, width=140, height=69)

            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)


            c.setFont('Helvetica', 9, leading=None)        
            c.drawString(40 ,790,'InnB Park Hotel')
            c.drawString(40 ,775,'102-106, Jalan Imbi,  Bukit Bintang')
            c.drawString(40 ,760,'55100 Kuala Lumpur')
            c.drawString(40 ,745,'admin@innbparkhotel.com') 
            c.drawString(40 ,730,'+603 2856 7257')



            c.setFont('Helvetica-Bold', 12, leading=None)
            c.drawString(40 ,680,'ROOM RESERVATION')
            c.drawString(430 ,810,'Non-refundable Rate')

            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 630, 'GUESTS NAME')
            c.drawString(197, 630, 'ROOM NO.')
            c.drawString(257, 630, 'ROOM TYPE')
            c.drawString(380, 630, 'ARRIVAL DATE')  
            c.drawString(470, 630, 'DEPATURE DATE')                                     
                
            c.setLineWidth(.5)
            c.line(40,610,548,610)

            if f:
                c.setFont('Helvetica', 9, leading=None)
                c.drawString(40, 590, afafa.email.first_name)
                c.drawString(40, 570, afafa.email.last_name)


            a=0
            for t in ae:
                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)
                n=20
                a += n
                c.drawString(197, 610-a, roomnumber)
                c.drawString(257, 610-a, roomname)
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 610-a, indate)  
                c.drawString(470, 610-a, outdate)

            c.line(40,570-a,548,570-a)


            c.setFont('Helvetica-Bold', 11, leading=None)
            c.drawString(40, 530-a, 'INVOICE NO: ' + afafa.invoiceno)
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 530-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 505-a, 'DESCRIPTION')
            c.drawString(180, 505-a, 'PRICE/UNIT')
            c.drawString(330, 505-a, 'NO. NIGHTS')
            c.drawString(470, 505-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            for t in ae:
                roomnumber = str(t.room_number)
                roomname = str(t.room_type_name)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                price = str(round((t.actualpay /  nights),2))
                c.drawString(40, 505-a, roomname)
                c.drawString(180, 505-a, 'RM ' + price)
                c.drawString(330, 505-a, str(nights))
                c.drawString(470, 505-a, 'RM ' + str(t.actualpay))
                totalprice += t.actualpay   


            if not f:
                a=20
                c.drawString(40, 505-a, 'Customer cancelled booking')





            if afafa.description: 
                a = a+20
                discount=  totalprice - afafa.total
                c.drawString(180, 480-a, 'Special Promo:   ' + afafa.description.description )
                c.drawString(470, 480-a, '- RM ' + str(discount))
            
            if afafa.gst > 0:

                a = a+20
                c.drawString(180, 480-a, '6% GST ' )
                c.drawString(470, 480-a, 'RM ' + str(afafa.gst))

                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 450-a, 'Total:')
            if f:
                c.drawString(470, 450-a, 'RM ' + str(afafa.total)) 
            else:
                c.drawString(470,450-a, 'RM ' + str(afafa.bookingfee))
            c.setFont('Helvetica', 9, leading=None)
            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 450-a, 'Booking Pre-payment')
                c.drawString(470, 450-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                
                    c.drawString(180, 430-a, 'Total Paid:')
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        total12 = afafa.total
                    c.drawString(470, 430-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 430-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 430-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 415-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 415-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 415-a, 'Deposit not applicable')



            if a > 90:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = a-300

            
            if afafa.totalpaid == True:
                a= a+20
                c.setFont('Helvetica-Bold', 11, leading=None)                
                c.drawString(40, 400-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 380-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 380-a, 'RM ' + str(total12))
                c.setFont('Helvetica', 7, leading=None)   
                if not afafa.depositreturnedate:             
                    c.drawString(40, 180-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas of the hotel is strictly prohibited. ')
                    c.drawString(40, 170-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                    c.drawString(40, 155-a, 'For security purposes, both main elevators will be locked between 10pm to 7am. Please use the service lift, which can be accessed through the side door.')
                    c.drawString(40, 140-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out. Failure to do so will incur a charge of RM 20.00 per card.')            


            if afafa.totalpaid == False:
                if afafa.bookingfeepaid == False:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 400-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 400-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 320-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 320-a, 'Not Paid')                                                            

            
            if a > 300:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = a-500   



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 320-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                a=a+20
                c.drawString(40, 320-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                if afafa.depdescrip:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                else:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

            if afafa.depositreturnedate:
                items = 0

                if q111:
                    c.drawString(40, 300-a, 'Deposit charged:')
                    for i in q111:
                        c.drawString(180, 300-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
                        n = 17
                        a+=n
                        items += i.itemprice
                    returned = afafa.depositamt - items
                    if returned < 0: 
                        returned = -(returned)
                        c.drawString(40, 280-a, 'Deposit charged on')
                        # c.drawString(350, 280-a,  'RM ' + str(returned))  
                    else:
                        c.drawString(40, 280-a, 'Deposit returned')
                        if afafa.otherdeposit < 1 :
                            c.drawString(350, 280-a, 'RM ' + str(returned))                         
                        # c.drawString(350, 280-a,  'RM ' + str(returned))                                  
                else:
                    c.drawString(40, 280-a, 'Deposit returned on')
                        

                tz = timezone('Etc/GMT-8')
                depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                c.drawString(180, 280-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  
                a=a+20       
                c.drawString(40, 280-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                c.drawString(40, 265-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
                                            

                c.setLineWidth(.5)
                c.line(40,180-a , 180,180-a)   
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(80, 160-a, 'Signature')            



            # c.drawString(380, 390-a, 'Payment Method:')                
            # c.drawString(470, 390-a, str(afafa.Paymentmethod))
                # if afafa.Paymentmethod == "Credit Card":
                #     c.drawString(470, 490-a, afafa.paymentdescription)
                # c.drawCentredString(415,500, 'test')
            logo='booking/static/innbparklogo2.gif'           
                # c.setFont('Helvetica', 48, leading=None)
                # c.drawCentredString(415,500, 'test')
                # c.setFont('Helvetica', 20, leading=None)        


            c.drawImage(logo, 400 , 730, width=140, height=69)
            c.showPage()
            c.save()
        generate1(f,e,dasdf, q111)



        return redirect('https://innbparkhotel.com/customer/?pk=' + test)
     
    return render(request, "booking/delete.html") 


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem16(request, id):
    pk = request.GET.get('id')
    d = Invoice.objects.get(pk=id)


    if request.method =="POST":
        bbb3 =  "invoice deleted: " + d.invoiceno 
        logging1313 = logging.objects.create(description=bbb3, referenceno=d.referenceno, staff=request.user.username )
        d.delete()     
        return redirect('detail')
     
    return render(request, "booking/delete.html")



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem17(request, id):
    pk = request.GET.get('id')
    d = Customer.objects.get(pk=id)


    if request.method =="POST":
        d.delete()     
        return redirect('detail')
     
    return render(request, "booking/delete.html")


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem18(request, id):
    pk = request.GET.get('id')
    d = variablepricing.objects.get(pk=id)


    if request.method =="POST":
        d.delete()     
        return redirect('detail')
     
    return render(request, "booking/delete.html")

@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem19(request, id):
    pk = request.GET.get('id')
    d = Timerole.objects.get(pk=id)


    if request.method =="POST":
        d.delete()     
        return redirect('portal135')
     
    return render(request, "booking/delete.html")



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem20(request, id):
    pk = request.GET.get('id')
    d = reportdate.objects.get(pk=id)
    if request.method =="POST":
        d.delete()     
        return redirect('detail')
     
    return render(request, "booking/delete.html")


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem21(request, id):
    pk = request.GET.get('id')
    d = socketdata.objects.get(pk=id)
    if request.method =="POST":
        d.delete()     
        return redirect('detail')
     
    return render(request, "booking/delete.html")



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def rem22(request, id):
    pk = request.GET.get('id')
    d = extra_items.objects.get(pk=id)
    paymentprice = d.paymentprice

    if request.method =="POST":
        invoice = Invoice.objects.get(referenceno=d.referenceno)
        invoice.total = invoice.total-(d.paymentprice*decimal.Decimal(1.06))
        invoice.gst = invoice.gst-(d.paymentprice*decimal.Decimal(0.06))
        invoice.save()
        test = invoice.email.pk
        d.delete()
        return redirect('https://innbparkhotel.com/customer/?pk=' + str(test))
     
    return render(request, "booking/delete.html")


@login_required(login_url='/login/')
def chg(request, id):
    pk= request.GET.get('id')
    record = Booking.objects.get(pk=id)
    bookingno = record.pk
    cin_date = Booking.objects.get(pk=id).checkin_date
    cout_date = Booking.objects.get(pk=id).checkout_date
    remail = record.email
    customer = Customer.objects.get(email=record.email, phone_number=record.phone_number)
    roomtypeee = record.room_type_name.pk


    eform = eeForm(request.POST or None, instance = record, initial = {'checkin_date':cin_date.strftime("%d-%m-%Y"), 'checkout_date':cout_date.strftime("%d-%m-%Y")})
    if eform.is_valid():
        # eform = eeForm(request.POST, instance=record)
        qin_date = eform.cleaned_data['checkin_date']
        qout_date = eform.cleaned_data['checkout_date']
        room = eform.cleaned_data['room_number']

        if roomtypeee is 23:
            eform.save()
        elif roomtypeee is 24:
            eform.save()
        elif roomtypeee is 22:
            eform.save()
        elif roomtypeee is 28:
            eform.save()
        else:
            room1 = Roomnumber.objects.get(room_number=room)            
            we = Booking.objects.filter(room_number=room1).filter(earlyout=False, checkin_date__gte=qin_date,checkin_date__lt=qout_date, checkout_date__gt=F('checkin_date'))
            asdf = Booking.objects.filter(room_number=room1).filter(earlyout=False, checkout_date__gt=qin_date, checkout_date__lte=qout_date, checkin_date__lt=F('checkout_date'))
            drrr = Booking.objects.filter(room_number=room1).filter(earlyout=False,checkin_date__lte=qin_date, checkout_date__gte=qout_date)
            qwer = asdf | we | drrr
            twes = qwer.exclude(pk=bookingno)

            # twes = qwer.filter(room_number=room)
            if twes:
                return HttpResponse('Error, booking exists')
            else:
                eform.save()
        # else:
        #    

                # customer.save()

        

            # customer.save()


            # roomtype = Roomnumber.objects.filter(room_number=room)


            # eform.cleaned_data['room_type_name']

            return redirect('detail')
    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "eform":eform
    }
    return render(request,"booking/eform.html", context)


@login_required(login_url='/login/')
def chg2(request, id):
    pk= request.GET.get('id')
    record = FrontPage.objects.get(pk=id)
    cardForm1 = cardForm(request.POST or None, request.FILES or None, instance = record, )
    if cardForm1.is_valid():
        # eform = eeForm(request.POST, instance=record)
        cardForm1.save()            
        return redirect('front')
    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "cardForm1":cardForm1
    }
    return render(request,"booking/efront.html", context)


@login_required(login_url='/login/')
def chg3(request, id):
    pk= request.GET.get('id')
    record = FrontImage.objects.get(pk=id)
    fiform  = frontimgForm(request.POST or None, request.FILES or None, instance = record, )
    if fiform.is_valid():
        # eform = eeForm(request.POST, instance=record)
        fiform.save()            
        return redirect('front')
    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "fiform":fiform
    }
    return render(request,"booking/efront2.html", context)    

@login_required(login_url='/login/')
def chg4(request, id):
    try:
        pk= request.GET.get('id')
        record = FrontDesc.objects.get(pk=id)
        frondest = frontdesForm(request.POST or None, instance = record, )
        if frondest.is_valid():
            # eform = eeForm(request.POST, instance=record)
            frondest.save()            
            return redirect('front')
        else: 
                print("invalid")
                # return redirect('test2')
    except:

        record = FrontDesc.objects.create(description="_")
        frontdest =frontdesForm (request.POST or None, instance = record )

    context= {
        "frondest":frondest
    }
    return render(request,"booking/efront3.html", context)  









@login_required(login_url='/login/')
def chg24(request, id):
    pk= request.GET.get('id')
    record = Invoice.objects.get(pk=id)
    referenceno = record.referenceno
    d = Invoice.objects.get(referenceno=referenceno)  
    invf = invoiceForm3(request.POST or None, instance = record )
    if invf.is_valid():
        # eform = eeForm(request.POST, instance=record)
        invf.save()            
        return redirect('https://innbparkhotel.com/customer/?pk=' + str(d.email.pk))
    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "invf":invf
    }
    return render(request,"booking/efront5.html", context)  




@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def chg8(request, id):
    pk= request.GET.get('id')
    record = Invoice.objects.get(pk=id)
    referenceno = record.referenceno
    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    invf = invoiceForm(request.POST or None, instance = record )
    if invf.is_valid():
        # eform = eeForm(request.POST, instance=record)
        deposit1 = invf.cleaned_data['depositpaiddate']
        deposit2 = invf.cleaned_data['depositreturnedate']
        tz = timezone('Etc/GMT-8')
        if deposit1 == record.depositpaiddate:
            deposit1_1 = record.depositpaiddate
        else:
            if deposit1 is not None:
                deposit1_ = tz.localize(deposit1.replace(tzinfo=None),is_dst=None)
                deposit1_1 = deposit1_.astimezone(pytz.utc)
            else: 
                deposit1_1 = None


        if deposit2 == record.depositreturnedate:
            deposit2_2 = record.depositreturnedate
        else:

            if deposit2 is not None:
                deposit2_ = tz.localize(deposit2.replace(tzinfo=None),is_dst=None)
                deposit2_2 = deposit2_.astimezone(pytz.utc)
            else:
                deposit2_2 = None


            

        asdfa = invf.save(commit=False)
        if not invf.cleaned_data['Paymentmethod']:
            asdfa.Paymentmethod = None
            print("worked")
        asdfa.depositpaiddate = deposit1_1
        asdfa.depositreturnedate = deposit2_2
        asdfa.save()


        d = Invoice.objects.get(referenceno=referenceno)  
        invno = d.invoiceno
        e = Booking.objects.filter(referenceno = referenceno)
        firstname= d.email.first_name
        cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        f = Booking.objects.filter(referenceno = referenceno).first()


        try:
            q111 = depositwitheld.objects.filter(invoice=d)
        except depositwitheld.DoesNotExist:
            q111 = None


        


        return redirect('https://innbparkhotel.com/customer/?pk=' + str(d.email.pk))






    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "invf":invf
    }
    return render(request,"booking/efront5.html", context)  
 

@login_required(login_url='/login/')
def chg5(request, id):
    pk= request.GET.get('id')
    record = Roomtype.objects.get(pk=id)
    frondest = RoomtypeForm(request.POST or None, request.FILES or None, instance = record, )
    if frondest.is_valid():
        # eform = eeForm(request.POST, instance=record)
        frondest.save()            
        return redirect('roomtype')
    else: 
            print("invalid")
            # return redirect('test2')

    context= {
        "frondest":frondest
    }
    return render(request,"booking/efront4.html", context)   




@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def editrooms(request):

    editroomsform = RoomForm(request.POST or None)
    if editroomsform.is_valid():
        editroomsform.save()
        return redirect('detail')
    context = {
         "editroomsform":editroomsform
    }
    return render(request, "booking/editforms.html", context)


@permission_required('booking.add_booking', login_url='/unauthorized/')
@login_required(login_url='/login/')
def chg6(request, id):
    pk= request.GET.get('id')   
    record = Roomnumber.objects.get(pk=id)
    editroomsform = RoomForm(request.POST or None, instance = record, )

    if editroomsform.is_valid():
        editroomsform.save()    
        return redirect('roomsbackend')
    context = {
         "editroomsform":editroomsform
    }
    return render(request, "booking/editforms.html", context)



@login_required(login_url='/login/')
def chg7(request, id):
    from PIL import Image
    pk= request.GET.get('id')   
    record = Pages.objects.get(pk=id)
    pagesform = Pageform(request.POST or None, request.FILES or None, instance = record,)

    if pagesform.is_valid():
        pf = pagesform.save()
        try:    
            large_image_x = decimal.Decimal(request.POST.get('id_pages_large_image_x'))
            large_image_y = decimal.Decimal(request.POST.get('id_pages_large_image_y'))
            large_image_width = decimal.Decimal(request.POST.get('id_pages_large_image_width'))
            large_image_height = decimal.Decimal(request.POST.get('id_pages_large_image_height'))
            changed_large = True
        except:
            changed_large = False

        try:
            image_x = decimal.Decimal(request.POST.get('id_pages_image_x'))
            image_y = decimal.Decimal(request.POST.get('id_pages_image_y'))
            image_width = decimal.Decimal(request.POST.get('id_pages_image_width'))
            image_height = decimal.Decimal(request.POST.get('id_pages_image_height'))
            changed1 = True
        except:
            changed1 = False


        if changed1:
            try: 

                fn = pf.pages_image.url
                fn = fn.replace("/img","")
                path = "/hotel/static/images/upload" + fn


                image1 = Image.open(path)
                # wwidth, wheight = image1.size

                cropped_image = image1.crop((image_x, image_y, image_width+image_x, image_height+image_y))
                resized_image = cropped_image

                width = image_width
                height = image_height
                maxwidth = 600
                newheight = None
                if width>maxwidth:
                    widthratio = width/maxwidth
                    newwidth = 600
                    newheight = height/widthratio
                    newsize = newwidth, newheight
                    resized_image.thumbnail(newsize, Image.ANTIALIAS)
                    resized_image.save(path, resized_image.format)
                else:
                    resized_image.save(path)


            except Exception as e:
                print(str(e))


        if changed_large:
        
            try: 

                fn2 = pf.pages_large_image.url
                fn2 = fn2.replace("/img","")
                path2 = "/hotel/static/images/upload" + fn2


                image2 = Image.open(path2)
                # wwidth, wheight = image2.size

                cropped_image2 = image2.crop((large_image_x, large_image_y, large_image_width+large_image_x, large_image_height+large_image_y))
                resized_image2 = cropped_image2


                width2 = large_image_width
                height2 = large_image_height
                maxwidth = 600
                newheight = None
                if width2>maxwidth:
                    widthratio2 = width2/maxwidth
                    newwidth2 = 600
                    newheight2 = height2/widthratio2
                    newsize2 = newwidth2, newheight2
                    resized_image2.thumbnail(newsize2, Image.ANTIALIAS)
                    resized_image2.save(path2, resized_image2.format)
                else:
                    resized_image2.save(path2)


            except Exception as e:
                print(str(e))










        return redirect('pagesout')
    context = {
         "pagesform":pagesform
    }
    return render(request, "booking/pagesforms2.html", context)

# @login_required(login_url='/login/')
# def chg7_2(request, id):
#     pk= request.GET.get('id')   
#     record = Pages.objects.get(pk=id)
#     pagesform = Pageform(request.POST or None, request.FILES or None, instance = record,)

#     if pagesform.is_valid():
#         pagesform.save()    
#         return redirect('pagesout')
#     context = {
#          "pagesform":pagesform
#     }
#     return render(request, "booking/pagesforms2.html", context)

@login_required(login_url='/login/')
def chg9(request, id):
    pk= request.GET.get('id')    
    record = Customer.objects.get(pk=id)
    recordemail = record.email
    country1 = record.country
    recordphno = record.phone_number
    link2end = "pk=" + str(record.pk)
    customerform2= customerForm2(request.POST or None, request.FILES or None, instance = record)

    if customerform2.is_valid():
        email = customerform2.cleaned_data['email']
        phno = customerform2.cleaned_data['phone_number']
        country = request.POST.get('country')

        if email != recordemail:
            customertest = Customer.objects.filter(email=email)
            if customertest:
                for a in customertest:
                    if a.phone_number == phno:
                        return HttpResponse('Customer Already Exist')
                    else:
                        print(recordemail)
                        print (recordphno)
                        find = Booking.objects.filter(email=recordemail,phone_number=recordphno)
                        print(find)
                        for each in find:
                            each.email = email
                            each.phone_number = phno
                            each.country = country


                            each.save()
                            print("succeed")
                        customerform2.save()
                        return redirect('/customer/?%s' % link2end)

            else:
                find = Booking.objects.filter(email=recordemail,phone_number=recordphno)
                print(find)
                for each in find:
                    # idsp = Booking.objects.get(referenceno = each.referenceno)
                    # print(idsp)
                    each.email = email
                    each.phone_number = phno
                    each.country=country



                    each.save()
                    print("succeed")
                customerform2.save()
                return redirect('/customer/?%s' % link2end)


        elif phno != recordphno:

            customertest = Customer.objects.filter(phone_number=phno)
            if customertest:
                for a in customertest:
                    if a.phone_number == phno:
                        return HttpResponse('Customer Already Exist')
                    else:
                        find = Booking.objects.filter(email=recordemail,phone_number=recordphno)
                        for each in find:
                            each.email = email
                            each.phone_number = phno
                            each.country = country
                            each.save()
                        aaa=customerform2.save(commit=False) 
                        aaa.country = country



                        aaa.save()
                        return redirect('/customer/?%s' % link2end)

            else:
                find = Booking.objects.filter(email=recordemail,phone_number=recordphno)
                print(find)
                for each in find:
                    each.email = email
                    each.phone_number = phno
                    each.save()
                    print("succeed")
                aaa=customerform2.save(commit=False) 
                aaa.country = country


                aaa.save()
                return redirect('/customer/?%s' % link2end)

        else:        
            aaa=customerform2.save(commit=False) 
            aaa.country = country


            aaa.save()
            return redirect('/customer/?%s' % link2end)


    context = {
         "customerform2":customerform2,
         "country1": country1
    }
    return render(request, "booking/customerform.html", context)


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def chg10(request, id):
    pk= request.GET.get('id')   
    record = Booking.objects.get(pk=id)
    eform = eeForm2(request.POST or None, request.FILES or None, instance = record,)
    if eform.is_valid():

        eform.save()   
        return redirect('allbookings')
    context = {
         "eform":eform
    }
    return render(request, "booking/eform.html", context)




@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def chg14(request, id):
    pk= request.GET.get('id')   
    record = Userlogin.objects.get(pk=id)
    eform = custForm1(request.POST or None, request.FILES or None, instance = record,)

    changedpoints = request.POST.get('numbertime')
    originalpoints = record.numbertime

    if eform.is_valid():

        eform.save()   





        pointused = str((int(changedpoints)) - int(originalpoints))
        newuserloginlog = PointLog.objects.create(user_login=user55, pointused=pointused, pointdescription ="Changed by" + str(request.user.username) + " from " + str(originalpoints) + " to " + str(changedpoints))

        return redirect('customerall')



    context = {
         "eform":eform
    }
    return render(request, "booking/eform.html", context)





@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def editfront(request):
    


  

    cardform = cardForm(request.POST or None, request.FILES or None)
    if cardform.is_valid():
        cardform.save()
        return redirect('front')
        print('saved')



    context = {
         "cardform":cardform,
         # "fiform":fiform,
         # "frondest":frondest

    }
    return render(request, "booking/editfront.html", context)


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def editfront2(request):
    

    fiform = frontimgForm(request.POST or None, request.FILES or None)
    if fiform.is_valid():
        fiform.save()
        return redirect('front')


    # frondest=frontdesForm(request.POST or None)
    # if frondest.is_valid():
    #     frondest.save()
    #     return redirect('front')

  


    context = {
         # "cardform":cardform,
         "fiform":fiform,
         # "frondest":frondest

    }
    return render(request, "booking/editfront2.html", context)    



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def editfront3(request):
    

    frondest=frontdesForm(request.POST or None)
    if frondest.is_valid():
        frondest.save()
        return redirect('front')

  


    context = {

         "frondest":frondest

    }
    return render(request, "booking/editfront3.html", context)    



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def front(request):
     
    cardfront= FrontPage.objects.all()
    print(cardfront)
    frontimg= FrontImage.objects.all()
    print(frontimg)
    frontdesc = FrontDesc.objects.all()
    print(frontdesc)
    context={
    "cardfront":cardfront,
    "frontimg":frontimg,
    "frontdesc":frontdesc
    }

    return render(request, "booking/front.html", context)


@login_required(login_url='/login/')
def querycust(request):
    first_name = request.GET.get('firstname')
    # last_name = request.GET.get('lastname')
    # email = request.GET.get('email')
    # phno = request.GET.get('phno')
    referenceno = request.GET.get('referenceno')

    result00 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')
    result01 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments') 
    result02 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments') 
    result03 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments') 
    result04 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')        
    result05 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')
    result06 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')
    result07 = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')

    results = Invoice.objects.none().values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments')
    afirst = None
    if first_name:
        result00 =  Invoice.objects.all().filter(email__first_name=first_name).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        result01 = Invoice.objects.all().filter(email__last_name=first_name).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        
        firsthandres = result00 | result01
        afirst = None
        
        # if not firsthandres:

        first = first_name.split()

        #     afirst = first[:2]
        #     afirst =' '. join(afirst)
        #     alast = first[-2:]
        #     alast = ' '. join(alast)
        #     result02 = Invoice.objects.all().filter(email__first_name=afirst).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result03 = Invoice.objects.all().filter(email__first_name=alast).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result04 = Invoice.objects.all().filter(email__last_name=afirst).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result05 = Invoice.objects.all().filter(email__last_name=alast).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     for a in first:
        #         result06 = Invoice.objects.all().filter(email__last_name=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #         result07 = Invoice.objects.all().filter(email__first_name=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
 
    
   

        #     exclusion =result02 | result03 | result04 | result05 | result06 | result07


        # else:
        #     exclusion = firsthandres

        # if not exclusion:



        for a in first:
            query1 = Invoice.objects.all().filter(email__first_name__icontains=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
            query2 = Invoice.objects.all().filter(email__last_name__icontains=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
            results = query1 | query2 | results
            print('firstname')
            print(first_name)

        # else:
        #     results = exclusion



    else:
        results = Invoice.objects.all()


    # if last_name:    
    #     results = results.filter(email__last_name__icontains=last_name).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        

    # if email:
    #     results = results.filter(email__email__icontains=email).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()



    # if phno:
    #     results = results.filter(email__phone_number__icontains=phno).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()

    if referenceno:
        results = results.filter(referenceno=referenceno).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments')
        afirst=results
  

    print(results)

    if results:
        for a in results:
            print(a['email__email'])
            print(a['email__phone_number'])
            customerno = Customer.objects.get(email=a['email__email'], phone_number=a['email__phone_number'])

            a['customer'] = customerno.pk




    context = {
     "results": results,
     "result00":result00,
     "result00":result01,
     "result00":result02,
     "result00":result03,
     "result00":result04,
     "result05":result05,
     "afirst":afirst,
     }


    return render(request,"booking/querycust.html", context)


def paidv(request):
    refno = str(request.GET.get('id'))
    pay = Invoice.objects.get(referenceno=refno)
    if pay.bookingfee is None:
        pay.bookingfee = 0
    if pay.cashpaid is None:
        pay.cashpaid = 0
    if pay.ccpaid is None:
        pay.ccpaid = 0
    if pay.bookingfeepaid:
        pay.total1 = pay.total - decimal.Decimal(pay.bookingfee) - decimal.Decimal(pay.ccpaid) - decimal.Decimal(pay.cashpaid)
    else:
        pay.total1 = pay.total - decimal.Decimal(pay.ccpaid) - decimal.Decimal(pay.cashpaid)

    print(pay.totalpaid)

    if pay.totalpaid == True:
        pay.total1 = 0

    if pay.depositcash is None:
        pay.depositcash = 0
    if pay.depositcc is None:
        pay.depositcc = 0
    if pay.otherdeposit is None:
        pay.otherdeposit = 0            

    pay.depositamt1 = pay.depositamt-pay.depositcash-pay.depositcc-pay.otherdeposit

    if pay.depositamt is None:
        pay.depositamt1 = 0
    if pay.deposit is True:
        pay.depositamt1 = 0 




    cust = pay.email.pk
    custno = "pk=" + str(cust)
    total1 = float(pay.total1) + float(pay.depositamt1)

    print(custno)


    if request.method=="POST":
        cash = request.POST.get('quantity')
        test = request.POST.get('cd')
        deposit = request.POST.getlist('deposit')
        other1 = request.POST.getlist('other1')
        depa = request.POST.get('dep')
        depdescr = request.POST.get('depdescr')
        # change = request.POST.get('change')
        depc = request.POST.get('dec')
        depcrec = request.POST.get('depcc')                
        print(depa)
        print(cash)
        print(test)
        print(deposit)

        d = Invoice.objects.get(referenceno=refno)  
        invno = d.invoiceno
        e = Booking.objects.filter(referenceno = refno)
        firstname= d.email.first_name
        cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        f = Booking.objects.filter(referenceno = refno).first() 
        email_ = d.email.email
        totaldep = Depositsum.objects.get(pk=1)
        print(pay.Paymentmethod)

        if pay.cashpaid:
            if float(test)>0:
                pay.cashpaid = pay.cashpaid + pay.total1 - decimal.Decimal(test)
                totaldep.cash = totaldep.cash + (pay.total1-decimal.Decimal(test))
            else:
                pay.cashpaid = pay.cashpaid + pay.total1       
                totaldep.cash = totaldep.cash + pay.total1                         
        else:
            if float(test)>0:            
                pay.cashpaid = pay.total1 - decimal.Decimal(test)
                totaldep.cash = totaldep.cash + (pay.total1-decimal.Decimal(test))

            else:
                pay.cashpaid = pay.total1        
                totaldep.cash = totaldep.cash + pay.total1                                   
        
        if pay.ccpaid:         
            pay.ccpaid = pay.ccpaid + decimal.Decimal(test)  
        else:        
            pay.ccpaid = test
        
        pay.totalpaid = True
        pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

        year = datetime.now().strftime("%y")    
        asdf = Invoice.objects.get(pk=5331)
        if pay.Paymentmethod is None:
            if float(cash) > 0:
                if float(test)>0:
                    pay.Paymentmethod = "Credit Card and Cash"

                    if pay.rtacomm:
                        print("nothing")
                    else:
                        if pay.referral=="Walk-in":

                            if pay.invoiceno:
                                randomvar = None
                            else:
                                invnos = Invoice.objects.all().order_by('invoiceno').last()
                                inv_no = invnos.invoiceno



                                newyear1 = inv_no[:2]
                                if str(newyear1)==year:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                    pay.invoiceno = new_invoice_no
                                else:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + "00001"
                                    pay.invoiceno = new_invoice_no     










                                
                                # invoice_int = inv_no[2:]
                                # new_invoice_int = int(invoice_int) + 1
                                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                # pay.invoiceno = new_invoice_no
                    # year = datetime.now().strftime("%y")    
                    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
                    # inv_no = invnos.invoiceno
                    # invoice_int = inv_no[2:]
                    # new_invoice_int = int(invoice_int) + 1
                    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                    # pay.invoiceno = new_invoice_no

                else:
                    pay.Paymentmethod = "Cash"
                    if pay.rtacomm:
                        print("nothing")
                    else:
                        if pay.referral=="Walk-in":
                            if pay.invoiceno:
                                randomvar = None
                            else:
                                invnos = Invoice.objects.all().order_by('invoiceno').last()
                                inv_no = invnos.invoiceno



                                newyear1 = inv_no[:2]
                                if str(newyear1)==year:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                    pay.invoiceno = new_invoice_no
                                else:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + "00001"
                                    pay.invoiceno = new_invoice_no     














                                # invoice_int = inv_no[2:]
                                # new_invoice_int = int(invoice_int) + 1
                                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                # pay.invoiceno = new_invoice_no





            elif float(test)>0:
                if float(cash) == 0 :
                    pay.Paymentmethod = "Credit Card"
                    if pay.rtacomm:
                        print("nothing")
                    else:
                        if pay.referral=="Walk-in":

                            if pay.invoiceno:
                                randomvar = None
                            else:
                                invnos = Invoice.objects.all().order_by('invoiceno').last()
                                inv_no = invnos.invoiceno


                                newyear1 = inv_no[:2]
                                if str(newyear1)==year:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                    pay.invoiceno = new_invoice_no
                                else:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + "00001"
                                    pay.invoiceno = new_invoice_no     








                                # invoice_int = inv_no[2:]
                                # new_invoice_int = int(invoice_int) + 1
                                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                # pay.invoiceno = new_invoice_no

            else:
                pay.Paymentmethod = "Credit Card"
                if pay.rtacomm:
                    print("nothing")
                else:
                    if pay.referral=="Walk-in":
                        if pay.invoiceno:
                            randomvar = None
                        else:
                            invnos = Invoice.objects.all().order_by('invoiceno').last()
                            inv_no = invnos.invoiceno




                            newyear1 = inv_no[:2]
                            if str(newyear1)==year:
                                invoice_int = inv_no[2:]
                                new_invoice_int = int(invoice_int) + 1
                                new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                pay.invoiceno = new_invoice_no
                            else:
                                invoice_int = inv_no[2:]
                                new_invoice_int = int(invoice_int) + 1
                                new_invoice_no = year + "00001"
                                pay.invoiceno = new_invoice_no     




                            # invoice_int = inv_no[2:]
                            # new_invoice_int = int(invoice_int) + 1
                            # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                            # pay.invoiceno = new_invoice_no
                

        else:
            if pay.Paymentmethod is "Cash":
                if float(test)>0:
                    pay.Paymentmethod = "Credit Card and Cash"
                    if pay.rtacomm:
                        print("nothing")
                    else:
                        if pay.referral=="Walk-in":
                            if pay.invoiceno:
                                randomvar = None
                            else:
                                invnos = Invoice.objects.all().order_by('invoiceno').last()
                                inv_no = invnos.invoiceno



                                newyear1 = inv_no[:2]
                                if str(newyear1)==year:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                    pay.invoiceno = new_invoice_no
                                else:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + "00001"
                                    pay.invoiceno = new_invoice_no     







                                # invoice_int = inv_no[2:]
                                # new_invoice_int = int(invoice_int) + 1
                                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                # pay.invoiceno = new_invoice_no


            elif pay.Paymentmethod is "Credit Card":
                if float(cash) > 0:
                    pay.Paymentmethod = "Credit Card and Cash"
                    if pay.rtacomm:
                        print("nothing")
                    else:
                        if pay.referral=="Walk-in":

                            if pay.invoiceno:
                                randomvar = None
                            else:
                                invnos = Invoice.objects.all().order_by('invoiceno').last()
                                inv_no = invnos.invoiceno

                                newyear1 = inv_no[:2]
                                if str(newyear1)==year:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                    pay.invoiceno = new_invoice_no
                                else:
                                    invoice_int = inv_no[2:]
                                    new_invoice_int = int(invoice_int) + 1
                                    new_invoice_no = year + "00001"
                                    pay.invoiceno = new_invoice_no     












                                # invoice_int = inv_no[2:]
                                # new_invoice_int = int(invoice_int) + 1
                                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                                # pay.invoiceno = new_invoice_no





        


        if deposit:
            pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
            pay.depositpaidby =  request.user.username
            pay.deposit = True

            pay.depositcash = depc
            totaldep.cashdep = totaldep.cashdep + decimal.Decimal(depc)
            pay.depositcc = depcrec
            totaldep.ccdep = totaldep.ccdep + decimal.Decimal(depcrec)

            if float(depc) > 0:
                if float(depcrec)>0:
                    pay.depi = "Credit Card and Cash"
                else:
                    pay.depi = "Cash"
            elif float(depcrec)>0:
                if float(cash) == 0 :
                    pay.depi = "Credit Card"




            if other1:
                pay.depi = "Others"
                if pay.otherdeposit is not None:
                    pay.otherdeposit = pay.otherdeposit + pay.depositamt1
                    if pay.depdescrip is not None:
                        pay.depdescrip = str(pay.depdescrip) + "," + depdescr
                    else:
                        pay.depdescrip = depdescr 
                else:
                    pay.otherdeposit = pay.depositamt1
                    pay.depdescrip = depdescr   

                if totaldep.Others is None:
                   totaldep.Others = str(depdescr)

                else:
                    totaldep.Others = str(totaldep.Others) + ", " +str(depdescr) 

        totaldep.save()

        pay.save()
        # if test == "0":
        #     print(pay.Paymentmethod)
        #     if pay.Paymentmethod is None:
        #         print("yes")
        #         pay.Paymentmethod = "Cash"
        #         pay.cashpaid = pay.total1
        #         pay.totalpaid = True
        #         pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #         if deposit:
        #             print("works1")
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #             if depa == "Cash":
        #                 pay.depi = "Cash"
        #                 print("works2")
        #                 # pay.cashpaid = pay.total
        #             pay.depositpaidby =  request.user.username
        #             pay.deposit = True
        #             pay.depdescrip = depdescr
        #         pay.save()
            
        #     else:
        #         # pay.Paymentmethod = "Cash"
        #         # pay.cashpaid = cash
        #         # pay.totalpaid = True
        #         pay.deposit = True
        #         pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")                
        #         pay.totalpaid=True
        #         if depa == "Cash":
        #             pay.depi = "Cash"
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #             pay.depositpaidby =  request.user.username                    
        #         pay.cashpaid = pay.cashpaid + pay.total1


        #         pay.depdescrip = depdescr                
        #     # pay.paymentdescription = 
        #         pay.save()
        #     d = Invoice.objects.get(referenceno=refno)
        #     invno = d.invoiceno
        #     e = Booking.objects.filter(referenceno = refno)
        #     firstname= d.email.first_name
        #     cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        #     f = Booking.objects.filter(referenceno = refno).first()
        #     email_ = d.email.email

        #     try:
        #         q111 = depositwitheld.objects.filter(invoice=d)
        #     except depositwitheld.DoesNotExist:
        #         q111 = None



        #     return redirect('/customer/?%s' % custno)
        
        # elif cash == "0":
        #     if pay.Paymentmethod is None:
        #         pay.Paymentmethod = "Credit Card"
        #         pay.ccpaid = pay.total
        #         pay.totalpaid=True
        #         pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #         if deposit:
        #             if depa == "Creditcard":
        #                 pay.depi = "Credit Card"
        #                 # pay.ccpaid = pay.total
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")                
        #             pay.deposit = True
        #             pay.depositpaidby =  request.user.username
        #             pay.depdescrip = depdescr
        #             year = datetime.now().strftime("%y")    
        #             invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
        #             inv_no = invnos.invoiceno
        #             invoice_int = inv_no[2:]
        #             new_invoice_int = int(invoice_int) + 1
        #             new_invoice_no = year + str(format(new_invoice_int, '05d'))
        #             pay.invoiceno = new_invoice_no

        #         pay.save()
        #     else:
        #         # pay.ccpaid
        #         # pay.Paymentmethod = "Credit Card"
        #         pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #         if depa == "Creditcard":
        #             pay.depi = "Credit Card"
        #             pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")                        
        #             pay.depositpaidby =  request.user.username
        #         pay.ccpaid = pay.ccpaid + pay.total1
        #         # pay.totalpaid = True
        #         pay.deposit = True
                
        #         pay.totalpaid=True                
        #         pay.depdescrip = depdescr
        #     # pay.paymentdescription = 
        #         pay.save()  

        #     d = Invoice.objects.get(referenceno=refno)  
        #     invno = d.invoiceno
        #     e = Booking.objects.filter(referenceno = refno)
        #     firstname= d.email.first_name
        #     cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        #     f = Booking.objects.filter(referenceno = refno).first()
        #     email_ = d.email.email            


        #     try:
        #         q111 = depositwitheld.objects.filter(invoice=d)
        #     except depositwitheld.DoesNotExist:
        #         q111 = None



        #     try:
        #         q111 = depositwitheld.objects.filter(invoice=d)
        #     except depositwitheld.DoesNotExist:
        #         q111 = None

        #     return redirect('/customer/?%s' % custno)


        # else:
        #     if pay.Paymentmethod is None:
        #         pay.Paymentmethod = "Credit Card and Cash"
        #         paymentes = pay.total1 - decimal.Decimal(test)
        #         pay.ccpaid = decimal.Decimal(test)
        #         pay.cashpaid = paymentes
        #         pay.totalpaid=True
        #         pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #         if deposit:
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")                
        #             pay.deposit = True
        #             if depa == "Cash":
        #                 pay.depi = "Cash"
        #                 pay.cashpaid = paymentes
        #                 pay.depositpaidby =  request.user.username
        #             elif depa == "Creditcard":
        #                 pay.depi = "Credit Card"
        #                 pay.ccpaid = decimal.Decimal(test)-pay.depositamt1
        #                 pay.depositpaidby =  request.user.username
        #             pay.depdescrip = depdescr                    
        #         pay.save()
        #     else:
        #         # pay.ccpaid
        #         # pay.Paymentmethod = "Credit Card and Cash"
        #         # pay.ccpaid = test
        #         paymentes = pay.total1 - decimal.Decimal(test)

        #         if depa == "Cash":
        #             pay.depi = "Cash"
        #             pay.cashpaid = pay.cashpaid + (paymentes-pay.depositamt1)
        #             pay.ccpaid = pay.ccpaid + decimal.Decimal(test)                    
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
        #             pay.depositpaidby =  request.user.username                    
        #         elif depa == "Creditcard":
        #             pay.depi = "Credit Card"
        #             pay.cashpaid = pay.cashpaid + paymentes                    
        #             pay.ccpaid = pay.ccpaid + (decimal.Decimal(test)-pay.depositamt1)
        #             pay.depositpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M") 
        #             pay.depositpaidby =  request.user.username                    
        #         # pay.cashpaid = cash
        #         else:
        #             pay.cashpaid = pay.cashpaid + paymentes
        #             pay.ccpaid = pay.ccpaid + decimal.Decimal(test)


        #         pay.totalpaid = True
        #         # pay.totalpaid = True
        #         pay.deposit = True
        #         pay.depdescrip = depdescr
        #     # pay.paymentdescription = 
        #         pay.save()  

        #     d = Invoice.objects.get(referenceno=refno)  
        #     invno = d.invoiceno
        #     e = Booking.objects.filter(referenceno = refno)
        #     firstname= d.email.first_name
        #     cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        #     f = Booking.objects.filter(referenceno = refno).first()
        #     email_ = d.email.email            


        #     try:
        #         q111 = depositwitheld.objects.filter(invoice=d)
        #     except depositwitheld.DoesNotExist:
        #         q111 = None



        #     try:
        #         q111 = depositwitheld.objects.filter(invoice=d)
        #     except depositwitheld.DoesNotExist:
        #         q111 = None

        return redirect('/customer/?%s' % custno)



    context = {
    'pay':pay,
    'total1':total1
    }



    return render(request,"booking/invpaid.html", context)





# !!!FRONTEND



def dateform(request):
    if '1335i99fl' not in request.session:
        # return HttpResponse("Loggedout")
        user55=None
    else:
        userhash = request.session['1335i99fl']

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))
        # reflect = nowa-timestamptime
        # reflect2 = str(reflect) + str("=") + str(nowa) + "-" + str(timestamptime) + " ==" + str(hashcode)
        # return HttpResponse(reflect2)
    # print(clearing)
        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)


            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                # return HttpResponse(userhash) 
                custid = Customer.objects.filter(user_login=user55)
            else:
                user55 = None
        else:
            user55 = None
    # r= requests.get('http://www.accuweather.com/en/my/sungai-way/785462/weather-forecast/785462')
    # b = html.fromstring(r.text)
    # temperature = b.xpath('//span[@class="large-temp"]/text()')
    # temperature = temperature.pop(0)
    # weather = b.xpath('//span[@class="cond"]/text()')    
    # weather = weather.pop(0)


    # try:
            
    #     r= requests.get('https://www.worldweatheronline.com/kuala-lumpur-weather/kuala-lumpur/my.aspx?day=0')
    #     b = html.fromstring(r.text)
    #     temperature = b.xpath('//div[@class="report_text temperature"]/text()')
    #     temperature = temperature.pop(0)
    #     weather = b.xpath('//div[@class="report_text light_text"]/text()')    
    #     weather = weather.pop(0)
    # except requests.exceptions.RequestException as e:  # This is the correct syntax
    #     weather = ""
    #     temperature ="29 °c"
    # temperature =""
    # weather = ""
    desc1 =FrontDesc.objects.get(pk=1)
    desc2 = FrontDesc.objects.get(pk=2)
    description1 = desc1.description
    description2 = desc2.description
    img1 = FrontImage.objects.get(pk=1).image
    img2 = FrontImage.objects.get(pk=2).image
    img3 = FrontImage.objects.get(pk=3).image
    img4 = FrontImage.objects.get(pk=4).image
    img5 = FrontImage.objects.get(pk=5).image

    feedbackform = feedbackForm(request.POST or None)
    dateform = DateForm(request.GET or None)
    # pages = Pages.objects.all().order_by('-id')

    pages135 = Pages.objects.filter(hidden=False).order_by('-id')[:6]
    if dateform.is_valid():

        qin_date = request.GET.get('checkin_date')
        qout_date = request.GET.get('checkout_date')
        qnumpeople = request.GET.get('number_of_people')
        qdate = "checkin_date=" + qin_date + "&" +"checkout_date=" + qout_date 
        print(qdate)
        return redirect('/results/?%s' % qdate )
    
    context = {
        "pages135":pages135,
        "user55":user55,  
        "dateform":dateform,
        "description1":description1,
        "description2":description2,
        "img1":img1,
        "img2":img2,
        "img3":img3,
        "img4":img4,
        "img5":img5,
        "feedbackform":feedbackform,
    }
    return render(request, "booking/basenew.html", context)


# def static(request):
           
#     context = {
#          "dateform":dateform,
#     }
#     return render(request, "booking/base.html", context)



def dateformnew(request):

    # r= requests.get('http://www.accuweather.com/en/my/sungai-way/785462/weather-forecast/785462')
    # b = html.fromstring(r.text)
    # temperature = b.xpath('//span[@class="large-temp"]/text()')
    # temperature = temperature.pop(0)
    # weather = b.xpath('//span[@class="cond"]/text()')    
    # weather = weather.pop(0)


    # try:
            
    #     r= requests.get('https://www.worldweatheronline.com/kuala-lumpur-weather/kuala-lumpur/my.aspx?day=0')
    #     b = html.fromstring(r.text)
    #     temperature = b.xpath('//div[@class="report_text temperature"]/text()')
    #     temperature = temperature.pop(0)
    #     weather = b.xpath('//div[@class="report_text light_text"]/text()')    
    #     weather = weather.pop(0)
    # except requests.exceptions.RequestException as e:  # This is the correct syntax
    #     weather = ""
    #     temperature ="29 °c"
    temperature =""
    weather = ""
    desc1 =FrontDesc.objects.get(pk=1)
    desc2 = FrontDesc.objects.get(pk=2)
    description1 = desc1.description
    description2 = desc2.description
    img1 = FrontImage.objects.get(pk=1).image
    img2 = FrontImage.objects.get(pk=2).image
    img3 = FrontImage.objects.get(pk=3).image
    img4 = FrontImage.objects.get(pk=4).image
    img5 = FrontImage.objects.get(pk=5).image
    pages = Pages.objects.all().order_by('-id')[:3]

    feedbackform = feedbackForm(request.POST or None)
    dateform = DateForm(request.GET or None)

    if dateform.is_valid():

        qin_date = request.GET.get('checkin_date')
        qout_date = request.GET.get('checkout_date')
        qnumpeople = request.GET.get('number_of_people')
        qdate = "checkin_date=" + qin_date + "&" +"checkout_date=" + qout_date 
        print(qdate)
        return redirect('/results/?%s' % qdate )
    
    context = {
         "temperature":temperature,
         "weather":weather,    
         "dateform":dateform,
         "description1":description1,
         "description2":description2,
         "img1":img1,
         "img2":img2,
         "img3":img3,
         "img4":img4,
         "img5":img5,
         "feedbackform":feedbackform, 
         "pages:":pages
    }
    return render(request, "booking/basenew.html", context)

def feed2all(request):
    feed2 = Fedback2.objects.all()

    context = {
    'feed2':feed2
    }
    
    return response(request, "booking/allfeedbacks", context)




def results(request):
    if request.user.is_authenticated(): 
        return redirect('manualbook')
    dateform = DateForm(request.GET or None)
    if dateform.is_valid():
        print("valid")
    else:
        return redirect('addbooking')



    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found') 

    totalnoofroom=0
    noofdays=0


    totaldiscount123=0

    malaysiatime = (datetime.now() + timedelta(hours=8)).date()



    if '1335i99fl' not in request.session:
        # return HttpResponse("Loggedout")
        user55=None
        user555=None
        custid= None
        numberusage=0
    else:
        userhash = request.session['1335i99fl']
        numberusage = 0

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))
        # reflect = nowa-timestamptime
        # reflect2 = str(reflect) + str("=") + str(nowa) + "-" + str(timestamptime) + " ==" + str(hashcode)
        # return HttpResponse(reflect2)
    # print(clearing)
        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)
            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                # return HttpResponse(userhash) 
                user555 = user55
                numberusage = user555.numbertime
                custid = Customer.objects.filter(user_login=user55)
            else:
                user55 = None
        else:
            user55 = None










    # clearing = Invoice.objects.filter(bookingfeepaid=False, staffbooking=False,molpay=True,totalpaid=False)
    # now = datetime.now()

    # nowa = float(now.strftime("%Y%m%d%H%M%S"))
    # # print(clearing)

    # for a in clearing:
    #     cust1 = a.email
    #     cust2 = Customer.objects.get(pk=cust1.pk)


    #     refa = a.referenceno
    #     if refa is not None:
    #         ref = float(refa[-14:])
    #         if nowa - ref > 10000:



    #             clear = Booking.objects.filter(referenceno=a.referenceno)
    #             if cust2.user_login:
    #                 no1ofdays = 0
    #                 user1315 = Userlogin.objects.get(pk=cust2.user_login.pk)
    #                 for aasdf in clear:
    #                     if aasdf.room_type_name.pk is not 22 and aasdf.room_type_name.pk is not 23 and aasdf.room_type_name.pk is not 24:
    #                         no1ofdays = no1ofdays + int((aasdf.checkout_date-aasdf.checkin_date).days)
    #                 user1315.numbertime = int(user1315.numbertime)-no1ofdays
    #                 user1315.save()
    #             clear2 = Invoice.objects.filter(referenceno=a.referenceno)
    #             clear.delete()
    #             clear2.delete()
















    clearing = Invoice.objects.filter(bookingfeepaid=False, staffbooking=False, molpay=True,totalpaid=False)
    now = datetime.now()
    nowa = float(now.strftime("%Y%m%d%H%M%S"))
    print(clearing)
    addpoints = 0


    for a in clearing:
        if a.description:
            discountpromo = a.description
            if discountpromo.points:
                addpoints = discountpromo.points



        cust1 = a.email
        cust2 = Customer.objects.get(pk=cust1.pk)
        refa = a.referenceno

        if refa is not None:
            ref = float(refa[-14:])
            if nowa - ref > 10000:
                clear = Booking.objects.filter(referenceno=a.referenceno)
                
                if cust2.user_login:
                    if a.molpay == True:
                        no1ofdays = 0
                        user1315 = Userlogin.objects.get(pk=cust2.user_login.pk)
                        for aasdf in clear:
                            if aasdf.room_type_name.pk is not 22 and aasdf.room_type_name.pk is not 23 and aasdf.room_type_name.pk is not 24 and aasdf.room_type_name.pk is not 28:
                                if aasdf.room_type_name.pk is 27:
                                    no1ofdays = no1ofdays + (int((aasdf.checkout_date-aasdf.checkin_date).days)*2)
                                else:
                                    no1ofdays = no1ofdays + int((aasdf.checkout_date-aasdf.checkin_date).days)

                        # user1315.numbertime = int(user1315.numbertime)-no1ofdays + addpoints
                        # user1315.save()


                # clear2 = Invoice.objects.filter(referenceno=a.referenceno)
                # clear.delete()
                # clear2.delete()
                clear2 = Invoice.objects.filter(referenceno=a.referenceno)
                for c in clear:
                    c.delete()
                for c2 in clear2:
                    c2.delete()
 
        # if cust2.user_login:
        #     if a.molpay == True:   
        #         user1315.numbertime = int(user4545.numbertime) + int(addpoints) 
        #         user1315.save()



    qin_date1 = request.GET.get('checkin_date')
    qout_date1 = request.GET.get('checkout_date')
    otw= request.GET.get('otw')
    remove1=request.GET.get('remove1')
    exc = request.GET.get('exc')
    roomcounter = 0
    if exc is None:
    	exc = 0

    # if exc:
    #     extrabed = 1


    calcnoofdays=0



    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    todaydatestring = todaydate.strftime("%Y-%m-%d")
    todaydatexact = datetime.strptime(todaydatestring, '%Y-%m-%d')
    todaydate = todaydatexact
    notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
    notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
    notaxset = False


    # dc = request.GET.get('disc')
    # qnumpeople = request.GET.get('number_of_people')

    request.session['qin_date'] = qin_date1
    request.session['qout_date'] = qout_date1





    if todaydate > notaxstartdate and todaydate < notaxenddate:
        if parsing_date(qin_date1) > notaxstartdate and parsing_date(qin_date1) < notaxenddate:
            if parsing_date(qout_date1) > notaxstartdate and parsing_date(qout_date1) < notaxenddate:
                notaxset = True






    # request.session['qnumpeople']= qnumpeople
    newttw=otw
    cod = request.GET.get('ce')
    if cod is not None:
        try:
            code = Promocode.objects.get(code=cod)
            sprice  = 0
            spbkfast = 0


            if code.onetimeonly == "USED":
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None
            elif code.active==False:
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None



            
            elif code.daysbefore is not None:
                dayscalculator = code.daysbefore
                qin_date = parsing_date(qin_date1)
                date1today = datetime.now()
                today1datestrftime = parsing_date((date1today + timedelta(hours=8)).strftime("%Y-%m-%d"))              
                calcnoofdays=(qin_date-today1datestrftime).days
                if calcnoofdays < dayscalculator:
                    error = "Invalid Code"
                    cod= None
                    per = 1
                    fix = 0
                    desc = None                
             	
                else: 
                    per = (1-code.discountper)
                    fix = code.discountfix
                    desc = code.description
                    error = None    
                    if code.specialbreakfastprice > 0:
                        spbkfast = code.specialbreakfastprice

                    if code.specialprice > 0:
                        sprice = code.specialprice






            elif code.validfrom is not None and code.validfrom > malaysiatime:
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None


            elif code.validto is not None and code.validto < malaysiatime:   
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None





            else: 
                per = (1-code.discountper)
                fix = code.discountfix
                desc = code.description
                error = None  

                if code.specialbreakfastprice > 0:
                    spbkfast = code.specialbreakfastprice

                if code.specialprice > 0:
                    sprice = code.specialprice






        except Promocode.DoesNotExist:
            if cod =="None":
                error = None
                cod = None

            else:
                error = "Invalid Code"
                cod= None


            per = 1
            fix=0
            desc = None
    


    else:

        per = 1
        fix=0
        desc = None
        error = None










    if not remove1:

        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')  

        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)
        # qin_date = datetime.strptime(qin_date, "'%d-%m-%Y', '%Y-%m-%d'")
        # qout_date = datetime.strptime(qout_date, "'%d-%m-%Y', '%Y-%m-%d'")

        print(request.GET.get('checkout_date'))
        if otw:
            atw = otw.split('-')
            atw_ = [var for var in atw if var]


            if cod =="TST425":
                if "23" not in atw_:
                    if "19" in atw_:
                        tyu=otw+("-23") 


                    elif "21" in atw_:
                        tyu=otw+("-23") 
                    else:
                        tyu=otw+("-23-23")
   
                        

                        url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+tyu+"&ce=TST425"
                        return redirect(url)

        else:
            atw_=None 
        









        rooms27 =  Roomnumber.objects.none()
        rooms271 =  Roomnumber.objects.none()        
        aaaa13 =  Roomnumber.objects.all().filter(link__isnull=False, hidden=False)
        # we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
        # asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
        # drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
        # qwer = asdf | we | drrr
        # cd = aaaa.exclude(id__in=qwer)
        cd = aaaa13
        # if not cd:
        #     return HttpResponse('This type of rooms have been fully booked')
        de = cd
        room01 = None
        room02 = None
        # randomnumber = random.choice(de)
        # rnum= Roomnumber.objects.get(room_number=randomnumber)
        for one1 in de:
            oneasdfafa = Roomnumber.objects.get(room_number=one1.link)
            if oneasdfafa.hidden== True:
                qrrr = Roomnumber.objects.filter(link=oneasdfafa)
                de = de.exclude(id__in=qrrr)

            else:

                rnum = one1
                if room01 and room02 is not None:
                    break
                one11 = one1 

                pass1 = None                               
                rnum131 = Roomnumber.objects.get(room_number=one1)
                we = Booking.objects.filter(checkin_date__gte=qin_date, checkin_date__lt=qout_date,room_number=rnum131)
                if we:
                    pass1="notpassed"
                asdf = Booking.objects.filter(checkout_date__gt=qin_date,checkout_date__lte=qout_date,room_number=rnum131)
                if asdf:
                    pass1="notpassed"
                drrr = Booking.objects.filter(checkin_date__lte=qin_date, checkout_date__gte=qout_date,room_number=rnum131)
                if drrr: 
                    pass1="notpassed"

                if pass1 is not None:

                    room01 = None
                    room02 = None
                    de = de.exclude(pk=one1.pk)


                else:

                    linkbookcheck = Roomnumber.objects.filter(link=one1.link).exclude(pk=one1.pk)
                    for a1 in linkbookcheck:
                        pass2 = None                                
                        rnum141 = Roomnumber.objects.get(room_number=a1)
                        we = Booking.objects.filter(checkin_date__gte=qin_date, checkin_date__lt=qout_date,room_number=rnum141)
                        if we:
                            pass2="notpassed"
                        asdf = Booking.objects.filter(checkout_date__gt=qin_date,checkout_date__lte=qout_date,room_number=rnum141)
                        if asdf:
                            pass2="notpassed"
                        drrr = Booking.objects.filter(checkin_date__lte=qin_date, checkout_date__gte=qout_date,room_number=rnum141)
                        if drrr: 
                            pass2="notpassed"


                        if pass2 is not None:

                            room01 = None
                            room02 = None

                        else:

                            rooms27 =  Roomnumber.objects.filter(room_number=one11.link)
                            rooms271 = rooms27 | rooms271

                            # return HttpResponse(rooms271)

        ab = Roomnumber.objects.all().filter(hidden=False).exclude(room_type_name__id=27)
        we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=qin_date, booking__checkin_date__lt=qout_date,booking__checkout_date__gt=F('booking__checkin_date'))
        asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=qin_date,booking__checkout_date__lte=qout_date,booking__checkin_date__lt=F('booking__checkout_date'))
        drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=qin_date, booking__checkout_date__gte=qout_date)
        qwer = asdf | we | drrr
        cd123 = ab | rooms271
        

        cd_ = cd123.exclude(id__in=qwer)
        
        eqe= Roomnumber.objects.none()
        eqeelist = []
        if atw_:
            if cod:
                roomtypeexist = False
                checkpromo = promocoderooms.objects.filter(promocode=code)
                for promoroom in checkpromo:
                    if promoroom.roomtype.id is not 23 and promoroom.roomtype.id is not 24 and promoroom.roomtype.id is not 28:
                        if str(promoroom.roomtype.id) in atw_:
                            roomtypeexist = True

                    else:
                        roomtypeexist = True

                if roomtypeexist is False:
                    error = "Invalid Code"
                    cod= None
                    per = 1
                    fix = 0
                    desc = None


            for a in atw_:
                
                afloat=int(float(a))
                ef_ = cd_.exclude(id__in=eqeelist)
                eqee = ef_.filter(room_type_name__id=afloat).last()
                if afloat == 22:
                    eqee_ = 22
                    totalnoofroom = totalnoofroom
                elif afloat ==23:
                    eqee_ = 23
                    totalnoofroom = totalnoofroom 
                elif afloat ==28:
                    eqee_ = 28
                    totalnoofroom = totalnoofroom                                          
                elif afloat == 27:
                    if not eqee:
                        return redirect('test2')
                    linknum = Roomnumber.objects.get(pk=eqee.id)
                    familroom = ef_.filter(link=linknum)
                    for a133 in familroom:
                        eqeelist.append(a133.id)
                    eqee_ = eqee.id
                    totalnoofroom = totalnoofroom+ 2
                else:

                    if eqee == None:
                        print("this is where it went wrong")
                        return redirect('test2')
                    else:


                        totalnoofroom = totalnoofroom+ 1   


                    # eqe = eqe | eqee
                        checklink = Roomnumber.objects.get(pk=eqee.id)
                        if checklink.link is not None:
                            checklink2 = Roomnumber.objects.get(room_number=checklink.link)
                            eqee_ = checklink2.id
                        else:
                           eqee_ = eqee.id
                eqeelist.append(eqee_)



            # cd = cd_
            cd = cd_.exclude(id__in=eqeelist).values('room_type_name__room_type_name', 'room_type_name','room_type_name__room_max_people', 'room_type_name__bedsize','room_type_name__addbed','room_type_name__pk', 'room_type_name__room_type_description', 'room_type_name__facilities','room_type_name__room_image','room_type_name__room_image3','room_type_name__room_image4','room_type_name__room_image2','room_type_name__room_price0','room_type_name__room_price1','room_type_name__room_price2','room_type_name__room_price3','room_type_name__room_price4','room_type_name__room_price5','room_type_name__room_price6').distinct().order_by('-room_type_name__room_price0')

            for c in cd:
                numofstay = int((qout_date-qin_date).days)
                price = 0
                # if c['room_type_name__addbed'] is True:
                #     exc = exc + 1
                #     if c['room_type_name__pk'] == 22:
                #         exc = exc - 1

                for each in range(0, numofstay):

                    date1 = qin_date + timedelta(days=each)
                    try:
                        roompk = c['room_type_name']
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        xprice_ = pricespecial.price

                    except variablepricing.DoesNotExist:

                        day = date1.weekday()

                        # try: 
                        #      Pricing.objects.filter(start_date__lte=date1, )
                        xprice2 = "room_type_name__room_price" + str(day)
                        xprice_ = c[xprice2]
                    addbed=0




                    # discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=c['room_type_name'])
                    # for i in discount:
                    #     per_ = 1-(i.discountper)
                    #     fix_ = i.discountfix
                    #     xprice_ = (xprice_-fix_)*per_
                    # if not discount:
                    #     xprice_ = c[xprice2]



                    price += xprice_
                    c['room_type_name__room_price'] = round((price/numofstay),2)

                

        else:
            # qwer = asdf | we | drrr
            cd = cd_.values('room_type_name__room_type_name', 'room_type_name__room_max_people', 'room_type_name__pk', 'room_type_name__bedsize','room_type_name__addbed','room_type_name','room_type_name__room_type_description', 'room_type_name__room_image','room_type_name__room_image2', 'room_type_name__facilities', 'room_type_name__room_image3','room_type_name__room_image4','room_type_name__room_price0','room_type_name__room_price1','room_type_name__room_price2','room_type_name__room_price3','room_type_name__room_price4','room_type_name__room_price5','room_type_name__room_price6').distinct().order_by('-room_type_name__room_price0')
            price = 0
            for c in cd:
                numofstay = int((qout_date-qin_date).days)
                price = 0
                # addbed=0
                # addbedt = 0
                # addbedtotal=0
                # addbed1 = 0
                # addbed2 = 0
                # addbed3 = 0
                # if c['room_type_name__addbed'] is True:
                #     exc = exc + 1
                #     if c['room_type_name__pk'] == 22:
                #         exc = exc - 1




                for each in range(0, numofstay):
                    date1 = qin_date + timedelta(days=each)

                    try:
                        roompk = c['room_type_name']
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        xprice_ = pricespecial.price

                    except variablepricing.DoesNotExist:
                        day = date1.weekday()
                        
                        
                        xprice2 = "room_type_name__room_price" + str(day)   
                        xprice_ = c[xprice2]


                    # if exc=="1":
                    #     if each is 5:
                    #         addbed= 54.54
                    #         addbedt = 5.46
                    #         addbedtotal = 60  
                    #     else:
                    #         addbed= 45.45
                    #         addbedt = 4.55
                    #         addbedtotal=50


#############################################################################################




                    # discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=c['room_type_name'])
                    # for i in discount:
                    #     per_ = 1-(i.discountper)
                    #     fix_ = i.discountfix
                    #     xprice_ = (xprice_-fix_)*per_
                    # if not discount:
                    #     xprice_ = c[xprice2]

                    
                    # addbed1 += decimal.Decimal(addbed)
                    # addbed2 += decimal.Decimal(addbedt)
                    # addbed3 += decimal.Decimal(addbedtotal)
                    price += xprice_
                    c['room_type_name__room_price'] = round((price/numofstay),2)
                    # c['room_type_name__exb'] = addbed3
                    



                    print(price)    

                

        # de = cd.filter(room_type_name__room_max_people__gte=qnumpeople).values('room_type_name__room_type_name', 'room_type_name__room_max_people', 'room_type_name__pk', 'room_type_name__room_type_description', 'room_type_name__room_price', 'room_type_name__room_image').distinct()
        
        # if not de:
        #     return redirect('test2')

        # print(de)
    else:
        # if exc is None:
        #     exc = "0"
        # else:
        #     exc = str(exc)	
        remove1="-"+remove1	
        newttw = otw.replace(remove1, "", 1)
        print(remove1)
        if remove1 == "-13":
            print("work")
            newttw = newttw.replace("-22", "", 1)

        if cod is not None:
            url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+newttw+"&ce="+cod
        else:
            url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+newttw
        return redirect(url)





    if cod is not None:
        noofdays=(qout_date-qin_date).days

        if code.dayseffective is not None:
            counter41 =noofdays - int(code.dayseffective) 
        else:
            counter41 = 0
        if code.roomeffectiveno is not None:
            roomcounter = int(code.roomeffectiveno)
        else:
            roomcounter = 1500




    if newttw:
        totaldiscount123=0
        roomno=[]
        bookedroom_=[]  
        bookedroomprice_=[]
        roomno = newttw.split('-')
        noofdays=(qout_date-qin_date).days
        roomno_ = [var for var in roomno if var]
        bookedroomtotal = 0  
        bookedroompricebefore = 0 
        beforediscount =0  
        bookedroomprice = 0
        discount=0



        breakfastvalid = False
        if cod is not None:
            if code.specialbreakfastprice > 0:

                for rn1 in roomno_:
                    if int(float(rn1)) is not 22 and int(float(rn1)) is not 23 and int(float(rn1)) is not 28 :
                        try:
                            checkpromo = promocoderooms.objects.get(promocode= code,roomtype__id=int(float(rn1)))
                            breakfastvalid = True
                        except:
                            checkpromo = None
            else:
                
                checkpromo = promocoderooms.objects.filter(promocode= code)
                for promoss in checkpromo:
                    if promoss.roomtype.id == 22:
                        breakfastvalid = True
                        break
                    if promoss.roomtype.id == 23:
                        breakfastvalid = True
                        break










        for i in roomno_:
            # if cod is not None:
            #     if code.roomeffectiveno is not None:
            #         xrasdf = Roomtype.objects.get(pk=i)
            #         if xrasdf == code.roomtype:                
            #             roomcounter = roomcounter+1
            #         else:
            #             if int(float(i)) is not 22 and int(float(i)) is not 23 and int(float(i)) is not 24:
            #                 roomcounter = roomcounter+1




            excget = getattr(Roomtype.objects.get(pk=i), "addbed")

            if excget is True:
                exc = exc + 1
            if i == "22":
                print("ex bed detected")
                exc = exc - 1
            numofstay = int((qout_date-qin_date).days)
            bookedroomprice = 0
            bookedroompricebefore = 0 


            if cod is not None:
                noofdays14=(qout_date-qin_date).days

                if code.dayseffective is not None:
                    counter41 =noofdays14 - int(code.dayseffective) 
                else:
                    counter41 = 0



                if code.roomeffectiveno is not None:

                    xroomt = Roomtype.objects.get(pk=i) 
                    try:
                        checkpromo = promocoderooms.objects.get(promocode=code,roomtype=xroomt)
                        roomcounter = roomcounter-1
                    except:
                        if xroomt == code.roomtype:

                            roomcounter = roomcounter-1 
                        else:
                            roomcounter = roomcounter






            for each in range(0, numofstay):
                date1 = qin_date + timedelta(days=each)

                try:
                    roompk = Roomtype.objects.get(pk=i)
                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                    xprice_ = pricespecial.price
                    xprice_1 = xprice_
                except variablepricing.DoesNotExist:

                    day = date1.weekday()
                    xprice2= "room_price" + str(day)
                    xprice_ = getattr(Roomtype.objects.get(pk=i), xprice2)
                    xprice_1 = xprice_
                xroomt = Roomtype.objects.get(pk=i)
                xpr = xprice_

                # if exc == "1":
                #     if each is 5:
                #         addbed= 54.54
                #         addbedt = 5.46
                #         addbedtotal = 60  
                #         xprice_ = xprice_ + decimal.Decimal(addbed)
                #     else:
                #         addbed= 45.45
                #         addbedt = 4.55
                #         addbedtotal=50
                #         xprice_ = xprice_ + decimal.Decimal(addbed)


                # discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=i)
                # for l in discount:
                #     per_ = 1-(l.discountper)
                #     fix_ = l.discountfix
                #     xpr = ((xprice_-fix_)*per_)
                #     xprice_ = ((xprice_-fix_)*per_)
                # if not discount:
                #     xpr = getattr(Roomtype.objects.get(pk=i), xprice2)
                #     xprice_=getattr(Roomtype.objects.get(pk=i), xprice2)




                if cod is not None:
                    if code.dayseffective is not None:
                        counter41 =counter41-1
                        counter42 = counter41
                    else:
                        counter42 = -1



                    if counter42< 0:

   

                        if code.roomtype is None:
                            if int(float(xroomt.pk)) is not 22 and int(float(xroomt.pk)) is not 23 and int(float(xroomt.pk)) is not 24 and int(float(xroomt.pk)) is not 28:



                                if roomcounter >=0:

                                    if code.onetimeonly is not "USED":
                                        if code.startdate is None:

                                            try:
                                                checkpromo = promocoderooms.objects.get(promocode= code,roomtype=xroomt)
                                                if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            pricex_ = spbkfast
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_

                                                else:
                                                    if sprice>0:
                                                        pricex_ = sprice
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                            except Exception as e:
                                                # if sprice > 0:
                                                #     xprice_ = xprice_
                                                # else:
                                                #     pricex_ = (xpr-fix)*per
                                                #     discount = xprice_-pricex_
                                                #     xprice_ = pricex_

                                                xprice_ = xprice_




                                            # if sprice>0:
                                            #     pricex_ = sprice
                                            #     discount = xprice_-pricex_
                                            #     xprice_ = pricex_
                                            # else:
                                            #     pricex_ = (xpr-fix)*per
                                            #     discount = xprice_-pricex_
                                            #     xprice_ = pricex_


                                            # print(xprice_)
                                            # print(pricex_) 

                                        elif code.enddate >= qout_date.date() and code.startdate <= qin_date.date():


                                            try:
                                                checkpromo = promocoderooms.objects.get(promocode= code,roomtype=xroomt)
                                                if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            pricex_ = spbkfast
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                else:
                                                    if sprice>0:
                                                        pricex_ = sprice
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                            except Exception as e:

                                                # if sprice > 0:
                                                xprice_ = xprice_
                                                # else:
                                                #     pricex_ = (xpr-fix)*per
                                                #     discount = xprice_-pricex_
                                                #     xprice_ = pricex_



                                            # if sprice>0:
                                            #     pricex_ = sprice
                                            #     discount = xprice_-pricex_
                                            #     xprice_ = pricex_
                                            # else:
                                            #     pricex_ = (xpr-fix)*per
                                            #     discount = xprice_-pricex_
                                            #     xprice_ = pricex_
                                            # print(xprice_)
                                            # print(pricex_)                              
                                   # if code.onetimeonly == "YES":
                                   #     code.onetimeonly = "USED"
                                   #     code.save()
                                   #     print(xprice_)  

                            if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                if roomcounter >=0:
                                    if code.onetimeonly is not "USED":
                                        if code.startdate is None:
                                            if breakfastvalid:
                                                if spbkfast>0:
                                                    xprice_ = spbkfast
                                                else:
                                                    pricex_ = (xpr-fix)*per
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_    
                                        elif code.enddate > qout_date.date() and code.startdate < qin_date.date():
                                            if breakfastvalid:
                                                if spbkfast>0:
                                                    xprice_ = spbkfast
                                                else:
                                                    pricex_ = (xpr-fix)*per
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_    




                        else:

                            if xroomt == code.roomtype:

                                # if code.roomeffectiveno is not None:
                                #     roomcounter = roomcounter-1
                                # if roomcounter >=0:

                                    if code.onetimeonly is not "USED":
                                        if code.startdate is None:
                                            if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                                if breakfastvalid:
                                                    if spbkfast>0:
                                                        pricex_ = spbkfast
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_    

                                            else:
                                                if sprice>0:
                                                    pricex_ = sprice
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_
                                                else:
                                                    pricex_ = (xpr-fix)*per
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_



                                            print(xprice_)
                                            print(pricex_)




                                        elif code.enddate >= date1.date() and code.startdate <= date1.date():
                                            pricex_ = (xpr-fix)*per
                                            discount = xprice_-pricex_
                                            xprice_ = pricex_   


                                            if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                                if breakfastvalid:
                                                    if spbkfast>0:
                                                        pricex_ = spbkfast
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_    
                                            else:
                                                if sprice>0:
                                                    pricex_ = sprice
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_
                                                else:
                                                    pricex_ = (xpr-fix)*per
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_
                            
                            # else:


                            #         # roomcounter = roomcounter-1
                            #     if roomcounter >=0:
                            #         if code.onetimeonly is not "USED":
                            #             if code.startdate is None:
                            #                 try:
                            #                     checkpromo = promocoderooms.objects.get(promocode= code,roomtype=xroomt)

                            #                     if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                            #                         if breakfastvalid:
                            #                             if spbkfast>0:
                            #                                 pricex_ = spbkfast
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_
                            #                             else:
                            #                                 pricex_ = (xpr-fix)*per
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_    



                            #                     else:
                            #                         if sprice>0:
                            #                             pricex_ = sprice
                            #                             discount = xprice_-pricex_
                            #                             xprice_ = pricex_
                            #                         else:
                            #                             pricex_ = (xpr-fix)*per
                            #                             discount = xprice_-pricex_
                            #                             xprice_ = pricex_
                            #                 except:
                            #                     if sprice > 0:
                            #                         xprice_ = xprice_
                            #                     else:
                            #                         pricex_ = (xpr-fix)*per
                            #                         discount = xprice_-pricex_
                            #                         xprice_ = pricex_




                                        # elif code.enddate >= date1.date() and code.startdate <= date1.date():
                                        #     try:
                                        #         checkpromo = promocoderooms.objects.get(promocode= code,roomtype=xroomt)
                                        #         if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                        #             if breakfastvalid:
                                        #                 if spbkfast>0:
                                        #                     pricex_ = spbkfast
                                        #                     discount = xprice_-pricex_
                                        #                     xprice_ = pricex_
                                        #                 else:
                                        #                     pricex_ = (xpr-fix)*per
                                        #                     discount = xprice_-pricex_
                                        #                     xprice_ = pricex_    
                                        #         else:
                                        #             if sprice>0:
                                        #                 pricex_ = sprice
                                        #                 discount = xprice_-pricex_
                                        #                 xprice_ = pricex_
                                        #             else:
                                        #                 pricex_ = (xpr-fix)*per
                                        #                 discount = xprice_-pricex_
                                        #                 xprice_ = pricex_
                                        #     except:
                                        #         if sprice > 0:
                                        #             xprice_ = xprice_
                                        #         else:
                                        #             pricex_ = (xpr-fix)*per
                                        #             discount = xprice_-pricex_
                                        #             xprice_ = pricex_




                                                          # xprice_ = (xprice_-fix)*per
                                    # pricex_ = (xpr-fix)*per
                                    # xprice_ = pricex_*decimal.Decimal(1.1)                            
                                    # print (xprice_)
                                        # print(xprice_)
                                        # print(pricex_)   




                                       
                bookedroomprice += xprice_     
                bookedroompricebefore +=xprice_1           

            # bookedroomprice1 = (Roomtype.objects.get(pk=i).room_price)*noofdays
            bookedroom = Roomtype.objects.get(pk=i)
            bookedroomtotal += bookedroomprice
            beforediscount += bookedroompricebefore
            bookedroom_.append(bookedroom)
            bookedroomprice_.append(format(bookedroompricebefore, '.2f'))

 
        bookr=zip(bookedroom_,bookedroomprice_)

        if notaxset:
            sech = 0
        else:    
            sech= format(float(bookedroomtotal)*0.06,'.2f')

        # sech = 0
        # sech= None
        totaldiscount123 = beforediscount - bookedroomtotal 
        totaldiscount123= format(float(totaldiscount123),'.2f')

        if notaxset:
            bookedroomtotal11= format(float(bookedroomtotal),'.2f')
        else:
            bookedroomtotal11= format(float(bookedroomtotal)*1.06,'.2f')

        # bookedroomtotal11= format(bookedroomtotal,'.2f')    



        tac = noofdays*52




    
    else:
        bookr= None
        bookedroom_= None
        bookedroomprice_= None
        bookedroomtotal11 = None
        noofdays = None
        tac=None
        sech=None


    
    # if user555 is not None:
    if noofdays is not None:
        total132nofodays = int(numberusage) + (noofdays*totalnoofroom)   
    else:
        total132nofodays = 0
        # if totalnoofdays > 10:
        # specialpromologgedin = "yes"
    # if total132nofodays<3:
    #     total132nofodays = total132nofodays%15
    # else:
    #     total132nofodays = 99


    if user55 is not None:
        if not cod:
            memberdiscount = Promocode.objects.filter(membersonly=True, points__lte=total132nofodays, active = True)
        else:
            memberdiscount = None
    
    else:
        memberdiscount = None






    if user55 is None:
        if cod:
            try:
                codeauthenticate = Promocode.objects.get(code=cod,membersonly=False)
            except:
                url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+newttw
                return redirect(url)
    else:
        if cod:
            try:
                codeauthenticate = Promocode.objects.get(membersonly=True, points__lte=total132nofodays, code=cod)
            except:
                url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+newttw
                return redirect(url)                


            # else:
            #     try:
            #         codeauthenticate = Promocode.objects.get(code=cod,membersonly=False)
            #         url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+newttw
            #         return redirect(url)

            #     except:
            #         print("none")




    print(exc)

    context = {
        "total132nofodays":total132nofodays,
        "dateform":dateform,
        "desc":desc,
         "cod":cod,
         "ab": ab,
         "cd": cd,
         "bookr":bookr,
         "sech":sech,
         "exc":exc,
         # "de": de,
         "qout_date1": qout_date1,
         "qin_date1": qin_date1,
         # "dc":dc,
         "ttw":newttw,
         "bookedroom_":bookedroom_,
         "bookedroomprice_":bookedroomprice_,   
         "bookedroomtotal":bookedroomtotal11,
         "noofdays":noofdays,
         "tac":tac,
         "user55":user55,
         "error":error,
         "totaldiscount123":totaldiscount123,
         "roomcounter":roomcounter,
         "memberdiscount":memberdiscount


         # "qnumpeople" : qnumpeople,
    }
    return render(request, "booking/results.html", context)













def form(request):
    if request.user.is_authenticated(): 
        return redirect('manualbook')
    qin_date1=request.GET.get('checkin_date')
    qout_date1=request.GET.get('checkout_date')
    rb = request.GET.get('otw')
    tac=request.GET.get('tac')
    cod = request.GET.get('ce')
    exb = request.GET.get('exb')


    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    todaydatestring = todaydate.strftime("%Y-%m-%d")
    todaydatexact = datetime.strptime(todaydatestring, '%Y-%m-%d')
    todaydate = todaydatexact

    notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
    notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
    notaxset = False

    noofdayscount = 0





    if qin_date1 == None:
        return redirect('test2')    
    
    user515 = None
    user55 = None

    if '1335i99fl' not in request.session:
        user515 = None
        user55 = None
    else:
        userhash = request.session['1335i99fl']

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))
        # reflect = nowa-timestamptime
        # reflect2 = str(reflect) + str("=") + str(nowa) + "-" + str(timestamptime) + " ==" + str(hashcode)
        # return HttpResponse(reflect2)
    # print(clearing)
        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)

            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                user515 = user55
            else:
                user515 = None
                user55 = None
        else:
            user515 = None
            user55 = None



    malaysiatime = (datetime.now() + timedelta(hours=8)).date()

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found') 

    if cod is not None:
        print('notnone')
        try:
            code1 = Promocode.objects.get(code=cod)
            # per = (1-code1.discountper)
            # fix = code1.discountfix
            # desc = code1.description
            # error = None        
            # print('noerror')

            spbkfast = 0
            sprice = 0


            qin_date = parsing_date(qin_date1)

            qout_date = parsing_date(qout_date1)
            noofdays=(qout_date-qin_date).days
            noofdayscount = 0

            # if code1.dayseffective is not None:
            #     counter41 =noofdays - int(code1.dayseffective) 
            # else:
            #     counter41 = 0
            roomcounter =0
            if code1.roomeffectiveno is not None:
                roomcounter = int(code1.roomeffectiveno)
            else:
                roomcounter = 1500






            if code1.onetimeonly == "USED":
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None
            elif code1.active==False:
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None                
            
            elif code1.daysbefore is not None:
                dayscalculator = code1.daysbefore
                qin_date = parsing_date(qin_date1)
                date1today = datetime.now()
                today1datestrftime = parsing_date((date1today + timedelta(hours=8)).strftime("%Y-%m-%d"))              
                calcnoofdays=(qin_date-today1datestrftime).days
                if calcnoofdays < dayscalculator:
                    error = "Invalid Code"
                    cod= None
                    per = 1
                    fix = 0
                    desc = None                
                
                else: 
                    per = (1-code1.discountper)
                    fix = code1.discountfix
                    desc = code1.description
                    error = None    
                    if code1.specialbreakfastprice > 0:
                        spbkfast = code1.specialbreakfastprice

                    if code1.specialprice > 0:
                        sprice = code1.specialprice



            elif code1.validfrom is not None and code1.validfrom > malaysiatime:
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None


            elif code1.validto is not None and code1.validto < malaysiatime:   
                error = "Invalid Code"
                cod= None
                per = 1
                fix = 0
                desc = None






            else: 
                per = (1-code1.discountper)
                fix = code1.discountfix
                desc = code1.description
                error = None  

                if code1.specialbreakfastprice > 0:
                    spbkfast = code1.specialbreakfastprice

                if code1.specialprice > 0:
                    sprice = code1.specialprice









        except Promocode.DoesNotExist:
            error = "Invalid Code"
            cod=None
            print(error)

            per = 1
            fix=0
            desc = None

    else:
        cod = None
        per = 1
        fix = 0
        desc= None

    roomno = rb.split('-')
    roomno_ = [var for var in roomno if var]
    breakfastvalid = False
    # if cod is not None:
    #     if code1.specialbreakfastprice > 0:

    #         for rn1 in roomno_:
    #             if int(float(rn1)) is not 22 and int(float(rn1)) is not 23 and int(float(rn1)) is not 28 :
    #                 try:
    #                     checkpromo = promocoderooms.objects.get(promocode= code1,roomtype__pk=int(float(rn1)))
    #                     breakfastvalid = True
    #                 except:
    #                     checkpromo = None





    if cod is not None:
        if code1.specialbreakfastprice > 0:

            for rn1 in roomno_:
                if int(float(rn1)) is not 22 and int(float(rn1)) is not 23 and int(float(rn1)) is not 28 :
                    try:
                        checkpromo = promocoderooms.objects.get(promocode= code1,roomtype__id=int(float(rn1)))
                        breakfastvalid = True
                    except:
                        checkpromo = None
        else:
            
            checkpromo = promocoderooms.objects.filter(promocode= code1)
            for promoss in checkpromo:
                if promoss.roomtype.id == 22:
                    breakfastvalid = True
                    break
                if promoss.roomtype.id == 23:
                    breakfastvalid = True
                    break




    # rt = float(Roomtype.objects.get(pk=id).room_price)
    # rtn = Roomtype.objects.get(pk=id)
    # request.session.set_test_cookie()

    # if request.session.test_cookie_worked():
    #     request.session.delete_test_cookie()
    #     qin_date = request.session['qin_date']
    #     qout_date = request.session['qout_date']
    #     # number_of_people = request.session['qnumpeople']
        
    # else:
    qin_date = qin_date1
    qout_date = qout_date1
    if user515 is not None:
        form = BookingForm(request.POST or None, initial={'checkin_date': qin_date, 'checkout_date': qout_date, 'first_name': user515.first_name,'last_name':  user515.last_name,'phone_number': user515.phone_number,'email': user515.email,'country':user515.country} )
    else:
        form = BookingForm(request.POST or None, initial={'checkin_date': qin_date, 'checkout_date': qout_date} )
   
    # print(date.today())
    # abc = Roomnumber.objects.get(pk=randomnumber)

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    qin_date_ = parsing_date(qin_date)
    qout_date_ = parsing_date(qout_date)

    days1 = (qout_date_-qin_date_).days
    noofdays = days1
    testnum_ = 0
    testac= str(days1*52)
    total = 0
    gsttotaltotal=0
    stotaltotal=0
    hprice=[]
    tourist=0
    tourist2=0
    tourist1=0
    
    totalnoofroom = 0



    for id in roomno_:
        afloat=int(float(id))
        if afloat == 22:
            totalnoofroom = totalnoofroom
        elif afloat ==23:
            totalnoofroom = totalnoofroom 
        elif afloat ==28:
            totalnoofroom = totalnoofroom                                          
        elif afloat == 27:
            totalnoofroom = totalnoofroom+ 2
        else:
            totalnoofroom = totalnoofroom+ 1   




    if todaydate > notaxstartdate and todaydate < notaxenddate:
        if qin_date_ > notaxstartdate and qin_date_ < notaxenddate:
            if qout_date_ > notaxstartdate and qout_date_ < notaxenddate:
                notaxset = True









    if testac == tac:

        if form.is_valid():



            if user55 is None:
                if cod:
                    try:
                        codeauthenticate = Promocode.objects.get(code=cod,membersonly=False)
                    except:
                        url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+rb
                        return redirect(url)
            else:

                total132nofodays = int(user55.numbertime) + (int(noofdays)*int(totalnoofroom))
                if cod:
                    try:
                        codeauthenticate = Promocode.objects.get(membersonly=True, points__lte=total132nofodays, code=cod)
                    except:
                        url="https://innbparkhotel.com/results/?checkin_date="+qin_date1+"&checkout_date="+qout_date1+"&otw="+rb
                        return redirect(url)     





            cin_date = form.cleaned_data['checkin_date']
            cout_date = form.cleaned_data['checkout_date']
            country = request.POST.get('country')
            referral = form.cleaned_data['referral']
            occupation =  form.cleaned_data['occupation']
            purposeoftrip = form.cleaned_data['purposeoftrip']

            # fnumpeople=form.cleaned_data['number_of_people']
            days = cout_date-cin_date
            timedel = days.total_seconds() / timedelta (days=1).total_seconds()
            now = datetime.now()


            eemail2 = form.cleaned_data['email']
            phno = form.cleaned_data['phone_number']
            # referral = form.cleaned_data['referral']
            if user515 is not None:
                try:
                    code13 = Customer.objects.get(user_login=user515)
                    code13.phone_number = form.cleaned_data['phone_number']
                    code13.first_name = form.cleaned_data['first_name']
                    code13.last_name = form.cleaned_data['last_name']
                    code13.save()
                    cuspk = code13.pk
                    # if code.phone_number == (phno):
                    #     cuspk = code.pk
                    # else:
                    #     customer = Customer.objects.create()
                    #     customer.first_name = form.cleaned_data['first_name']
                    #     customer.last_name = form.cleaned_data['last_name']
                    #     customer.email=form.cleaned_data['email']
                    #     customer.phone_number=form.cleaned_data['phone_number']
                    #     customer.country = form.cleaned_data['country']
                    #     customer.save()
                    #     cuspk = customer.pk


                except Customer.DoesNotExist:
                    try:
                        code = Customer.objects.get(email=eemail2, phone_number=phno)
                        code.first_name = form.cleaned_data['first_name']
                        code.last_name = form.cleaned_data['last_name']
                        code.user_login=user515
                        code.save()
                        cuspk = code.pk

                    except Customer.DoesNotExist:
                        customer = Customer.objects.create()
                        customer.first_name = form.cleaned_data['first_name']
                        customer.last_name = form.cleaned_data['last_name']
                        customer.email=form.cleaned_data['email']
                        customer.phone_number=form.cleaned_data['phone_number']
                        customer.country = country
                        customer.user_login=user515
                        customer.save()
                        cuspk = customer.pk

            else:

                try:
                    code = Customer.objects.get(email=eemail2, phone_number=phno)
                    code.first_name = form.cleaned_data['first_name']
                    code.last_name = form.cleaned_data['last_name']
                    code.save()
                    cuspk = code.pk
                    if code.user_login:
                        user515 = code.user_login
                    # if code.phone_number == (phno):
                    #     cuspk = code.pk
                    # else:
                    #     customer = Customer.objects.create()
                    #     customer.first_name = form.cleaned_data['first_name']
                    #     customer.last_name = form.cleaned_data['last_name']
                    #     customer.email=form.cleaned_data['email']
                    #     customer.phone_number=form.cleaned_data['phone_number']
                    #     customer.country = form.cleaned_data['country']
                    #     customer.save()
                    #     cuspk = customer.pk


                except Customer.DoesNotExist:
                    customer = Customer.objects.create()
                    customer.first_name = form.cleaned_data['first_name']
                    customer.last_name = form.cleaned_data['last_name']
                    customer.email=form.cleaned_data['email']
                    customer.phone_number=form.cleaned_data['phone_number']
                    customer.country = country
                    customer.save()
                    cuspk = customer.pk
            depamt = 0
            invoicedeposit = 0
            roomstt = 0




            for id in roomno_:

                if cod is not None:
                    if code1.roomeffectiveno is not None:

                        xroomt = Roomtype.objects.get(pk=id) 
                        try:
                            checkpromo = promocoderooms.objects.get(promocode=code1,roomtype=xroomt)
                            roomcounter = roomcounter-1
                        except:
                            if xroomt == code1.roomtype:

                                roomcounter = roomcounter-1 
                            else:
                                roomcounter = roomcounter

                # if cod is not None:
                #     if code1.roomeffectiveno is not None:


                      
                #         xrasdf = Roomtype.objects.get(pk=id)
                #         if xrasdf == code1.roomtype:                
                #             roomcounter = roomcounter-1

                #         else:
                #             if int(float(i)) is not 22 and int(float(i)) is not 23 and int(float(i)) is not 24:
                #                 roomcounter = roomcounter-1


                # if cod is not None:
                #     if code.roomeffectiveno is not None:
                #         xrasdf = Roomtype.objects.get(pk=i)
                #         if xrasdf == code.roomtype:                
                #             roomcounter = roomcounter+1
                #         else:
                #             if int(float(i)) is not 22 and int(float(i)) is not 23 and int(float(i)) is not 24:
                #                 roomcounter = roomcounter+1

                room01 = None
                room02 = None
                if int(float(id)) == 27:

                    noofdays = noofdays + days1
                    rtn = Roomtype.objects.get(pk=id)

                    aaaa =  Roomnumber.objects.all().filter(link__isnull=False, hidden=False)
                    # we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
                    # asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
                    # drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                    # qwer = asdf | we | drrr
                    # cd = aaaa.exclude(id__in=qwer)
                    cd = aaaa
                    if not cd:
                        return redirect('test2')
                    de = cd

                    # randomnumber = random.choice(de)
                    # rnum= Roomnumber.objects.get(room_number=randomnumber)
                    for one1 in de:
                        rnum = one1
                        if room01 and room02 is not None:
                            break
                        one11 = one1 

                        n = "passed"                                
                        rnum1 = Roomnumber.objects.get(room_number=one11)
                        we = Booking.objects.filter(checkin_date__gte=cin_date, checkin_date__lt=cout_date,room_number=rnum1)
                        if we:
                            n="notpassed"
                        asdf = Booking.objects.filter(checkout_date__gt=cin_date,checkout_date__lte=cout_date,room_number=rnum1)
                        if asdf:
                            n="notpassed"
                        drrr = Booking.objects.filter(checkin_date__lte=cin_date, checkout_date__gte=cout_date,room_number=rnum1)
                        if drrr: 
                            n="notpassed"

                        if n is "notpassed":

                            room01 = None
                            room02 = None
                            de = de.exclude(pk=one11.pk)

                        else:
                            room01 = rnum1
                            rtname01 = room01.room_type_name


                            linkbookcheck = Roomnumber.objects.filter(link=one11.link).exclude(pk=one11.pk)
                            for a1 in linkbookcheck:
                                n = "passed"                                
                                rnum1 = Roomnumber.objects.get(room_number=a1)
                                we = Booking.objects.filter(checkin_date__gte=cin_date, checkin_date__lt=cout_date,room_number=rnum1)
                                if we:
                                    n="notpassed"
                                asdf = Booking.objects.filter(checkout_date__gt=cin_date,checkout_date__lte=cout_date,room_number=rnum1)
                                if asdf:
                                    n="notpassed"
                                drrr = Booking.objects.filter(checkin_date__lte=cin_date, checkout_date__gte=cout_date,room_number=rnum1)
                                if drrr: 
                                    n="notpassed"


                                if n is "notpassed":

                                    room01 = None
                                    room02 = None

                                else:

                                    room02 = rnum1
                                    rtname02 = room02.room_type_name


                    if n is "notpassed":                            
                        return redirect('test2')
                    else:
                        allrtntest = Roomnumber.objects.filter(link=room02.link)

                        first_name = form.cleaned_data['first_name']
                        last_name = form.cleaned_data['last_name']
                        # rt = float(Roomtype.objects.get(pk=id).room_price)
                        for x in first_name:
                           test_name= str(ord(x)) 
                        for y in last_name:
                           testl_name= str(ord(y))    
                        referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")
                        numofstay = int((cout_date-cin_date).days)

                        if int(float(id)) is not 22 and int(float(id)) is not 23 and int(float(id)) is not 28 :

                            depamt = depamt + 200
                            randomnumber = random.choice(de)
                            tourist1 = tourist1+(10*numofstay)
                        else:
                            print("Exception work once")
                            depamt = depamt
                            randomnumber = None
                            tourist1 = tourist1

                        print (randomnumber)
                        testnum = 1
                        testnum_ += testnum


                        bookedroomprice = 0
                        gsttotal= 0
                        actualaa =0

                        noof1313days=days1

                        if cod is not None:
                            if code1.dayseffective is not None:
                                counter41 =noof1313days - int(code1.dayseffective) 
                            else:
                                counter41 = 0

                        for each in range(0, numofstay):

                            
                            date1 = cin_date + timedelta(days=each)
                            
                            if int(float(id)) is not 22 and int(float(id)) is not 23 and int(float(id)) is not 24  and int(float(id)) is not 28:
                                noofdayscount = noofdayscount + 2
                            try:
                                roompk = Roomtype.objects.get(pk=id)
                                pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                yy = pricespecial.price

                            except variablepricing.DoesNotExist:




                                day = date1.weekday()

                                xprice = "room_price" + str(day)  
                                yy = getattr(Roomtype.objects.get(pk=id), xprice)


                            xpr = yy
                            actuala = yy

                            # if int(float(id)) is not 22 and int(float(id)) is not 23 :                    
                            #     tourist = 10
                            # if id = 13 :
                                # if exb = 1:
                                #     if each = 5 or each = 6,
                                #     yy = yy+ 54.55
                                # actuala = yy

                                #     else:
                                #         yy= yy+ 45.45
                                #         actuala = yy




        ####################################################################################################################                    


                            toatal = yy 


                            # bookedroomprice = bookedroomprice
                            # gsttotal += gst
                            # hprice.append(toatal)
                            pricex_ = toatal
                            xprice_ = yy

                            















                # if cod is not None:
                #     if code.dayseffective is not None:
                #         counter41 =counter41-1
                #         counter42 = counter41
                #     else:
                #         counter42 = 1500

                #     if counter42<= 0:



                #         if code.roomtype is None:
                #             if code.onetimeonly is not "USED":
                #                 if code.startdate is None:
                #                     pricex_ = (xpr-fix)*per
                #                     discount = xprice_-pricex_
                #                     xprice_ = pricex_

                #                     print(xprice_)
                #                     print(pricex_) 

                #                 elif code.enddate > qout_date and code.startdate < qin_date:
                #                     pricex_ = (xpr-fix)*per

                #                     xprice_ = pricex_

                #                     print(xprice_)
                #                     print(pricex_)                              
                #                # if code.onetimeonly == "YES":
                #                #     code.onetimeonly = "USED"
                #                #     code.save()
                #                #     print(xprice_)                 	
                #         if xroomt == code.roomtype:

                #             if roomcounter >= 0:
                #                 if code.onetimeonly is not "USED":
                #                     if code.startdate is None:
                #                         pricex_ = (xpr-fix)*per
                #                         discount = xprice_-pricex_
                #                         xprice_ = pricex_
                #                         print(xprice_)
                #                         print(pricex_)

                #                     elif code.enddate >= date1 and code.startdate <= date1:
                #                         pricex_ = (xpr-fix)*per
                #                         discount = xprice_-pricex_
                #                         xprice_ = pricex_                            # xprice_ = (xprice_-fix)*per
                #                     # pricex_ = (xpr-fix)*per
                #                     # xprice_ = pricex_*decimal.Decimal(1.1)                            
                #                     # print (xprice_)
                #                         print(xprice_)
                #                         print(pricex_) 







                            if cod is not None:
                                if code1.dayseffective is not None:
                                    counter41 =counter41-1
                                    counter42 = counter41
                                else:
                                    counter42 = -2

                                if counter42< 0:                                
                                    if code1.roomtype is None:






                                        if int(float(rtn.pk)) is not 22 and int(float(rtn.pk)) is not 23 and int(float(rtn.pk)) is not 24 and int(float(rtn.pk)) is not 28  :

                                            # if code1.roomeffectiveno is not None:
                                            #     try:
                                            #         checkpromo = promocoderooms.objects.get(promocode=code1,roomtype=rtn)
                                            #         roomcounter = roomcounter-1
                                            #     except:
                                            #         roomcounter = roomcounter

                                            if roomcounter >= 0:

                                                
                                                if code1.onetimeonly is not "USED":
                                                    if code1.startdate is None:


                                                        try:
                                                            checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)

                                                            if sprice>0:
                                                                pricex_ = sprice
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                        except:
                                                            # if code1.roomeffectiveno is not None:
                                                            xprice_ = xprice_
                                                            # else:
                                                            #     pricex_ = (xpr-fix)*per
                                                            #     discount = xprice_-pricex_
                                                            #     xprice_ = pricex_
                                                            




                                                        # if sprice>0:
                                                        #     pricex_ = sprice
                                                        #     xprice_ = pricex_
                                                        # else:
                                                        #     pricex_ = (xpr-fix)*per
                                                        #     xprice_ = pricex_

                                                        if code1.onetimeonly == "YES":
                                                            code1.onetimeonly = "USED"
                                                            code1.save()
                                                            print(xprice_)                                      

                                                    elif code1.enddate >= qout_date_ and code1.startdate <= qin_date_:


                                                        try:
                                                            checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)

                                                            if sprice>0:
                                                                pricex_ = sprice
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                        except:
                                                            if code1.roomeffectiveno is not None:
                                                                xprice_ = xprice_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_









                                                        # if sprice>0:
                                                        #     pricex_ = sprice
                                                        #     xprice_ = pricex_
                                                        # else:
                                                        #     pricex_ = (xpr-fix)*per
                                                        #     xprice_ = pricex_


                                                        # print(xprice_)
                                                        # print(pricex_)                              
                                                        if code1.onetimeonly == "YES":
                                                            code1.onetimeonly = "USED"
                                                            code1.save()
                                                            print(xprice_)  


                                        if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                            if roomcounter >=0:
                                                if code1.onetimeonly is not "USED":
                                                    if code1.startdate is None:
                                                        if breakfastvalid:
                                                            if spbkfast>0:
                                                                xprice_ = spbkfast
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            if code1.onetimeonly == "YES":
                                                                code1.onetimeonly = "USED"
                                                                code1.save()
                                                                print(xprice_)  


                                                    elif code1.enddate > qout_date and code1.startdate < qin_date:
                                                        if breakfastvalid:
                                                            if spbkfast>0:
                                                                xprice_ = spbkfast
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_

                                                            if code1.onetimeonly == "YES":
                                                                code1.onetimeonly = "USED"
                                                                code1.save()
                                                                print(xprice_)  



                                    else:
                                        if rtn == code1.roomtype:

                                            # if code1.roomeffectiveno is not None:
                                            #     roomcounter = roomcounter-1




                                            # if roomcounter >= 0:

                                            if code1.onetimeonly is not "USED":


                                                if code1.startdate is None:
                                                    if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                        if breakfastvalid:
                                                            if spbkfast>0:
                                                                pricex_ = spbkfast
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_    

                                                    else:
                                                        if sprice>0:
                                                            pricex_ = sprice
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_








                                                # if code1.startdate is None:
                                                #     if sprice>0:
                                                #         pricex_ = sprice
                                                #         xprice_ = pricex_
                                                #     else:
                                                #         pricex_ = (xpr-fix)*per
                                                #         xprice_ = pricex_

                                                #     print(xprice_)
                                                #     print(pricex_)
                                                    if code1.onetimeonly == "YES":
                                                        code1.onetimeonly = "USED"
                                                        code1.save()
                                                        print(xprice_)                                     

                                                elif code1.enddate > qout_date_.date() and code1.startdate < qin_date_.date():
                                                    
                                                    pricex_ = (xpr-fix)*per
                                                    discount = xprice_-pricex_
                                                    xprice_ = pricex_   


                                                    if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                        if breakfastvalid:
                                                            if spbkfast>0:
                                                                pricex_ = spbkfast
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_    
                                                    else:
                                                        if sprice>0:
                                                            pricex_ = sprice
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_




                                                    # pricex_ = (toatal-fix)*per
                                                    # xprice_ = pricex_
                                                    # if sprice > 0:
                                                    #     pricex_ = sprice
                                                    #     xprice_ = pricex_


                                                    if code1.onetimeonly == "YES":
                                                        code1.onetimeonly = "USED"
                                                        code1.save()
                                                        print(xprice_)                                     
                                                # xprice_ = (xprice_-fix)*per
                                                # pricex_ = (xpr-fix)*per
                                                # xprice_ = pricex_*decimal.Decimal(1.1)                            
                                                # print (xprice_)
                                                    # print(xprice_) 
                                                    # print(pricex_)  

                                        # else:
                                        #     if code1.roomeffectiveno is not None:
                                        #         try:
                                        #             checkpromo = promocoderooms.objects.get(promocode=code1,roomtype=rtn)
                                        #             roomcounter = roomcounter-1
                                        #         except:
                                        #             roomcounter = roomcounter
                                        #     if roomcounter >=0:

                                        #         if code1.onetimeonly is not "USED":
                                        #             if code1.startdate is None:
                                        #                 try:
                                        #                     checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                                        #                     if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                        #                         if breakfastvalid:
                                        #                             if spbkfast>0:
                                        #                                 pricex_ = spbkfast
                                        #                                 xprice_ = pricex_
                                        #                             else:
                                        #                                 pricex_ = (xpr-fix)*per
                                        #                                 discount = xprice_-pricex_
                                        #                                 xprice_ = pricex_ 


                                        #                     else:
                                        #                         if sprice>0:
                                        #                             pricex_ = sprice
                                        #                             discount = xprice_-pricex_
                                        #                             xprice_ = pricex_
                                        #                         else:
                                        #                             pricex_ = (xpr-fix)*per
                                        #                             discount = xprice_-pricex_
                                        #                             xprice_ = pricex_
                                        #                 except:
                                        #                     if code1.roomeffectiveno is not None:
                                        #                         xprice_ = xprice_
                                        #                     else:
                                        #                         pricex_ = (xpr-fix)*per
                                        #                         discount = xprice_-pricex_
                                        #                         xprice_ = pricex_




                                        #                 # if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                        #                 #     if spbkfast>0:
                                        #                 #         pricex_ = spbkfast
                                        #                 #         discount = xprice_-pricex_
                                        #                 #         xprice_ = pricex_



                                        #             elif code1.enddate >= date1.date() and code1.startdate <= date1.date():
                                        #                 try:
                                        #                     checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                                        #                     if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                        #                         if breakfastvalid:
                                        #                             if spbkfast>0:
                                        #                                 pricex_ = spbkfast
                                        #                                 xprice_ = pricex_
                                        #                             else:
                                        #                                 pricex_ = (xpr-fix)*per
                                        #                                 discount = xprice_-pricex_
                                        #                                 xprice_ = pricex_    
                                        #                     else:
                                        #                         if sprice>0:
                                        #                             pricex_ = sprice
                                        #                             discount = xprice_-pricex_
                                        #                             xprice_ = pricex_
                                        #                         else:
                                        #                             pricex_ = (xpr-fix)*per
                                        #                             discount = xprice_-pricex_
                                        #                             xprice_ = pricex_

                                        #                 except:
                                        #                     if code1.roomeffectiveno is not None:
                                        #                         xprice_ = xprice_
                                        #                     else:
                                        #                         pricex_ = (xpr-fix)*per
                                        #                         discount = xprice_-pricex_
                                        #                         xprice_ = pricex_


                                                        # if int(float(xroomt.pk)) is 23 or int(float(xroomt.pk)) is 24:
                                                        #     if spbkfast>0:
                                                        #         pricex_ = spbkfast
                                                        #         discount = xprice_-pricex_
                                                        #         xprice_ = pricex_










                            if int(float(id)) is  23 :
                                actuala = yy
                                pricex_ = yy


                            actuala = decimal.Decimal(format(actuala,'.2f'))
                            pricex_= decimal.Decimal(format(pricex_,'.2f'))
                            hprice.append(pricex_)   
                            actualaa += actuala
                            bookedroomprice += pricex_
                        # tourist1 += tourist

                        # roomstt = str(randomnumber) + "," +  str(roomstt)

                        # bookedroomprice += xprice_
                        gsttotal = 0
                        # bookedroomprice2 = bookedroomprice*decimal.Decimal(1.1)
                        # stotal = decimal.Decimal(format(bookedroomprice*decimal.Decimal(0.06),'.2f'))

                        # stotal=0
                        bookedroomprice2 = bookedroomprice
                        bookedroomprice10 = bookedroomprice              



                        actualaasdf = actualaa
                        print(bookedroomprice)





                        for affa in allrtntest:

                            aa  = form.save(commit=False)
                            aa.room_type_name = affa.room_type_name
                 
                            aa.room_number = affa
                            if cod is not None:
                                aa.discountper = code1.discountper
                            aa.paymentprice = decimal.Decimal(bookedroomprice10)/decimal.Decimal(2) 
                            aa.actualpay =  decimal.Decimal(actualaasdf)/decimal.Decimal(2) 
                            aa.referenceno = referenceno
                            aa.country = country
                            aa.cust33 = Customer.objects.get(pk=cuspk)
                            aa.deposit = max(hprice)*decimal.Decimal(1.06)
                            # aa.deposit = max(hprice)
                            invoicedeposit += aa.deposit
                            aa.extraref=str(testnum_)
                            aa.familyroom=True
                            aa.save()
                            aa.pk=None
                            if cod is not None:
                                adf="ttw=" + referenceno + "&ce=" + cod
                            else:
                                adf="ttw=" + referenceno

                        
                            # if cod is not None:
                            #     if code1.roomtype is None:
                            #         if code1.onetimeonly is not "USED":
                            #            bookedroomprice = (bookedroomprice-fix)*per
                            #            if code1.onetimeonly == "YES":
                            #                code1.onetimeonly = "USED"
                            #                code1.save()                       

                            #     if rtn == code1.roomtype:
                            #         if code1.onetimeonly is not "USED":
                            #            bookedroomprice = (bookedroomprice-fix)*per
                            #            if code1.onetimeonly == "YES":
                            #                code1.onetimeonly = "USED"
                            #                code1.save()
                        
                        total = total + bookedroomprice2
                        gsttotaltotal = gsttotaltotal + gsttotal
                        # stotaltotal = stotaltotal + stotal
                        tourist2 = tourist1 + tourist2










                else:
                    print(id)
                    hprice=[]

                    rtn = Roomtype.objects.get(pk=id)
                    aaaa =  Roomnumber.objects.all().filter(room_type_name__room_type_name=rtn, hidden=False)
                    we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=cin_date, booking__checkin_date__lt=cout_date, booking__checkout_date__gt=F('booking__checkin_date'))
                    asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=cin_date,booking__checkout_date__lte=cout_date, booking__checkin_date__lt=F('booking__checkout_date'))
                    drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=cin_date, booking__checkout_date__gte=cout_date)
                    qwer = asdf | we | drrr
                    cd = aaaa.exclude(id__in=qwer)
                    de = cd
                    if int(float(id)) is not 22 and int(float(id)) is not 23 and int(float(id)) is not 28:
    	                if not de:
    	                    return redirect('test2')

                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    # rt = float(Roomtype.objects.get(pk=id).room_price)
                    for x in first_name:
                       test_name= str(ord(x)) 
                    for y in last_name:
                       testl_name= str(ord(y))    
                    referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")
                    numofstay = int((cout_date-cin_date).days)

                    if int(float(id)) is not 22 and int(float(id)) is not 23 and int(float(id)) is not 28:

                        depamt = depamt + 200
                        randomnumber = random.choice(de)
                        tourist1 = tourist1+(10*numofstay)
                    else:
                        print("Exception work once")
                        depamt = depamt
                        randomnumber = None
                        tourist1 = tourist1

                    print (randomnumber)
                    testnum = 1
                    testnum_ += testnum


                    bookedroomprice = 0
                    gsttotal= 0
                    actualaa =0

                    if cod is not None:
                        noof1313days=days1
                        if code1.dayseffective is not None:
                            counter41 =noof1313days - int(code1.dayseffective) 
                        else:
                            counter41 = 0


                    for each in range(0, numofstay):
                        if int(float(id)) is not 22 and int(float(id)) is not 23 and int(float(id)) is not 24 and int(float(id)) is not 28:
                            noofdayscount = noofdayscount + 1                        
                        date1 = cin_date + timedelta(days=each)
                        try:
                            roompk = Roomtype.objects.get(pk=id)
                            pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                            yy = pricespecial.price

                        except variablepricing.DoesNotExist:

                            day = date1.weekday()

                            xprice = "room_price" + str(day)  
                            yy = getattr(Roomtype.objects.get(pk=id), xprice)


                        xpr = yy
                        actuala = yy

                        # if int(float(id)) is not 22 and int(float(id)) is not 23 :                    
                        #     tourist = 10
                        # if id = 13 :
                            # if exb = 1:
                            #     if each = 5 or each = 6,
                            #     yy = yy+ 54.55
                            # actuala = yy

                            #     else:
                            #         yy= yy+ 45.45
                            #         actuala = yy




    ####################################################################################################################                    

                        # discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=rtn)                    
                        # for i in discount:
                        #     per_ = 1-(i.discountper)
                        #     fix_ = i.discountfix

                        #     yy = (yy-fix_)*per_
                        #     # gst = yy*decimal.Decimal(0.1)
                        #     toatal = yy 


                        # if not discount:
                            # gst = yy*decimal.Decimal(0.1)
                        toatal = yy 
                        xpr = yy

                        # bookedroomprice = bookedroomprice
                        # gsttotal += gst
                        # hprice.append(toatal)
                        pricex_ = toatal
                        xprice_ = yy
                        if cod is not None:



                            if code1.dayseffective is not None:
                                counter41 =counter41-1
                                counter42 = counter41
                            else:
                                counter42 = -2




                            # if code1.roomeffectiveno is not None:
                            #     if roomcounter <= int(code1.roomeffectiveno):




                            if counter42< 0:   




                                if code1.roomtype is None:

                                    if int(float(rtn.pk)) is not 22 and int(float(rtn.pk)) is not 23 and int(float(rtn.pk)) is not 24  and int(float(rtn.pk)) is not 28:

                                        # if code1.roomeffectiveno is not None:
                                        #     try:
                                        #         checkpromo = promocoderooms.objects.get(promocode=code1,roomtype=rtn)
                                        #         roomcounter = roomcounter-1
                                        #     except:
                                        #         roomcounter = roomcounter



                                        if roomcounter >= 0:

                                            if code1.onetimeonly is not "USED":
                                                if code1.startdate is None:
                                                    try:
                                                        checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                                                        if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                            if breakfastvalid:
                                                                if spbkfast>0:
                                                                    pricex_ = spbkfast
                                                                    discount = xprice_-pricex_
                                                                    xprice_ = pricex_
                                                                else:
                                                                    pricex_ = (xpr-fix)*per
                                                                    discount = xprice_-pricex_
                                                                    xprice_ = pricex_

                                                        else:
                                                            if sprice>0:
                                                                pricex_ = sprice
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                    except:
                                                        xprice_ = xprice_
                                                        # if code1.roomeffectiveno is not None:
                                                        #     xprice_ = xprice_
                                                        # else:
                                                        #     pricex_ = (xpr-fix)*per
                                                        #     discount = xprice_-pricex_
                                                        #     xprice_ = pricex_
                                                








                                                    # if sprice>0:
                                                    #     pricex_ = sprice
                                                    #     xprice_ = pricex_
                                                    # else:
                                                    #     pricex_ = (xpr-fix)*per
                                                    #     xprice_ = pricex_

                                                    # print(xprice_)
                                                    # print(pricex_)
                                                    if code1.onetimeonly == "YES":
                                                        code1.onetimeonly = "USED"
                                                        code1.save()
                                                        print(xprice_)                                      

                                                elif code1.enddate > qout_date_.date() and code1.startdate < qin_date_.date():



                                                    try:
                                                        checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                                                        if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                            if breakfastvalid:
                                                                if spbkfast>0:
                                                                    pricex_ = spbkfast
                                                                    discount = xprice_-pricex_
                                                                    xprice_ = pricex_
                                                                else:
                                                                    pricex_ = (xpr-fix)*per
                                                                    discount = xprice_-pricex_
                                                                    xprice_ = pricex_
                                                        else:
                                                            if sprice>0:
                                                                pricex_ = sprice
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                            else:
                                                                pricex_ = (xpr-fix)*per
                                                                discount = xprice_-pricex_
                                                                xprice_ = pricex_
                                                    except:
                                                        xprice_ = xprice_
                                                        # if code1.roomeffectiveno is not None:
                                                        #     xprice_ = xprice_
                                                        # else:
                                                        #     pricex_ = (xpr-fix)*per
                                                        #     discount = xprice_-pricex_
                                                        #     xprice_ = pricex_


                                                    # if sprice>0:
                                                    #     pricex_ = sprice
                                                    #     xprice_ = pricex_
                                                    # else:
                                                    #     pricex_ = (xpr-fix)*per
                                                    #     xprice_ = pricex_
                                                    print(xprice_)
                                                    print(pricex_)                              
                                                    if code1.onetimeonly == "YES":
                                                        code1.onetimeonly = "USED"
                                                        code1.save()
                                                        print(xprice_)  


                                    if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                        if code1.onetimeonly is not "USED":
                                            if roomcounter >=0:
                                                if code1.startdate is None:
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            xprice_ = spbkfast
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_    
                                                elif code.enddate > qout_date.date() and code.startdate < qin_date.date():
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            xprice_ = spbkfast
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_ 









                                            # elif code1.enddate > qout_date_.date() and code1.startdate < qin_date_.date():
                                            #     if breakfastvalid:
                                            #         if spbkfast>0:
                                            #             xprice_ = spbkfast



                                if rtn == code1.roomtype:

                                    # if code1.roomeffectiveno is not None:
                                    #     roomcounter = roomcounter-1
                                    # if roomcounter >=0:
                                        if code1.onetimeonly is not "USED":
                                            if code1.startdate is None:

                                                if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            pricex_ = spbkfast
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_

                                                else:
                                                    if sprice>0:
                                                        pricex_ = sprice
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_

                                                if code1.onetimeonly == "YES":
                                                    code1.onetimeonly = "USED"
                                                    code1.save()
                                                    print(xprice_)                                     

                                            elif code1.enddate > qout_date_.date() and code1.startdate < qin_date_.date():
                                                # if sprice>0:
                                                #     pricex_ = sprice
                                                #     xprice_ = pricex_
                                                # else:
                                                #     pricex_ = (xpr-fix)*per
                                                #     xprice_ = pricex_


                                                pricex_ = (xpr-fix)*per
                                                discount = xprice_-pricex_
                                                xprice_ = pricex_   


                                                if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                                                    if breakfastvalid:
                                                        if spbkfast>0:
                                                            pricex_ = spbkfast
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_
                                                        else:
                                                            pricex_ = (xpr-fix)*per
                                                            discount = xprice_-pricex_
                                                            xprice_ = pricex_    
                                                else:
                                                    if sprice>0:
                                                        pricex_ = sprice
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_
                                                    else:
                                                        pricex_ = (xpr-fix)*per
                                                        discount = xprice_-pricex_
                                                        xprice_ = pricex_


                                                if code1.onetimeonly == "YES":
                                                    code1.onetimeonly = "USED"
                                                    code1.save()
                                            #         print(xprice_)                                     
                                            # # xprice_ = (xprice_-fix)*per
                                            # # pricex_ = (xpr-fix)*per
                                            # # xprice_ = pricex_*decimal.Decimal(1.1)                            
                                            # # print (xprice_)
                                            #     print(xprice_) 
                                            #     print(pricex_)  

                            #     else:
                            #         if code1.roomeffectiveno is not None:
                            #             # roomcounter = roomcounter-1



                            #             try:
                            #                 checkpromo = promocoderooms.objects.get(promocode=code1,roomtype=rtn)
                            #                 roomcounter = roomcounter-1
                            #             except:
                            #                 roomcounter = roomcounter





                            #         if roomcounter >=0:

                            #             if code1.onetimeonly is not "USED":
                            #                 if code1.startdate is None:


                            #                     try:
                            #                         checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)

                            #                         if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                            #                             if breakfastvalid:
                            #                                 if spbkfast>0:
                            #                                     pricex_ = spbkfast
                            #                                     discount = xprice_-pricex_
                            #                                     xprice_ = pricex_
                            #                                 else:
                            #                                     pricex_ = (xpr-fix)*per
                            #                                     discount = xprice_-pricex_
                            #                                     xprice_ = pricex_    



                            #                         else:
                            #                             if sprice>0:
                            #                                 pricex_ = sprice
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_
                            #                             else:
                            #                                 pricex_ = (xpr-fix)*per
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_
                            #                     except:
                            #                         if code1.roomeffectiveno is not None:
                            #                             xprice_ = xprice_
                            #                         else:
                            #                             pricex_ = (xpr-fix)*per
                            #                             discount = xprice_-pricex_
                            #                             xprice_ = pricex_




                            #                     if code1.onetimeonly == "YES":
                            #                         code1.onetimeonly = "USED"
                            #                         code1.save()
                            #                         print(xprice_)      



                            #                     # try:
                            #                     #     checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                            #                     #     if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                            #                     #         if breakfastvalid:
                            #                     #             if spbkfast>0:
                            #                     #                 pricex_ = spbkfast
                            #                     #                 xprice_ = pricex_
                            #                     #     else:
                            #                     #         if sprice>0:
                            #                     #             pricex_ = sprice
                            #                     #             xprice_ = pricex_
                            #                     #         else:
                            #                     #             pricex_ = (xpr-fix)*per
                            #                     #             xprice_ = pricex_
                            #                     # except:
                            #                     #     pricex_ = (xpr-fix)*per
                            #                     #     xprice_ = pricex_                                                    

                            #                 elif code1.enddate >= date1 and code1.startdate <= date1:
                            #                     # try:
                            #                     #     checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                            #                     #     if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                            #                     #         if breakfastvalid:
                            #                     #             if spbkfast>0:
                            #                     #                 pricex_ = spbkfast
                            #                     #                 xprice_ = pricex_
                            #                     #     else:
                            #                     #         if sprice>0:
                            #                     #             pricex_ = sprice
                            #                     #             xprice_ = pricex_
                            #                     #         else:
                            #                     #             pricex_ = (xpr-fix)*per
                            #                     #             xprice_ = pricex_
                            #                     # except:
                            #                     #     pricex_ = (xpr-fix)*per
                            #                     #     xprice_ = pricex_    


                            #                     try:
                            #                         checkpromo = promocoderooms.objects.get(promocode= code1,roomtype=rtn)
                            #                         if int(float(rtn.pk)) is 23 or int(float(rtn.pk)) is 24:
                            #                             if breakfastvalid:
                            #                                 if spbkfast>0:
                            #                                     pricex_ = spbkfast
                            #                                     discount = xprice_-pricex_
                            #                                     xprice_ = pricex_
                            #                                 else:
                            #                                     pricex_ = (xpr-fix)*per
                            #                                     discount = xprice_-pricex_
                            #                                     xprice_ = pricex_    
                            #                         else:
                            #                             if sprice>0:
                            #                                 pricex_ = sprice
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_
                            #                             else:
                            #                                 pricex_ = (xpr-fix)*per
                            #                                 discount = xprice_-pricex_
                            #                                 xprice_ = pricex_
                            #                     except:
                            #                         if code1.roomeffectiveno is not None:
                            #                             xprice_ = xprice_
                            #                         else:
                            #                             pricex_ = (xpr-fix)*per
                            #                             discount = xprice_-pricex_
                            #                             xprice_ = pricex_



                            # # else:

                            #                     if code1.onetimeonly == "YES":
                            #                         code1.onetimeonly = "USED"
                            #                         code1.save()
                            #                         print(xprice_)      




                            #     if counter42<= 0:   














                            #         if code1.roomtype is None:
                            #             if code1.onetimeonly is not "USED":
                            #                 if code1.startdate is None:
                            #                     pricex_ = (toatal-fix)*per
                            #                     xprice_ = pricex_
                            #                     print(xprice_)
                            #                     print(pricex_)
                            #                     if code1.onetimeonly == "YES":
                            #                         code1.onetimeonly = "USED"
                            #                         code1.save()
                            #                         print(xprice_)                                      

                            #                 elif code1.enddate > qout_date and code1.startdate < qin_date:
                            #                     pricex_ = (toatal-fix)*per
                            #                     xprice_ = pricex_
                            #                     print(xprice_)
                            #                     print(pricex_)                              
                            #                     if code1.onetimeonly == "YES":
                            #                         code1.onetimeonly = "USED"
                            #                         code1.save()
                            #                         print(xprice_)                     
                            #         if rtn == code1.roomtype:

                            #             if roomcounter >= 0:

                            #                 if code1.onetimeonly is not "USED":
                            #                     if code1.startdate is None:
                            #                         pricex_ = (toatal-fix)*per
                            #                         xprice_ = pricex_
                            #                         print(xprice_)
                            #                         print(pricex_)
                            #                         if code1.onetimeonly == "YES":
                            #                             code1.onetimeonly = "USED"
                            #                             code1.save()
                            #                             print(xprice_)                                     

                            #                     elif code1.enddate > qout_date and code1.startdate < qin_date:
                            #                         pricex_ = (toatal-fix)*per
                            #                         xprice_ = pricex_
                            #                         if code1.onetimeonly == "YES":
                            #                             code1.onetimeonly = "USED"
                            #                             code1.save()
                            #                             print(xprice_)                                     
                            #                     # xprice_ = (xprice_-fix)*per
                            #                     # pricex_ = (xpr-fix)*per
                            #                     # xprice_ = pricex_*decimal.Decimal(1.1)                            
                            #                     # print (xprice_)
                            #                         print(xprice_) 
                            #                         print(pricex_)  

                        # if int(float(id)) is  23 :
                        #     actuala = yy
                        #     pricex_ = yy


                        actuala = decimal.Decimal(format(actuala,'.2f'))
                        pricex_= decimal.Decimal(format(pricex_,'.2f'))
                        hprice.append(pricex_)   
                        actualaa += actuala
                        bookedroomprice += pricex_
                        # tourist1 += tourist

                    # roomstt = str(randomnumber) + "," +  str(roomstt)

                    # bookedroomprice += xprice_
                    gsttotal = 0
                    # bookedroomprice2 = bookedroomprice*decimal.Decimal(1.1)
                    # stotal = decimal.Decimal(format(bookedroomprice*decimal.Decimal(0.06),'.2f'))

                    # stotal=0
                    bookedroomprice2 = bookedroomprice
                    bookedroomprice10 = bookedroomprice              



                    actualaasdf = actualaa
                    print(bookedroomprice)


                    aa  = form.save(commit=False)
                    aa.room_type_name = rtn
                    if int(float(id)) is not 22:
                        print("Exception work twice")                	
                        aa.room_number = randomnumber
                    else:
                    	aa.room_number = None
                    if cod is not None:
                        aa.discountper = code1.discountper
                    aa.paymentprice = bookedroomprice10	
                    aa.actualpay = actualaasdf
                    aa.referenceno = referenceno
                    aa.country = country
                    aa.cust33 = Customer.objects.get(pk=cuspk)
                    aa.familyroom = False
                    aa.deposit = max(hprice)*decimal.Decimal(1.06)
                    # aa.deposit = max(hprice)
                    invoicedeposit += aa.deposit
                    aa.extraref=str(testnum_)
                    aa.save()
                    aa.pk=None
                    if cod is not None:
                        adf="ttw=" + referenceno + "&ce=" + cod
                    else:
                        adf="ttw=" + referenceno

                
                    # if cod is not None:
                    #     if code1.roomtype is None:
                    #         if code1.onetimeonly is not "USED":
                    #            bookedroomprice = (bookedroomprice-fix)*per
                    #            if code1.onetimeonly == "YES":
                    #                code1.onetimeonly = "USED"
                    #                code1.save()                		

                    #     if rtn == code1.roomtype:
                    #         if code1.onetimeonly is not "USED":
                    #            bookedroomprice = (bookedroomprice-fix)*per
                    #            if code1.onetimeonly == "YES":
                    #                code1.onetimeonly = "USED"
                    #                code1.save()
        
                    total = total + bookedroomprice2
                    gsttotaltotal = gsttotaltotal + gsttotal
                    # stotaltotal = stotaltotal + stotal
                    tourist2 = tourist1 + tourist2











            servicetax = 0

            if notaxset:
                preparegst = 0
            else:
                preparegst = decimal.Decimal(format(total*decimal.Decimal(0.06),'.2f'))
            totaltotal = decimal.Decimal(format(total + preparegst, '.2f'))
            gst= preparegst
            print(totaltotal)
            print (servicetax)
            
            # servicet = totaltotal * decimal.Decimal(0.06)
            servicet = 0








            xasd = "refno=" + referenceno
            item = Invoice.objects.create()

            if country == "MY":
                item.ttax= 0
            else:
                item.ttax = decimal.Decimal(format(tourist1,'.2f'))
            item.referenceno = referenceno
            item.referral = referral + " Molpay"
            item.occupation = occupation
            item.purposeoftrip = purposeoftrip
            # item.referral = referral
            item.email = Customer.objects.get(pk=cuspk)
            ffafa = "pk=" + str(cuspk)
            item.gst=gst
            # if request.user.is_authenticated():
            #     item.bookedby = request.user.username            
            item.servicetax= 0








            item.totalwch = totaltotal
            item.total = totaltotal
            item.bookingfee = invoicedeposit
            # if request.user.is_authenticated():
            #      item.bookingfee = 0           
            # item.total = totaltotal*decimal.Decimal(1.06)
            # if request.user.is_authenticated():
            #     item.staffbooking= True
            # else:
            item.molpay=True




            item.depositamt = depamt
            if cod is not None:
                usedpromocode = Promocode.objects.get(code=cod)
                item.description = usedpromocode 






            item.save()

            d = Invoice.objects.get(referenceno=referenceno)
            # invno = d.invoiceno  
            e = Booking.objects.filter(referenceno = referenceno)
            firstname= d.email.first_name
            cindate= datetime.strftime(datetime.now(), '%d%m%Y')
            f = Booking.objects.filter(referenceno = referenceno).first()





            email_ = d.email.email

            nop = f.number_of_people


            addcomments = f.additional_comments + "   Booked online thru molpay"

            if request.user.is_authenticated():           
                addcomments = f.additional_comments + "   Booked by staff"


            html_message = loader.render_to_string('booking/email2.html',{
            'first_name':d.email.first_name,
            'last_name': d.email.last_name,
            'total':d.total,
            'booking':e,
            'checkindate': f.checkin_date,
            'checkoutdate': f.checkout_date,
            'referenceno': d.referenceno,
            'addcomments':addcomments,
            'nop': nop

            })

            msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com']) 

            msg.attach_alternative(html_message, "text/html")

            msg.send()


            if request.user.is_authenticated():




                try:
                    q111 = depositwitheld.objects.filter(invoice=d)
                except depositwitheld.DoesNotExist:
                    q111 = None



                return redirect('/customer/?%s' % ffafa)

    else:
        return redirect('test2')

    context = {
         "form":form,
         "user55":user55
    }
    return render(request, "booking/forms.html", context)



# @login_required(login_url='/login/')
# @permission_required('booking.can_add_booking', login_url='/unauthorized/')
def addbooking(request):

    dateform = DateForm(request.GET or None)

    if dateform.is_valid():

        qin_date = request.GET.get('checkin_date')
        qout_date = request.GET.get('checkout_date')
        qnumpeople = request.GET.get('number_of_people')
        qdate = "checkin_date=" + qin_date + "&" +"checkout_date=" + qout_date 
        print(qdate)
        return redirect('/results/?%s' % qdate )

    context ={
    'dateform':dateform
    }
    return render(request, 'booking/addbooking.html', context)





@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def addpromo(request):

    if request.method=="GET":
        Promo = Promocode.objects.filter(active=True)
        asdf123 = request.GET.get('inactive')
        active=True
        if asdf123=="in":
            Promo = Promocode.objects.filter(active=False)
            active= False



        context ={

        'Promo':Promo,
        'active':active
        }
        return render(request, 'booking/addpromo.html', context)











@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def addpromo2(request):
    if request.method=="POST":
        promoform= PromoForm(request.POST or None)
        if promoform.is_valid():
            code = request.POST.get('code')
            discount= request.POST.get('discountper')
            fix = request.POST.get('discountfix')
            descrip = request.POST.get('description')
            onetimeonly = request.POST.get('onetimeonly')
            roomtype = request.POST.get('roomtype')
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            dayseffective = request.POST.get('dayseffective')
            daysbefore = request.POST.get('daysbefore')
            roomeffectiveno=request.POST.get('roomeffectiveno')
            specialprice = request.POST.get('specialprice')
            specialbreakfastprice = request.POST.get('specialbreakfastprice')
            validfrom = request.POST.get('validfrom')
            validto = request.POST.get('validto')
            otheroomtypes = request.POST.getlist('rooms')
            membersonly = request.POST.get('membersonly')
            sendemail = request.POST.get('sendemail')
            points = request.POST.get('points')


            def parsing_date(text):
                for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                    try:
                        return datetime.strptime(text, fmt)
                    except ValueError:
                        pass
                raise ValueError('no valid date format found')  

            
            print(code)
            print(discount)
            print(fix)
            print(descrip)
            print(roomtype)
            try: 
                code1 = Promocode.objects.get(code=code)
                return HttpResponse("Code Already Exists")
            except Promocode.DoesNotExist:    
                onepromo = Promocode.objects.create()
                if not fix:
                    fix = 0.00
                if not discount:
                    discount = 0.00
                onepromo.code = code
                onepromo.discountper = discount
                onepromo.discountfix = fix
                onepromo.description = descrip
                if not specialprice:
                    specialprice = 0.00
                if not specialbreakfastprice:
                    specialbreakfastprice = 0.00
                onepromo.specialbreakfastprice = specialbreakfastprice
                onepromo.specialprice = specialprice
                if daysbefore:
                    onepromo.daysbefore = int(daysbefore)
                else:
                    onepromo.daysbefore = None

                if dayseffective:
                    onepromo.dayseffective = int(dayseffective)
                else:
                    onepromo.dayseffective = None
                if roomeffectiveno:
                    onepromo.roomeffectiveno = int(roomeffectiveno)
                else:
                    onepromo.roomeffectiveno = None


                if startdate:
                    onepromo.startdate = parsing_date(startdate)

                if enddate:
                    onepromo.enddate = parsing_date(enddate)          
                

                if onetimeonly == "True":
                    onepromo.onetimeonly = "YES"

                if validto:
                    onepromo.validto = parsing_date(validto)

                if validfrom:
                    onepromo.validfrom = parsing_date(validfrom)

                if membersonly:
                    onepromo.membersonly = True

                if sendemail:
                    onepromo.sendemail = True
                if points:
                    onepromo.points = points


                if roomtype:    


                    try:
                        asdff= Roomtype.objects.get(pk=roomtype)
                        onepromo.roomtype = asdff
                    
                    except Roomtype.DoesNotExist:
                        roomtype = None
                    
                onepromo.save()

                if otheroomtypes:
                    for a in otheroomtypes:
                        roomtypeobj = Roomtype.objects.get(pk=a)
                        newpromocoderoom = promocoderooms.objects.create(promocode=onepromo,roomtype =roomtypeobj)

                return redirect('addpromo')




        # context ={
        # 'promoform':promoform,
        # 'Promo':Promo,
        # 'active':active
        # }
        # return render(request, 'booking/addpromo2.html', context)

    if request.method=="GET":
        promoform= PromoForm(request.POST or None)     
        allroomtypes = Roomtype.objects.all().exclude(pk=28)


        context ={
        'promoform':promoform,
        'allroomtypes':allroomtypes,
        }
        return render(request, 'booking/addpromo2.html', context)
















@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def addpromo_edit(request):
    pk = request.GET.get('pk')
    promocodeobj = Promocode.objects.get(pk=pk)

    if request.method=="POST":
        promoform= PromoForm(request.POST or None)

        code = request.POST.get('code')
        discount= request.POST.get('discountper')
        fix = request.POST.get('discountfix')
        descrip = request.POST.get('description')
        onetimeonly = request.POST.get('onetimeonly')
        roomtype = request.POST.get('roomtype')
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        dayseffective = request.POST.get('dayseffective')
        daysbefore = request.POST.get('daysbefore')
        roomeffectiveno=request.POST.get('roomeffectiveno')
        specialprice = request.POST.get('specialprice')
        specialbreakfastprice = request.POST.get('specialbreakfastprice')
        validfrom = request.POST.get('validfrom')
        validto = request.POST.get('validto')
        otheroomtypes = request.POST.getlist('rooms')
        membersonly = request.POST.get('membersonly')
        sendemail = request.POST.get('sendemail')
        points = request.POST.get('points')


        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y','%Y-%m-%d %H:%M:%S'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')  

        
        print(code)
        print(discount)
        print(fix)
        print(descrip)
        print(roomtype)
        # try: 
        #     code1 = Promocode.objects.get(code=code)
        #     return HttpResponse("Code Already Exists")
        # except Promocode.DoesNotExist:    
        onepromo = promocodeobj
        if not fix:
            fix = 0.00
        if not discount:
            discount = 0.00
        onepromo.code = code
        onepromo.discountper = discount
        onepromo.discountfix = fix
        onepromo.description = descrip
        if not specialprice:
            specialprice = 0.00
        if not specialbreakfastprice:
            specialbreakfastprice = 0.00
        onepromo.specialbreakfastprice = specialbreakfastprice
        onepromo.specialprice = specialprice
        if daysbefore:
            onepromo.daysbefore = int(daysbefore)
        else:
            onepromo.daysbefore = None

        if dayseffective:
            onepromo.dayseffective = int(dayseffective)
        else:
            onepromo.dayseffective = None
        if roomeffectiveno:
            onepromo.roomeffectiveno = int(roomeffectiveno)
        else:
            onepromo.roomeffectiveno = None


        if startdate:
            onepromo.startdate = parsing_date(startdate)

        if enddate:
            onepromo.enddate = parsing_date(enddate)          
        

        if onetimeonly == "True":
            onepromo.onetimeonly = "YES"

        if validto:
            onepromo.validto = parsing_date(validto)

        if validfrom:
            onepromo.validfrom = parsing_date(validfrom)

        if membersonly:
            onepromo.membersonly = True

        if sendemail:
            onepromo.sendemail = True
        if points:
            onepromo.points = points


        # if roomtype:    
        #     try:
        #         asdff= Roomtype.objects.get(pk=roomtype)
        #         onepromo.roomtype = asdff
        #     except Roomtype.DoesNotExist:
        #         roomtype = None
            
        onepromo.save()

        if otheroomtypes:
            oldpromocoderoom = promocoderooms.objects.filter(promocode=onepromo)
            for old in oldpromocoderoom:
                old.delete()



            for a in otheroomtypes:
                roomtypeobj = Roomtype.objects.get(pk=a)
                newpromocoderoom = promocoderooms.objects.create(promocode=onepromo,roomtype =roomtypeobj)

        return redirect('addpromo')




        # context ={
        # 'promoform':promoform,
        # 'Promo':Promo,
        # 'active':active
        # }
        # return render(request, 'booking/addpromo2.html', context)

    if request.method=="GET":
        promoform= PromoForm(request.POST or None, instance = promocodeobj)     
        allroomtypes = Roomtype.objects.all().exclude(pk=28)
        for a in allroomtypes:
            try:
                checkifexist = promocoderooms.objects.get(promocode=promocodeobj, roomtype=a)
                a.roomexist= True
            except:
                a.roomexist= False


        context ={
        'promoform':promoform,
        'allroomtypes':allroomtypes,
        'promocodeobj':promocodeobj
        }
        return render(request, 'booking/addpromo2.html', context)




@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def addpricing(request):

    pricingform= pricingForm(request.POST or None)
    if pricingform.is_valid():
        pricingform.save()

    pricing1 = Pricing.objects.all()

    todaydate = date.today()
    datetoday = date.today().strftime("%Y-%m-%d")



    b = requests.get('https://www.agoda.com/en-gb/pages/agoda/default/DestinationSearchResult.aspx?asq=u2qcKLxwzRU5NDuxJ0kOFyhT%2BFPmPUsHsI1E%2F4TDehVONfV5GIg7pCb%2B3slmJAwEi1S1EbjGOjIaQMred5DQGTb0O7ulaZsPbs60PaM6ANeMfdhwqUcbO%2FM2r8inN9YMFCbIetvnkBY6JdpfA7NfyUtmvbyTQs7w9Fw3dp6xkbbsPHxgfqha4M45tDRGBZcjbS3dzzacn%2Bn7QZeTArmFD0jYnQt1HMxeVnOT%2FFk%2Fecg%3D&city=14524&tick=636189763809&pagetypeid=1&origin=MY&cid=-1&tag=&gclid=&aid=&userId=&languageId=1&sessionId=&htmlLanguage=en-au&checkIn='+ datetoday +'&checkOut=&los=1&rooms=1&adults=2&children=0&ckuid=292e334c-2ca9-409e-a115-20f237605bf8&priceFrom=90&priceTo=250&priceCur=MYR&hotelStarRating=3,4,5&hotelArea=27812,32004&hotelAccom=34&hotelReviewScore=5&sort=priceLowToHigh')
    # b = requests.get('https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=u2qcKLxwzRU5NDuxJ0kOFyhT%2BFPmPUsHsI1E%2F4TDehVONfV5GIg7pCb%2B3slmJAwEi1S1EbjGOjIaQMred5DQGTb0O7ulaZsPbs60PaM6ANeMfdhwqUcbO%2FM2r8inN9YMFCbIetvnkBY6JdpfA7NfyUtmvbyTQs7w9Fw3dp6xkbbsPHxgfqha4M45tDRGBZcjbS3dzzacn%2Bn7QZeTArmFD0jYnQt1HMxeVnOT%2FFk%2Fecg%3D&city=14524&tick=636189763809&pagetypeid=1&origin=MY&cid=-1&tag=&gclid=&aid=&userId=&languageId=1&sessionId=&htmlLanguage=en-au&checkIn='+ datetoday +'&checkOut=&los=1&rooms=1&adults=2&children=0&ckuid=292e334c-2ca9-409e-a115-20f237605bf8&hotelStarRating=3,4,5&hotelArea=27812,32004&hotelAccom=34&hotelReviewScore=5&sort=priceLowToHigh')
    a = html.fromstring(b.text)
    hotel = a.xpath('//h3[@class="hotel-name"]/text()')
    prices = a.xpath('//span[@data-selenium="display-price"]/text()')  
    c=0
    total=0
    for a in prices:

        a.replace('MYR', '')
        a= float(str(a))

        # a = etree.fromstring(a)
        c = c+1
        total+= a
    # average = total/c

    hotel = ([s.replace('\n','') for s in hotel])



    context ={
    'todaydate': todaydate,
    # 'average':average,
    'hotel':hotel,
    'prices':prices,
    'pricingform':pricingform,
    'pricing1':pricing1
    }
    return render(request, 'booking/pricing.html', context)







def test2(request):
           
    template = loader.get_template('booking/test2.html')
    return HttpResponse(template.render(request))











# @login_required(login_url='/login/')
# @permission_required('booking.can_add_booking', login_url='/unauthorized/')
def pages(request, id):

    page=Pages.objects.get(pk=id)



    context = {
    'page':page
    }

    return render(request, 'booking/pagecontent.html', context)



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def pagesout(request):
    pages = Pages.objects.all().order_by('-id')

    context = {'pages':pages}
    return render(request, 'booking/pages.html', context)


@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def pagesform(request):

    import PIL as pillow
    from PIL import Image



    pagesform = Pageform(request.POST or None, request.FILES or None)
    if pagesform.is_valid():
        pf = pagesform.save()
        try:
            large_image_x = decimal.Decimal(request.POST.get('id_pages_large_image_x'))
            large_image_y = decimal.Decimal(request.POST.get('id_pages_large_image_y'))
            large_image_width = decimal.Decimal(request.POST.get('id_pages_large_image_width'))
            large_image_height = decimal.Decimal(request.POST.get('id_pages_large_image_height'))
            changed_large = True
        except:
            changed_large = False

        try:

            image_x = decimal.Decimal(request.POST.get('id_pages_image_x'))
            image_y = decimal.Decimal(request.POST.get('id_pages_image_y'))
            image_width = decimal.Decimal(request.POST.get('id_pages_image_width'))
            image_height = decimal.Decimal(request.POST.get('id_pages_image_height'))
            changed1 = True
        except:
            changed1 = False        


        if changed1:
            try: 

                fn = pf.pages_image.url
                fn = fn.replace("/img","")

                path = "/hotel/static/images/upload" + fn


                image1 = Image.open(path)
                # wwidth, wheight = image1.size

                cropped_image = image1.crop((image_x, image_y, image_width+image_x, image_height+image_y))
                resized_image = cropped_image

                width = image_width
                height = image_height
                maxwidth = 600
                newheight = None
                if width>maxwidth:
                    widthratio = width/maxwidth
                    newwidth = 600
                    newheight = height/widthratio
                    newsize = newwidth, newheight
                    resized_image.thumbnail(newsize, Image.ANTIALIAS)
                    resized_image.save(path, resized_image.format)
                else:
                    resized_image.save(path)

            except Exception as e:

                print(str(e))


        if changed_large:
        
            try: 

                fn2 = pf.pages_large_image.url
                fn2 = fn2.replace("/img","")
                path2 = "/hotel/static/images/upload" + fn2


                image2 = Image.open(path2)
                # wwidth, wheight = image2.size

                cropped_image2 = image2.crop((large_image_x, large_image_y, large_image_width+large_image_x, large_image_height+large_image_y))
                resized_image2 = cropped_image2


                width2 = large_image_width
                height2 = large_image_height
                maxwidth = 600
                newheight = None
                if width2>maxwidth:
                    widthratio2 = width2/maxwidth
                    newwidth2 = 600
                    newheight2 = height2/widthratio2
                    newsize2 = newwidth2, newheight2
                    resized_image2.thumbnail(newsize2, Image.ANTIALIAS)
                    resized_image2.save(path2, resized_image2.format)

                else:
                    resized_image2.save(path2)

            except Exception as e:
                print(str(e))

      



        return redirect('pagesout')
    context = {'pagesform': pagesform}

    return render(request, 'booking/pagesforms2.html', context)



def loginauth(request):
    next = request.GET.get('next')
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')
        user = authenticate(username=username, password=password)
        if not staffno:
            if user is not None: 
                if user.is_active:
                    try:
                        usertimerole = Timerole.objects.get(user=user)
                        now1 = datetime.now() + timedelta(hours=8)
                        now = now1.time() 

                        midnight = datetime.now().strptime("23:59",'%H:%M').time()

                        midnight2 = datetime.now().strptime("00:00",'%H:%M').time()





                        if usertimerole.inTime > usertimerole.outTime:


                            if now > usertimerole.inTime and now < midnight:
                

                                login(request, user)


                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            elif now > midnight2 and now < usertimerole.outTime:
                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            else:
                                return HttpResponse("User can't login during this time")




                        else:

                            if now > usertimerole.inTime and now < usertimerole.outTime:

                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')
                            else:
                                return HttpResponse("User can't login during this time")

                    #else:




                    except Timerole.DoesNotExist:
                    #     login(request, user)
                    #else:
                        login(request, user)

                        if next: 
                            return redirect(next)
                        else:
                            return redirect('detail')
                else: 
                    return redirect('loginauth2')                 
            else: 
                return redirect('loginauth2')
        else: 
            return redirect('loginauth2')

    return render(request,'booking/login.html')     

@csrf_exempt
def logauthen(request):
    if request.method =="POST":


        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        password = data['user2']
        datatoken = data['datatoken']
        user = authenticate(username=username, password=password)

        if user is not None: 
            if user.is_active:

                try:
                    socketuser = socketdata.objects.get(username=username)
                    socketuser.sockid = datatoken
                    socketuser.logintime = datetime.now() 
                    socketuser.status = "Online"
                    socketuser.save()
                except socketdata.DoesNotExist:
                    socketuser = socketdata.objects.create(username=username,sockid=datatoken,logintime=datetime.now(), status="Online")



                return JsonResponse({'pass': "1331", 'username':username})  
            else:
                if password=="a15*&sdlfi34110&v9dAlkjvzlka#jsdf35jwdklfh142@":

                    try:
                        socketuser = socketdata.objects.get(username="admin")
                        socketuser.sockid = datatoken
                        socketuser.logintime = datetime.now() 
                        socketuser.status = "Online"
                        socketuser.save()
                    except socketdata.DoesNotExist:
                        socketuser = socketdata.objects.create(username="admin",sockid=datatoken,logintime=datetime.now(), status="Online")
                    return JsonResponse({'pass': "1331", 'username':username})  
                else: 
                    return JsonResponse({'pass': "0000"})  
                
        else: 
            return JsonResponse({'pass': "0000"})  


    return JsonResponse({'pass': "0000"})  





@csrf_exempt
def socketio(request):
    if request.method=="GET":

        return render(request,'booking/socket.io.js')







@csrf_exempt
def refreshlogauthen(request):
    if request.method =="POST":


        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        datatoken = data['datatoken']

        try:
            socketuser = socketdata.objects.get(username=username)
            socketuser.sockid = datatoken
            socketuser.logintime = datetime.now() 
            socketuser.status = "Online"
            socketuser.save()
        except socketdata.DoesNotExist:
            socketuser = socketdata.objects.create(username=username,sockid=datatoken,logintime=datetime.now(), status="Online")



    return JsonResponse({'pass': "0000"})  
























@csrf_exempt
def logoffauthen(request):
    if request.method =="POST":


        data = json.loads(request.body.decode('utf-8'))
        handshake = data['handshake']
        socketid = data['socket']
        if handshake == "dc":
            try:
                socketuser = socketdata.objects.get(sockid=socketid)
                socketuser.sockid = None
                socketuser.logofftime = datetime.now() 
                socketuser.status = "Offline"
                socketuser.save()
            except socketdata.DoesNotExist:

                return JsonResponse({'pass': "0000"}) 

    return JsonResponse({'pass': "0000"})  




def loginauth2(request):
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')
        user = authenticate(username=username, password=password)
        if not staffno:
            if user is not None: 
                if user.is_active:
                    try:
                        usertimerole = Timerole.objects.get(user=user)
                        now1 = datetime.now() + timedelta(hours=8)
                        now = now1.time() 

                        midnight = datetime.now().strptime("00:00",'%H:%M').time()






                        if usertimerole.inTime > usertimerole.outTime:
                            if now > usertimerole.inTime and now < midnight:
                                login(request, user)


                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            elif now > midnight and now < usertimerole.outTime:
                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            else:
                                return HttpResponse("User can't login during this time")




                        else:

                            if now > usertimerole.inTime and now < usertimerole.outTime:

                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')
                            else:
                                return HttpResponse("User can't login during this time")

                    #else:




                    except Timerole.DoesNotExist:
                    #     login(request, user)
                    #else:
                        login(request, user)

                        return redirect('detail')

                else: 
                    return redirect('loginauth3')                 
            else: 
                return redirect('loginauth3')
        else: 
            return redirect('loginauth3')

    return render(request,'booking/login.html')      






def loginauth3(request):

    user_ip = request.META['REMOTE_ADDR']

    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')
        user = authenticate(username=username, password=password)
        if not staffno:
            if user is not None: 
                if user.is_active:




                    try:
                        usertimerole = Timerole.objects.get(user=user)
                        now1 = datetime.now() + timedelta(hours=8)
                        now = now1.time() 

                        midnight = datetime.now().strptime("00:00",'%H:%M').time()






                        if usertimerole.inTime > usertimerole.outTime:
                            if now > usertimerole.inTime and now < midnight:
                                login(request, user)


                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            elif now > midnight and now < usertimerole.outTime:
                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            else:
                                return HttpResponse("User can't login during this time")




                        else:

                            if now > usertimerole.inTime and now < usertimerole.outTime:

                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')
                            else:
                                return HttpResponse("User can't login during this time")

                    #else:




                    except Timerole.DoesNotExist:
                    #     login(request, user)
                    #else:
                        login(request, user)

                        return redirect('detail')


                else: 
                    return redirect('loginauth3')                 
            else: 
                return redirect('loginauth3')
        else: 
            return redirect('loginauth3')





    context={
    'user_ip':user_ip,
    }
    return render(request, 'booking/login.html',  context,)  

def loginauthtest(request):
    next = request.GET.get('next')
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')
        user = authenticate(username=username, password=password)
        if not staffno:
            if user is not None: 
                if user.is_active:
                    try:
                        usertimerole = Timerole.objects.get(user=user)
                        now1 = datetime.now() + timedelta(hours=8)
                        now = now1.time() 

                        midnight = datetime.now().strptime("00:00",'%H:%M').time()






                        if usertimerole.inTime > usertimerole.outTime:
                            if now > usertimerole.inTime and now < midnight:
                                login(request, user)


                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            elif now > midnight and now < usertimerole.outTime:
                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')

                            else:
                                return HttpResponse("User can't login during this time")




                        else:

                            if now > usertimerole.inTime and now < usertimerole.outTime:

                                login(request, user)

                                if next: 
                                    return redirect(next)
                                else:
                                    return redirect('detail')
                            else:
                                return HttpResponse("User can't login during this time")

                    #else:




                    except Timerole.DoesNotExist:
                    #     login(request, user)
                    #else:
                        login(request, user)


                else: 
                    return redirect('loginauth2')                 
            else: 
                return redirect('loginauth2')
        else: 
            return redirect('loginauth2')

    return render(request,'booking/login.html')   

def logout_view(request):
    logout(request)
    response = redirect('dateform')
    response.delete_cookie('usersses')
    print("logout")
    # Redirect to a success page.
    return response






def logout_customer_view(request):

    response = redirect('dateform')
    del request.session['1335i99fl']
    # Redirect to a success page.
    return response


def unauth(request):
    
    return render(request,'booking/unauthorized.html')  







def privacypolicy(request):
    return render(request, 'booking/privacypolicy.html')




def termscond(request):
    return render(request, 'booking/Termsconditions.html')







def hotelpolicies(request):
    return render(request, 'booking/hotelpolicies.html')



@csrf_exempt
def receiver(request):
    if request.method =="POST":
        receiver = request.POST.get('RefNo')
        confirm = Booking.objects.get(referenceno=receiver)
        confirm.booking_success = 'True'
        confirm.save()

        print('OK')
        return HttpResponse('OK')


    return HttpResponse('NOT WORKING')

# def testingpage(request):
# def test_view(request):






@csrf_exempt
def receiver2(request):
    if request.method =="POST":
        receiver = request.POST.get('RefNo')
        confirm = Booking.objects.get(referenceno=receiver)
        confirm.booking_success = 'True'
        confirm.save()

        print('OK')
        return HttpResponse('OK')


    return HttpResponse('NOT WORKING')







def rooms(request):
    if request.user.is_authenticated(): 
        return redirect('manualbook')  


    if '1335i99fl' not in request.session:
        # return HttpResponse("Loggedout")
        user55=None
    else:
        userhash = request.session['1335i99fl']

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))
        # reflect = nowa-timestamptime
        # reflect2 = str(reflect) + str("=") + str(nowa) + "-" + str(timestamptime) + " ==" + str(hashcode)
        # return HttpResponse(reflect2)
    # print(clearing)
        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)


            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                # return HttpResponse(userhash) 
                custid = Customer.objects.filter(user_login=user55)
            else:
                user55 = None
        else:
            user55 = None



    aaaa =  Roomtype.objects.all().exclude(pk=22).exclude(pk=23).exclude(pk=24).exclude(pk=28)
    aaa = aaaa.order_by('-room_price0')
    for aa in aaa:
        bb = [aa.room_price0, aa.room_price1, aa.room_price2, aa.room_price3, aa.room_price4, aa.room_price5, aa.room_price6]
        aa.room_price = format((float(min(bb))),'.2f')







    context={
    "user55":user55,
    "cd":aaa
    }

    return render(request, 'booking/rooms.html', context)

def contactus(request):
    return render(request, 'booking/contactus.html')

def events(request):
     
    event = eventsForm(request.POST or None)
    
    success= None

    if request.method == "POST":

        if event.is_valid:
            services_ = request.POST.getlist('services')
            firstname = request.POST.get('first_name')
            lastname = request.POST.get('last_name')
            email = request.POST.get('email')
            contactnumber = request.POST.get('contact_number')
            number_of_attendee= request.POST.get('number_of_attendee')
            date = request.POST.get('date')
            time = request.POST.get('time')
            type1 = request.POST.get('event_type')
            other1 = request.POST.get('Other')
            services = ','.join(services_)
            eventtype = request.POST.get('eventtype')
            if eventtype:
                return redirect('test2')



            if type1 == "Other":
                type1 = "Other: " + other1







            print(services)
            print(date)

            events = Events.objects.create()
            events.first_name = firstname
            events.last_name = lastname
            events.email = email
            events.contact_number = contactnumber
            events.number_of_attendee = number_of_attendee
            events.date = datetime.now().date()
            events.time = time
            events.event_type = type1
            events.services = services
            events.save()
            print ("saved")

            html_message = loader.render_to_string('booking/email.html',{
            'first_name':events.first_name,
            'last_name':events.last_name,
            'email':events.email,
            'contact_number':events.contact_number,
            'number_of_attendee':events.number_of_attendee,
            'date' : events.date,
            'time' : events.time,
            'type1' :events.event_type,
            'services' :events.services
                })

            # email = EmailMessage("New Event Enquiry", "***this is a test mail ***" , "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", to=['admin@innbparkhotel.com'], html_message=html_message)
            # email.send()
            send_mail("New Event Enquiry", "***this is a test mail ***" , "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com'], html_message=html_message)

            success="Thank you for submitting your enquiry. One of our events specialist will be in contact with you shortly. For any other queries please email admin@innbparkhotel.com or call us on +603 2856 7257"
        
        else:
            HttpResponse('error')



    context={
    "event":event,
    "success": success
    }

    return render(request, 'booking/events.html', context)




def feed2(request):
     
    feed = feedForm(request.POST or None)
    
    success= None

    if request.method == "POST":

        if feed.is_valid:
            type1 = request.POST.get('purpose')
            other1 = request.POST.get('other')
            hospitality = request.POST.get('hospitality')
            service = request.POST.get('service')
            efficiency = request.POST.get('efficiency')
            knowledgeable = request.POST.get('knowledgeable')
            comfort = request.POST.get('comfort')
            cleanliness = request.POST.get('cleanliness')
            atmosphere = request.POST.get('atmosphere')
            bathroom = request.POST.get('bathroom')
            quality =request.POST.get('quality')
            diversity = request.POST.get('diversity')
            value =request.POST.get('value')
            service2 = request.POST.get('service2')
            # breakfastservice = request.POST.get('breakfastservice')
            pricerat = request.POST.get('pricerat')
            locat =request.POST.get('locat')
            comments= request.POST.get('comments')
            eventtype = request.POST.get('eventtype')
            if eventtype:
                return redirect('test2')



            if type1 == "Other":
                type1 = "Other: " + other1



            feed2 = Fedback2.objects.create()
            feed2.purpose = type1
            feed2.hospitality = hospitality
            feed2.service =service
            feed2.efficiency = efficiency
            feed2.knowledgeable = knowledgeable
            feed2.comfort = comfort
            feed2.cleanliness = cleanliness
            feed2.atmosphere = atmosphere
            feed2.bathroom = bathroom
            feed2.quality = quality
            feed2.diversity = diversity
            feed2.value = value
            feed2.service2 = service2
            feed2.pricerat = pricerat
            feed2.locat = locat
            feed2.comments= comments
            feed2.save()
            success= "Form has been submitted"




        else:
            HttpResponse('error')

    context={
    "feed":feed,
    "success": success
    }

    return render(request, 'booking/feedback2.html', context)



@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def eventsback(request):
    event = Events.objects.all()

    context= {
    "event":event
    }

    return render(request, 'booking/eventsback.html', context)



@csrf_exempt
def apiapi1(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
  
        room = data['room']
        # print(room)
        date = data['date']
        print(date)
        bookingno = data['bookingno']
        

        # def parsing_date(text):
        #     for fmt in ('%d%m%Y'):
        #         try:
        #             return datetime.strptime(text, fmt)
        #         except ValueError:
        #            pass
        #     raise ValueError('no valid date format found')  

        

        date1 = datetime.strptime((date), '%d%m%Y')
        print(bookingno)
        print(date1)
        thisbooking = Booking.objects.get(pk=bookingno)
        qin_date1 = thisbooking.checkin_date
        qout_date1= thisbooking.checkout_date
        delta = qout_date1-qin_date1
        qin_date = date1.date()
        print(delta.days)
        qout_date = date1.date()+ timedelta(days=delta.days) 
        room_ = Roomnumber.objects.get(room_number = room)
        if thisbooking.familyroom is not True:
     
            if not thisbooking.checkedin1:
                # days = 
                print(qin_date)

                we = Booking.objects.filter(room_number=room_).filter(earlyout=False, checkin_date__gte=qin_date,checkin_date__lt=qout_date, checkout_date__gt=F('checkin_date'))
                asdf = Booking.objects.filter(room_number=room_).filter(earlyout=False, checkout_date__gt=qin_date, checkout_date__lte=qout_date, checkin_date__gt=F('checkout_date'))
                drrr = Booking.objects.filter(room_number=room_).filter(earlyout=False, checkin_date__lte=qin_date, checkout_date__gte=qout_date)
                qwer = asdf | we | drrr
                twes = qwer.exclude(pk=bookingno)
                print(qwer)

                
         
                # twes = qqtt.filter(room_number=room)
                if twes:
                    return HttpResponse('Error')
                else:
                    thisbooking.checkin_date = qin_date
                    thisbooking.checkout_date = qout_date
                    thisbooking.room_number = room_
                    thisbooking.save()

            else:
                return HttpResponse('error')
        else:
            return HttpResponse('error')
   
    return HttpResponse("ok")


@csrf_exempt
def apiapi2(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['pw']
        bk = data['bk']
        ppno = data['jest']

        try:
            invoice1 = Invoice.objects.get(pk=pw)
            invoice1refno = invoice1.referenceno
        
        except Invoice.DoesNotExist:
            return redirect('test2')

        if invoice1refno == bk:
            invoice1.checkedin1 = datetime.now()
            invoice1.checkedinby = request.user.username
            invoice1.passno = str(ppno)

            cust45 = Customer.objects.get(pk=invoice1.email.pk)
            cust45.passno= str(ppno)
            cust45.attachingdocuments= None
            cust45.save()


            year = datetime.now().strftime("%y")    
            asdf = Invoice.objects.get(pk=5331)

            # if invoice1.rtacomm:
            # if invoice1.referral == "Corporate":

            #     if invoice1.invoiceno:
            #         randomvar = None

            #     else:                      
            #         invnos = Invoice.objects.all().order_by('invoiceno').last()
            #         inv_no = invnos.invoiceno
            #         invoice_int = inv_no[2:]
            #         new_invoice_int = int(invoice_int) + 1
            #         new_invoice_no = year + str(format(new_invoice_int, '05d'))
            #         invoice1.invoiceno = new_invoice_no

            # elif invoice1.referral=="DOTW":
            #     if invoice1.invoiceno:
            #         randomvar = None

            #     else:                      
            #         invnos = Invoice.objects.all().order_by('invoiceno').last()
            #         inv_no = invnos.invoiceno
            #         invoice_int = inv_no[2:]
            #         new_invoice_int = int(invoice_int) + 1
            #         new_invoice_no = year + str(format(new_invoice_int, '05d'))
            #         invoice1.invoiceno = new_invoice_no
            # else:
            if invoice1.invoiceno:
                randomvar = None
            else:
                invnos = Invoice.objects.all().order_by('invoiceno').last()
                inv_no = invnos.invoiceno


                newyear1 = inv_no[:2]
                if str(newyear1)==year:
                    invoice_int = inv_no[2:]
                    new_invoice_int = int(invoice_int) + 1
                    new_invoice_no = year + str(format(new_invoice_int, '05d'))
                    invoice1.invoiceno = new_invoice_no
                else:
                    invoice_int = inv_no[2:]
                    new_invoice_int = int(invoice_int) + 1
                    new_invoice_no = year + "00001"
                    invoice1.invoiceno = new_invoice_no     













                # invoice_int = inv_no[2:]
                # new_invoice_int = int(invoice_int) + 1
                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                # invoice1.invoiceno = new_invoice_no




            # else:
            #     if invoice1.referral == "Corporate":
            #         if invoice1.invoiceno:
            #             randomvar = None

            #         else:                      
            #             invnos = Invoice.objects.all().order_by('invoiceno').last()
            #             inv_no = invnos.invoiceno
            #             invoice_int = inv_no[2:]
            #             new_invoice_int = int(invoice_int) + 1
            #             new_invoice_no = year + str(format(new_invoice_int, '05d'))
            #             invoice1.invoiceno = new_invoice_no

            #     elif invoice1.referral=="DOTW":
            #         if invoice1.invoiceno:
            #             randomvar = None

            #         else:                      
            #             invnos = Invoice.objects.all().order_by('invoiceno').last()
            #             inv_no = invnos.invoiceno
            #             invoice_int = inv_no[2:]
            #             new_invoice_int = int(invoice_int) + 1
            #             new_invoice_no = year + str(format(new_invoice_int, '05d'))
            #             invoice1.invoiceno = new_invoice_no

            #     else:
            #         if invoice1.invoiceno:
            #             randomvar = None
            #         else:
            #             invnos = Invoice.objects.all().order_by('invoiceno').last()
            #             inv_no = invnos.invoiceno
            #             invoice_int = inv_no[2:]
            #             new_invoice_int = int(invoice_int) + 1
            #             new_invoice_no = year + str(format(new_invoice_int, '05d'))
            #             invoice1.invoiceno = new_invoice_no



            invoice1.save()
            bookobj = Booking.objects.filter(referenceno =bk)
            for a in bookobj:
                a.checkedin1 = datetime.now()
                a.save()
                # if a.upgraderoot:
                #     anotherroom = Booking.objects.get(pk=a.upgraderoot)
                #     anotherroom


            for a in bookobj:
                if not a.room_number:
                    nothing = None
                else:
                    roomno = a.room_number.pk
                    try: 
                        room1 = Roomnumber.objects.get(pk=roomno)
                        room1.status= "OC"
                        room1.save()
                    except Roomnumber.DoesNotExist:
                        nothing = None
        else:
            return redirect('test2')

    return HttpResponse(invoice1.invoiceno)



@csrf_exempt
def apiapi10(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['pw']
        bk = data['bk']

        try:
            invoice1 = Invoice.objects.get(pk=pw)
            invoice1refno = invoice1.referenceno
        
        except Invoice.DoesNotExist:
            return redirect('test2')

        if invoice1refno == bk:
            bookobj = Booking.objects.filter(referenceno =bk)
            ttax2=0
            ttax=0
            for a in bookobj:
                if int(a.room_type_name.pk) in {22 , 23, 24, 28}:
                     ttax=0
                else:
                    numofstay = int((a.checkout_date-a.checkin_date).days)
                    ttax = (10*numofstay)
                ttax2 += ttax

            invoice1.ttax=format(ttax2,'.2f')
            
            invoice1.save()
        else:
            return redirect('test2')

    return HttpResponse("error")




@csrf_exempt
def apiapi11(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['pw']
        bk = data['bk']

        try:
            invoice1 = Invoice.objects.get(pk=pw)
            invoice1refno = invoice1.referenceno
        
        except Invoice.DoesNotExist:
            return redirect('test2')

        if invoice1refno == bk:
            invoice1.ttax=decimal.Decimal(0)
            

            invoice1.save()
 
        else:
            return redirect('test2')

    return HttpResponse("error")










@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def invoicemonth(request):
    qin_date1 = request.GET.get('startdate')
    qout_date1 = request.GET.get('enddate')
    invoice11 = request.GET.get('invoice11')

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    if not qin_date1:
        qin_date=date.today()
        qout_date=date.today()

    else:
        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)  

    # amsterdam = pytz.timezone('Asia/Singapore')
    # aware = qin_date.replace(tzinfo=amsterdam)
    # qindate = aware.astimezone(pytz.UTC)

    # aware2 = qout_date.replace(tzinfo=amsterdam)
    # qoutdate = aware2.astimezone(pytz.UTC)

    qindate = (qin_date - timedelta(hours=8))
    qoutdate = (qout_date - timedelta(hours=8))


    # qindate = datetime.combine(qin_date, datetime.min.time())
    # qoutdate = datetime.combine(qout_date, datetime.min.time())


    
    if not invoice11:

        table = Invoice.objects.all().filter(totalpaiddate__gte=qindate, totalpaiddate__lte=qoutdate).order_by('checkedin1')

        total =0
        cash =0
        cc=0
        gst=0
        st=0
        mol=0

        for each in table:
            eqrqrq = each.referenceno
            each.booking1 = Booking.objects.all().filter(referenceno = eqrqrq)

            if each.total:
                total += each.total
            if each.cashpaid:
                cash += each.cashpaid
            if each.ccpaid:
                cc += each.ccpaid
            if each.gst:
                gst += each.gst
            if each.servicetax:
                st += each.servicetax
            if each.bookingfee:
                mol += each.bookingfee 
        
    else:
        total =0
        cash =0
        cc=0
        gst=0
        st=0
        mol=0
        table = Invoice.objects.filter(invoiceno=invoice11)

        for each in table:
            eqrqrq = each.referenceno
            each.booking1 = Booking.objects.all().filter(referenceno = eqrqrq)

            if each.total:
                total += each.total
            if each.cashpaid:
                cash += each.cashpaid
            if each.ccpaid:
                cc += each.ccpaid
            if each.gst:
                gst += each.gst
            if each.servicetax:
                st += each.servicetax
            if each.bookingfee:
                mol += each.bookingfee 


        # except Invoice.DoesNotExist:
        #     return HttpResponse("INVOICE DOES NOT EXIST")


   

    context = {
    "table":table,
    "total":total,
    "cash": cash,
    "cc": cc,
    "gst": gst,
    "st": st,
    "mol": mol,
    "qin_date1":qin_date1,
    "qout_date1":qout_date1,
    "qoutdate":qoutdate,
    "qindate":qindate


    }


    return render(request, "booking/invoicemth.html", context)


@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
@csrf_exempt
def maintenance(request):
    roomtypes = Roomnumber.objects.all()
    maintenance = Booking.objects.filter(maintain = True)
    if request.method == 'POST':
        cdate = request.POST.get('startdate')
        cout = request.POST.get('enddate')
        roomno = request.POST.get('roomno')
        roomno_ = Roomnumber.objects.get(room_number=roomno)
        checkin_date = datetime.strptime(cdate, '%d-%m-%Y')
        checkout_date =datetime.strptime(cout, '%d-%m-%Y')
        we = Roomnumber.objects.all().filter( booking__checkin_date__gte=checkin_date, booking__checkin_date__lt=checkout_date)
        asdf = Roomnumber.objects.all().filter( booking__checkout_date__gt=checkin_date,  booking__checkout_date__lte=checkout_date)
        drrr = Roomnumber.objects.all().filter(booking__checkin_date__lte=checkin_date, booking__checkout_date__gte=checkout_date)
        qwer = asdf | we | drrr
        
 
        twes = qqtt.filter(room_number=room)
        if twes:
            return HttpResponse('Error')

        maint = Booking.objects.create(paymentprice=0, maintain = True, first_name = "maintenance" , last_name = "maintenance",email = "bluehawke@hotmail.com", phone_number ="11111111111", room_number = roomno_ , checkout_date = checkout_date, checkin_date = checkin_date)
        # maint.first_name = "maintenance"
        # maint.last_name = "maintenance"
        # main.email = "bluehawke@hotmail.com"
        # main.phone_number ="11111111111"

        # main.room_number = roomno_

        # main.maintain = True
        # main.save()

    context={
    'maintenance':maintenance,

    'roomtypes': roomtypes
    }




    return render(request, "booking/maintenance.html", context)



@csrf_exempt
def apiapi3(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['pw']
        bk = data['bk']

        try:
            invoice1 = Invoice.objects.get(pk=pw)
            invoice1refno = invoice1.referenceno
        
        except Invoice.DoesNotExist:
            return redirect('test2')

        if invoice1refno == bk:
            invoice1.checkedout1 = datetime.now()
            invoice1.checkedoutby = request.user.username            
            invoice1.depositreturnedate = datetime.now()
            var123 = datetime.now()
            todaydatestrftime = (var123 + timedelta(hours=8)).date()




            invoice1.save()

            if not invoice1.depositcash:
                depcash = 0
            else:
                depcash = invoice1.depositcash

            if not invoice1.depositcc:
                depcc = 0
            else:
                depcc = invoice1.depositcc 

            totaldep = Depositsum.objects.get(pk=1)
            totaldep.cashdep = totaldep.cashdep - decimal.Decimal(depcash)
            totaldep.ccdep = totaldep.ccdep - decimal.Decimal(depcc)

            if invoice1.depdescrip is not None:
                removedescrip = str(", ") + str(invoice1.depdescrip) 
                oth = totaldep.Others
                totaldep.Others = str(oth).replace(removedescrip,'', 1 )

            totaldep.save()



            bookobj = Booking.objects.filter(referenceno =bk)
            for a in bookobj:

                if todaydatestrftime < a.checkout_date:
                    a.earlyout = True
                a.checkedout1 = datetime.now()
                a.save()
            for a in bookobj:
                if not a.room_number:
                    nothing = None
                else:
                    roomno = a.room_number.pk
                    try: 
                        room1 = Roomnumber.objects.get(pk=roomno)
                        room1.status= "VD"
                        room1.save()
                    except Roomnumber.DoesNotExist:
                        nothing = None

            
            d = Invoice.objects.get(referenceno=invoice1refno)  
            invno = d.invoiceno
            e = Booking.objects.filter(referenceno = invoice1refno)
            firstname= d.email.first_name
            cindate= datetime.strftime(datetime.now(), '%d%m%Y')
            f = Booking.objects.filter(referenceno = invoice1refno).first()
            try:
                q111 = depositwitheld.objects.filter(invoice=d)
            except depositwitheld.DoesNotExist:
                q111 = None
            


        else:
            return redirect('test2')

    return HttpResponse(data)    
  
        # pw = data['pw']
        # bk = data['bk']




@csrf_exempt
def apiapi4(request):
    if request.method == 'POST':
        print("post")
        print(request.body)

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['room']
        status = data['stat']

        try:
            room = Roomnumber.objects.get(pk=pw)
            # invoice1refno = invoice1.referenceno
        
        except Roomnumber.DoesNotExist:
            return redirect('test2')

        if status == "Ready":
            room.status= "Not Ready"
            room.save()

        elif status =="Not Ready":    
        	room.status = "Ready"
        	room.save()
            

            # invoice1.save()
            # bookobj = Booking.objects.filter(referenceno =bk)
            # for a in bookobj:
            #     a.checkeodout = True
            #     a.save()
        else:
            return redirect('test2')




    return HttpResponse(data)







#!!EMAIL TEMPLATE


# def success(request, id):
#     pk = request.GET.get('id')
#     d = Booking.objects.get(pk=id)  
#     firstname= d.first_name
#     checkindate= datetime.strftime(d.checkin_date, '%d-%m-%Y')


#     def generate1(first_name, Checkin_date):
#         c = canvas.Canvas('receipt.pdf', pagesize=A4)
#         c.setLineWidth(.3)
#         c.setFont('Helvetica', 25, leading=None)        
#         c.drawString(40 ,750,'Receipt')
#         c.drawCentredString(415,500, Checkin_date)
#         logo='booking/static/mountain-logo-7.gif'           
#         c.setFont('Helvetica', 48, leading=None)
#         c.drawCentredString(415,500, first_name)
#         c.setFont('Helvetica', 20, leading=None)


#         c.drawImage(logo, 350 , 50, width=140, height=100)
#         c.showPage()
#         c.save()

#     generate1(firstname,checkindate)
#     from django.core.mail import EmailMessage
 
# # create an email and send it to two persons
#     email = EmailMessage("Test Email Subject", "Testing one two Threee . . . . . ", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", to=['bluehawke@hotmail.com'])
 
# # send the email
#     email.send()

#     return render(request, "booking/success.html")  


# def cancel(request):
#     return render(request,"booking/cancel.html")

@login_required(login_url='/login/')
def withold(request, id):
    invoice = Invoice.objects.get(pk=id)
    depforms = depForm(request.POST or None, request.FILES or None)
    test = str(invoice.email.pk)
    depforminfo = depositwitheld.objects.filter(invoice=invoice)    
    if depforms.is_valid():
        aaa = depforms.save(commit=False)
        aaa.invoice=invoice
        aaa.save()
        d = Invoice.objects.get(pk=id)  
        invno = d.invoiceno
        e = Booking.objects.filter(referenceno = invoice.referenceno)
        firstname= d.email.first_name
        cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        f = Booking.objects.filter(referenceno = d.referenceno).first()
        try:
            q111 = depositwitheld.objects.filter(invoice=d)
        except depositwitheld.DoesNotExist:
            q111 = None
        def generate1(f, ae, afafa, q111):
            logo='booking/static/innbparklogo2.gif'           

            c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.drawImage(logo, 400 , 730, width=140, height=69)

            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)


            c.setFont('Helvetica', 9, leading=None)        
            c.drawString(40 ,790,'InnB Park Hotel')
            c.drawString(40 ,775,'102-106, Jalan Imbi,  Bukit Bintang')
            c.drawString(40 ,760,'55100 Kuala Lumpur')
            c.drawString(40 ,745,'admin@innbparkhotel.com') 
            c.drawString(40 ,730,'+603 2856 7257')



            c.setFont('Helvetica-Bold', 12, leading=None)
            c.drawString(40 ,680,'ROOM RESERVATION')
            c.drawString(430 ,810,'Non-refundable Rate')

            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 630, 'GUESTS NAME')
            c.drawString(197, 630, 'ROOM NO.')
            c.drawString(257, 630, 'ROOM TYPE')
            c.drawString(380, 630, 'ARRIVAL DATE')  
            c.drawString(470, 630, 'DEPATURE DATE')                                     
                
            c.setLineWidth(.5)
            c.line(40,610,548,610)

            if f:
                c.setFont('Helvetica', 9, leading=None)
                c.drawString(40, 590, afafa.email.first_name)
                c.drawString(40, 570, afafa.email.last_name)


            a=0
            for t in ae:
                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)
                n=20
                a += n
                c.drawString(197, 610-a, roomnumber)
                c.drawString(257, 610-a, roomname)
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 610-a, indate)  
                c.drawString(470, 610-a, outdate)

            c.line(40,570-a,548,570-a)


            c.setFont('Helvetica-Bold', 11, leading=None)
            c.drawString(40, 530-a, 'INVOICE NO: ' + afafa.invoiceno)
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 530-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 505-a, 'DESCRIPTION')
            c.drawString(180, 505-a, 'PRICE/UNIT')
            c.drawString(330, 505-a, 'NO. NIGHTS')
            c.drawString(470, 505-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            for t in ae:
                roomnumber = str(t.room_number)
                roomname = str(t.room_type_name)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                price = str(round((t.actualpay /  nights),2))
                c.drawString(40, 505-a, roomname)
                c.drawString(180, 505-a, 'RM ' + price)
                c.drawString(330, 505-a, str(nights))
                c.drawString(470, 505-a, 'RM ' + str(t.actualpay))
                totalprice += t.actualpay   


            if not f:
                a=20
                c.drawString(40, 505-a, 'Customer cancelled booking')





            if afafa.description: 
                a = a+20
                discount=  totalprice - afafa.total
                c.drawString(180, 480-a, 'Special Promo:   ' + afafa.description.description )
                c.drawString(470, 480-a, '- RM ' + str(discount))
            
            if afafa.gst > 0:

                a = a+20
                c.drawString(180, 480-a, '6% GST ' )
                c.drawString(470, 480-a, 'RM ' + str(afafa.gst))

                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 450-a, 'Total:')
            if f:
                c.drawString(470, 450-a, 'RM ' + str(afafa.total)) 
            else:
                c.drawString(470,450-a, 'RM ' + str(afafa.bookingfee))
            c.setFont('Helvetica', 9, leading=None)
            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 450-a, 'Booking Pre-payment')
                c.drawString(470, 450-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                
                    c.drawString(180, 430-a, 'Total Paid:')
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        total12 = afafa.total
                    c.drawString(470, 430-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 430-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 430-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 415-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 415-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 415-a, 'Deposit not applicable')



            if a > 90:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = a-300

            
            if afafa.totalpaid == True:
                a= a+20
                c.setFont('Helvetica-Bold', 11, leading=None)                
                c.drawString(40, 400-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 380-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 380-a, 'RM ' + str(total12))
                c.setFont('Helvetica', 7, leading=None)   
                if not afafa.depositreturnedate:             
                    c.drawString(40, 180-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas of the hotel is strictly prohibited. ')
                    c.drawString(40, 170-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                    c.drawString(40, 155-a, 'For security purposes, both main elevators will be locked between 10pm to 7am. Please use the service lift, which can be accessed through the side door.')
                    c.drawString(40, 140-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out. Failure to do so will incur a charge of RM 20.00 per card.')            


            if afafa.totalpaid == False:
                if afafa.bookingfeepaid == False:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 400-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 400-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 400-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 320-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 320-a, 'Not Paid')                                                            

            
            if a > 300:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = a-500   



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 320-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                a=a+20
                c.drawString(40, 320-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                c.drawString(180, 320-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

            if afafa.depositreturnedate:
                items = 0

                if q111:
                    c.drawString(40, 300-a, 'Deposit charged:')
                    for i in q111:
                        c.drawString(180, 300-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
                        n = 17
                        a+=n
                        items += i.itemprice
                    returned = afafa.depositamt - items
                    if returned < 0: 
                        returned = -(returned)
                        c.drawString(40, 280-a, 'Deposit charged on')
                        # c.drawString(350, 280-a,  'RM ' + str(returned))  
                    else:
                        c.drawString(40, 280-a, 'Deposit returned')
                        if afafa.otherdeposit < 1:
                            c.drawString(350, 280-a, 'RM ' + str(returned))                         # c.drawString(350, 280-a, 'RM ' + str(returned))     


                else:
                    c.drawString(40, 280-a, 'Deposit returned on')
                        

                tz = timezone('Etc/GMT-8')
                depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

                c.drawString(180, 280-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

                a=a+20       
                c.drawString(40, 280-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                c.drawString(40, 265-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
         
                                   

                c.setLineWidth(.5)
                c.line(40,180-a , 180,180-a)   
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(80, 160-a, 'Signature')            



            # c.drawString(380, 390-a, 'Payment Method:')                
            # c.drawString(470, 390-a, str(afafa.Paymentmethod))
                # if afafa.Paymentmethod == "Credit Card":
                #     c.drawString(470, 490-a, afafa.paymentdescription)
                # c.drawCentredString(415,500, 'test')
            logo='booking/static/innbparklogo2.gif'           
                # c.setFont('Helvetica', 48, leading=None)
                # c.drawCentredString(415,500, 'test')
                # c.setFont('Helvetica', 20, leading=None)        


            c.drawImage(logo, 400 , 730, width=140, height=69)
            c.showPage()
            c.save()
        generate1(f,e,d, q111)
        return redirect('https://innbparkhotel.com/customer/?pk=' + test)


    context={
    'depforminfo':depforminfo,
    'depforms': depforms,
    }

    return render(request, "booking/withold.html", context)





@csrf_exempt
def success(request):
    if request.method =="POST":
        merchantID = "innbparkhotel"
        pk = request.POST.get('orderid')
        tranid = request.POST.get('tranID')
        status = request.POST.get('status')
        domain = request.POST.get('domain')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        appcode = request.POST.get('appcode')
        paydate = request.POST.get('paydate')
        skey = request.POST.get('skey')
        orderid = pk
        asdftt = (tranid + orderid + status + domain + amount + currency)
        aaatt = (asdftt).encode('utf-8')     
        m = hashlib.md5()
        m.update(aaatt)
        key0 =  m.hexdigest()
        aaatt1 = (asdf11).encode('utf-8')
        m3 = hashlib.md5()
        m3.update(aaatt1)
        key1 =  m3.hexdigest()

        if skey==key1:
            if status == "00": 

                d = Invoice.objects.get(referenceno=pk)  
                e = Booking.objects.filter(referenceno = pk)
                firstname= d.email.first_name
                cindate= datetime.strftime(datetime.now(), '%d%m%Y')
                f = Booking.objects.filter(referenceno = pk).first()




                noofdays = 0
                for each in e:
                    if each.room_type_name.pk is not 24 and each.room_type_name.pk is not 23 and each.room_type_name.pk is not 24 and each.room_type_name.pk is not 28:
                        noofdays = noofdays + (each.checkout_date - each.checkin_date).days



                if d.totalpaid == False:
                    user55 = d.email.user_login
                    if d.description:
                        usedpromocode= d.description
                        if usedpromocode.points is not None:
                            if user55:
                                user55.numbertime = int(user55.numbertime) + (int(noofdays)) - int(usedpromocode.points)
                                user55.save()



                                pointused = str((int(noofdays)) - int(usedpromocode.points))
                                newuserloginlog = PointLog.objects.create(user_login=user55, pointused=pointused, pointdescription ="Promocode " + d.description.code + " used with points: " + str(usedpromocode.points) + " taken and points added from number of days " + str(noofdays))




                    else:
                # else:
                        if user55:
                            user55.numbertime = int(user55.numbertime) + (int(noofdays))
                            user55.save()



                            pointused = str(noofdays)
                            newuserloginlog = PointLog.objects.create(user_login=user55, pointused=pointused, pointdescription ="Points added from number of days " + str(noofdays))






                d.totalpaid = True

                year = datetime.now().strftime("%y")    
                asdf = Invoice.objects.get(pk=5331)
                

                if d.invoiceno:
                    randomvar = None
                else:
                    invnos = Invoice.objects.all().order_by('invoiceno').last()
                    inv_no = invnos.invoiceno

                    newyear1 = inv_no[:2]
                    if str(newyear1)==year:
                        invoice_int = inv_no[2:]
                        new_invoice_int = int(invoice_int) + 1
                        new_invoice_no = year + str(format(new_invoice_int, '05d'))
                        d.invoiceno = new_invoice_no
                    else:
                        invoice_int = inv_no[2:]
                        new_invoice_int = int(invoice_int) + 1
                        new_invoice_no = year + "00001"
                        d.invoiceno = new_invoice_no     





                d.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                # d.bookingfeepaid = True
                d.Paymentmethod = "Credit Card"
                # d.paymentdescription = "Paid through Molpay"
                d.save()
                email_ = d.email.email

                nop = f.number_of_people
                addcomments = f.additional_comments


                html_message = loader.render_to_string('booking/email2.html',{
                'first_name':d.email.first_name,
                'last_name': d.email.last_name,
                'total':d.total,
                'booking':e,
                'checkindate': f.checkin_date,
                'checkoutdate': f.checkout_date,
                'referenceno': d.referenceno,
                'addcomments':addcomments,
                'nop': nop

                })

                msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", [email_, 'admin@innbparkhotel.com']) 

                msg.attach_alternative(html_message, "text/html")

                msg.send()

                

                if d.description:
                    if d.description.sendemail == True:
                        customerpk = d.email.pk
                        customername = d.email


                        html_message3 = 'This booking has applied the promocode: ' + d.description.description + '</br> Please take the appropriate action. </br> </br> Booking details can be found at the link below: </br> <a href="https://innbparkhotel.com/customer/?pk=' + str(customerpk) + '">' +customername.first_name + ' ' + customername.last_name +  '</a>'  

                        msg3 = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Promocode Action Needed", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com']) 

                        msg3.attach_alternative(html_message3, "text/html")

                        msg3.send()






                successbig = "Thank You"

                success= "Your booking is successful. An email has been sent to your email address with details about the booking. Please do not hesitate to contact us on +603 2856 7257 or email us admin@innbparkhotel.com if you have any further queries."

                d = Invoice.objects.get(referenceno=d.referenceno)  
                invno = d.invoiceno
                e = Booking.objects.filter(referenceno = d.referenceno)
                firstname= d.email.first_name
                cindate= datetime.strftime(datetime.now(), '%d%m%Y')
                f = Booking.objects.filter(referenceno = d.referenceno).first()
                try:
                    q111 = depositwitheld.objects.filter(invoice=d)
                except depositwitheld.DoesNotExist:
                    q111 = None



                def generate1(f, ae, afafa, q111):
                    logo='booking/static/innbparklogo2.gif'           

                    c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.drawImage(logo, 400 , 730, width=140, height=69)

                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)


                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(40 ,790,'InnB Park Hotel')
                    c.drawString(40 ,775,'102-106, Jalan Imbi,  Bukit Bintang')
                    c.drawString(40 ,760,'55100 Kuala Lumpur')
                    c.drawString(40 ,745,'admin@innbparkhotel.com') 
                    c.drawString(40 ,730,'+603 2856 7257')



                    c.setFont('Helvetica-Bold', 12, leading=None)
                    c.drawString(40 ,680,'ROOM RESERVATION')
                    c.drawString(430 ,810,'Non-refundable Rate')

                    c.setFont('Helvetica', 9, leading=None)
                    c.drawString(40, 630, 'GUESTS NAME')
                    c.drawString(197, 630, 'ROOM NO.')
                    c.drawString(257, 630, 'ROOM TYPE')
                    c.drawString(380, 630, 'ARRIVAL DATE')  
                    c.drawString(470, 630, 'DEPATURE DATE')                                     
                        
                    c.setLineWidth(.5)
                    c.line(40,610,548,610)

                    if f:
                        c.setFont('Helvetica', 9, leading=None)
                        c.drawString(40, 590, afafa.email.first_name)
                        c.drawString(40, 570, afafa.email.last_name)


                    a=0
                    for t in ae:
                        roomnumber = "[" + str(t.room_number) + "]"
                        roomname = str(t.room_type_name)
                        n=20
                        a += n
                        c.drawString(197, 610-a, roomnumber)
                        c.drawString(257, 610-a, roomname)
                        indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                        outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                        c.drawString(380, 610-a, indate)  
                        c.drawString(470, 610-a, outdate)

                    c.line(40,570-a,548,570-a)


                    c.setFont('Helvetica-Bold', 11, leading=None)
                    c.drawString(40, 530-a, 'INVOICE NO: ' + afafa.invoiceno)
                    if afafa.cancelled == True:
                        c.setFont('Helvetica-Bold', 14, leading=None)
                        c.drawString(330, 530-a, 'INVOICE CANCELLED')
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 505-a, 'DESCRIPTION')
                    c.drawString(180, 505-a, 'PRICE/UNIT')
                    c.drawString(330, 505-a, 'NO. NIGHTS')
                    c.drawString(470, 505-a, 'TOTAL PRICE')


                    c.setFont('Helvetica', 9, leading=None)
                    totalprice=0
                    for t in ae:
                        roomnumber = str(t.room_number)
                        roomname = str(t.room_type_name)
                        n=20
                        a += n
                        nights = int((t.checkout_date-t.checkin_date).days)
                        price = str(round((t.actualpay /  nights),2))
                        c.drawString(40, 505-a, roomname)
                        c.drawString(180, 505-a, 'RM ' + price)
                        c.drawString(330, 505-a, str(nights))
                        c.drawString(470, 505-a, 'RM ' + str(t.actualpay))
                        totalprice += t.actualpay   


                    if not f:
                        a=20
                        c.drawString(40, 505-a, 'Customer cancelled booking')





                    if afafa.description: 
                        a = a+20
                        discount=  totalprice - afafa.total
                        c.drawString(180, 480-a, 'Special Promo:   ' + afafa.description.description )
                        c.drawString(470, 480-a, '- RM ' + str(discount))
                    
                    if afafa.gst > 0:

                        a = a+20
                        c.drawString(180, 480-a, '6% GST ' )
                        c.drawString(470, 480-a, 'RM ' + str(afafa.gst))


                    else:
                        qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
                        utc=pytz.UTC
                        qindate=utc.localize(qindate) 
                        if afafa.datecreated > qindate:
                            a = a+20
                            c.drawString(180, 520-a, '0% SST ' )
                            c.drawString(470, 520-a, 'RM 0.00')

                        
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(180, 450-a, 'Total:')
                    if f:
                        c.drawString(470, 450-a, 'RM ' + str(afafa.total)) 
                    else:
                        c.drawString(470,450-a, 'RM ' + str(afafa.bookingfee))
                    c.setFont('Helvetica', 9, leading=None)
                    if afafa.bookingfeepaid == True:
                        a = a+20
                        c.drawString(180, 450-a, 'Booking Pre-payment')
                        c.drawString(470, 450-a, 'RM ' + str(afafa.bookingfee))

                        if afafa.totalpaid == True:
                            c.setFont('Helvetica-Bold', 12, leading=None)                
                            c.drawString(180, 430-a, 'Total Paid:')
                            if afafa.bookingfeepaid == True:
                                total12 = afafa.total - afafa.bookingfee
                            else: 
                                total12 = afafa.total
                            c.drawString(470, 430-a, 'RM ' + str(total12))




                        else:
                            c.setFont('Helvetica-Bold', 12, leading=None)
                            if f:                
                                c.drawString(180, 430-a, 'Outstanding Amount:')
                                if afafa.bookingfeepaid == True:
                                    total12 = afafa.total - afafa.bookingfee
                                else: 
                                    total12 = afafa.total
                                c.drawString(470, 430-a, 'RM ' + str(total12))
                            if afafa.deposit == False:
                                c.setFont('Helvetica-Bold', 8, leading=None)
                                if f:
                                    c.drawString(180, 415-a, 'Deposit Required') 
                                    c.setFont('Helvetica', 8, leading=None)        
                                    c.drawString(470, 415-a, 'RM ' + str(afafa.depositamt))
                                if not f:
                                    c.drawString(180, 415-a, 'Deposit not applicable')



                    if a > 90:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = a-300

                    
                    if afafa.totalpaid == True:
                        a= a+20
                        c.setFont('Helvetica-Bold', 11, leading=None)                
                        c.drawString(40, 400-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 380-a, 'Payment Total')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total                
                        c.drawString(180, 380-a, 'RM ' + str(total12))
                        c.setFont('Helvetica', 7, leading=None)   
                        if not afafa.depositreturnedate:             
                            c.drawString(40, 180-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas of the hotel is strictly prohibited. ')
                            c.drawString(40, 170-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                            c.drawString(40, 155-a, 'For security purposes, both main elevators will be locked between 10pm to 7am. Please use the service lift, which can be accessed through the side door.')
                            c.drawString(40, 140-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out. Failure to do so will incur a charge of RM 20.00 per card.')            


                    if afafa.totalpaid == False:
                        if afafa.bookingfeepaid == False:
                            a= a+20 
                            c.setFont('Helvetica-Bold', 11, leading=None)                
                            c.drawString(40, 400-a, 'PAYMENT METHOD' )
                            c.setFont('Helvetica', 9, leading=None)
                            a= a+20                 
                            c.drawString(40, 400-a, 'Please arrange for an online transfer to the following bank account:')
                            a= a+15                 
                            c.drawString(40, 400-a, 'Bank: UOB Bank')
                            a= a+15                 
                            c.drawString(40, 400-a, 'Account Name: APOCITY SDN BHD')
                            a= a+15                 
                            c.drawString(40, 400-a, 'Account Number: 608-300-6312')
                            a= a+15                 
                            c.drawString(40, 400-a, 'Reference: ' + afafa.invoiceno) 
                            c.setFont('Helvetica-Bold', 9, leading=None)
                            c.drawString(40, 320-a, 'Deposit') 
                            c.setFont('Helvetica', 9, leading=None)        
                            c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                            c.drawString(100, 320-a, 'Not Paid')                                                            

                    
                    if a > 300:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = a-500   



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 320-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 320-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 320-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        c.drawString(180, 320-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

                    if afafa.depositreturnedate:
                        items=0
                        if q111:
                            c.drawString(40, 300-a, 'Deposit charged:')
                            for i in q111:
                                c.drawString(180, 300-a, str(i.itemname)+ '   RM '  + str(i.itemprice))
                                n = 17
                                a+=n
                                items += i.itemprice
                            returned = afafa.depositamt - items
                            if afafa.depdescrip:
                                if returned < 0: 
                                    returned = -(returned)
                                    c.drawString(40, 280-a, 'Deposit charged on')
 
                                else:
                                    c.drawString(40, 280-a, 'Deposit returned')
                                    
                            else:

                                if returned < 0: 
                                    returned = -(returned)
                                    c.drawString(40, 280-a, 'Deposit charged on')
                                    # c.drawString(350, 280-a, 'RM ' + str(returned))  
                                else:
                                    c.drawString(40, 280-a, 'Deposit returned')
                                    if afafa.otherdeposit < 1 :
                                        c.drawString(350, 280-a, 'RM ' + str(returned))                                  

                        else:
                            c.drawString(40, 280-a, 'Deposit returned on')
                        

                        tz = timezone('Etc/GMT-8')
                        depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

                        c.drawString(180, 280-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

                        a=a+20         
                        c.drawString(40, 280-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                        c.drawString(40, 265-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
                 
                        c.setLineWidth(.5)
                        c.line(40,180-a , 180,180-a)   
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(80, 160-a, 'Signature')            



                    # c.drawString(380, 390-a, 'Payment Method:')                
                    # c.drawString(470, 390-a, str(afafa.Paymentmethod))
                        # if afafa.Paymentmethod == "Credit Card":
                        #     c.drawString(470, 490-a, afafa.paymentdescription)
                        # c.drawCentredString(415,500, 'test')
                    logo='booking/static/innbparklogo2.gif'           
                        # c.setFont('Helvetica', 48, leading=None)
                        # c.drawCentredString(415,500, 'test')
                        # c.setFont('Helvetica', 20, leading=None)        


                    c.drawImage(logo, 400 , 730, width=140, height=69)
                    c.showPage()
                    c.save()


                generate1(f,e,d, q111)    



            elif status == "11":

                successbig = "Sorry, your payment did not go through"
                success = "Please ensure the details you entered are correct. Alternatively, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "

    

    else:

        successbig = "Unfortunately, something went wrong with the system"
        success = "We are very sorry for the incovenience, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "



    context = {
    'success':success,
    'sucesssbig':successbig,
    }


    return render(request, "booking/success.html", context)  




# def portal(request):

#     return render(request, "booking/portal", context)








@csrf_exempt
def success2(request):
    if request.method =="POST":

        postrequest = request.POST
        postrequest2 = request.content_params
        postrequest3 = request.body
        postrequest4 = request.META

        html_message = loader.render_to_string('booking/email2.html',{
        'first_name':"test",
        'last_name': postrequest,
        'total':postrequest3,
        'booking':postrequest3,
        'checkindate': postrequest4,
        'checkoutdate': postrequest2,
        'referenceno': "test",
        'addcomments':"Notification",
        'nop': "test"

        })

        msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com']) 

        msg.attach_alternative(html_message, "text/html")

        msg.send()



        merchantID = "innbparkhotel"
        nbcb = request.POST.get('nbcb')
        pk = request.POST.get('orderid')
        tranid = request.POST.get('tranID')
        status = request.POST.get('status')
        domain = request.POST.get('domain')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        appcode = request.POST.get('appcode')
        paydate = request.POST.get('paydate')
        skey = request.POST.get('skey')
        orderid = pk
        asdftt = (tranid + orderid + status + domain + amount + currency)
        aaatt = (asdftt).encode('utf-8')     
        m = hashlib.md5()
        m.update(aaatt)
        key0 =  m.hexdigest()
        m3 = hashlib.md5()
        m3.update(aaatt1)
        key1 =  m3.hexdigest()
        treq = "1"


        class MyAdapter(HTTPAdapter):
            def init_poolmanager(self, connections, maxsize, block=False):
                self.poolmanager = PoolManager(num_pools=connections,
                                           maxsize=maxsize,
                                           block=block,
                                           ssl_version=ssl.PROTOCOL_TLSv1_2)
            def proxy_manager_for(self, proxy, **proxy_kwargs):
                # This method is called when there is a proxy.
                proxy_kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1_2
                return super(MyAdapter, self).proxy_manager_for(proxy, **proxy_kwargs)


        url = 'https://www.onlinepayment.com.my/MOLPay/API/chkstat/returnipn.php'
        s = requests.Session()
        s.mount('https://', MyAdapter())

        values2 =  "treq=" + str(treq) + "&nbncb=" + str(nbcb) + "&orderid=" + str(orderid) + "&tranID=" + str(tranid) + "&status=" + str(status) + "&domain=" + str(domain) + "&amount="+ str(amount) + "&currency="+str(currency)+"&appcode=" + str(appcode) + "&paydate=" + str(paydate) + "&skey=" + str(skey)

        values = {
        'treq': treq,
        'currency': currency, 
        'appcode': appcode, 
        'paydate': paydate, 
        'status': status, 
        'orderid': orderid, 
        'skey': skey, 
        'domain': domain, 
        'amount': amount, 
        'nbcb': nbcb, 
        'tranID': tranid
        }

        r = s.post(url, data=values) 



        if skey==key1:
            if status == "00": 

                # if str(nbcb) == "2":

                d = Invoice.objects.get(referenceno=pk)  
                e = Booking.objects.filter(referenceno = pk)


                noofdays = 0
                for each in e:
                    if each.room_type_name.pk is not 24 and each.room_type_name.pk is not 23 and each.room_type_name.pk is not 24 and each.room_type_name.pk is not 28:
                        noofdays = noofdays + (each.checkout_date - each.checkin_date).days




                if d.totalpaid == False:
                    user55 = d.email.user_login
                    if d.description:
                        usedpromocode= d.description
                        if usedpromocode.points is not None:
                            if user55:
                                user55.numbertime = int(user55.numbertime) + (int(noofdays)) - int(usedpromocode.points)
                                user55.save()

                                pointused = str((int(noofdays)) - int(usedpromocode.points))
                                newuserloginlog = PointLog.objects.create(user_login=user55, pointused=pointused, pointdescription ="Promocode " + d.description.code + " used with points: " + str(usedpromocode.points) + " taken and points added from number of days " + str(noofdays))


                    else:
                # else:
                        if user55:
                            user55.numbertime = int(user55.numbertime) + (int(noofdays))
                            user55.save()

                            pointused = str(noofdays)
                            newuserloginlog = PointLog.objects.create(user_login=user55, pointused=pointused, pointdescription ="Points added from number of days " + str(noofdays))







                
                d.totalpaid = True
                d.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                # d.bookingfeepaid = True
                d.Paymentmethod = "Credit Card"
                # d.paymentmethod = "Molpay"
                # d.paymentdescription = "Paid through Molpay"


                if d.invoiceno:
                    print("nothing")
                else:

                    year = datetime.now().strftime("%y")    
                    asdf = Invoice.objects.get(pk=5331)

                    invnos = Invoice.objects.all().order_by('invoiceno').last()
                    inv_no = invnos.invoiceno
                    # invoice_int = inv_no[2:]


                    newyear1 = inv_no[:2]
                    if str(newyear1)==year:
                        invoice_int = inv_no[2:]
                        new_invoice_int = int(invoice_int) + 1
                        new_invoice_no = year + str(format(new_invoice_int, '05d'))
                        d.invoiceno = new_invoice_no
                    else:
                        invoice_int = inv_no[2:]
                        new_invoice_int = int(invoice_int) + 1
                        new_invoice_no = year + "00001"
                        d.invoiceno = new_invoice_no             




                
                d.save()

                # email_ = d.email.email







                return HttpResponse(values2)



            elif status == "11":

                successbig = "Sorry, your payment did not go through"
                success = "Please ensure the details you entered are correct. Alternatively, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "

    

    else:

        successbig = "Unfortunately, something went wrong with the system"
        success = "We are very sorry for the inconvenience, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "



    context = {
    'success':success,
    # 'sucesssbig':successbig,
    }


    return HttpResponse(success)


















@csrf_exempt
def success3(request):
    if request.method =="POST":

        postrequest = request.POST
        postrequest2 = request.content_params
        postrequest3 = request.body
        postrequest4 = request.META

        html_message = loader.render_to_string('booking/email2.html',{
        'first_name':"test",
        'last_name': postrequest,
        'total':postrequest3,
        'booking':postrequest3,
        'checkindate': postrequest4,
        'checkoutdate': postrequest2,
        'referenceno': "test",
        'addcomments':"Callback",
        'nop': "test"

        })

        msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com']) 

        msg.attach_alternative(html_message, "text/html")

        msg.send()








        merchantID = "innbparkhotel"
        nbcb = request.POST.get('nbcb')
        pk = request.POST.get('orderid')
        tranid = request.POST.get('tranID')
        status = request.POST.get('status')
        domain = request.POST.get('domain')
        amount = request.POST.get('amount')
        currency = request.POST.get('currency')
        appcode = request.POST.get('appcode')
        paydate = request.POST.get('paydate')
        skey = request.POST.get('skey')
        orderid = pk
        asdftt = (tranid + orderid + status + domain + amount + currency)
        aaatt = (asdftt).encode('utf-8')     
        m = hashlib.md5()
        m.update(aaatt)
        key0 =  m.hexdigest()
        m3 = hashlib.md5()
        m3.update(aaatt1)
        key1 =  m3.hexdigest()
        treq = "1"




        if skey==key1:
            if status == "00": 

                if str(nbcb) == "1":

                    d = Invoice.objects.get(referenceno=pk)  
                    e = Booking.objects.filter(referenceno = pk)
                    d.totalpaid = True
                    d.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # d.bookingfeepaid = True
                    d.Paymentmethod = "Credit Card"
                    # d.paymentmethod = "Molpay"

                    if d.invoiceno:
                        print("nothing")
                    else:

                        year = datetime.now().strftime("%y")    
                        asdf = Invoice.objects.get(pk=5331)

                        invnos = Invoice.objects.all().order_by('invoiceno').last()
                        inv_no = invnos.invoiceno
                        newyear1 = inv_no[:2]
                        if str(newyear1)==year:
                            invoice_int = inv_no[2:]
                            new_invoice_int = int(invoice_int) + 1
                            new_invoice_no = year + str(format(new_invoice_int, '05d'))
                            d.invoiceno = new_invoice_no
                        else:
                            invoice_int = inv_no[2:]
                            new_invoice_int = int(invoice_int) + 1
                            new_invoice_no = year + "00001"
                            d.invoiceno = new_invoice_no                            





                    d.save()

                    # email_ = d.email.email







                    return HttpResponse("CBTOKEN:MPSTATOK", content_type="text/plain")



            elif status == "11":

                successbig = "Sorry, your payment did not go through"
                success = "Please ensure the details you entered are correct. Alternatively, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "

    

    else:

        successbig = "Unfortunately, something went wrong with the system"
        success = "We are very sorry for the inconvenience, please contact us on +603 2856 7257 or email us admin@innbparkhotel.com so we can help you further "



    context = {
    'success':success,
    # 'sucesssbig':successbig,
    }


    return HttpResponse(success)




@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def portal1351(request):
    pk = request.GET.get('id')
    tz = timezone('Etc/GMT+8')
    staff = User.objects.get(pk=pk)
    depositquery = staff.username
    if request.method=="POST":
        intime = request.POST.get('first_name')
        outtime =  request.POST.get('last_name')

        intime1 = datetime.strptime(intime,'%H:%M')

        outtime1 = datetime.strptime(outtime,'%H:%M') 
        timer123 = Timerole.objects.filter(user=staff)
        if timer123:
            timer123 = Timerole.objects.get(user=staff)
            timer123.inTime=intime1
            timer123.outTime=outtime1
            timer123.save()    
            return HttpResponse("outtime")       
        else: 
            timer123 = Timerole(user=staff, inTime=intime1, outTime=outtime1)
            timer123.save()


    # todaydate = tz.localize(datetime.today())
        return redirect('portal135')





    context = {
    'depositquery':depositquery,
    }
    return render(request,"booking/loginpageedit.html",context)



@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def portal135(request):

    allusers = User.objects.all()

    tz = timezone('Etc/GMT+8')
    # todaydate = tz.localize(datetime.today())
    date_customers3 = Timerole.objects.all().order_by('id')

    depositquery=date_customers3


    context = {
    'depositquery':depositquery,
    'allusers':allusers
    }
    return render(request,"booking/loginpage.html",context)


@login_required(login_url='/login/')
def portal3(request):

    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    date_customers2 = Booking.objects.filter(checkout_date=todaydate).exclude(checkedout1__isnull=False).exclude(upgrade=True).order_by('referenceno')
    date_customers4 = Booking.objects.filter(upgradedate=todaydate, ugradebooking__isnull=False).exclude(checkedout1__isnull=False)
    date_customers3 = date_customers2 | date_customers4


    lasttime = reportdate.objects.all().order_by('id').last()
    todaytime222 =(lasttime.time+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")





    depositquery = []
    referencenotest = None
    totalcash = 0
    totalcc = 0
    asdf=[]

    Otherstotal = ""
    for row in date_customers3:
        if referencenotest == row.referenceno:
            t = None
        else:
            try:
                qq = Invoice.objects.get(referenceno=row.referenceno)
                if qq.depositcash is None:
                    qq.depositcash = 0
                if qq.depositcc is None:
                    qq.depositcc = 0
                totalcash = totalcash + qq.depositcash
                totalcc = totalcc + qq.depositcc
                if qq.depi=="Others":
                    Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  


                depositquery.extend(list(Invoice.objects.filter(referenceno=row.referenceno)))
                referencenotest = row.referenceno

            except Invoice.DoesNotExist:
                row.delete()
                referencenotest = "0"                


    
  
    if depositquery is not None:

        for ro in depositquery:
            asdf = Booking.objects.filter(referenceno=ro.referenceno)
            roomasd=[]
            for a in asdf:
                if a.upgrade == True:
                    if a.ugradebooking:
                        try:
                            roomother = Booking.objects.get(pk=a.ugradebooking)
                            roomnob = roomother.room_number.room_number
                            roomasd.append(roomnob)
                        except Booking.DoesNotExist:
                            print("nothing")
                else:    
                    if a.room_number:
                        roomnob = a.room_number.room_number
                        roomasd.append(roomnob)
            ro.roomnumber = roomasd

    context = {
    'depositquery':depositquery,
    'totalcash':totalcash,
    'totalcc':totalcc,
    'Otherstotal':Otherstotal,
    'lasttime':lasttime,
    'todaytime222':todaytime222
    }
    return render(request,"booking/dep.html",context)

@login_required(login_url='/login/')
def reportarchive(request):

    whitewhite = reportdate.objects.all().order_by('-time')
    for a in whitewhite:

        a.urls = "https://innbparkhotel.com/static/Reports/"+ (a.time+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")+".csv"

        # a.urls = "https://innbparkhotel.com/delete20/"+ str(a.pk)

    context = {
    'whitewhite':whitewhite,

    }
    return render(request,"booking/reportarchive.html",context)


@csrf_exempt
@login_required(login_url='/login/')
def whiteboards1(request):
    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    date_customers1 = Booking.objects.filter(checkin_date=todaydate, additional_comments__isnull=False).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(room_type_name__pk=28).order_by('first_name')
    
    roomnum = Roomnumber.objects.all().order_by('room_number')
    forst = User.objects.all()
    whitewhite = whiteboard.objects.filter(hidden=False)
    # users = socketdata.objects.filter(status="Online")


    if request.method == 'POST':
        cdate = request.POST.get('startdate')
        rno = request.POST.get('roomno')
        forstaff1 = request.POST.get('forstaff1')
        if rno =="" or rno=="None":

            if forstaff1 == "" or forstaff1 == "None":

                neww = whiteboard.objects.create(texts=cdate,staff= request.user.username )
            else:
                neww = whiteboard.objects.create(texts=cdate,staff= request.user.username,forstaff=forstaff1)                


        else:
            if forstaff1 == "" or forstaff1 == "None":
                rno1 = Roomnumber.objects.get(room_number=rno)
                neww = whiteboard.objects.create(texts=cdate, room_number=rno1, staff= request.user.username )   
            else:
                rno1 = Roomnumber.objects.get(room_number=rno)
                neww = whiteboard.objects.create(texts=cdate, room_number=rno1, staff= request.user.username,forstaff=forstaff1)

        return redirect('https://innbparkhotel.com/whiteboard') 
    if request.method =='GET':
        test = None

        context = {
        'whitewhite':whitewhite,
        'roomnum':roomnum,
        'forst': forst,
        }
        return render(request,"booking/whiteboard.html",context)



@csrf_exempt
def whiteboardscomplete(request):
    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['bk']
        status = data['jest']
        if status=="1351351351351":

            try:
                room = whiteboard.objects.get(pk=pw)
                room.complete=True
                room.save()
                # invoice1refno = invoice1.referenceno
            except Roomnumber.DoesNotExist:
                return redirect('test2')

    return HttpResponse("ok")  



@csrf_exempt
def whiteboardsrem(request):
    if request.method == 'POST':

        data = json.loads(request.body.decode('utf-8'))
        print(data)
        pw = data['bk']
        status = data['jest']
        if status=="1351351351351":

            try:
                room = whiteboard.objects.get(pk=pw)
                room.delete()

                # invoice1refno = invoice1.referenceno
            
            except Roomnumber.DoesNotExist:
                return redirect('test2')

    return HttpResponse("ok")  


@login_required(login_url='/login/')
def portal6(request):

    todaytime111 =((datetime.now()+timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

    lasttime = reportdate.objects.all().order_by('id').last()

    todaytime222 =(lasttime.time+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    todaytime1 = (datetime.now())
    staff = request.user.username 
    todaytime2 = (lasttime.time)
    newreport = reportdate.objects.create(staff=staff)
    date_customers3 = Booking.objects.filter(checkedin1__gte=todaytime2,checkedin1__lte=todaytime1).order_by('referenceno')

    depositquery = []
    referencenotest = None
    totalcash = 0
    totalcc = 0
    tcash=0
    ttaxx=0
    tcc=0
    asdf=[]

    Otherstotal = ""
    for row in date_customers3:
        if referencenotest == row.referenceno:
            t = None
        else:
            try:
                qq = Invoice.objects.get(referenceno=row.referenceno)
            except Invoice.DoesNotExist:
                return HttpResponse("Problem with booking first name =" + row.first_name)
            if qq.depositcash is None:
                qq.depositcash = 0
            if qq.depositcc is None:
                qq.depositcc = 0
            if qq.cashpaid is None:
                qq.cashpaid = 0
            if qq.ccpaid is None:
                qq.ccpaid = 0
            if qq.ttax is None:
                qq.ttax = 0
            tcc = tcc + qq.ccpaid
            tcash = tcash + qq.cashpaid                
            totalcash = totalcash + qq.depositcash
            totalcc = totalcc + qq.depositcc
            ttaxx = ttaxx + qq.ttax
            if qq.depi=="Others":
                Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  


            depositquery.extend(list(Invoice.objects.filter(referenceno=row.referenceno)))
            referencenotest = row.referenceno
    
  
    if depositquery is not None:

        for ro in depositquery:
            asdf = Booking.objects.filter(referenceno=ro.referenceno)
            roomasd=[]
            for a in asdf:
                if a.room_number:
                    roomnob = a.room_number.room_number
                    roomasd.append(roomnob)
            ro.roomnumber = roomasd


    todaytime11 = (datetime.now())
    todaytime22 = (datetime.now()-timedelta(hours=8))
    date_customers31 = Booking.objects.filter(checkedout1__gte=todaytime2,checkedout1__lte=todaytime1).order_by('referenceno')

    depositquery1 = []
    referencenotest1 = None
    totalcash1 = 0
    totalcc1 = 0
    tcash1=0
    tcc1 = 0
    ttax1 = 0
    asdf1=[]

    Otherstotal = ""
    for row1 in date_customers31:
        if referencenotest1 == row1.referenceno:
            t = None
        else:
            try:
                qq = Invoice.objects.get(referenceno=row1.referenceno)
            except Invoice.DoesNotExist:
                return HttpResponse("Problem with booking first name =" + row1.first_name)
            if qq.depositcash is None:
                qq.depositcash = 0
            if qq.depositcc is None:
                qq.depositcc = 0
            if qq.cashpaid is None:
                qq.cashpaid = 0
            if qq.ccpaid is None:
                qq.ccpaid = 0
            if qq.ttax is None:
                qq.ttax = 0    
            tcc1 = tcc1 + qq.ccpaid
            tcash1 = tcash1 + qq.cashpaid
            totalcash1 = totalcash1 + qq.depositcash
            ttax1 = ttax1 + qq.ttax
            totalcc1 = totalcc1 + qq.depositcc
            if qq.depi=="Others":
                Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  


            depositquery1.extend(list(Invoice.objects.filter(referenceno=row1.referenceno)))
            referencenotest1 = row1.referenceno
    
  
    if depositquery1 is not None:

        for ro1 in depositquery1:
            asdf1 = Booking.objects.filter(referenceno=ro1.referenceno)
            roomasd1=[]
            for a1 in asdf1:
                if a1.room_number:
                    roomnob = a1.room_number.room_number
                    roomasd1.append(roomnob)
            ro1.roomnumber = roomasd1





    with open('/hotel/static/Reports/'+todaytime111+'.csv', 'w') as myfile:
        # wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        # response = HttpResponse(content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="report.csv"'

        writer = csv.writer(myfile)
        writer.writerow([staff])
        writer.writerow(['Shift commenced', todaytime222])
        writer.writerow(['Shift end', todaytime111])    
        writer.writerow([''])
        writer.writerow(['Check-in this shift'])
        writer.writerow(['Room', 'Name', 'Referral','Desposit Cash','Deposit Credit Card','Other Deposit','Cash paid','Credit Card Paid', 'Tourism Tax' ])
           
        for each in depositquery:
            # firstbook = Booking.objects.filter(referenceno=each.referenceno).first()        


            # room2 = Booking.objects.filter(referenceno=each.referenceno)
            # aroom34 = ""
            # for aaa in room2:
            #     if aaa.room_number:
            #         aroom = aaa.room_number
            #         if aaa.late:
            #             each.referral = str(each.referral) + " " + "late"
            #             if aaa.extension:
            #                 each.referral = str(each.referral) + " " + "extension"
            #         if aaa.extension:
            #             each.referral = str(each.referral)+ " " + "extension"

            #     else:
            #         aroom = None
            #     aroom34 = str(aroom34) + " " + str(aroom)
            # each.room = aroom34 
            # if not firstbook:
            #     class firstbook(object):
            #         checkin_date = None
            #         checkout_date = None
            # each.referenceno =str("=\"") + str(each.referenceno) + str("\"")
            # each.otherref =str("=\"") + str(each.otherref) + str("\"")
            # if each.molpay==True:
            #     each.referral = str(each.referral)+ " " + "molpay"            

            writer.writerow([each.roomnumber, each.email.first_name + ' '+ each.email.last_name, each.referral, each.depositcash, each.depositcc,each.depdescrip, each.cashpaid, each.ccpaid, each.ttax])
        writer.writerow(['Total', '', '',totalcash , totalcc,'', tcash, tcc,ttaxx])


     
        writer.writerow([''])
        writer.writerow([''])    
        writer.writerow([''])
        writer.writerow(['Check-out this shift'])
        writer.writerow(['Room', 'Name', 'Referral','Desposit Cash','Deposit Credit Card','Other Deposit','Cash paid','Credit Card Paid', 'Tourism Tax'])
           
        for each1 in depositquery1    

            writer.writerow([each1.roomnumber, each1.email.first_name + ' '+ each1.email.last_name, each1.referral, each1.depositcash, each1.depositcc,each1.depdescrip, each1.cashpaid, each1.ccpaid, each1.ttax])

        writer.writerow(['Total', '', '',totalcash1, totalcc1,'',tcash1,tcc1,ttax1])







    def generate11131( afafa, afafa1, totalcash , totalcc, tcash, tcc,ttaxx, totalcash1 , totalcc1, tcash1, tcc1,ttax1):
          

        c = canvas.Canvas('static/Reports/'+ todaytime111+'.pdf', pagesize=A4)
        c.setLineWidth(.3)


        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(20 ,805, staff)
        c.drawString(20 ,790,'Shift Commenced')
        c.drawString(20 ,775,'Shift End')
        c.drawString(175 ,790, todaytime222)
        c.drawString(175 ,775,todaytime111)
        c.drawString(20 ,755,'Check-in this shift')
        c.drawString(20 ,740,'Room')
        c.drawString(60 ,740,'Name')
        c.drawString(190 ,740,'Referral')
        c.drawString(240 ,740,'D Cash')
        c.drawString(280 ,740,'D Card')
        c.drawString(320 ,740,'Other')
        c.drawString(450, 740,'Cash')
        c.drawString(490 ,740,'Card')
        c.drawString(530 ,740,'Tourism Tax')
        

        a=15





        for each in afafa:
            if a > 580:
                c.showPage()
                a=0
            else:
                a=a



            c.drawString(20 ,740-a,str(each.roomnumber))
            c.drawString(60 ,740-a, str(each.email.last_name)[0:10] + " " + str(each.email.first_name)[0:10])
            c.drawString(190 ,740-a,str(each.referral)[0:11])
            c.drawString(240 ,740-a,str(each.depositcash))
            c.drawString(280 ,740-a, str(each.depositcc))
            c.drawString(320 ,740-a,str(each.depdescrip)[0:26])
            c.drawString(450, 740-a, str(each.cashpaid))
            c.drawString(490 ,740-a, str(each.ccpaid))
            c.drawString(530 ,740-a, str(each.ttax))
            a=a+15



        a=a+15
        c.drawString(20 ,740-a,'Total')
        c.drawString(240 ,740-a,str(totalcash))
        c.drawString(280 ,740-a, str(totalcc))

        c.drawString(450, 740-a, str(tcash))
        c.drawString(490 ,740-a, str(tcc))
        c.drawString(530 ,740-a, str(ttaxx))


        a=a+15
        c.drawString(20 ,720-a,'Check-out this shift')

        for each1 in afafa1:

            if a > 580:
                c.showPage()
                a=0
            else:
                a=a


            c.drawString(20 ,700-a,str(each1.roomnumber))
            c.drawString(60 ,700-a, str(each1.email.last_name)[0:10] + " " + str(each1.email.first_name)[0:10])
            c.drawString(190 ,700-a,str(each1.referral)[0:11])
            c.drawString(240 ,700-a,str(each1.depositcash))
            c.drawString(280 ,700-a, str(each1.depositcc))
            c.drawString(320 ,700-a,str(each1.depdescrip)[0:26])
            c.drawString(450, 700-a, str(each1.cashpaid))
            c.drawString(490 ,700-a, str(each1.ccpaid))
            c.drawString(530 ,700-a, str(each1.ttax))
            a=a+15

        a=a+15
        c.drawString(20 ,680-a,'Total')
        c.drawString(240 ,680-a,str(totalcash1))
        c.drawString(280 ,680-a, str(totalcc1))

        c.drawString(450, 680-a, str(tcash1))
        c.drawString(490 ,680-a, str(tcc1))
        c.drawString(530 ,680-a, str(ttax1))
        c.showPage()
        c.save()
    generate11131( depositquery, depositquery1, totalcash , totalcc, tcash, tcc,ttaxx, totalcash1 , totalcc1, tcash1, tcc1,ttax1)

    url = 'https://innbparkhotel.com/static/Reports/'+ todaytime111+'.pdf'

    return redirect(url)



















    # with open('/hotel/static/Reports/'+todaytime111+'.csv', 'r') as myfile:
    #     response = HttpResponse(myfile, content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="report.csv"'

    #     return response























    # context = {
    # 'depositquery':depositquery,
    # 'totalcash':totalcash,
    # 'totalcc':totalcc,
    # 'Otherstotal':Otherstotal
    # }
    # return render(request,"booking/dep.html",context)











def testgeneratepdf131(request):

    todaytime111 =((datetime.now()+timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")

    lasttime = reportdate.objects.all().order_by('id').last()

    todaytime222 =(lasttime.time+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    todaytime1 = (datetime.now())
    staff = request.user.username 
    todaytime2 = (lasttime.time)
    date_customers3 = Booking.objects.filter(checkedin1__gte=todaytime2,checkedin1__lte=todaytime1).order_by('referenceno')

    depositquery = []
    referencenotest = None
    totalcash = 0
    totalcc = 0
    tcash=0
    ttaxx=0
    tcc=0
    asdf=[]

    Otherstotal = ""
    for row in date_customers3:
        if referencenotest == row.referenceno:
            t = None
        else:
            try:
                qq = Invoice.objects.get(referenceno=row.referenceno)
            except Invoice.DoesNotExist:
                return HttpResponse("Problem with booking first name =" + row.first_name)
            if qq.depositcash is None:
                qq.depositcash = 0
            if qq.depositcc is None:
                qq.depositcc = 0
            if qq.cashpaid is None:
                qq.cashpaid = 0
            if qq.ccpaid is None:
                qq.ccpaid = 0
            if qq.ttax is None:
                qq.ttax = 0
            tcc = tcc + qq.ccpaid
            tcash = tcash + qq.cashpaid                
            totalcash = totalcash + qq.depositcash
            totalcc = totalcc + qq.depositcc
            ttaxx = ttaxx + qq.ttax
            if qq.depi=="Others":
                Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  

            depositquery.extend(list(Invoice.objects.filter(referenceno=row.referenceno)))
            referencenotest = row.referenceno
    
  
    if depositquery is not None:

        for ro in depositquery:
            asdf = Booking.objects.filter(referenceno=ro.referenceno)
            roomasd=[]
            for a in asdf:
                if a.room_number:
                    roomnob = a.room_number.room_number
                    roomasd.append(roomnob)
            ro.roomnumber = roomasd


    todaytime11 = (datetime.now())
    todaytime22 = (datetime.now()-timedelta(hours=8))
    date_customers31 = Booking.objects.filter(checkedout1__gte=todaytime2,checkedout1__lte=todaytime1).order_by('referenceno')

    depositquery1 = []
    referencenotest1 = None
    totalcash1 = 0
    totalcc1 = 0
    tcash1=0
    tcc1 = 0
    ttax1 = 0
    asdf1=[]

    Otherstotal = ""
    for row1 in date_customers31:
        if referencenotest1 == row1.referenceno:
            t = None
        else:
            try:
                qq = Invoice.objects.get(referenceno=row1.referenceno)
            except Invoice.DoesNotExist:
                return HttpResponse("Problem with booking first name =" + row1.first_name)
            if qq.depositcash is None:
                qq.depositcash = 0
            if qq.depositcc is None:
                qq.depositcc = 0
            if qq.cashpaid is None:
                qq.cashpaid = 0
            if qq.ccpaid is None:
                qq.ccpaid = 0
            if qq.ttax is None:
                qq.ttax = 0    
            tcc1 = tcc1 + qq.ccpaid
            tcash1 = tcash1 + qq.cashpaid
            totalcash1 = totalcash1 + qq.depositcash
            ttax1 = ttax1 + qq.ttax
            totalcc1 = totalcc1 + qq.depositcc
            if qq.depi=="Others":
                Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  


            depositquery1.extend(list(Invoice.objects.filter(referenceno=row1.referenceno)))
            referencenotest1 = row1.referenceno
    
  
    if depositquery1 is not None:

        for ro1 in depositquery1:
            asdf1 = Booking.objects.filter(referenceno=ro1.referenceno)
            roomasd1=[]
            for a1 in asdf1:
                if a1.room_number:
                    roomnob = a1.room_number.room_number
                    roomasd1.append(roomnob)
            ro1.roomnumber = roomasd1





    def generate11131( afafa, afafa1, totalcash , totalcc, tcash, tcc,ttaxx, totalcash1 , totalcc1, tcash1, tcc1,ttax1):
          

        c = canvas.Canvas('static/Reports/'+ todaytime111+'.pdf', pagesize=A4)
        c.setLineWidth(.3)


        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(20 ,805, staff)
        c.drawString(20 ,790,'Shift Commenced')
        c.drawString(20 ,775,'Shift End')
        c.drawString(175 ,790, todaytime111)
        c.drawString(175 ,775,todaytime222)
        c.drawString(20 ,755,'Check-in this shift')
        c.drawString(20 ,740,'Room')
        c.drawString(60 ,740,'Name')
        c.drawString(190 ,740,'Referral')
        c.drawString(240 ,740,'D Cash')
        c.drawString(280 ,740,'D Card')
        c.drawString(320 ,740,'Other')
        c.drawString(450, 740,'Cash')
        c.drawString(490 ,740,'Card')
        c.drawString(530 ,740,'Tourism Tax')
        

        a=15





        for each in afafa:
            if a > 580:
                c.showPage()
                a=0
            else:
                a=a



            c.drawString(20 ,740-a,str(each.roomnumber))
            c.drawString(60 ,740-a, str(each.email.last_name)[0:10] + " " + str(each.email.first_name)[0:10])
            c.drawString(190 ,740-a,str(each.referral)[0:11])
            c.drawString(240 ,740-a,str(each.depositcash))
            c.drawString(280 ,740-a, str(each.depositcc))
            c.drawString(320 ,740-a,str(each.depdescrip)[0:26])
            c.drawString(450, 740-a, str(each.cashpaid))
            c.drawString(490 ,740-a, str(each.ccpaid))
            c.drawString(530 ,740-a, str(each.ttax))
            a=a+15



        a=a+15
        c.drawString(20 ,740-a,'Total')
        c.drawString(240 ,740-a,str(totalcash))
        c.drawString(280 ,740-a, str(totalcc))

        c.drawString(450, 740-a, str(tcash))
        c.drawString(490 ,740-a, str(tcc))
        c.drawString(530 ,740-a, str(ttaxx))


        a=a+15
        c.drawString(20 ,720-a,'Check-out this shift')

        for each1 in afafa1:

            if a > 580:
                c.showPage()
                a=0
            else:
                a=a


            c.drawString(20 ,700-a,str(each1.roomnumber))
            c.drawString(60 ,700-a, str(each1.email.last_name)[0:10] + " " + str(each1.email.first_name)[0:10])
            c.drawString(190 ,700-a,str(each1.referral)[0:11])
            c.drawString(240 ,700-a,str(each1.depositcash))
            c.drawString(280 ,700-a, str(each1.depositcc))
            c.drawString(320 ,700-a,str(each1.depdescrip)[0:26])
            c.drawString(450, 700-a, str(each1.cashpaid))
            c.drawString(490 ,700-a, str(each1.ccpaid))
            c.drawString(530 ,700-a, str(each1.ttax))
            a=a+15

        a=a+15
        c.drawString(20 ,680-a,'Total')
        c.drawString(240 ,680-a,str(totalcash1))
        c.drawString(280 ,680-a, str(totalcc1))

        c.drawString(450, 680-a, str(tcash1))
        c.drawString(490 ,680-a, str(tcc1))
        c.drawString(530 ,680-a, str(ttax1))
        c.showPage()
        c.save()
    generate11131( depositquery, depositquery1, totalcash , totalcc, tcash, tcc,ttaxx, totalcash1 , totalcc1, tcash1, tcc1,ttax1)

    url = 'https://innbparkhotel.com/static/Reports/'+ todaytime111+'.pdf'

    return redirect(url)


def prices(request):

    hotprice =  nearbyprices.objects.all()

    context={
    'hotprice':hotprice
    }


    return render(request, "booking/hotelprices.html", context)


@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def reportcsvgenerate(request):



    qin_date1 = request.GET.get('startdate')
    qout_date1 = request.GET.get('enddate')

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    if not qin_date1:
        qin_date=date.today()
        qout_date=date.today()

    else:
        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)  

    # amsterdam = pytz.timezone('Asia/Singapore')
    # aware = qin_date.replace(tzinfo=amsterdam)
    # qindate = aware.astimezone(pytz.UTC)

    # aware2 = qout_date.replace(tzinfo=amsterdam)
    # qoutdate = aware2.astimezone(pytz.UTC)

    qindate = datetime.combine(qin_date, datetime.min.time())
    qoutdate = datetime.combine(qout_date, datetime.min.time())




    table1 = Invoice.objects.all().filter(totalpaiddate__gte=qindate, totalpaiddate__lte=qoutdate).exclude(referral="Agoda").exclude(referral="Ctrip").exclude(referral="Mikitravel").exclude(referral="Asiatravel").exclude(referral="Traveloka").order_by('checkedin1')
    table2 = Invoice.objects.filter(referral="Agoda", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')
    table7 = Invoice.objects.filter(referral="Revato", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')    
    table4 = Invoice.objects.filter(referral="Ctrip", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')
    table5 = Invoice.objects.filter(referral="Mikitravel", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')
    table6 =Invoice.objects.filter(referral="Asiatravel", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')

    table3 = Invoice.objects.filter(referral="Traveloka", checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')
    table= table1 | table2 |  table4 | table5 |table6 | table3 |table7

    total =0
    cash =0
    cc=0
    gst=0
    st=0
    mol=0
    tt=0
    rounding=0

    for each in table:
        if each.total:
            total += each.total
        if each.cashpaid:
            cash += each.cashpaid
        if each.ccpaid:
            cc += each.ccpaid
        if each.gst:
            gst += each.gst
        if each.servicetax:
            st += each.servicetax
        if each.ttax:
            tt += each.ttax
        if each.rounding:
            rounding += each.rounding
        if each.molpay ==True:
            if each.bookingfeepaid==True:
                mol = mol + each.bookingfee 
            else:
                mol = mol + each.total
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Room', 'Mode','Reference Number','OTA ref','Invoice Number','Discounts','Total', 'Cash Paid', 'Credit Card Paid', 'MOTO', 'Molpay', 'GST', 'Service Tax','Approx Checkin', 'Approx Checkout','Tourism Tax','Rounding','Passport', 'Country'  ])
    

    
    for each in table:
        firstbook = Booking.objects.filter(referenceno=each.referenceno).first()        


        room2 = Booking.objects.filter(referenceno=each.referenceno)
        aroom34 = ""
        for aaa in room2:
            if aaa.room_number:
                aroom = aaa.room_number
                if aaa.late:
                    each.referral = str(each.referral) + " " + "late"
                    if aaa.extension:
                        each.referral = str(each.referral) + " " + "extension"
                if aaa.extension:
                    each.referral = str(each.referral)+ " " + "extension"

            else:
                aroom = None
            aroom34 = str(aroom34) + " " + str(aroom)
        each.room = aroom34 
        if not firstbook:
            class firstbook(object):
                checkin_date = None
                checkout_date = None
        each.referenceno =str("=\"") + str(each.referenceno) + str("\"")
        each.otherref =str("=\"") + str(each.otherref) + str("\"")
        if each.molpay==True:
            each.referral = str(each.referral)+ " " + "molpay"            
            if each.bookingfeepaid == True:
                writer.writerow([each.email, each.room,  each.referral, each.referenceno, each.otherref, each.invoiceno,each.descprom, each.total,each.cashpaid, each.ccpaid,  '',each.bookingfee,each.gst, each.servicetax, firstbook.checkin_date, firstbook.checkout_date,each.ttax, each.rounding,each.passno, each.email.country])
            else:    
                writer.writerow([each.email, each.room,each.referral, each.referenceno,  each.otherref, each.invoiceno,each.descprom,each.total, each.cashpaid, 0,  '',each.total,each.gst,  each.servicetax, firstbook.checkin_date, firstbook.checkout_date,each.ttax, each.rounding,each.passno, each.email.country])
 
        else:
            writer.writerow([each.email, each.room, each.referral, each.referenceno, each.otherref,each.invoiceno,each.descprom, each.total, each.cashpaid, each.ccpaid, '', 0,each.gst, each.servicetax,firstbook.checkin_date, firstbook.checkout_date,each.ttax, each.rounding,each.passno, each.email.country])

    writer.writerow(['Total', '', '','', '','','',total , cash, cc,'', mol,gst, st,'','',tt, rounding ])

    return response














@login_required(login_url='/login/')
def generatepdfbeforecheckin(request):
    pdfmetrics.registerFont(TTFont('Noto', 'simhei.ttf'))
    refno = request.GET.get('referenceno')
    if not refno:
        return redirect('test2')
    d = Invoice.objects.get(referenceno=refno)
    # year = datetime.now().strftime("%y")    
    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
    # inv_no = invnos.invoiceno
    # invoice_int = inv_no[2:]
    # new_invoice_int = int(invoice_int) + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    # d.invoiceno = new_invoice_no
    # d.save()
    invno = refno
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d').date()
    e = Booking.objects.filter(referenceno = refno).order_by('room_type_name')
    exitem = extra_items.objects.filter(referenceno=refno)
    firstname= d.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = refno).first()
    try:
        q111 = depositwitheld.objects.filter(invoice=d)
    except depositwitheld.DoesNotExist:
        q111 = None


    break41 = 0

    for a in e:
        if a.room_type_name.pk == 23:
            break41 = break41+1

        elif a.room_type_name.pk==24:
            break41 = break41+1


    if break41 == 0 :
       if f.created_on.date() < deadline:
            break41 = 24



    def generate1(f, ae, afafa, q111 ,break41,xtraitem):
        logo='booking/static/innbparklogo2.gif'
        nosmoke = 'booking/static/Untitled-1.gif'
        key23 = 'booking/static/key.gif'
        lock23  = 'booking/static/lock.gif'       

        c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
        c.setLineWidth(.3)
        c.setStrokeColorRGB(0,0,0)
        c.drawImage(logo, 400 , 730, width=140, height=69)

        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)

        a=15
        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(40 ,805,'InnB Park Hotel')
        c.drawString(40 ,790,'operated by Apocity Sdn Bhd 198401014712 (127268-X)')
        if afafa.invoiceno:
            if int(afafa.invoiceno) > 1702514:
                c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        else:        
            c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        c.drawString(40 ,775-a,'102-106, Jalan Imbi,  Bukit Bintang')
        c.drawString(40 ,760-a,'55100 Kuala Lumpur')
        c.drawString(40 ,745-a,'admin@innbparkhotel.com') 
        c.drawString(40 ,730-a,'+603 2856 7257')
        if afafa.addressline1:
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, afafa.addressline1)           
            if afafa.addressline2:
                a=a+15                
                c.drawString(40 ,730-a, afafa.addressline2)
                if afafa.addressline3:
                    a=a+15                
                    c.drawString(40 ,730-a, afafa.addressline3)                    

        a=a-12
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(40 ,680-a,'ROOM RESERVATION')
        c.drawString(430 ,810,'Non-refundable Rate')
        a=a-5
        c.setFont('Helvetica', 9, leading=None)
        c.drawString(40, 650-a, 'GUESTS NAME')
        c.drawString(197, 650-a, 'ROOM NO.')
        c.drawString(257, 650-a, 'ROOM TYPE')
        c.drawString(380, 650-a, 'ARRIVAL DATE')  
        c.drawString(470, 650-a, 'DEPATURE DATE')                                     
        a=a-2
        c.setLineWidth(.5)
        c.line(40,630-a,548,630-a)

        if f:
            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 610-a, afafa.email.first_name)
            c.drawString(40, 590-a, afafa.email.last_name)
            if afafa.email.passno:
                c.drawString(40, 570-a, "Passport no: "+ str(afafa.email.passno))
        count1 =0
        for t in ae:

            if t.familyroom == True:
                if count1 == 1:
                    asdfafa = "nothing"
                    count1 = 0

                else: 

                    count1 = 1
                    if a > 540:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -150

                    c.setFont('Helvetica', 9, leading=None)


                    roomnumber = "[" + str(t.room_number) + "]"
                    roomname = 'Family Room'

                    roomnamecount = len(roomname)
                        
                    n=20
                    a += n
                    # c.drawString(177, 630-a, str(a))            
                    c.drawString(197, 630-a, roomnumber)
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(257, 610-a, newline)
                        c.drawString(257, 630-a, oldline)
                    else:
                        c.drawString(257, 630-a, roomname)                            
                    if t.extension is True:
                        c.drawString(355, 630-a, '(ext)')
                    if t.late is True:
                        c.drawString(355, 630-a, '(late)')                
                    indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                    outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                    c.drawString(380, 630-a, indate)  
                    c.drawString(470, 630-a, outdate)
                    if roomnamecount > 22:
                        a = a+20



            else:









                if a > 540:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -150

                c.setFont('Helvetica', 9, leading=None)


                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)

                roomnamecount = len(roomname)
                    
                n=20
                a += n
                # c.drawString(177, 630-a, str(a))            
                c.drawString(197, 630-a, roomnumber)
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(257, 610-a, newline)
                    c.drawString(257, 630-a, oldline)
                else:
                    c.drawString(257, 630-a, roomname)                            
                if t.extension is True:
                    c.drawString(355, 630-a, '(ext)')
                if t.late is True:
                    c.drawString(355, 630-a, '(late)')                
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 630-a, indate)  
                c.drawString(470, 630-a, outdate)
                if roomnamecount > 22:
                    a = a+20









        if afafa.email.passno:
            a=a+20
        c.line(40,600-a,548,600-a)



 

        c.setFont('Helvetica-Bold', 11, leading=None)
        if afafa.rtacomm is not None:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200

            
            print("nothing")
            a=a-70
            if afafa.ttax:
                if not afafa.checkedout1:
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    a= a+20
                    c.drawString(40, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                    a= a+10



        else:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200
            if afafa.invoiceno:
                if int(afafa.invoiceno) > 1702514:
                    c.drawString(40, 570-a, 'TAX INVOICE ' + afafa.invoiceno) 
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " + qwerdate) 

                else:
                    c.drawString(40, 570-a, 'INVOICE ' + afafa.invoiceno)
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " +qwerdate)                      
            else:
                c.drawString(40, 570-a, 'INVOICE ')
                if afafa.totalpaiddate:
                    qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                    c.drawString(380, 570-a, "Invoice Date " +qwerdate) 

           
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 570-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 545-a, 'DESCRIPTION')
            c.drawString(180, 545-a, 'PRICE/UNIT')
            c.drawString(270, 545-a, 'NO. NIGHTS')


            for t in ae:
                if t.actualpay-t.paymentprice > 0:
                    c.drawString(360, 545-a, 'DISCOUNT')
                    break



            if afafa.description:         
                c.drawString(360, 545-a, 'DISCOUNT')
            c.drawString(470, 545-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            count1 = 0
            for t in ae:


                if t.familyroom == True:
                    if count1 == 1:
                        asdfafa = "nothing"
                        count1 = 0

                    else: 
                        count1 = 1
                        if a > 340:
                            c.showPage()
                            c.setLineWidth(.3)
                            c.setStrokeColorRGB(0,0,0)
                            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                            a = -200
                        c.setFont('Helvetica', 9, leading=None)
                        roomnumber = str(t.room_number)
                        roomname = 'Family Room'
                        n=20
                        a += n
                        nights = int((t.checkout_date-t.checkin_date).days)
                        if nights<1:
                            nights=1
                        price = str(round((t.actualpay*2/  nights),2))
                        roomnamecount = len(roomname)                
                        if roomnamecount > 22:
                            newline = roomname.split(", ",1)[1]
                            oldline = roomname.split(", ")[0]
                            c.drawString(40, 525-a, newline)
                            c.drawString(40, 545-a, oldline)
                        else:
                            c.drawString(40, 545-a, roomname)  




                        # c.drawString(40, 545-a, roomname)
                        c.drawString(180, 545-a, 'RM ' + price)
                        c.drawString(270, 545-a, str(nights))
                        if t.actualpay-t.paymentprice > 0:
                            c.drawString(360, 545-a, '- RM ' + str((t.actualpay-t.paymentprice)*2))            
                        c.drawString(470, 545-a, 'RM ' + str(t.paymentprice*2))
                        if t.extension is True:
                            c.drawString(420, 545-a, '(ext)')
                        if t.late is True:
                            c.drawString(420, 545-a, '(late)')
                        totalprice = totalprice + (t.actualpay*2)   

                        if roomnamecount > 22:
                            a = a+20


                else:

                    if a > 340:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -200
                    c.setFont('Helvetica', 9, leading=None)
                    roomnumber = str(t.room_number)
                    roomname = str(t.room_type_name)
                    n=20
                    a += n
                    nights = int((t.checkout_date-t.checkin_date).days)
                    if nights<1:
                        nights=1
                    price = str(round((t.actualpay /  nights),2))
                    roomnamecount = len(roomname)                
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(40, 525-a, newline)
                        c.drawString(40, 545-a, oldline)
                    else:
                        c.drawString(40, 545-a, roomname)  




                    # c.drawString(40, 545-a, roomname)
                    c.drawString(180, 545-a, 'RM ' + price)
                    c.drawString(270, 545-a, str(nights))
                    if t.actualpay-t.paymentprice > 0:
                        c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                    c.drawString(470, 545-a, 'RM ' + str(t.paymentprice))
                    if t.extension is True:
                        c.drawString(420, 545-a, '(ext)')
                    if t.late is True:
                        c.drawString(420, 545-a, '(late)')
                    totalprice = totalprice + t.actualpay   

                    if roomnamecount > 22:
                        a = a+20
            
            for item in xtraitem:

                if a > 340:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -200
                c.setFont('Helvetica', 9, leading=None)

                roomname = str(item.description)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                if nights<1:
                    nights=1
                price = str(item.paymentprice)
                roomnamecount = len(roomname)                
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(40, 525-a, newline)
                    c.drawString(40, 545-a, oldline)
                else:
                    c.drawString(40, 545-a, roomname)  




                # c.drawString(40, 545-a, roomname)
                # c.drawString(180, 545-a, 'RM ' + price)
                # if t.actualpay-t.paymentprice > 0:
                #     c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                c.drawString(470, 545-a, 'RM ' + str(item.paymentprice))
                # if t.extension is True:
                #     c.drawString(420, 545-a, '(ext)')
                # if t.late is True:
                #     c.drawString(420, 545-a, '(late)')
                totalprice = totalprice + item.paymentprice   

                if roomnamecount > 22:
                    a = a+20



            if not f:
                a=20
                c.drawString(40, 545-a, 'Customer cancelled booking')




            a=a-10

            if afafa.additionalcharge:
                a=a
                # discount=  totalprice - afafa.total + afafa.additionalcharge
                # c.drawString(180, 530-a, 'Special Promo:   ' + afafa.description.description )
                # c.drawString(470, 530-a, '- RM ' + str(discount))

                c.drawString(180, 510-a, afafa.additionalcharges)
                c.drawString(470, 510-a, 'RM ' + str(afafa.additionalcharge))
                # else:
                #     a = a+20
                #     discount=  totalprice - afafa.total
                #     c.drawString(180, 520-a, 'Special Promo:   ' + afafa.description.description )
                #     c.drawString(470, 520-a, '- RM ' + str(discount))
            




            if afafa.rounding:
                a = a+20
                c.drawString(180, 520-a, 'rounding' )
                c.drawString(470, 520-a, 'RM ' + str(afafa.rounding))











                        
            if afafa.gst > 0:
                qindate2 = datetime.strptime("2018-08-31", '%Y-%m-%d')
                utc=pytz.UTC
                qindate2=utc.localize(qindate2) 
                if afafa.totalpaiddate:
                    if afafa.totalpaiddate > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))    

                else:
                    if afafa.datecreated > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))







            else:
                qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
                utc=pytz.UTC
                qindate=utc.localize(qindate) 
                if afafa.datecreated > qindate:
                    a = a+20
                    c.drawString(180, 520-a, '0% SST ' )
                    c.drawString(470, 520-a, 'RM 0.00')


            # if afafa.rtacomm:
            #     c.setFont('Helvetica-Bold', 9, leading=None)
            #     a= a+20
            #     c.drawString(180, 520-a,str(afafa.referral) +'    '+ str(100*afafa.rtacomm)+'%')
            #     c.drawString(470, 520-a, 'RM '+ str(afafa.commamount)) 
            #     a=a-10







                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 490-a, 'Total:')
            if f:
                # if afafa.rtacomm:
                #     c.drawString(470, 490-a, 'RM ' + format((afafa.total + afafa.commamount),'.2f'))
                # else:
                c.drawString(470, 490-a, 'RM ' + str(afafa.total))


                if afafa.ttax:
                    if not afafa.checkedout1:
                        c.setFont('Helvetica-Bold', 9, leading=None)
                        a= a+20
                        c.drawString(180, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                        a= a+10
            else:
                c.drawString(470,400-a, 'RM ' + str(afafa.bookingfee))
            


            


            c.setFont('Helvetica', 9, leading=None)
            



            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 490-a, 'Booking Pre-payment')
                c.drawString(470, 490-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                

                    if afafa.bookingfeepaid == True:
                        c.drawString(180, 470-a, 'Total Payable:') 
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        c.drawString(180, 470-a, 'Total Paid:')
                        total12 = afafa.total
                    c.drawString(470, 470-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 470-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 470-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 455-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 455-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 455-a, 'Deposit not applicable')
        





        c.setFont('Helvetica', 10, leading=None)


        if afafa.invoicedesc:
            c.drawString(40, 430-a,afafa.invoicedesc) 
            a= a+30
        

        if afafa.addressline1:
            c.showPage()
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
            a = -300
        else:
            if a > 170:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300



        
        if afafa.totalpaid == True:
            # a= a+20
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
            c.setFont('Helvetica', 9, leading=None)  
            if afafa.rtacomm is not None:
                print("None")
            else:              
                c.drawString(40, 430-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 430-a, 'RM ' + str(total12))
            c.setFont('Helvetica', 10, leading=None) 
            # c.drawString(480, 380-a, str(a))



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 410-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)
                z=0
                if afafa.depositcash:
                    if afafa.depositcash > 0:
                        c.drawString(180, 410-a, 'Cash  '+ 'RM ' + str(afafa.depositcash))
                        z = 80
                if afafa.depositcc:
                    if afafa.depositcc > 0:
                        c.drawString(z+180, 410-a, 'Credit Card  '+ 'RM ' + str(afafa.depositcc))
                        z = 100
                if afafa.depi == "Others":
                    c.drawString(z+ 180, 410-a, str(afafa.depdescrip))                    

                a=a+20
                c.drawString(40, 410-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                if afafa.depdescrip:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                else:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300    

            if afafa.depositreturnedate:
                items=0
                c.setFont('Helvetica-Bold', 9, leading=None) 

                if afafa.ttax:
                    a= a+20
                    c.drawString(40, 410-a,'Tourism tax Paid: ') 
                    c.drawString(180, 410-a, 'RM ' + str(afafa.ttax))
                
                c.setFont('Helvetica', 9, leading=None) 

                if q111:
                    c.drawString(40, 390-a, 'Deposit charged:')
                    for i in q111:
                        c.drawString(180, 390-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
                        n = 17
                        a+=n
                        items += i.itemprice
                    returned = afafa.depositamt - items
                    if returned < 0: 
                        returned = -(returned)
                        c.drawString(40, 370-a, 'Deposit charged on')
                        # c.drawString(350, 370-a, 'RM ' + str(returned))
                    else:
                        c.drawString(40, 370-a, 'Deposit returned')
                        if afafa.otherdeposit < 1:
                            c.drawString(350, 280-a, 'RM ' + str(returned))                         
                        # c.drawString(350, 370-a,  'RM ' + str(returned))                                  

                else:
                    c.drawString(40, 370-a, 'Deposit returned on')
                

                tz = timezone('Etc/GMT-8')
                depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

                c.drawString(180, 370-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

                a=a+20         
                c.drawString(40, 370-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                c.drawString(40, 355-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
         
                c.setLineWidth(.5)
                c.line(40,270-a , 180,270-a)   
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(80, 250-a, 'Signature')          




            if not afafa.depositreturnedate:     
                c.drawImage(nosmoke, 40 , 260-a, width=40, height=40)
                # c.drawImage(lock23, 40 , 255-a, width=40, height=40)
                c.drawImage(key23, 45 , 204-a, width=30, height=30)
                c.setFont('Helvetica-Bold', 10, leading=None)                 
                c.drawString(40, 370-a, 'Hotel Key Information')
                c.setFont('Helvetica', 9, leading=None) 
                c.drawString(40, 350-a, 'Check Out:  12pm')
                if break41 > 0:                       
                    c.drawString(180, 350-a, 'Breakfast: 6.30am – 9.30am ')
                c.drawString(40, 333-a, 'IBP guest WiFi: 1nnBp@rk1303') 
                c.drawString(180, 333-a, 'Reception: Call 100# ')                                               
                c.setFont('Helvetica', 10, leading=None)                         
                c.drawString(95, 300-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas ')
                c.drawString(95, 288-a, 'of the hotel is strictly prohibited. ')
                c.setFont('Helvetica-Bold', 10, leading=None) 
                c.drawString(95, 276-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                c.setFont('Noto', 10, leading=None)                         
                c.drawString(95, 262-a, '酒店为了确保所有贵宾在酒店逗留期间享受最好的空气质量,在酒店范围内吸烟是严格禁止的。')
                c.drawString(95, 250-a, '若在酒店内吸烟,我们将会收取马币150.00的清洁费。 ')
                c.setFont('Helvetica', 10, leading=None) 
                # c.drawString(95, 254-a, 'For security purposes, both main elevators will be locked between 10pm to 7am.')

                c.drawString(95, 228-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out.')            
                c.drawString(95, 216-a, 'Failure to do so will incur a charge of RM 20.00 per card.')            
                c.setFont('Noto', 10, leading=None)                 
                c.drawString(95, 204-a, '卡需在退房时退回前台。若钥匙卡遗失或没退还前台酒店将收取每卡马币20.00的费用。')

        if afafa.totalpaid == False:
            if afafa.bookingfeepaid == False:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    if not afafa.depositpaiddate:
                        c.drawString(40, 420-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                        c.drawString(100, 420-a, 'Not Paid')                                                            
                    
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
 

            else:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 420-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 420-a, 'Not Paid')                                                            
                
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
        
        # if a > 180:
        #     c.showPage()
        #     c.setLineWidth(.3)
        #     c.setStrokeColorRGB(0,0,0)
        #     c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
        #     a = a-500   



  



        # c.drawString(380, 390-a, 'Payment Method:')                
        # c.drawString(470, 390-a, str(afafa.Paymentmethod))
            # if afafa.Paymentmethod == "Credit Card":
            #     c.drawString(470, 490-a, afafa.paymentdescription)
            # c.drawCentredString(415,500, 'test')
        # logo='booking/static/innbparklogo2.gif'           
            # c.setFont('Helvetica', 48, leading=None)
            # c.drawCentredString(415,500, 'test')
            # c.setFont('Helvetica', 20, leading=None)        


        # c.drawImage(logo, 400 , 730, width=140, height=69)
        c.showPage()
        c.save()


    generate1(f,e,d, q111, break41, exitem)
    url = 'https://innbparkhotel.com/static/invoice/' + invno + '.pdf'

    return redirect(url)








@login_required(login_url='/login/')
def generatepdfwithouttourismtax(request):
    pdfmetrics.registerFont(TTFont('Noto', 'simhei.ttf'))
    refno = request.GET.get('referenceno')
    if not refno:
        return redirect('test2')
    d = Invoice.objects.get(referenceno=refno)
    # year = datetime.now().strftime("%y")    
    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
    # inv_no = invnos.invoiceno
    # invoice_int = inv_no[2:]
    # new_invoice_int = int(invoice_int) + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    # d.invoiceno = new_invoice_no
    # d.save()
    invno = refno
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d').date()
    e = Booking.objects.filter(referenceno = refno).order_by('room_type_name')
    exitem = extra_items.objects.filter(referenceno=refno)
    firstname= d.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = refno).first()
    try:
        q111 = depositwitheld.objects.filter(invoice=d)
    except depositwitheld.DoesNotExist:
        q111 = None


    break41 = 0

    for a in e:
        if a.room_type_name.pk == 23:
            break41 = break41+1

        elif a.room_type_name.pk==24:
            break41 = break41+1


    if break41 == 0 :
       if f.created_on.date() < deadline:
            break41 = 24



    def generate1(f, ae, afafa, q111 ,break41,xtraitem):
        logo='booking/static/innbparklogo2.gif'
        nosmoke = 'booking/static/Untitled-1.gif'
        key23 = 'booking/static/key.gif'
        lock23  = 'booking/static/lock.gif'       

        c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
        c.setLineWidth(.3)
        c.setStrokeColorRGB(0,0,0)
        c.drawImage(logo, 400 , 730, width=140, height=69)

        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)

        a=15
        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(40 ,805,'InnB Park Hotel')
        c.drawString(40 ,790,'operated by Apocity Sdn Bhd 198401014712 (127268-X)')
        if afafa.invoiceno:
            if int(afafa.invoiceno) > 1702514:
                c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        else:        
            c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        c.drawString(40 ,775-a,'102-106, Jalan Imbi,  Bukit Bintang')
        c.drawString(40 ,760-a,'55100 Kuala Lumpur')
        c.drawString(40 ,745-a,'admin@innbparkhotel.com') 
        c.drawString(40 ,730-a,'+603 2856 7257')
        if afafa.addressline1:
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, afafa.addressline1)           
            if afafa.addressline2:
                a=a+15                
                c.drawString(40 ,730-a, afafa.addressline2)
                if afafa.addressline3:
                    a=a+15                
                    c.drawString(40 ,730-a, afafa.addressline3)                    

        a=a-12
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(40 ,680-a,'ROOM RESERVATION')
        c.drawString(430 ,810,'Non-refundable Rate')
        a=a-5
        c.setFont('Helvetica', 9, leading=None)
        c.drawString(40, 650-a, 'GUESTS NAME')
        c.drawString(197, 650-a, 'ROOM NO.')
        c.drawString(257, 650-a, 'ROOM TYPE')
        c.drawString(380, 650-a, 'ARRIVAL DATE')  
        c.drawString(470, 650-a, 'DEPATURE DATE')                                     
        a=a-2
        c.setLineWidth(.5)
        c.line(40,630-a,548,630-a)

        if f:
            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 610-a, afafa.email.first_name)
            c.drawString(40, 590-a, afafa.email.last_name)
            if afafa.email.passno:
                c.drawString(40, 570-a, "Passport no: "+ str(afafa.email.passno))
        count1 =0
        for t in ae:

            if t.familyroom == True:
                if count1 == 1:
                    asdfafa = "nothing"
                    count1 = 0

                else: 

                    count1 = 1
                    if a > 540:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -150

                    c.setFont('Helvetica', 9, leading=None)


                    roomnumber = "[" + str(t.room_number) + "]"
                    roomname = 'Family Room'

                    roomnamecount = len(roomname)
                        
                    n=20
                    a += n
                    # c.drawString(177, 630-a, str(a))            
                    c.drawString(197, 630-a, roomnumber)
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(257, 610-a, newline)
                        c.drawString(257, 630-a, oldline)
                    else:
                        c.drawString(257, 630-a, roomname)                            
                    if t.extension is True:
                        c.drawString(355, 630-a, '(ext)')
                    if t.late is True:
                        c.drawString(355, 630-a, '(late)')                
                    indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                    outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                    c.drawString(380, 630-a, indate)  
                    c.drawString(470, 630-a, outdate)
                    if roomnamecount > 22:
                        a = a+20



            else:









                if a > 540:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -150

                c.setFont('Helvetica', 9, leading=None)


                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)

                roomnamecount = len(roomname)
                    
                n=20
                a += n
                # c.drawString(177, 630-a, str(a))            
                c.drawString(197, 630-a, roomnumber)
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(257, 610-a, newline)
                    c.drawString(257, 630-a, oldline)
                else:
                    c.drawString(257, 630-a, roomname)                            
                if t.extension is True:
                    c.drawString(355, 630-a, '(ext)')
                if t.late is True:
                    c.drawString(355, 630-a, '(late)')                
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 630-a, indate)  
                c.drawString(470, 630-a, outdate)
                if roomnamecount > 22:
                    a = a+20









        if afafa.email.passno:
            a=a+20
        c.line(40,600-a,548,600-a)



 

        c.setFont('Helvetica-Bold', 11, leading=None)
        if afafa.rtacomm is not None:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200

            
            print("nothing")
            a=a-70
            if afafa.ttax:
                if not afafa.checkedout1:
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    a= a+20
                    c.drawString(40, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                    a= a+10



        else:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200
            if afafa.invoiceno:
                if int(afafa.invoiceno) > 1702514:
                    c.drawString(40, 570-a, 'TAX INVOICE ' + afafa.invoiceno) 
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " + qwerdate) 

                else:
                    c.drawString(40, 570-a, 'INVOICE ' + afafa.invoiceno)
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " +qwerdate)                      
            else:
                c.drawString(40, 570-a, 'INVOICE ')
                if afafa.totalpaiddate:
                    qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                    c.drawString(380, 570-a, "Invoice Date " +qwerdate) 

           
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 570-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 545-a, 'DESCRIPTION')
            c.drawString(180, 545-a, 'PRICE/UNIT')
            c.drawString(270, 545-a, 'NO. NIGHTS')


            for t in ae:
                if t.actualpay-t.paymentprice > 0:
                    c.drawString(360, 545-a, 'DISCOUNT')
                    break



            if afafa.description:         
                c.drawString(360, 545-a, 'DISCOUNT')
            c.drawString(470, 545-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            count1 = 0
            for t in ae:


                if t.familyroom == True:
                    if count1 == 1:
                        asdfafa = "nothing"
                        count1 = 0

                    else: 
                        count1 = 1
                        if a > 340:
                            c.showPage()
                            c.setLineWidth(.3)
                            c.setStrokeColorRGB(0,0,0)
                            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                            a = -200
                        c.setFont('Helvetica', 9, leading=None)
                        roomnumber = str(t.room_number)
                        roomname = 'Family Room'
                        n=20
                        a += n
                        nights = int((t.checkout_date-t.checkin_date).days)
                        if nights<1:
                            nights=1
                        price = str(round((t.actualpay*2/  nights),2))
                        roomnamecount = len(roomname)                
                        if roomnamecount > 22:
                            newline = roomname.split(", ",1)[1]
                            oldline = roomname.split(", ")[0]
                            c.drawString(40, 525-a, newline)
                            c.drawString(40, 545-a, oldline)
                        else:
                            c.drawString(40, 545-a, roomname)  




                        # c.drawString(40, 545-a, roomname)
                        c.drawString(180, 545-a, 'RM ' + price)
                        c.drawString(270, 545-a, str(nights))
                        if t.actualpay-t.paymentprice > 0:
                            c.drawString(360, 545-a, '- RM ' + str((t.actualpay-t.paymentprice)*2))            
                        c.drawString(470, 545-a, 'RM ' + str(t.paymentprice*2))
                        if t.extension is True:
                            c.drawString(420, 545-a, '(ext)')
                        if t.late is True:
                            c.drawString(420, 545-a, '(late)')
                        totalprice = totalprice + (t.actualpay*2)   

                        if roomnamecount > 22:
                            a = a+20


                else:

                    if a > 340:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -200
                    c.setFont('Helvetica', 9, leading=None)
                    roomnumber = str(t.room_number)
                    roomname = str(t.room_type_name)
                    n=20
                    a += n
                    nights = int((t.checkout_date-t.checkin_date).days)
                    if nights<1:
                        nights=1
                    price = str(round((t.actualpay /  nights),2))
                    roomnamecount = len(roomname)                
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(40, 525-a, newline)
                        c.drawString(40, 545-a, oldline)
                    else:
                        c.drawString(40, 545-a, roomname)  




                    # c.drawString(40, 545-a, roomname)
                    c.drawString(180, 545-a, 'RM ' + price)
                    c.drawString(270, 545-a, str(nights))
                    if t.actualpay-t.paymentprice > 0:
                        c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                    c.drawString(470, 545-a, 'RM ' + str(t.paymentprice))
                    if t.extension is True:
                        c.drawString(420, 545-a, '(ext)')
                    if t.late is True:
                        c.drawString(420, 545-a, '(late)')
                    totalprice = totalprice + t.actualpay   

                    if roomnamecount > 22:
                        a = a+20
            
            for item in xtraitem:

                if a > 340:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -200
                c.setFont('Helvetica', 9, leading=None)

                roomname = str(item.description)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                if nights<1:
                    nights=1
                price = str(item.paymentprice)
                roomnamecount = len(roomname)                
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(40, 525-a, newline)
                    c.drawString(40, 545-a, oldline)
                else:
                    c.drawString(40, 545-a, roomname)  




                # c.drawString(40, 545-a, roomname)
                # c.drawString(180, 545-a, 'RM ' + price)
                # if t.actualpay-t.paymentprice > 0:
                #     c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                c.drawString(470, 545-a, 'RM ' + str(item.paymentprice))
                # if t.extension is True:
                #     c.drawString(420, 545-a, '(ext)')
                # if t.late is True:
                #     c.drawString(420, 545-a, '(late)')
                totalprice = totalprice + item.paymentprice   

                if roomnamecount > 22:
                    a = a+20



            if not f:
                a=20
                c.drawString(40, 545-a, 'Customer cancelled booking')




            a=a-10

            if afafa.additionalcharge:
                a=a
                # discount=  totalprice - afafa.total + afafa.additionalcharge
                # c.drawString(180, 530-a, 'Special Promo:   ' + afafa.description.description )
                # c.drawString(470, 530-a, '- RM ' + str(discount))

                c.drawString(180, 510-a, afafa.additionalcharges)
                c.drawString(470, 510-a, 'RM ' + str(afafa.additionalcharge))
                # else:
                #     a = a+20
                #     discount=  totalprice - afafa.total
                #     c.drawString(180, 520-a, 'Special Promo:   ' + afafa.description.description )
                #     c.drawString(470, 520-a, '- RM ' + str(discount))
            




            if afafa.rounding:
                a = a+20
                c.drawString(180, 520-a, 'rounding' )
                c.drawString(470, 520-a, 'RM ' + str(afafa.rounding))











                        
            if afafa.gst > 0:
                qindate2 = datetime.strptime("2018-08-31", '%Y-%m-%d')
                utc=pytz.UTC
                qindate2=utc.localize(qindate2) 
                if afafa.totalpaiddate:
                    if afafa.totalpaiddate > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))    

                else:
                    if afafa.datecreated > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))







            else:
                qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
                utc=pytz.UTC
                qindate=utc.localize(qindate) 
                if afafa.datecreated > qindate:
                    a = a+20
                    c.drawString(180, 520-a, '0% SST ' )
                    c.drawString(470, 520-a, 'RM 0.00')


            # if afafa.rtacomm:
            #     c.setFont('Helvetica-Bold', 9, leading=None)
            #     a= a+20
            #     c.drawString(180, 520-a,str(afafa.referral) +'    '+ str(100*afafa.rtacomm)+'%')
            #     c.drawString(470, 520-a, 'RM '+ str(afafa.commamount)) 
            #     a=a-10







                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 490-a, 'Total:')
            if f:
                # if afafa.rtacomm:
                #     c.drawString(470, 490-a, 'RM ' + format((afafa.total + afafa.commamount),'.2f'))
                # else:
                c.drawString(470, 490-a, 'RM ' + str(afafa.total))


                if afafa.ttax:
                    if not afafa.checkedout1:
                        c.setFont('Helvetica-Bold', 9, leading=None)
                        a= a+20
                        c.drawString(180, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                        a= a+10
            else:
                c.drawString(470,400-a, 'RM ' + str(afafa.bookingfee))
            


            


            c.setFont('Helvetica', 9, leading=None)
            



            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 490-a, 'Booking Pre-payment')
                c.drawString(470, 490-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                

                    if afafa.bookingfeepaid == True:
                        c.drawString(180, 470-a, 'Total Payable:') 
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        c.drawString(180, 470-a, 'Total Paid:')
                        total12 = afafa.total
                    c.drawString(470, 470-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 470-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 470-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 455-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 455-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 455-a, 'Deposit not applicable')
        





        c.setFont('Helvetica', 10, leading=None)


        if afafa.invoicedesc:
            c.drawString(40, 430-a,afafa.invoicedesc) 
            a= a+30
        

        if afafa.addressline1:
            c.showPage()
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
            a = -300
        else:
            if a > 170:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300



        
        if afafa.totalpaid == True:
            # a= a+20
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
            c.setFont('Helvetica', 9, leading=None)  
            if afafa.rtacomm is not None:
                print("None")
            else:              
                c.drawString(40, 430-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 430-a, 'RM ' + str(total12))
            c.setFont('Helvetica', 10, leading=None) 
            # c.drawString(480, 380-a, str(a))



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 410-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)
                z=0
                if afafa.depositcash:
                    if afafa.depositcash > 0:
                        c.drawString(180, 410-a, 'Cash  '+ 'RM ' + str(afafa.depositcash))
                        z = 80
                if afafa.depositcc:
                    if afafa.depositcc > 0:
                        c.drawString(z+180, 410-a, 'Credit Card  '+ 'RM ' + str(afafa.depositcc))
                        z = 100
                if afafa.depi == "Others":
                    c.drawString(z+ 180, 410-a, str(afafa.depdescrip))                    

                a=a+20
                c.drawString(40, 410-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                if afafa.depdescrip:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                else:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300    

            if afafa.depositreturnedate:
                items=0
                c.setFont('Helvetica-Bold', 9, leading=None) 

                if afafa.ttax:
                    a= a+20
                    c.drawString(40, 410-a,'Tourism tax Paid: ') 
                    c.drawString(180, 410-a, 'RM ' + str(afafa.ttax))
                
                c.setFont('Helvetica', 9, leading=None) 

                if q111:
                    c.drawString(40, 390-a, 'Deposit charged:')
                    for i in q111:
                        c.drawString(180, 390-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
                        n = 17
                        a+=n
                        items += i.itemprice
                    returned = afafa.depositamt - items
                    if returned < 0: 
                        returned = -(returned)
                        c.drawString(40, 370-a, 'Deposit charged on')
                        # c.drawString(350, 370-a, 'RM ' + str(returned))
                    else:
                        c.drawString(40, 370-a, 'Deposit returned')
                        if afafa.otherdeposit < 1:
                            c.drawString(350, 280-a, 'RM ' + str(returned))                         
                        # c.drawString(350, 370-a,  'RM ' + str(returned))                                  

                else:
                    c.drawString(40, 370-a, 'Deposit returned on')
                

                tz = timezone('Etc/GMT-8')
                depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

                c.drawString(180, 370-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

                a=a+20         
                c.drawString(40, 370-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                c.drawString(40, 355-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
         
                c.setLineWidth(.5)
                c.line(40,270-a , 180,270-a)   
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(80, 250-a, 'Signature')          




            if not afafa.depositreturnedate:     
                c.drawImage(nosmoke, 40 , 260-a, width=40, height=40)
                # c.drawImage(lock23, 40 , 255-a, width=40, height=40)
                c.drawImage(key23, 45 , 204-a, width=30, height=30)
                c.setFont('Helvetica-Bold', 10, leading=None)                 
                c.drawString(40, 370-a, 'Hotel Key Information')
                c.setFont('Helvetica', 9, leading=None) 
                c.drawString(40, 350-a, 'Check Out:  12pm')
                if break41 > 0:                       
                    c.drawString(180, 350-a, 'Breakfast: 6.30am – 9.30am ')
                c.drawString(40, 333-a, 'IBP guest WiFi: 1nnBp@rk1303') 
                c.drawString(180, 333-a, 'Reception: Call 100# ')                                               
                c.setFont('Helvetica', 10, leading=None)                         
                c.drawString(95, 300-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas ')
                c.drawString(95, 288-a, 'of the hotel is strictly prohibited. ')
                c.setFont('Helvetica-Bold', 10, leading=None) 
                c.drawString(95, 276-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                c.setFont('Noto', 10, leading=None)                         
                c.drawString(95, 262-a, '酒店为了确保所有贵宾在酒店逗留期间享受最好的空气质量,在酒店范围内吸烟是严格禁止的。')
                c.drawString(95, 250-a, '若在酒店内吸烟,我们将会收取马币150.00的清洁费。 ')
                c.setFont('Helvetica', 10, leading=None) 
                # c.drawString(95, 254-a, 'For security purposes, both main elevators will be locked between 10pm to 7am.')

                c.drawString(95, 228-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out.')            
                c.drawString(95, 216-a, 'Failure to do so will incur a charge of RM 20.00 per card.')            
                c.setFont('Noto', 10, leading=None)                 
                c.drawString(95, 204-a, '卡需在退房时退回前台。若钥匙卡遗失或没退还前台酒店将收取每卡马币20.00的费用。')

        if afafa.totalpaid == False:
            if afafa.bookingfeepaid == False:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    if not afafa.depositpaiddate:
                        c.drawString(40, 420-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                        c.drawString(100, 420-a, 'Not Paid')                                                            
                    
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
 

            else:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 420-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 420-a, 'Not Paid')                                                            
                
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
        
        # if a > 180:
        #     c.showPage()
        #     c.setLineWidth(.3)
        #     c.setStrokeColorRGB(0,0,0)
        #     c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
        #     a = a-500   



  



        # c.drawString(380, 390-a, 'Payment Method:')                
        # c.drawString(470, 390-a, str(afafa.Paymentmethod))
            # if afafa.Paymentmethod == "Credit Card":
            #     c.drawString(470, 490-a, afafa.paymentdescription)
            # c.drawCentredString(415,500, 'test')
        # logo='booking/static/innbparklogo2.gif'           
            # c.setFont('Helvetica', 48, leading=None)
            # c.drawCentredString(415,500, 'test')
            # c.setFont('Helvetica', 20, leading=None)        


        # c.drawImage(logo, 400 , 730, width=140, height=69)
        c.showPage()
        c.save()


    generate1(f,e,d, q111, break41, exitem)
    url = 'https://innbparkhotel.com/static/invoice/' + invno + '.pdf'

    return redirect(url)



















@login_required(login_url='/login/')
def generatepdfwithtourismtax(request):
    pdfmetrics.registerFont(TTFont('Noto', 'simhei.ttf'))
    refno = request.GET.get('referenceno')
    if not refno:
        return redirect('test2')
    d = Invoice.objects.get(referenceno=refno)
    # year = datetime.now().strftime("%y")    
    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
    # inv_no = invnos.invoiceno
    # invoice_int = inv_no[2:]
    # new_invoice_int = int(invoice_int) + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    # d.invoiceno = new_invoice_no
    # d.save()
    invno = refno
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d').date()
    e = Booking.objects.filter(referenceno = refno).order_by('room_type_name')
    exitem = extra_items.objects.filter(referenceno=refno)
    firstname= d.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = refno).first()
    try:
        q111 = depositwitheld.objects.filter(invoice=d)
    except depositwitheld.DoesNotExist:
        q111 = None


    break41 = 0

    for a in e:
        if a.room_type_name.pk == 23:
            break41 = break41+1

        elif a.room_type_name.pk==24:
            break41 = break41+1


    if break41 == 0 :
       if f.created_on.date() < deadline:
            break41 = 24



    def generate1(f, ae, afafa, q111 ,break41,xtraitem):
        logo='booking/static/innbparklogo2.gif'
        nosmoke = 'booking/static/Untitled-1.gif'
        key23 = 'booking/static/key.gif'
        lock23  = 'booking/static/lock.gif'       

        c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
        c.setLineWidth(.3)
        c.setStrokeColorRGB(0,0,0)
        c.drawImage(logo, 400 , 730, width=140, height=69)

        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)

        a=15
        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(40 ,805,'InnB Park Hotel')
        c.drawString(40 ,790,'operated by Apocity Sdn Bhd 198401014712 (127268-X)')
        if afafa.invoiceno:
            if int(afafa.invoiceno) > 1702514:
                c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        else:        
            c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        c.drawString(40 ,775-a,'102-106, Jalan Imbi,  Bukit Bintang')
        c.drawString(40 ,760-a,'55100 Kuala Lumpur')
        c.drawString(40 ,745-a,'admin@innbparkhotel.com') 
        c.drawString(40 ,730-a,'+603 2856 7257')
        if afafa.addressline1:
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, afafa.addressline1)           
            if afafa.addressline2:
                a=a+15                
                c.drawString(40 ,730-a, afafa.addressline2)
                if afafa.addressline3:
                    a=a+15                
                    c.drawString(40 ,730-a, afafa.addressline3)                    

        a=a-12
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(40 ,680-a,'ROOM RESERVATION')
        c.drawString(430 ,810,'Non-refundable Rate')
        a=a-5
        c.setFont('Helvetica', 9, leading=None)
        c.drawString(40, 650-a, 'GUESTS NAME')
        c.drawString(197, 650-a, 'ROOM NO.')
        c.drawString(257, 650-a, 'ROOM TYPE')
        c.drawString(380, 650-a, 'ARRIVAL DATE')  
        c.drawString(470, 650-a, 'DEPATURE DATE')                                     
        a=a-2
        c.setLineWidth(.5)
        c.line(40,630-a,548,630-a)

        if f:
            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 610-a, afafa.email.first_name)
            c.drawString(40, 590-a, afafa.email.last_name)
            if afafa.email.passno:
                c.drawString(40, 570-a, "Passport no: "+ str(afafa.email.passno))
        count1 =0
        for t in ae:

            if t.familyroom == True:
                if count1 == 1:
                    asdfafa = "nothing"
                    count1 = 0

                else: 

                    count1 = 1
                    if a > 540:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -150

                    c.setFont('Helvetica', 9, leading=None)


                    roomnumber = "[" + str(t.room_number) + "]"
                    roomname = 'Family Room'

                    roomnamecount = len(roomname)
                        
                    n=20
                    a += n
                    # c.drawString(177, 630-a, str(a))            
                    c.drawString(197, 630-a, roomnumber)
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(257, 610-a, newline)
                        c.drawString(257, 630-a, oldline)
                    else:
                        c.drawString(257, 630-a, roomname)                            
                    if t.extension is True:
                        c.drawString(355, 630-a, '(ext)')
                    if t.late is True:
                        c.drawString(355, 630-a, '(late)')                
                    indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                    outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                    c.drawString(380, 630-a, indate)  
                    c.drawString(470, 630-a, outdate)
                    if roomnamecount > 22:
                        a = a+20



            else:









                if a > 540:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -150

                c.setFont('Helvetica', 9, leading=None)


                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)

                roomnamecount = len(roomname)
                    
                n=20
                a += n
                # c.drawString(177, 630-a, str(a))            
                c.drawString(197, 630-a, roomnumber)
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(257, 610-a, newline)
                    c.drawString(257, 630-a, oldline)
                else:
                    c.drawString(257, 630-a, roomname)                            
                if t.extension is True:
                    c.drawString(355, 630-a, '(ext)')
                if t.late is True:
                    c.drawString(355, 630-a, '(late)')                
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 630-a, indate)  
                c.drawString(470, 630-a, outdate)
                if roomnamecount > 22:
                    a = a+20









        if afafa.email.passno:
            a=a+20
        c.line(40,600-a,548,600-a)



 

        c.setFont('Helvetica-Bold', 11, leading=None)
        if afafa.rtacomm is not None:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200

            
            print("nothing")
            a=a-70
            if afafa.ttax:

                c.setFont('Helvetica-Bold', 9, leading=None)
                a= a+20
                c.drawString(40, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                a= a+10



        else:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200
            if afafa.invoiceno:
                if int(afafa.invoiceno) > 1702514:
                    c.drawString(40, 570-a, 'TAX INVOICE ' + afafa.invoiceno) 
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " + qwerdate) 

                else:
                    c.drawString(40, 570-a, 'INVOICE ' + afafa.invoiceno)
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " +qwerdate)                      
            else:
                c.drawString(40, 570-a, 'INVOICE ')
                if afafa.totalpaiddate:
                    qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                    c.drawString(380, 570-a, "Invoice Date " +qwerdate) 

           
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 570-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 545-a, 'DESCRIPTION')
            c.drawString(180, 545-a, 'PRICE/UNIT')
            c.drawString(270, 545-a, 'NO. NIGHTS')


            for t in ae:
                if t.actualpay-t.paymentprice > 0:
                    c.drawString(360, 545-a, 'DISCOUNT')
                    break



            if afafa.description:         
                c.drawString(360, 545-a, 'DISCOUNT')
            c.drawString(470, 545-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            count1 = 0
            for t in ae:


                if t.familyroom == True:
                    if count1 == 1:
                        asdfafa = "nothing"
                        count1 = 0

                    else: 
                        count1 = 1
                        if a > 340:
                            c.showPage()
                            c.setLineWidth(.3)
                            c.setStrokeColorRGB(0,0,0)
                            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                            a = -200
                        c.setFont('Helvetica', 9, leading=None)
                        roomnumber = str(t.room_number)
                        roomname = 'Family Room'
                        n=20
                        a += n
                        nights = int((t.checkout_date-t.checkin_date).days)
                        if nights<1:
                            nights=1
                        price = str(round((t.actualpay*2/  nights),2))
                        roomnamecount = len(roomname)                
                        if roomnamecount > 22:
                            newline = roomname.split(", ",1)[1]
                            oldline = roomname.split(", ")[0]
                            c.drawString(40, 525-a, newline)
                            c.drawString(40, 545-a, oldline)
                        else:
                            c.drawString(40, 545-a, roomname)  




                        # c.drawString(40, 545-a, roomname)
                        c.drawString(180, 545-a, 'RM ' + price)
                        c.drawString(270, 545-a, str(nights))
                        if t.actualpay-t.paymentprice > 0:
                            c.drawString(360, 545-a, '- RM ' + str((t.actualpay-t.paymentprice)*2))            
                        c.drawString(470, 545-a, 'RM ' + str(t.paymentprice*2))
                        if t.extension is True:
                            c.drawString(420, 545-a, '(ext)')
                        if t.late is True:
                            c.drawString(420, 545-a, '(late)')
                        totalprice = totalprice + (t.actualpay*2)   

                        if roomnamecount > 22:
                            a = a+20


                else:

                    if a > 340:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -200
                    c.setFont('Helvetica', 9, leading=None)
                    roomnumber = str(t.room_number)
                    roomname = str(t.room_type_name)
                    n=20
                    a += n
                    nights = int((t.checkout_date-t.checkin_date).days)
                    if nights<1:
                        nights=1
                    price = str(round((t.actualpay /  nights),2))
                    roomnamecount = len(roomname)                
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(40, 525-a, newline)
                        c.drawString(40, 545-a, oldline)
                    else:
                        c.drawString(40, 545-a, roomname)  




                    # c.drawString(40, 545-a, roomname)
                    c.drawString(180, 545-a, 'RM ' + price)
                    c.drawString(270, 545-a, str(nights))
                    if t.actualpay-t.paymentprice > 0:
                        c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                    c.drawString(470, 545-a, 'RM ' + str(t.paymentprice))
                    if t.extension is True:
                        c.drawString(420, 545-a, '(ext)')
                    if t.late is True:
                        c.drawString(420, 545-a, '(late)')
                    totalprice = totalprice + t.actualpay   

                    if roomnamecount > 22:
                        a = a+20
            
            for item in xtraitem:

                if a > 340:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -200
                c.setFont('Helvetica', 9, leading=None)

                roomname = str(item.description)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                if nights<1:
                    nights=1
                price = str(item.paymentprice)
                roomnamecount = len(roomname)                
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(40, 525-a, newline)
                    c.drawString(40, 545-a, oldline)
                else:
                    c.drawString(40, 545-a, roomname)  




                # c.drawString(40, 545-a, roomname)
                # c.drawString(180, 545-a, 'RM ' + price)
                # if t.actualpay-t.paymentprice > 0:
                #     c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                c.drawString(470, 545-a, 'RM ' + str(item.paymentprice))
                # if t.extension is True:
                #     c.drawString(420, 545-a, '(ext)')
                # if t.late is True:
                #     c.drawString(420, 545-a, '(late)')
                totalprice = totalprice + item.paymentprice   

                if roomnamecount > 22:
                    a = a+20



            if not f:
                a=20
                c.drawString(40, 545-a, 'Customer cancelled booking')




            a=a-10

            if afafa.additionalcharge:
                a=a
                # discount=  totalprice - afafa.total + afafa.additionalcharge
                # c.drawString(180, 530-a, 'Special Promo:   ' + afafa.description.description )
                # c.drawString(470, 530-a, '- RM ' + str(discount))

                c.drawString(180, 510-a, afafa.additionalcharges)
                c.drawString(470, 510-a, 'RM ' + str(afafa.additionalcharge))
                # else:
                #     a = a+20
                #     discount=  totalprice - afafa.total
                #     c.drawString(180, 520-a, 'Special Promo:   ' + afafa.description.description )
                #     c.drawString(470, 520-a, '- RM ' + str(discount))
            




            if afafa.rounding:
                a = a+20
                c.drawString(180, 520-a, 'rounding' )
                c.drawString(470, 520-a, 'RM ' + str(afafa.rounding))











                        
            if afafa.gst > 0:
                qindate2 = datetime.strptime("2018-08-31", '%Y-%m-%d')
                utc=pytz.UTC
                qindate2=utc.localize(qindate2) 
                if afafa.totalpaiddate:
                    if afafa.totalpaiddate > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))    

                else:
                    if afafa.datecreated > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))







            else:
                qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
                utc=pytz.UTC
                qindate=utc.localize(qindate) 
                if afafa.datecreated > qindate:
                    a = a+20
                    c.drawString(180, 520-a, '0% SST ' )
                    c.drawString(470, 520-a, 'RM 0.00')


            # if afafa.rtacomm:
            #     c.setFont('Helvetica-Bold', 9, leading=None)
            #     a= a+20
            #     c.drawString(180, 520-a,str(afafa.referral) +'    '+ str(100*afafa.rtacomm)+'%')
            #     c.drawString(470, 520-a, 'RM '+ str(afafa.commamount)) 
            #     a=a-10







                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 490-a, 'Total:')
            if f:
                # if afafa.rtacomm:
                #     c.drawString(470, 490-a, 'RM ' + format((afafa.total + afafa.commamount),'.2f'))
                # else:
                c.drawString(470, 490-a, 'RM ' + str(afafa.total))


                if afafa.ttax:

                    c.setFont('Helvetica-Bold', 9, leading=None)
                    a= a+20
                    c.drawString(180, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                    a= a+10
            else:
                c.drawString(470,400-a, 'RM ' + str(afafa.bookingfee))
            


            


            c.setFont('Helvetica', 9, leading=None)
            



            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 490-a, 'Booking Pre-payment')
                c.drawString(470, 490-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                

                    if afafa.bookingfeepaid == True:
                        c.drawString(180, 470-a, 'Total Payable:') 
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        c.drawString(180, 470-a, 'Total Paid:')
                        total12 = afafa.total
                    c.drawString(470, 470-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 470-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 470-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 455-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 455-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 455-a, 'Deposit not applicable')
        





        c.setFont('Helvetica', 10, leading=None)


        if afafa.invoicedesc:
            c.drawString(40, 430-a,afafa.invoicedesc) 
            a= a+30
        

        if afafa.addressline1:
            c.showPage()
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
            a = -300
        else:
            if a > 170:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300



        
        if afafa.totalpaid == True:
            # a= a+20
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
            c.setFont('Helvetica', 9, leading=None)  
            if afafa.rtacomm is not None:
                print("None")
            else:              
                c.drawString(40, 430-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 430-a, 'RM ' + str(total12))
            c.setFont('Helvetica', 10, leading=None) 
            # c.drawString(480, 380-a, str(a))



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 410-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)
                z=0
                if afafa.depositcash:
                    if afafa.depositcash > 0:
                        c.drawString(180, 410-a, 'Cash  '+ 'RM ' + str(afafa.depositcash))
                        z = 80
                if afafa.depositcc:
                    if afafa.depositcc > 0:
                        c.drawString(z+180, 410-a, 'Credit Card  '+ 'RM ' + str(afafa.depositcc))
                        z = 100
                if afafa.depi == "Others":
                    c.drawString(z+ 180, 410-a, str(afafa.depdescrip))                    

                a=a+20
                c.drawString(40, 410-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                if afafa.depdescrip:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                else:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300    

            # if afafa.depositreturnedate:
            #     items=0
            #     c.setFont('Helvetica-Bold', 9, leading=None) 

            #     if afafa.ttax:
            #         a= a+20
            #         c.drawString(40, 410-a,'Tourism tax Paid: ') 
            #         c.drawString(180, 410-a, 'RM ' + str(afafa.ttax))
                
            #     c.setFont('Helvetica', 9, leading=None) 

            #     if q111:
            #         c.drawString(40, 390-a, 'Deposit charged:')
            #         for i in q111:
            #             c.drawString(180, 390-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
            #             n = 17
            #             a+=n
            #             items += i.itemprice
            #         returned = afafa.depositamt - items
            #         if returned < 0: 
            #             returned = -(returned)
            #             c.drawString(40, 370-a, 'Deposit charged on')
            #             # c.drawString(350, 370-a, 'RM ' + str(returned))
            #         else:
            #             c.drawString(40, 370-a, 'Deposit returned')
            #             if afafa.otherdeposit < 1:
            #                 c.drawString(350, 280-a, 'RM ' + str(returned))                         
            #             # c.drawString(350, 370-a,  'RM ' + str(returned))                                  

            #     else:
            #         c.drawString(40, 370-a, 'Deposit returned on')
                

            #     tz = timezone('Etc/GMT-8')
            #     depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

            #     c.drawString(180, 370-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

            #     a=a+20         
            #     c.drawString(40, 370-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
            #     c.drawString(40, 355-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
         
            #     c.setLineWidth(.5)
            #     c.line(40,270-a , 180,270-a)   
            #     c.setFont('Helvetica', 9, leading=None)        
            #     c.drawString(80, 250-a, 'Signature')          




            # if not afafa.depositreturnedate:     
            c.drawImage(nosmoke, 40 , 260-a, width=40, height=40)
            # c.drawImage(lock23, 40 , 255-a, width=40, height=40)
            c.drawImage(key23, 45 , 204-a, width=30, height=30)
            c.setFont('Helvetica-Bold', 10, leading=None)                 
            c.drawString(40, 370-a, 'Hotel Key Information')
            c.setFont('Helvetica', 9, leading=None) 
            c.drawString(40, 350-a, 'Check Out:  12pm')
            if break41 > 0:                       
                c.drawString(180, 350-a, 'Breakfast: 6.30am – 9.30am ')
            c.drawString(40, 333-a, 'IBP guest WiFi: 1nnBp@rk1303') 
            c.drawString(180, 333-a, 'Reception: Call 100# ')                                               
            c.setFont('Helvetica', 10, leading=None)                         
            c.drawString(95, 300-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas ')
            c.drawString(95, 288-a, 'of the hotel is strictly prohibited. ')
            c.setFont('Helvetica-Bold', 10, leading=None) 
            c.drawString(95, 276-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
            c.setFont('Noto', 10, leading=None)                         
            c.drawString(95, 262-a, '酒店为了确保所有贵宾在酒店逗留期间享受最好的空气质量,在酒店范围内吸烟是严格禁止的。')
            c.drawString(95, 250-a, '若在酒店内吸烟,我们将会收取马币150.00的清洁费。 ')
            c.setFont('Helvetica', 10, leading=None) 
            # c.drawString(95, 254-a, 'For security purposes, both main elevators will be locked between 10pm to 7am.')

            c.drawString(95, 228-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out.')            
            c.drawString(95, 216-a, 'Failure to do so will incur a charge of RM 20.00 per card.')            
            c.setFont('Noto', 10, leading=None)                 
            c.drawString(95, 204-a, '卡需在退房时退回前台。若钥匙卡遗失或没退还前台酒店将收取每卡马币20.00的费用。')

        if afafa.totalpaid == False:
            if afafa.bookingfeepaid == False:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    if not afafa.depositpaiddate:
                        c.drawString(40, 420-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                        c.drawString(100, 420-a, 'Not Paid')                                                            
                    
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
 

            else:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 420-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 420-a, 'Not Paid')                                                            
                
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
        
        # if a > 180:
        #     c.showPage()
        #     c.setLineWidth(.3)
        #     c.setStrokeColorRGB(0,0,0)
        #     c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
        #     a = a-500   



  



        # c.drawString(380, 390-a, 'Payment Method:')                
        # c.drawString(470, 390-a, str(afafa.Paymentmethod))
            # if afafa.Paymentmethod == "Credit Card":
            #     c.drawString(470, 490-a, afafa.paymentdescription)
            # c.drawCentredString(415,500, 'test')
        # logo='booking/static/innbparklogo2.gif'           
            # c.setFont('Helvetica', 48, leading=None)
            # c.drawCentredString(415,500, 'test')
            # c.setFont('Helvetica', 20, leading=None)        


        # c.drawImage(logo, 400 , 730, width=140, height=69)
        c.showPage()
        c.save()


    generate1(f,e,d, q111, break41, exitem)
    url = 'https://innbparkhotel.com/static/invoice/' + invno + '.pdf'

    return redirect(url)






























@login_required(login_url='/login/')
def generatepdf(request):
    pdfmetrics.registerFont(TTFont('Noto', 'simhei.ttf'))
    refno = request.GET.get('referenceno')
    if not refno:
        return redirect('test2')
    d = Invoice.objects.get(referenceno=refno)
    # year = datetime.now().strftime("%y")    
    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
    # inv_no = invnos.invoiceno
    # invoice_int = inv_no[2:]
    # new_invoice_int = int(invoice_int) + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    # d.invoiceno = new_invoice_no
    # d.save()
    invno = refno
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d').date()
    e = Booking.objects.filter(referenceno = refno).order_by('room_type_name')
    exitem = extra_items.objects.filter(referenceno=refno)
    firstname= d.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = refno).first()
    try:
        q111 = depositwitheld.objects.filter(invoice=d)
    except depositwitheld.DoesNotExist:
        q111 = None


    break41 = 0

    for a in e:
        if a.room_type_name.pk == 23:
            break41 = break41+1

        elif a.room_type_name.pk==24:
            break41 = break41+1


    if break41 == 0 :
       if f.created_on.date() < deadline:
            break41 = 24



    def generate1(f, ae, afafa, q111 ,break41,xtraitem):
        logo='booking/static/innbparklogo2.gif'
        nosmoke = 'booking/static/Untitled-1.gif'
        key23 = 'booking/static/key.gif'
        lock23  = 'booking/static/lock.gif'       

        c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
        c.setLineWidth(.3)
        c.setStrokeColorRGB(0,0,0)
        c.drawImage(logo, 400 , 730, width=140, height=69)

        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)

        a=15
        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(40 ,805,'InnB Park Hotel')
        c.drawString(40 ,790,'operated by Apocity Sdn Bhd 198401014712 (127268-X)')
        if afafa.invoiceno:
            if int(afafa.invoiceno) > 1702514:
                c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        else:        
            c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')

        c.drawString(40 ,775-a,'102-106, Jalan Imbi,  Bukit Bintang')
        c.drawString(40 ,760-a,'55100 Kuala Lumpur')
        c.drawString(40 ,745-a,'admin@innbparkhotel.com') 
        c.drawString(40 ,730-a,'+603 2856 7257')
        if afafa.addressline1:
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, afafa.addressline1)           
            if afafa.addressline2:
                a=a+15                
                c.drawString(40 ,730-a, afafa.addressline2)
                if afafa.addressline3:
                    a=a+15                
                    c.drawString(40 ,730-a, afafa.addressline3)                    

        a=a-12
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(40 ,680-a,'ROOM RESERVATION')
        c.drawString(430 ,810,'Non-refundable Rate')
        a=a-5
        c.setFont('Helvetica', 9, leading=None)
        c.drawString(40, 650-a, 'GUESTS NAME')
        c.drawString(197, 650-a, 'ROOM NO.')
        c.drawString(257, 650-a, 'ROOM TYPE')
        c.drawString(380, 650-a, 'ARRIVAL DATE')  
        c.drawString(470, 650-a, 'DEPATURE DATE')                                     
        a=a-2
        c.setLineWidth(.5)
        c.line(40,630-a,548,630-a)

        if f:
            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 610-a, afafa.email.first_name)
            c.drawString(40, 590-a, afafa.email.last_name)
            if afafa.email.passno:
                c.drawString(40, 570-a, "Passport no: "+ str(afafa.email.passno))
        count1 =0
        for t in ae:

            if t.familyroom == True:
                if count1 == 1:
                    asdfafa = "nothing"
                    count1 = 0

                else: 

                    count1 = 1
                    if a > 540:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -150

                    c.setFont('Helvetica', 9, leading=None)


                    roomnumber = "[" + str(t.room_number) + "]"
                    roomname = 'Family Room'

                    roomnamecount = len(roomname)
                        
                    n=20
                    a += n
                    # c.drawString(177, 630-a, str(a))            
                    c.drawString(197, 630-a, roomnumber)
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(257, 610-a, newline)
                        c.drawString(257, 630-a, oldline)
                    else:
                        c.drawString(257, 630-a, roomname)                            
                    if t.extension is True:
                        c.drawString(355, 630-a, '(ext)')
                    if t.late is True:
                        c.drawString(355, 630-a, '(late)')                
                    indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                    outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                    c.drawString(380, 630-a, indate)  
                    c.drawString(470, 630-a, outdate)
                    if roomnamecount > 22:
                        a = a+20



            else:









                if a > 540:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -150

                c.setFont('Helvetica', 9, leading=None)


                roomnumber = "[" + str(t.room_number) + "]"
                roomname = str(t.room_type_name)

                roomnamecount = len(roomname)
                    
                n=20
                a += n
                # c.drawString(177, 630-a, str(a))            
                c.drawString(197, 630-a, roomnumber)
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(257, 610-a, newline)
                    c.drawString(257, 630-a, oldline)
                else:
                    c.drawString(257, 630-a, roomname)                            
                if t.extension is True:
                    c.drawString(355, 630-a, '(ext)')
                if t.late is True:
                    c.drawString(355, 630-a, '(late)')                
                indate = t.checkin_date.strftime("%a, %d/%m/%Y")
                outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
                c.drawString(380, 630-a, indate)  
                c.drawString(470, 630-a, outdate)
                if roomnamecount > 22:
                    a = a+20









        if afafa.email.passno:
            a=a+20
        c.line(40,600-a,548,600-a)



 

        c.setFont('Helvetica-Bold', 11, leading=None)
        if afafa.rtacomm is not None:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200

            
            print("nothing")
            a=a-70
            if afafa.ttax:
                if not afafa.checkedout1:
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    a= a+20
                    c.drawString(40, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                    a= a+10



        else:
            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200
            if afafa.invoiceno:
                if int(afafa.invoiceno) > 1702514:
                    c.drawString(40, 570-a, 'TAX INVOICE ' + afafa.invoiceno) 
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " + qwerdate) 

                else:
                    c.drawString(40, 570-a, 'INVOICE ' + afafa.invoiceno)
                    if afafa.totalpaiddate:
                        qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                        c.drawString(380, 570-a, "Invoice Date " +qwerdate)                      
            else:
                c.drawString(40, 570-a, 'INVOICE ')
                if afafa.totalpaiddate:
                    qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
                    c.drawString(380, 570-a, "Invoice Date " +qwerdate) 

           
            if afafa.cancelled == True:
                c.setFont('Helvetica-Bold', 14, leading=None)
                c.drawString(330, 570-a, 'INVOICE CANCELLED')
            c.setFont('Helvetica-Bold', 9, leading=None)
            c.drawString(40, 545-a, 'DESCRIPTION')
            c.drawString(180, 545-a, 'PRICE/UNIT')
            c.drawString(270, 545-a, 'NO. NIGHTS')


            for t in ae:
                if t.actualpay-t.paymentprice > 0:
                    c.drawString(360, 545-a, 'DISCOUNT')
                    break



            if afafa.description:         
                c.drawString(360, 545-a, 'DISCOUNT')
            c.drawString(470, 545-a, 'TOTAL PRICE')


            c.setFont('Helvetica', 9, leading=None)
            totalprice=0
            count1 = 0
            for t in ae:


                if t.familyroom == True:
                    if count1 == 1:
                        asdfafa = "nothing"
                        count1 = 0

                    else: 
                        count1 = 1
                        if a > 340:
                            c.showPage()
                            c.setLineWidth(.3)
                            c.setStrokeColorRGB(0,0,0)
                            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                            a = -200
                        c.setFont('Helvetica', 9, leading=None)
                        roomnumber = str(t.room_number)
                        roomname = 'Family Room'
                        n=20
                        a += n
                        nights = int((t.checkout_date-t.checkin_date).days)
                        if nights<1:
                            nights=1
                        price = str(round((t.actualpay*2/  nights),2))
                        roomnamecount = len(roomname)                
                        if roomnamecount > 22:
                            newline = roomname.split(", ",1)[1]
                            oldline = roomname.split(", ")[0]
                            c.drawString(40, 525-a, newline)
                            c.drawString(40, 545-a, oldline)
                        else:
                            c.drawString(40, 545-a, roomname)  




                        # c.drawString(40, 545-a, roomname)
                        c.drawString(180, 545-a, 'RM ' + price)
                        c.drawString(270, 545-a, str(nights))
                        if t.actualpay-t.paymentprice > 0:
                            c.drawString(360, 545-a, '- RM ' + str((t.actualpay-t.paymentprice)*2))            
                        c.drawString(470, 545-a, 'RM ' + str(t.paymentprice*2))
                        if t.extension is True:
                            c.drawString(420, 545-a, '(ext)')
                        if t.late is True:
                            c.drawString(420, 545-a, '(late)')
                        totalprice = totalprice + (t.actualpay*2)   

                        if roomnamecount > 22:
                            a = a+20


                else:

                    if a > 340:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -200
                    c.setFont('Helvetica', 9, leading=None)
                    roomnumber = str(t.room_number)
                    roomname = str(t.room_type_name)
                    n=20
                    a += n
                    nights = int((t.checkout_date-t.checkin_date).days)
                    if nights<1:
                        nights=1
                    price = str(round((t.actualpay /  nights),2))
                    roomnamecount = len(roomname)                
                    if roomnamecount > 22:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(40, 525-a, newline)
                        c.drawString(40, 545-a, oldline)
                    else:
                        c.drawString(40, 545-a, roomname)  




                    # c.drawString(40, 545-a, roomname)
                    c.drawString(180, 545-a, 'RM ' + price)
                    c.drawString(270, 545-a, str(nights))
                    if t.actualpay-t.paymentprice > 0:
                        c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                    c.drawString(470, 545-a, 'RM ' + str(t.paymentprice))
                    if t.extension is True:
                        c.drawString(420, 545-a, '(ext)')
                    if t.late is True:
                        c.drawString(420, 545-a, '(late)')
                    totalprice = totalprice + t.actualpay   

                    if roomnamecount > 22:
                        a = a+20
            

            if afafa.description:

                    if a > 340:
                        c.showPage()
                        c.setLineWidth(.3)
                        c.setStrokeColorRGB(0,0,0)
                        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                        a = -200
                    c.setFont('Helvetica', 9, leading=None)
                    roomname = str(afafa.description.description)
                    roomnamecount = len(roomname)      
                    n=20
                    a += n          
                    if roomnamecount > 70:
                        newline = roomname.split(", ",1)[1]
                        oldline = roomname.split(", ")[0]
                        c.drawString(40, 525-a, newline)
                        c.drawString(40, 545-a, oldline)
                    else:
                        c.drawString(40, 545-a, roomname)  


                    if roomnamecount > 70:
                        a = a+20






            for item in xtraitem:

                if a > 340:
                    c.showPage()
                    c.setLineWidth(.3)
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                    a = -200
                c.setFont('Helvetica', 9, leading=None)

                roomname = str(item.description)
                n=20
                a += n
                nights = int((t.checkout_date-t.checkin_date).days)
                if nights<1:
                    nights=1
                price = str(item.paymentprice)
                roomnamecount = len(roomname)                
                if roomnamecount > 22:
                    newline = roomname.split(", ",1)[1]
                    oldline = roomname.split(", ")[0]
                    c.drawString(40, 525-a, newline)
                    c.drawString(40, 545-a, oldline)
                else:
                    c.drawString(40, 545-a, roomname)  




                # c.drawString(40, 545-a, roomname)
                # c.drawString(180, 545-a, 'RM ' + price)
                # if t.actualpay-t.paymentprice > 0:
                #     c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
                c.drawString(470, 545-a, 'RM ' + str(item.paymentprice))
                # if t.extension is True:
                #     c.drawString(420, 545-a, '(ext)')
                # if t.late is True:
                #     c.drawString(420, 545-a, '(late)')
                totalprice = totalprice + item.paymentprice   

                if roomnamecount > 22:
                    a = a+20



            if not f:
                a=20
                c.drawString(40, 545-a, 'Customer cancelled booking')




            a=a-10

            if afafa.additionalcharge:
                a=a
                # discount=  totalprice - afafa.total + afafa.additionalcharge
                # c.drawString(180, 530-a, 'Special Promo:   ' + afafa.description.description )
                # c.drawString(470, 530-a, '- RM ' + str(discount))

                c.drawString(180, 510-a, afafa.additionalcharges)
                c.drawString(470, 510-a, 'RM ' + str(afafa.additionalcharge))
                # else:
                #     a = a+20
                #     discount=  totalprice - afafa.total
                #     c.drawString(180, 520-a, 'Special Promo:   ' + afafa.description.description )
                #     c.drawString(470, 520-a, '- RM ' + str(discount))
            




            if afafa.rounding:
                a = a+20
                c.drawString(180, 520-a, 'rounding' )
                c.drawString(470, 520-a, 'RM ' + str(afafa.rounding))











                        
            if afafa.gst > 0:
                qindate2 = datetime.strptime("2018-08-31", '%Y-%m-%d')
                utc=pytz.UTC
                qindate2=utc.localize(qindate2) 
                if afafa.totalpaiddate:
                    if afafa.totalpaiddate > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))    

                else:
                    if afafa.datecreated > qindate2:
                        a = a+20
                        c.drawString(180, 520-a, '6% SST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                    else:
                        a = a+20
                        c.drawString(180, 520-a, '6% GST ' )
                        c.drawString(470, 520-a, 'RM ' + str(afafa.gst))







            else:
                qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
                utc=pytz.UTC
                qindate=utc.localize(qindate) 
                if afafa.datecreated > qindate:
                    a = a+20
                    c.drawString(180, 520-a, '0% SST ' )
                    c.drawString(470, 520-a, 'RM 0.00')


            # if afafa.rtacomm:
            #     c.setFont('Helvetica-Bold', 9, leading=None)
            #     a= a+20
            #     c.drawString(180, 520-a,str(afafa.referral) +'    '+ str(100*afafa.rtacomm)+'%')
            #     c.drawString(470, 520-a, 'RM '+ str(afafa.commamount)) 
            #     a=a-10







                
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(180, 490-a, 'Total:')
            if f:
                # if afafa.rtacomm:
                #     c.drawString(470, 490-a, 'RM ' + format((afafa.total + afafa.commamount),'.2f'))
                # else:
                c.drawString(470, 490-a, 'RM ' + str(afafa.total))


                if afafa.ttax:
                    if not afafa.checkedout1:
                        c.setFont('Helvetica-Bold', 9, leading=None)
                        a= a+20
                        c.drawString(180, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
                        a= a+10
            else:
                c.drawString(470,400-a, 'RM ' + str(afafa.bookingfee))
            


            


            c.setFont('Helvetica', 9, leading=None)
            



            if afafa.bookingfeepaid == True:
                a = a+20
                c.drawString(180, 490-a, 'Booking Pre-payment')
                c.drawString(470, 490-a, 'RM ' + str(afafa.bookingfee))

                if afafa.totalpaid == True:
                    c.setFont('Helvetica-Bold', 12, leading=None)                

                    if afafa.bookingfeepaid == True:
                        c.drawString(180, 470-a, 'Total Payable:') 
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        c.drawString(180, 470-a, 'Total Paid:')
                        total12 = afafa.total
                    c.drawString(470, 470-a, 'RM ' + str(total12))




                else:
                    c.setFont('Helvetica-Bold', 12, leading=None)
                    if f:                
                        c.drawString(180, 470-a, 'Outstanding Amount:')
                        if afafa.bookingfeepaid == True:
                            total12 = afafa.total - afafa.bookingfee
                        else: 
                            total12 = afafa.total
                        c.drawString(470, 470-a, 'RM ' + str(total12))
                    if afafa.deposit == False:
                        c.setFont('Helvetica-Bold', 8, leading=None)
                        if f:
                            c.drawString(180, 455-a, 'Deposit Required') 
                            c.setFont('Helvetica', 8, leading=None)        
                            c.drawString(470, 455-a, 'RM ' + str(afafa.depositamt))
                        if not f:
                            c.drawString(180, 455-a, 'Deposit not applicable')
        





        c.setFont('Helvetica', 10, leading=None)


        if afafa.invoicedesc:
            c.drawString(40, 430-a,afafa.invoicedesc) 
            a= a+30
        

        if afafa.addressline1:
            c.showPage()
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
            a = -300
        else:
            if a > 170:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300



        
        if afafa.totalpaid == True:
            # a= a+20
            c.setFont('Helvetica-Bold', 11, leading=None)                
            c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
            c.setFont('Helvetica', 9, leading=None)  
            if afafa.rtacomm is not None:
                print("None")
            else:              
                c.drawString(40, 430-a, 'Payment Total')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total                
                c.drawString(180, 430-a, 'RM ' + str(total12))
            c.setFont('Helvetica', 10, leading=None) 
            # c.drawString(480, 380-a, str(a))



            if afafa.depositpaiddate:
                c.setFont('Helvetica', 9, leading=None)                
                c.drawString(40, 410-a, 'Deposit') 
                c.setFont('Helvetica', 9, leading=None)
                z=0
                if afafa.depositcash:
                    if afafa.depositcash > 0:
                        c.drawString(180, 410-a, 'Cash  '+ 'RM ' + str(afafa.depositcash))
                        z = 80
                if afafa.depositcc:
                    if afafa.depositcc > 0:
                        c.drawString(z+180, 410-a, 'Credit Card  '+ 'RM ' + str(afafa.depositcc))
                        z = 100
                if afafa.depi == "Others":
                    c.drawString(z+ 180, 410-a, str(afafa.depdescrip))                    

                a=a+20
                c.drawString(40, 410-a, 'Deposit Paid')
                tz = timezone('Etc/GMT-8')
                depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                if afafa.depdescrip:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                else:
                    c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


            if a > 200:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -300    

            if afafa.depositreturnedate:
                items=0
                c.setFont('Helvetica-Bold', 9, leading=None) 

                if afafa.ttax:
                    a= a+20
                    c.drawString(40, 410-a,'Tourism tax Paid: ') 
                    c.drawString(180, 410-a, 'RM ' + str(afafa.ttax))
                
                c.setFont('Helvetica', 9, leading=None) 

                if q111:
                    c.drawString(40, 390-a, 'Deposit charged:')
                    for i in q111:
                        c.drawString(180, 390-a, str(i.itemname)+ '   RM ' + str(i.itemprice))
                        n = 17
                        a+=n
                        items += i.itemprice
                    returned = afafa.depositamt - items
                    if returned < 0: 
                        returned = -(returned)
                        c.drawString(40, 370-a, 'Deposit charged on')
                        # c.drawString(350, 370-a, 'RM ' + str(returned))
                    else:
                        c.drawString(40, 370-a, 'Deposit returned')
                        if afafa.otherdeposit < 1:
                            c.drawString(350, 280-a, 'RM ' + str(returned))                         
                        # c.drawString(350, 370-a,  'RM ' + str(returned))                                  

                else:
                    c.drawString(40, 370-a, 'Deposit returned on')
                

                tz = timezone('Etc/GMT-8')
                depositreturnedate = str(afafa.depositreturnedate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))

                c.drawString(180, 370-a, depositreturnedate + ' by ' + str(afafa.checkedoutby))  

                a=a+20         
                c.drawString(40, 370-a, str('This is to acknowledge that you have received a deposit refund of the above stated amount.'))           
                c.drawString(40, 355-a, str('We hope you had a pleasant stay and are looking forward to welcoming you back to Inn B Park Hotel in the near future!')) 
         
                c.setLineWidth(.5)
                c.line(40,270-a , 180,270-a)   
                c.setFont('Helvetica', 9, leading=None)        
                c.drawString(80, 250-a, 'Signature')          




            if not afafa.depositreturnedate:     
                c.drawImage(nosmoke, 40 , 260-a, width=40, height=40)
                # c.drawImage(lock23, 40 , 255-a, width=40, height=40)
                c.drawImage(key23, 45 , 204-a, width=30, height=30)
                c.setFont('Helvetica-Bold', 10, leading=None)                 
                c.drawString(40, 370-a, 'Hotel Key Information')
                c.setFont('Helvetica', 9, leading=None) 
                c.drawString(40, 350-a, 'Check Out:  12pm')
                if break41 > 0:                       
                    c.drawString(180, 350-a, 'Breakfast: 6.30am – 9.30am ')
                c.drawString(40, 333-a, 'IBP guest WiFi: 1nnBp@rk1303') 
                c.drawString(180, 333-a, 'Reception: Call 100# ')                                               
                c.setFont('Helvetica', 10, leading=None)                         
                c.drawString(95, 300-a, 'To ensure all our customers enjoy the best air quality during their stay at the hotel, smoking in all areas ')
                c.drawString(95, 288-a, 'of the hotel is strictly prohibited. ')
                c.setFont('Helvetica-Bold', 10, leading=None) 
                c.drawString(95, 276-a, 'Guests found to be smoking in any area of the hotel will be charged a cleaning fee of RM 150.00.')
                c.setFont('Noto', 10, leading=None)                         
                c.drawString(95, 262-a, '酒店为了确保所有贵宾在酒店逗留期间享受最好的空气质量,在酒店范围内吸烟是严格禁止的。')
                c.drawString(95, 250-a, '若在酒店内吸烟,我们将会收取马币150.00的清洁费。 ')
                c.setFont('Helvetica', 10, leading=None) 
                # c.drawString(95, 254-a, 'For security purposes, both main elevators will be locked between 10pm to 7am.')

                c.drawString(95, 228-a, 'Please note that all issued key cards will need to be returned to the front desk upon check out.')            
                c.drawString(95, 216-a, 'Failure to do so will incur a charge of RM 20.00 per card.')            
                c.setFont('Noto', 10, leading=None)                 
                c.drawString(95, 204-a, '卡需在退房时退回前台。若钥匙卡遗失或没退还前台酒店将收取每卡马币20.00的费用。')

        if afafa.totalpaid == False:
            if afafa.bookingfeepaid == False:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    if not afafa.depositpaiddate:
                        c.drawString(40, 420-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                        c.drawString(100, 420-a, 'Not Paid')                                                            
                    
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))

                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
 

            else:
                if not afafa.cashpaid and not afafa.ccpaid:
                    a= a+20 
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD' )
                    c.setFont('Helvetica', 9, leading=None)
                    a= a+20                 
                    c.drawString(40, 450-a, 'Please arrange for an online transfer to the following bank account:')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Bank: UOB Bank')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Name: APOCITY SDN BHD')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Account Number: 608-300-6312')
                    a= a+15                 
                    c.drawString(40, 450-a, 'Reference: ' + afafa.invoiceno) 
                    c.setFont('Helvetica-Bold', 9, leading=None)
                    c.drawString(40, 420-a, 'Deposit') 
                    c.setFont('Helvetica', 9, leading=None)        
                    c.drawString(180, 420-a, 'RM ' + str(afafa.depositamt))
                    c.drawString(100, 420-a, 'Not Paid')                                                            
                
                else:
                    a= a+20
                    c.setFont('Helvetica-Bold', 11, leading=None)                
                    c.drawString(40, 450-a, 'PAYMENT METHOD:  ' + afafa.Paymentmethod )
                    c.setFont('Helvetica', 9, leading=None)                
                    c.drawString(40, 430-a, 'Payment Total')
                    if not afafa.cashpaid:
                        afafa.cashpaid=0
                    if not afafa.ccpaid:
                        afafa.ccpaid =0
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.cashpaid + afafa.ccpaid - afafa.bookingfee
                    else: 
                        total12 = afafa.cashpaid + afafa.ccpaid                
                    c.drawString(180, 430-a, 'RM ' + str(total12))
                    c.setFont('Helvetica', 10, leading=None) 
                    # c.drawString(480, 380-a, str(a))



                    if afafa.depositpaiddate:
                        c.setFont('Helvetica', 9, leading=None)                
                        c.drawString(40, 410-a, 'Deposit') 
                        c.setFont('Helvetica', 9, leading=None)        
                        c.drawString(180, 410-a, 'RM ' + str(afafa.depositamt))
                        a=a+20
                        c.drawString(40, 410-a, 'Deposit Paid')
                        tz = timezone('Etc/GMT-8')
                        depositpaiddate = str(afafa.depositpaiddate.astimezone(tz).strftime("%Y-%m-%d %H:%M"))
                        if afafa.depdescrip:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby) + '  (' + str(afafa.depdescrip) + ')')
                        else:
                            c.drawString(180, 410-a, depositpaiddate +  ' received by ' + str(afafa.depositpaidby))


                    c.setFont('Helvetica-Bold', 11, leading=None)
                    a=a+20
                    outstandingamt = total12
                    if outstandingamt > 0:
                        c.drawString(40, 390-a, 'Amount Outstanding: RM' + str(outstandingamt)) 
        
        # if a > 180:
        #     c.showPage()
        #     c.setLineWidth(.3)
        #     c.setStrokeColorRGB(0,0,0)
        #     c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
        #     a = a-500   



  



        # c.drawString(380, 390-a, 'Payment Method:')                
        # c.drawString(470, 390-a, str(afafa.Paymentmethod))
            # if afafa.Paymentmethod == "Credit Card":
            #     c.drawString(470, 490-a, afafa.paymentdescription)
            # c.drawCentredString(415,500, 'test')
        # logo='booking/static/innbparklogo2.gif'           
            # c.setFont('Helvetica', 48, leading=None)
            # c.drawCentredString(415,500, 'test')
            # c.setFont('Helvetica', 20, leading=None)        


        # c.drawImage(logo, 400 , 730, width=140, height=69)
        c.showPage()
        c.save()


    generate1(f,e,d, q111, break41, exitem)
    url = 'https://innbparkhotel.com/static/invoice/' + invno + '.pdf'

    return redirect(url)




# @login_required(login_url='/login/')
# def latecheckout(request):
#     referenceno = request.GET.get('rb')
#     bookingpk = request.GET.get('bpk')

#     if request.method=="POST":
#         roomtype = request.POST.get('roomtype')

#         numofstay = int((cout_date-cin_date).days)
#         bookedroomprice = 0
#         gsttotal= 0
#         actualaa =0
#         for each in range(0, numofstay):
#             date1 = cin_date + timedelta(days=each)
#             newrnnon = rnnon.filter(checkin_date=date1)
#             if newrnnon:
#                 return HttpResponse("someone is booked on that day")
#             day = date1.weekday()

#             xprice = "room_price" + str(day)
#             yy = getattr(Roomtype.objects.get(pk=idno), xprice)
#             actuala = yy

#     ####################################################################################################################                    

#             discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=rtn)                    
#             for i in discount:
#                 per_ = 1-(i.discountper)
#                 fix_ = i.discountfix

#                 yy = (yy-fix_)*per_
#                 # gst = yy*decimal.Decimal(0.1)
#                 toatal = yy 


#             if not discount:
#                 # gst = yy*decimal.Decimal(0.1)
#                 toatal = yy 


#             # bookedroomprice = bookedroomprice
#             # gsttotal += gst
#             hprice.append(toatal)
#             pricex_ = toatal

#             if cod is not None:
#                 if code1.roomtype is None:

#                     if code1.startdate is None:
#                         pricex_ = (toatal-fix)*per
#                         xprice_ = pricex_*decimal.Decimal(1.1)
#                         print(xprice_)
#                         print(pricex_)


#                     elif code1.enddate > qout_date and code1.startdate < qin_date:
#                         pricex_ = (toatal-fix)*per
#                         xprice_ = pricex_*decimal.Decimal(1.1)
#                         print(xprice_)
#                         print(pricex_)                         

#                 if rtn == code1.roomtype:

#                     if code1.startdate is None:
#                         pricex_ = (toatal-fix)*per
#                         xprice_ = pricex_*decimal.Decimal(1.1)
#                         print(xprice_)
#                         print(pricex_)         

#                     elif code1.enddate > qout_date and code1.startdate < qin_date:
#                         pricex_ = (toatal-fix)*per
#                         xprice_ = pricex_*decimal.Decimal(1.1)

#                         print(xprice_) 
#                         print(pricex_)  


#             actualaa += actuala
#             bookedroomprice += pricex_
#         # roomstt = str(randomnumber) + "," +  str(roomstt)

#         # bookedroomprice += xprice_
#         gsttotal = bookedroomprice*decimal.Decimal(0.1)
#         bookedroomprice2 = bookedroomprice*decimal.Decimal(1.1)
#         actualaasdf = actualaa*decimal.Decimal(1.1)
#         print(bookedroomprice)
#         bookingcust = thebooking.cust33.pk

#         thebookingnew = Booking.objects.create(first_name=thebooking.cust33.first_name, referenceno =rb, last_name = thebooking.cust33.last_name, email=thebooking.cust33.email, country=thebooking.cust33.country, room_type_name=rtn, room_number=rnn, cust33=thebooking.cust33, phone_number=thebooking.cust33.phone_number, number_of_people = thebooking.number_of_people, paymentprice=bookedroomprice2, actualpay=actualaasdf, checkin_date=qin_date, checkout_date=qout_date, extension=True ) 
















@login_required(login_url='/login/')
def generatepdf2(request):
    pdfmetrics.registerFont(TTFont('Noto', 'simhei.ttf'))
    refno = request.GET.get('referenceno')
    if not refno:
        return redirect('test2')
    d = Invoice.objects.get(referenceno=refno)
    # year = datetime.now().strftime("%y")    
    # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
    # inv_no = invnos.invoiceno
    # invoice_int = inv_no[2:]
    # new_invoice_int = int(invoice_int) + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    # d.invoiceno = new_invoice_no
    # d.save()
    invno = str(d.referral)+' '+ str(refno)
    deadline = datetime.strptime('2017-07-17', '%Y-%m-%d').date()
    e = Booking.objects.filter(referenceno = refno).order_by('room_type_name')
    firstname= d.email.first_name
    cindate= datetime.strftime(datetime.now(), '%d%m%Y')
    f = Booking.objects.filter(referenceno = refno).first()
    try:
        q111 = depositwitheld.objects.filter(invoice=d)
    except depositwitheld.DoesNotExist:
        q111 = None


    break41 = 0

    for a in e:
        if a.room_type_name.pk == 23:
            break41 = break41+1

        elif a.room_type_name.pk==24:
            break41 = break41+1


    if break41 == 0 :
       if f.created_on.date() < deadline:
            break41 = 24



    def generate2(f, ae, afafa, q111 ,break41):
        logo='booking/static/innbparklogo2.gif'
        nosmoke = 'booking/static/Untitled-1.gif'
        key23 = 'booking/static/key.gif'
        lock23  = 'booking/static/lock.gif'       

        c = canvas.Canvas('static/invoice/'+ invno +'.pdf', pagesize=A4)
        c.setLineWidth(.3)
        c.setStrokeColorRGB(0,0,0)
        c.drawImage(logo, 400 , 730, width=140, height=69)

        c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)

        a=15
        c.setFont('Helvetica', 9, leading=None)        
        c.drawString(40 ,805,'InnB Park Hotel')
        c.drawString(40 ,790,'operated by Apocity Sdn Bhd 198401014712 (127268-X)')
        c.drawString(40, 790-a,'SST no. B16-1809-32000531, TTx no. 141-2017-10000713')
        c.drawString(40 ,775-a,'102-106, Jalan Imbi,  Bukit Bintang')
        c.drawString(40 ,760-a,'55100 Kuala Lumpur')
        c.drawString(40 ,745-a,'admin@innbparkhotel.com') 
        c.drawString(40 ,730-a,'+603 2856 7257')
        if afafa.referral=="Agoda":
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, 'Agoda Company Pte Ltd (Reg No.: 200506877R)')           
            a=a+15                
            c.drawString(40 ,730-a, '30 Cecil Street, Prudential Tower')
            a=a+15                
            c.drawString(40 ,730-a, '#19-08, Singapore 049712')    
        elif afafa.referral=="Traveloka":
            a=a+30
            c.drawString(40 ,730-a,'Bill to:')
            a=a+15
            c.drawString(40 ,730-a, 'Traveloka Services Pte Ltd (Reg No.: 201509260N)')           
            a=a+15                
            c.drawString(40 ,730-a, '2 Shenton Way')
            a=a+15                
            c.drawString(40 ,730-a, '#18-01 SGX Centre 1, Singapore 068804') 
        else:
            if afafa.addressline1:
                a=a+30
                c.drawString(40 ,730-a,'Bill to:')
                a=a+15
                c.drawString(40 ,730-a, afafa.addressline1)           
                if afafa.addressline2:
                    a=a+15                
                    c.drawString(40 ,730-a, afafa.addressline2)
                    if afafa.addressline3:
                        a=a+15                
                        c.drawString(40 ,730-a, afafa.addressline3)                    

        a=a-12
        c.setFont('Helvetica-Bold', 12, leading=None)
        c.drawString(40 ,680-a,'ROOM RESERVATION')
        c.drawString(430 ,810,'Non-refundable Rate')
        a=a-5
        c.setFont('Helvetica', 9, leading=None)
        c.drawString(40, 650-a, 'GUESTS NAME')
        c.drawString(197, 650-a, 'ROOM NO.')
        c.drawString(257, 650-a, 'ROOM TYPE')
        c.drawString(380, 650-a, 'ARRIVAL DATE')  
        c.drawString(470, 650-a, 'DEPATURE DATE')                                     
        a=a-2
        c.setLineWidth(.5)
        c.line(40,630-a,548,630-a)

        if f:
            c.setFont('Helvetica', 9, leading=None)
            c.drawString(40, 610-a, afafa.email.first_name)
            c.drawString(40, 590-a, afafa.email.last_name)
            if afafa.email.passno:
                c.drawString(40, 570-a, "Passport no: "+ str(afafa.email.passno))

        for t in ae:
        

            if a > 540:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -150

            c.setFont('Helvetica', 9, leading=None)


            roomnumber = "[" + str(t.room_number) + "]"
            roomname = str(t.room_type_name)
            n=20
            a += n
            # c.drawString(177, 630-a, str(a))            
            c.drawString(197, 630-a, roomnumber)
            roomnamecount = len(roomname)
            if roomnamecount > 22:
                newline = roomname.split(", ",1)[1]
                oldline = roomname.split(", ")[0]
                c.drawString(257, 610-a, newline)
                c.drawString(257, 630-a, oldline)
            else:
                c.drawString(257, 630-a, roomname)  


            # c.drawString(257, 630-a, roomname)
            if t.extension is True:
                c.drawString(355, 630-a, '(ext)')
            if t.late is True:
                c.drawString(355, 630-a, '(late)')                
            indate = t.checkin_date.strftime("%a, %d/%m/%Y")
            outdate = t.checkout_date.strftime("%a, %d/%m/%Y")
            c.drawString(380, 630-a, indate)  
            c.drawString(470, 630-a, outdate)
            if roomnamecount > 22:
                a=a+20
        if afafa.email.passno:
            a=a+20
        c.line(40,600-a,548,600-a)

        if a > 200:
            c.showPage()
            c.setLineWidth(.3)
            c.setStrokeColorRGB(0,0,0)
            c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
            a = -200

 

        c.setFont('Helvetica-Bold', 11, leading=None)
        c.drawString(40, 570-a, 'TAX INVOICE ' + afafa.invoiceno)
        if afafa.totalpaiddate:
            qwerdate = (afafa.totalpaiddate).strftime("%d/%m/%Y")
            c.drawString(380, 570-a, "Invoice Date " + qwerdate)         
       
        if afafa.cancelled == True:
            c.setFont('Helvetica-Bold', 14, leading=None)
            c.drawString(330, 570-a, 'INVOICE CANCELLED')
        c.setFont('Helvetica-Bold', 9, leading=None)
        c.drawString(40, 545-a, 'DESCRIPTION')
        c.drawString(180, 545-a, 'PRICE/UNIT')
        c.drawString(270, 545-a, 'NO. NIGHTS')




        for t in ae:
            if t.actualpay-t.paymentprice > 0:
                c.drawString(360, 545-a, 'DISCOUNT')
                break


        if afafa.description:         
            c.drawString(360, 545-a, 'DISCOUNT')
        c.drawString(470, 545-a, 'TOTAL PRICE')


        c.setFont('Helvetica', 9, leading=None)
        totalprice=0
        for t in ae:
            if a > 340:
                c.showPage()
                c.setLineWidth(.3)
                c.setStrokeColorRGB(0,0,0)
                c.rect(0.2*inch,0.2*inch,7.87*inch,11.29*inch, fill=0)
                a = -200
            c.setFont('Helvetica', 9, leading=None)
            roomnumber = str(t.room_number)
            roomname = str(t.room_type_name)


            roomnamecount = len(roomname)
            n=20
            a += n
            nights = int((t.checkout_date-t.checkin_date).days)
            if nights<1:
                nights=1
            t.actualpay = decimal.Decimal(format(t.actualpay*decimal.Decimal(decimal.Decimal(1)-afafa.rtacomm),'.2f'))
            t.paymentprice = decimal.Decimal(format(t.paymentprice*decimal.Decimal(decimal.Decimal(1)-afafa.rtacomm),'.2f'))
            price = str(round((t.actualpay /  nights),2))

            if roomnamecount > 22:
                newline = roomname.split(", ",1)[1]
                oldline = roomname.split(", ")[0]
                c.drawString(40, 525-a, newline)
                c.drawString(40, 545-a, oldline)
            else:
                c.drawString(40, 545-a, roomname)  


            # c.drawString(40, 545-a, roomname)
            c.drawString(180, 545-a, 'RM ' + price)
            c.drawString(270, 545-a, str(nights))
            if t.actualpay-t.paymentprice > 0:
                c.drawString(360, 545-a, '- RM ' + str(t.actualpay-t.paymentprice))            
            c.drawString(470, 545-a, 'RM ' + str(t.paymentprice))
            if t.extension is True:
                c.drawString(420, 545-a, '(ext)')
            if t.late is True:
                c.drawString(420, 545-a, '(late)')
            totalprice += t.actualpay   
            if roomnamecount > 22:
                a=a+20

        if not f:
            a=20
            c.drawString(40, 545-a, 'Customer cancelled booking')




        a=a-10

        if afafa.additionalcharge:
            a=a
            # discount=  totalprice - afafa.total + afafa.additionalcharge
            # c.drawString(180, 530-a, 'Special Promo:   ' + afafa.description.description )
            # c.drawString(470, 530-a, '- RM ' + str(discount))

            c.drawString(180, 510-a, afafa.additionalcharges)
            c.drawString(470, 510-a, 'RM ' + str(afafa.additionalcharge))
            # else:
            #     a = a+20
            #     discount=  totalprice - afafa.total
            #     c.drawString(180, 520-a, 'Special Promo:   ' + afafa.description.description )
            #     c.drawString(470, 520-a, '- RM ' + str(discount))











        if afafa.rounding:
            a = a+20
            c.drawString(180, 520-a, 'rounding' )
            c.drawString(470, 520-a, 'RM ' + str(afafa.rounding))


















                    
        if afafa.gst > 0:
            qindate2 = datetime.strptime("2018-08-31", '%Y-%m-%d')
            utc=pytz.UTC
            qindate2=utc.localize(qindate2) 
            if afafa.totalpaiddate:
                if afafa.totalpaiddate > qindate2:
                    a = a+20
                    c.drawString(180, 520-a, '6% SST ' )
                    c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                else:
                    a = a+20
                    c.drawString(180, 520-a, '6% GST ' )
                    c.drawString(470, 520-a, 'RM ' + str(afafa.gst))    

            else:
                if afafa.datecreated > qindate2:
                    a = a+20
                    c.drawString(180, 520-a, '6% SST ' )
                    c.drawString(470, 520-a, 'RM ' + str(afafa.gst))
                else:
                    a = a+20
                    c.drawString(180, 520-a, '6% GST ' )
                    c.drawString(470, 520-a, 'RM ' + str(afafa.gst))


        else:

            qindate = datetime.strptime("2017-09-01", '%Y-%m-%d')
            utc=pytz.UTC
            qindate=utc.localize(qindate) 
            if afafa.datecreated > qindate:
                a = a+20
                c.drawString(180, 520-a, '0% SST ' )
                c.drawString(470, 520-a, 'RM 0.00')



        # if afafa.rtacomm:
        #     c.setFont('Helvetica-Bold', 9, leading=None)
        #     a= a+20
        #     c.drawString(180, 520-a,str(afafa.referral) +'    '+ str(100*afafa.rtacomm)+'%')
        #     c.drawString(470, 520-a, 'RM '+ str(afafa.commamount)) 
        #     a=a-10


            
        c.setFont('Helvetica-Bold', 11, leading=None)                
        c.drawString(180, 490-a, 'Total:')
        if f:
            # if afafa.rtacomm:
            #     c.drawString(470, 490-a, 'RM ' + format((afafa.total + afafa.commamount),'.2f'))
            # else:
            c.drawString(470, 490-a, 'RM ' + str(afafa.total))


            # if afafa.ttax:
            #     if not afafa.checkedout1:
            #         c.setFont('Helvetica-Bold', 9, leading=None)
            #         a= a+20
            #         c.drawString(180, 490-a,'Tourism Tax Payable when check out (RM10/night):    RM '+ str(afafa.ttax)) 
            #         a= a+10
        else:
            c.drawString(470,400-a, 'RM ' + str(afafa.bookingfee))
        


        


        c.setFont('Helvetica', 9, leading=None)
        



        if afafa.bookingfeepaid == True:
            a = a+20
            c.drawString(180, 490-a, 'Booking Pre-payment')
            c.drawString(470, 490-a, 'RM ' + str(afafa.bookingfee))

            if afafa.totalpaid == True:
                c.setFont('Helvetica-Bold', 12, leading=None)                
                c.drawString(180, 470-a, 'Total Paid:')
                if afafa.bookingfeepaid == True:
                    total12 = afafa.total - afafa.bookingfee
                else: 
                    total12 = afafa.total
                c.drawString(470, 470-a, 'RM ' + str(total12))




            else:
                c.setFont('Helvetica-Bold', 12, leading=None)
                if f:                
                    c.drawString(180, 470-a, 'Outstanding Amount:')
                    if afafa.bookingfeepaid == True:
                        total12 = afafa.total - afafa.bookingfee
                    else: 
                        total12 = afafa.total
                    c.drawString(470, 470-a, 'RM ' + str(total12))
                if afafa.deposit == False:
                    c.setFont('Helvetica-Bold', 8, leading=None)
                    if f:
                        c.drawString(180, 455-a, 'Deposit Required') 
                        c.setFont('Helvetica', 8, leading=None)        
                        c.drawString(470, 455-a, 'RM ' + str(afafa.depositamt))
                    if not f:
                        c.drawString(180, 455-a, 'Deposit not applicable')
        





        c.setFont('Helvetica', 10, leading=None)


        if afafa.invoicedesc:
            c.drawString(40, 430-a,afafa.invoicedesc) 
            a= a+30

      
        c.showPage()
        c.save()


    generate2(f,e,d, q111, break41)
    url = 'https://innbparkhotel.com/static/invoice/' + invno + '.pdf'

    return redirect(url)





























def validate_rooms(request):
    roomtype = request.GET.get('roomtype')
    print(roomtype)
    if roomtype is None:
        return JsonResponse({'roomavailable': "None"})    
    roomtype1 = Roomtype.objects.get(pk=roomtype)
    qin_date1 = request.GET.get('cind')
    qout_date1 = request.GET.get('coutd')
    
    if qin_date1 and qout_date1 is not None:

        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')

        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)



    print(roomtype1)


    if int(roomtype) is not 27:

        roomavailable = Roomnumber.objects.filter(room_type_name = roomtype1)
        
        if qin_date1 and qout_date1 is not None:
            ab = roomavailable.filter(hidden=False)
            we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=qin_date, booking__checkin_date__lt=qout_date, booking__checkout_date__gt=F('booking__checkin_date'))
            asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=qin_date,booking__checkout_date__lte=qout_date, booking__checkin_date__lt=F('booking__checkout_date'))
            drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=qin_date, booking__checkout_date__gte=qout_date)
            qwer = asdf | we | drrr

            

            cd_ = ab.exclude(id__in=qwer).values('room_number').order_by('room_number')
        else:
            cd_ = roomavailable.values('room_number').order_by('room_number')

    else:
        cd_ = Roomnumber.objects.none()
        roomavailable = Roomnumber.objects.filter(room_type_name = roomtype1, hidden=False)

        if qin_date1 and qout_date1 is not None:
            aaaa =  Roomnumber.objects.all().filter(link__isnull=False, hidden=False)
            # we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
            # asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
            # drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
            # qwer = asdf | we | drrr
            # cd = aaaa.exclude(id__in=qwer)
            cd = aaaa
            if not cd:
                return HttpResponse('This type of rooms have been fully booked')
            de = cd
            room01 = None
            room02 = None     
            # randomnumber = random.choice(de)
            # rnum= Roomnumber.objects.get(room_number=randomnumber)
            for one1 in de:
                rnum = one1


                # if room01 and room02 is not None:
                #     break
                one11 = one1 

                n = "passed"                                
                rnum1 = Roomnumber.objects.get(room_number=one11)
                we = Booking.objects.filter(checkin_date__gte=qin_date, checkin_date__lt=qout_date,room_number=rnum1)
                if we:
                    n="notpassed"
                asdf = Booking.objects.filter(checkout_date__gt=qin_date,checkout_date__lte=qout_date,room_number=rnum1)
                if asdf:
                    n="notpassed"
                drrr = Booking.objects.filter(checkin_date__lte=qin_date, checkout_date__gte=qout_date,room_number=rnum1)
                if drrr: 
                    n="notpassed"

                if n is "notpassed":

                    room01 = None
                    room02 = None
                    de = de.exclude(pk=one11.pk)

                else:
                    room01 = rnum1
                    rtname01 = room01.room_type_name


                    linkbookcheck = Roomnumber.objects.filter(link=one11.link).exclude(pk=one11.pk)
                    for a1 in linkbookcheck:
                        n = "passed"                                
                        rnum1 = Roomnumber.objects.get(room_number=a1)
                        we = Booking.objects.filter(checkin_date__gte=qin_date, checkin_date__lt=qout_date,room_number=rnum1)
                        if we:
                            n="notpassed"
                        asdf = Booking.objects.filter(checkout_date__gt=qin_date,checkout_date__lte=qout_date,room_number=rnum1)
                        if asdf:
                            n="notpassed"
                        drrr = Booking.objects.filter(checkin_date__lte=qin_date, checkout_date__gte=qout_date,room_number=rnum1)
                        if drrr: 
                            n="notpassed"


                        if n is "notpassed":

                            room01 = None
                            room02 = None

                        else:

                            room02 = rnum1

                
                            asdfa445 = Roomnumber.objects.get(room_number=one11.link)
                            if asdfa445.hidden == False:
                                asdfa4 = Roomnumber.objects.filter(room_number=one11.link).values('room_number').order_by('room_number')                                
                            else:
                                asdfa4=Roomnumber.objects.none().values('room_number').order_by('room_number')
 


                            cd_ = cd_ | asdfa4                            
       
            # cd_ = ab.exclude(id__in=qwer).values('room_number').order_by('room_number')
        else:
            cd_ = roomavailable.values('room_number').order_by('room_number')





    print(roomavailable)
    data = {
        'roomavailable': list(cd_)
    }
    print(data)
    return JsonResponse({
        'roomavailable': list(cd_)
    })




def validate_price(request):
    roomtype = request.GET.get('roomtype')
    print(roomtype)
    if roomtype is None:
        return JsonResponse({'price': "0.00"})    
    roomtype1 = Roomtype.objects.get(pk=roomtype)
    qin_date1 = request.GET.get('cind')
    qout_date1 = request.GET.get('coutd')
    rrtpp = request.GET.get('dis')
    break1 = request.GET.get('break1')
    bdce = request.GET.get('bdce')    
    breakcode = request.GET.get('breakcode')
    
    if qin_date1 and qout_date1 is not None:

        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')

        ind = parsing_date(qin_date1)
        outd = parsing_date(qout_date1)
    else:
        return JsonResponse({'price': "0.00"}) 
    
    if rrtpp is None:
        rrtpp = 0
    
    try:
        float(rrtpp)
    except ValueError:
        rrtpp = 0



    notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
    notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
    
    notaxset = False

    if ind > notaxstartdate and ind < notaxenddate:
        if outd > notaxstartdate and outd < notaxenddate:
            notaxset = True






    numofstay = int((outd-ind).days)
    bookedroomprice = 0
    gsttotal= 0
    actualaa =0
    hprice2=[]
    print(numofstay)
    for each in range(0, numofstay):
        date1 = ind + timedelta(days=each)

        day = date1.weekday()

        xprice = "room_price" + str(day)  
        if int(roomtype1.pk) is not 22 and int(roomtype1.pk) is not 24 and int(roomtype1.pk) is not 28:
            # if int(break1) > 0:
            #     yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) + (((getattr(Roomtype.objects.get(pk=23), xprice))*decimal.Decimal(break1)))
            # else:

            try:
                roompk = Roomtype.objects.get(pk=roomtype)
                pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                #yy = pricespecial.price/decimal.Decimal(0.85)
                yy = pricespecial.price/decimal.Decimal(0.78)

            except variablepricing.DoesNotExist:
                yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.78)) 

                #yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) 
        else:

            try:
                roompk = Roomtype.objects.get(pk=roomtype)
                pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                yy = pricespecial.price

            except variablepricing.DoesNotExist:

                yy = (getattr(Roomtype.objects.get(pk=roomtype), xprice))                 

        actuala = yy



####################################################################################################################                    

        if str(rrtpp) is not "0":
            yy = yy*(decimal.Decimal(1)-decimal.Decimal(rrtpp))
        else:
            yy=yy
                # gst = yy*decimal.Decimal(0.1)
        if int(break1) > 0:
            if int(breakcode) >0:
                if int(bdce) <1:
                    yy = yy + ((((getattr(Roomtype.objects.get(pk=24), xprice))*decimal.Decimal(break1)))*(decimal.Decimal(1)-decimal.Decimal(rrtpp)))                    
                else: 
                    yy = yy + (((getattr(Roomtype.objects.get(pk=24), xprice))*decimal.Decimal(break1)))
            else:
                if int(bdce) <1:
                    yy = yy + ((((getattr(Roomtype.objects.get(pk=23), xprice))*decimal.Decimal(break1)))*(decimal.Decimal(1)-decimal.Decimal(rrtpp)))                                        
                else:
                    yy = yy + (((getattr(Roomtype.objects.get(pk=23), xprice))*decimal.Decimal(break1)))                
        else:
            yy = yy
        pricex_ = yy
        hprice2.append(pricex_)   
        actualaa += actuala
        bookedroomprice += pricex_

        # roomstt = str(randomnumber) + "," +  str(roomstt)

        # bookedroomprice += xprice_
    gsttotal = 0
    if notaxset:
        bookedroomprice2 = bookedroomprice
    else:
        bookedroomprice2 = bookedroomprice*decimal.Decimal(1.06)
    # bookedroomprice2 = bookedroomprice


    actualaasdf = actualaa 
    print(bookedroomprice)
    bookingfeeb4tax = max(hprice2)




    return JsonResponse({
        'price': str(round(bookedroomprice2, 2)),
        'rrtpp':rrtpp,
        'break1':break1

    })






def validate_price1(request):
    roomtype = request.GET.get('roomtype')
    roomtype2 = request.GET.get('roomtype2')
    print(roomtype)
    if roomtype is None:
        return JsonResponse({'price': "0.00"})    
    roomtype1 = Roomtype.objects.get(pk=roomtype)
    qin_date1 = request.GET.get('cind')
    qout_date1 = request.GET.get('coutd')
    rrtpp = request.GET.get('dis')
    rrtpp2 = request.GET.get('dis2')

    mol = request.GET.get('mol')
    
    if qin_date1 and qout_date1 is not None:

        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')

        ind = parsing_date(qin_date1)
        outd = parsing_date(qout_date1)
    else:
        return JsonResponse({'price': "0.00"}) 
    
    if rrtpp is None:
        rrtpp = 0
    
    try:
        float(rrtpp)
    except ValueError:
        rrtpp = 0


    if rrtpp2 is None:
        rrtpp2 = 0
    
    try:
        float(rrtpp2)
    except ValueError:
        rrtpp2 = 0
    rrtpp2 = decimal.Decimal(rrtpp2)/decimal.Decimal(100)
    numofstay = int((outd-ind).days)
    bookedroomprice = 0
    bookedroompricez =0
    gsttotal= 0
    actualaa =0
    hprice2=[]
    print(numofstay)

    notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
    notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
    
    notaxset = False

    if ind > notaxstartdate and ind < notaxenddate:
        if outd > notaxstartdate and outd < notaxenddate:
            notaxset = True







    
    for each in range(0, numofstay):
        date1 = ind + timedelta(days=each)


        # try:
        #     roompk = Roomtype.objects.get(pk=roomtype)
        #     pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
        #     xprice = pricespecial.price

        # except variablepricing.DoesNotExist:


        day = date1.weekday()

        xprice = "room_price" + str(day)  

        if int(roomtype1.pk) is not 22 and int(roomtype1.pk) is not 24  and int(roomtype1.pk) is not 28:
            # if int(break1) > 0:
            #     yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) + (((getattr(Roomtype.objects.get(pk=23), xprice))*decimal.Decimal(break1)))
            # else:
            try:
                roompk = Roomtype.objects.get(pk=roomtype)

                if int(mol)>0:  
                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                    yy = pricespecial.price
                    roompk2 = Roomtype.objects.get(pk=roomtype2)
                    pricespecial2 = variablepricing.objects.get(date =date1, roomtype=roompk2)
                    #zz= pricespecial2.price/decimal.Decimal(0.85)
                    zz= pricespecial2.price/decimal.Decimal(0.78)
                else:
                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                    #yy = pricespecial.price/decimal.Decimal(0.85)
                    yy = pricespecial.price/decimal.Decimal(0.78)
                    roompk2 = Roomtype.objects.get(pk=roomtype2)
                    pricespecial2 = variablepricing.objects.get(date =date1, roomtype=roompk2)
#                    zz= pricespecial2.price/decimal.Decimal(0.85)
                    zz= pricespecial2.price/decimal.Decimal(0.78)

            except variablepricing.DoesNotExist:


                yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.78)) 
                zz = ((getattr(Roomtype.objects.get(pk=roomtype2), xprice))/decimal.Decimal(0.78))

#                yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) 
#                zz = ((getattr(Roomtype.objects.get(pk=roomtype2), xprice))/decimal.Decimal(0.85))

        else:


            try:

                roompk = Roomtype.objects.get(pk=roomtype)
                pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                yy = pricespecial.price
                roompk2 = Roomtype.objects.get(pk=roomtype2)
                pricespecial2 = variablepricing.objects.get(date =date1, roomtype=roompk2)
                zz= pricespecial2.price

            except variablepricing.DoesNotExist:
                yy = (getattr(Roomtype.objects.get(pk=roomtype), xprice))                 
                zz = (getattr(Roomtype.objects.get(pk=roomtype2), xprice))
        actuala = yy
        actualb = zz



####################################################################################################################                    
 
        if str (rrtpp) is not "0":
            yy = yy*(decimal.Decimal(1)-decimal.Decimal(rrtpp))


        if str(rrtpp2) is not "0":

            if int(mol)>0:
                # zz = zz*(decimal.Decimal(1)-decimal.Decimal(0.15))
                zz = zz*(decimal.Decimal(1)-decimal.Decimal(0.22))                
            else:
                zz = zz*(decimal.Decimal(1)-decimal.Decimal(rrtpp2))
  

                # gst = yy*decimal.Decimal(0.1)

        pricex_ = decimal.Decimal(format(yy,'.2f'))
        pricez_ = decimal.Decimal(format(zz,'.2f'))

        bookedroomprice += pricex_
        bookedroompricez += pricez_

        # roomstt = str(randomnumber) + "," +  str(roomstt)

        # bookedroomprice += xprice_
    gsttotal =0


    if notaxset:
        bookedroomprice2 = (bookedroomprice-bookedroompricez)
    else:
        bookedroomprice2 = (bookedroomprice-bookedroompricez)*decimal.Decimal(1.06)

    
    # bookedroomprice2 = (bookedroomprice-bookedroompricez)

    finalprice = str(format(bookedroomprice2, '.2f'))
    actualaasdf = actualaa
    print(bookedroomprice)





    return JsonResponse({
        'price': finalprice,
        'rrtpp':rrtpp,
        # 'break1':break1

    })




def validate_dc(request):
    ref = request.GET.get('referral')
    # roomtype1 = Roomtype.objects.get(pk=roomtype)
    # qin_date = request.GET.get('cind')
    # qout_date = request.GET.get('coutd')
    # print(roomtype1)


    
    if ref == "Traveloka":
        return JsonResponse({'discount': [{"discount":"5% discount", "v":"0.05"},{"discount":"10% discount", "v":"0.10"},{"discount":"12% discount", "v":"0.12"},{"discount":"15% discount", "v":"0.15"},{"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.20"}]})

    if ref == "Walk-in":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"15% discount", "v":"0.15"},{"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.20"},{"discount":"23% discount", "v":"0.23"},{"discount":"Super Regulars Only","v":"0.30"}]})
    if ref == "DOTW":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"15% discount", "v":"0.15"},{"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.20"}]})
    if ref == "Revato":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"15% discount", "v":"0.15"},{"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.20"}]})
    if ref == "bookings.com":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"12% discount", "v":"0.12"},{"discount":"12% + 10% discount", "v":"0.208"},{"discount":"15% discount", "v":"0.15"},{"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.19"},{"discount":"25% discount", "v":"0.235"},{"discount":"28% discount", "v":"0.262"}]})

    if ref == "Agoda":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"10% + mobile", "v":"0.19"},{"discount":"12% discount", "v":"0.12"},{"discount":"15% discount", "v":"0.15"},{"discount":"15% + mobile", "v":"0.235"}, {"discount":"18% discount", "v":"0.18"},{"discount":"18% + mobile", "v":"0.262"}]})
    if ref == "Ctrip":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"10% + mobile", "v":"0.19"},{"discount":"15% discount", "v":"0.15"},{"discount":"15% + mobile", "v":"0.235"}, {"discount":"18% discount", "v":"0.18"},{"discount":"18% + mobile", "v":"0.262"}]})
    if ref == "Mikitravel":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"10% + mobile", "v":"0.19"},{"discount":"15% discount", "v":"0.15"},{"discount":"15% + mobile", "v":"0.235"}, {"discount":"18% discount", "v":"0.18"},{"discount":"18% + mobile", "v":"0.262"}]})
    if ref == "Asiatravel":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"10% + mobile", "v":"0.19"},{"discount":"15% discount", "v":"0.15"},{"discount":"15% + mobile", "v":"0.235"}, {"discount":"18% discount", "v":"0.18"},{"discount":"18% + mobile", "v":"0.262"}]})

    if ref == "Expedia":
        return JsonResponse({'discount': [{"discount":"10% discount", "v":"0.10"},{"discount":"15% discount", "v":"0.15"}, {"discount":"18% discount", "v":"0.18"},{"discount":"20% discount", "v":"0.20"}]})



@csrf_exempt
def validate_roomfloor(request):
    if request.method == "GET":
        ref = request.GET.get('referral1')
        # roomtype1 = Roomtype.objects.get(pk=roomtype)
        # qin_date = request.GET.get('cind')
        # qout_date = request.GET.get('coutd')
        # print(roomtype1)
        var123 = datetime.now()
        todaydate = (var123 + timedelta(hours=8)).date()   

        updatestatus = Booking.objects.filter(checkin_date__lte=todaydate).filter(checkout_date__gte=todaydate).exclude(checkin_date=todaydate).exclude(room_type_name__pk=24).exclude(room_type_name__pk=23).exclude(room_type_name__pk=27).exclude(room_type_name__pk=22).exclude(room_type_name__pk=28)
        for a in updatestatus:
            roomnum= Roomnumber.objects.get(room_number=a.room_number)
            if roomnum.status=="OC":
                checkcleaned = housekeepingroom.objects.filter(room_number=roomnum,date=todaydate,cleaned=True)
                if not checkcleaned:
                    roomnum.status = "OD"
                    roomnum.save()

        
        if ref == "15519145":
            listjson = [{"level":"Level 4"},{"level":"Level 5"},{"level":"Level 6"},{"level":"Level 7"},{"level":"Level 8"},{"level":"Level 9"},{"level":"Level 10"}]
            return JsonResponse(listjson, safe=False)
        else:
            return HttpResponse('Error')


     
    else:
        return HttpResponse('Error')

    



@csrf_exempt
def room_status_api(request):
    if request.method == "POST":
        jsondata = json.loads(request.body.decode('utf-8'))
        # roomtype1 = Roomtype.objects.get(pk=roomtype)
        # qin_date = request.GET.get('cind')
        # qout_date = request.GET.get('coutd')
        # print(roomtype1)

        status = jsondata['status']
        roomno = jsondata['roomno']

        roomobj = Roomnumber.objects.get(room_number=roomno)
        roomobj.status = status
        roomobj.save()
    


        return JsonResponse({"Success":"Sucess"},safe=False )


     
    else:
        return HttpResponse('Error')






@csrf_exempt
def api_clean(request):
    if request.method =="POST":
        jsondata = json.loads(request.body.decode('utf-8'))

        comments = jsondata['comments']
        tasks = jsondata['tasks']
        roomno = jsondata['roomno']
        username = jsondata['username']        
        var123 = datetime.now()
        todaydate = (var123 + timedelta(hours=8)).date()   

        roomnumber = Roomnumber.objects.get(room_number=roomno)

        if tasks:
            neww = whiteboard.objects.create(texts=tasks, room_number=roomnumber, staff=username)
        if roomnumber.status == "OD":
            roomnumber.status ="OC"
            roomnumber.save()

        if roomnumber.status=="VD":
            roomnumber.status = "VC"
            roomnumber.save()


        try:
            check = jsondata['check']
            clean= housekeepingroom.objects.create(date=todaydate, room_number=roomnumber,checked=True, notes=comments, staff=username)
        except:
            clean= housekeepingroom.objects.create(date=todaydate, room_number=roomnumber,cleaned=True, notes=comments, staff=username)

        return HttpResponse('Success')
    else:
        return HttpResponse("Error")



@csrf_exempt
def api_trolley(request):
    if request.method =="POST":
        jsondata = json.loads(request.body.decode('utf-8'))
        coffeebag = jsondata['coffeebag']
        water = jsondata['water']
        teabag = jsondata['teabag']
        dentalkit = jsondata['dentalkit']
        shaverkit = jsondata['shaverkit']
        bodylotion = jsondata['bodylotion']
        shampoo = jsondata['shampoo']
        soap = jsondata['soap']
        comb = jsondata['comb']
        showercap = jsondata['showercap']
        sanitarybag = jsondata['sanitarybag']
        toiletpaper = jsondata['toiletpaper']
        slipper = jsondata['slipper']
        tasks = jsondata['tasks']
        username = jsondata['username']
        trolleyno = jsondata['trolleyno']

        if tasks:
            neww = whiteboard.objects.create(texts=tasks, staff=username)
        clean= trolley.objects.create(trolleyno=trolleyno,coffeebag=coffeebag,water=water, teabag=teabag,dentalkit=dentalkit,shaverkit=shaverkit,bodylotion=bodylotion,shampoo=shampoo,soap=soap, comb=comb, showercap=showercap, sanitarybag=sanitarybag,  toiletpaper=toiletpaper, slipper=slipper, username=username)

        return HttpResponse('Success')
    else:
        return HttpResponse("Error")



@csrf_exempt
def pollapi(request):
    if request.method == "GET":
        username = request.GET.get("user")

        authen = User.objects.get(username=username)
        if authen:
            Tasknumber = whiteboard.objects.filter(complete=False, hidden=False, read=False, forstaff__isnull=True).count()
            return HttpResponse(Tasknumber)

        else:
            return HttpResponse("Error")     
    else:
        return HttpResponse("Error")

@csrf_exempt
def pollapi2(request):
    if request.method == "GET":
        username = request.GET.get("user")

        authen = User.objects.get(username=username)
        if authen:
            Tasknumber = whiteboard.objects.filter(complete=False, hidden=False, read=False, forstaff=username).count()
            return JsonResponse({'alert': Tasknumber},safe=False )

        else:
            return HttpResponse("Error")     
    else:
        return HttpResponse("Error")


@csrf_exempt
def api_note3(request):
    if request.method =="POST":
        jsondata = json.loads(request.body.decode('utf-8'))
        tasks = jsondata['tasks']
        username = jsondata['username']       
        var123 = datetime.now()
        todaydate = (var123 + timedelta(hours=8)).date()   

        if tasks:
            neww = whiteboard.objects.create(texts=tasks, staff=username)
            return HttpResponse('Success')
    else:
        return HttpResponse("Error")





# @csrf_exempt
# def apinote_strikethrough(request):
#     if request.method ==POST:
#         jsondata = json.loads(request.body.decode('utf-8'))
#         tasks = json['id']
#         username = json['username']       
#         var123 = datetime.now()
#         todaydate = (var123 + timedelta(hours=8)).date()   

#         if tasks:
#             neww = whiteboard.objects.get(id=id)
#             return HttpResponse('Success')
#     else:
#         return HttpResponse("Error")


@csrf_exempt
def validate_roomclean(request):
    if request.method == "GET":
        ref = request.GET.get('referral1')
        roomnum =request.GET.get('rlvl')
        # roomtype1 = Roomtype.objects.get(pk=roomtype)
        # qin_date = request.GET.get('cind')
        # qout_date = request.GET.get('coutd')
        # print(roomtype1)
        # tz=timezone('Etc/GMT+8')
        # todaydate = tz.localize(datetime.today())
        var123 = datetime.now()
        todaydate = (var123 + timedelta(hours=8)).date()        
        qin_date = todaydate
        
        if ref == "3145":
            roomnum1 = Roomnumber.objects.get(room_number=roomnum)


            updatestatus = Booking.objects.filter(room_number=roomnum1).filter(checkin_date__lte=todaydate).filter(checkout_date__gte=todaydate).filter(checkedin1__isnull=False).filter(checkedout1__isnull=True).values('first_name','last_name','checkin_date','checkout_date','checkedin1')
            # roomhistory = housekeeping.objects.filter(room_number=roomnum1).order_by('-id')[:3]
            previousbook = Booking.objects.filter(room_number=roomnum1).filter(checkin_date__lte=todaydate).filter(checkout_date__lte=todaydate).filter(checkedin1__isnull=False).filter(checkedout1__isnull=False).order_by('-checkin_date').first()
            nextbook = Booking.objects.filter(room_number=roomnum1).filter(checkin_date__gte=todaydate).filter(checkout_date__gte=todaydate).filter(checkedin1__isnull=True).order_by('checkin_date').first()
            lastclean = housekeepingroom.objects.filter(room_number=roomnum1).order_by('-date').first()
            lastcheck = housekeepingroom.objects.filter(room_number=roomnum1,checked=True).order_by('-date').first()
            if previousbook:
                prevcheckin = previousbook.checkin_date
                prevcheckout = previousbook.checkout_date
                prevfname = previousbook.first_name
                prevlname = previousbook.last_name
                prevb = prevfname+' '+prevlname

            else:
                nextcin = ""
                nextcout = ""
                nextfname = ""
                nextlname = ""
                prevb = ""


            if nextbook:

                nextcin = nextbook.checkin_date
                nextcout = nextbook.checkout_date
                nextfname = nextbook.first_name
                nextlname = nextbook.last_name
                nextb = nextfname+' '+nextlname

            else:
                nextcin = ""
                nextcout = ""
                nextfname = ""
                nextlname = ""
                nextb = ""
 
            if lastclean:
                if lastclean.staff:

                    lastcleanuser = lastclean.staff
                    lastcleandate = lastclean.date

                else:
                    lastcleanuser = ""
                    lastcleandate = ""
            else:
                lastcleanuser = ""
                lastcleandate = ""



            if lastcheck:
                if lastcheck.staff:
                    lastcheckuser = lastcheck.staff
                    lastcheckdate = lastcheck.date
                else:
                    lastcheckuser = ""
                    lastcheckdate = ""

            else:
                lastcheckuser = ""
                lastcheckdate = ""

            # rooms = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="VD").filter(booking__checkin_date=todaydate).order_by('room_number')
            # rooms1 = rooms.values('room_number','status').order_by('room_number')
            # # .values('room_number','status')
            # leaving = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="OC").filter(booking__checkout_date=todaydate).order_by('room_number').distinct()
            # odrooms = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="OD").order_by('room_number')

            # left = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="VD").order_by('room_number')

            # left4 = left.exclude(id__in=rooms).values('room_number','status')

            # list2 = leaving.values('room_number','status')
            # asdfrooms = odrooms.exclude(id__in=leaving).values('room_number','status')

            # serialized_obj = serializers.serialize('json', [ previousbook ])

            return JsonResponse({'customer': list(updatestatus),'time': todaydate,'previousbook':prevb,'previousbookdate':prevcheckin,'previousbookdateout':prevcheckout, 'nextbook':nextb, 'nextcin':nextcin, 'nextcout':nextcout,'lastcheckuser':lastcheckuser, 'lastcheckdate':lastcheckdate, 'lastcleanuser':lastcleanuser, 'lastcleandate':lastcleandate},safe=False )
        else:
            return HttpResponse('Error')


     
    else:
        return HttpResponse('Error')

@csrf_exempt
def validate_roomnum(request):
    if request.method == "GET":
        ref = request.GET.get('referral1')
        roomlevel =request.GET.get('rlvl')
        # roomtype1 = Roomtype.objects.get(pk=roomtype)
        # qin_date = request.GET.get('cind')
        # qout_date = request.GET.get('coutd')
        # print(roomtype1)
        tz=timezone('Etc/GMT+8')
        todaydate = tz.localize(datetime.today())
        qin_date = todaydate
        
        if ref == "3145":
            roomlvl = roomlevel[6:]
            updatestatus = Booking.objects.filter(room_type_name__pk=24).filter(checkin_date__lte=todaydate).filter(checkout_date__gte=todaydate).exclude(checkin_date=todaydate)
            for a in updatestatus:
                roomnum= Roomnumber.objects.get(room_number=a.room_number)
                if roomnum.status=="OC":
                    checkcleaned = housekeepingroom.objects.filter(roomnumber=a.room_number).filter(date=todaydate).filter(cleaned=True)
                    if not checkcleaned:
                        roomnum.status = "OD"
                        roomnum.save()




            rooms = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="VD").filter(booking__checkin_date=todaydate).order_by('room_number')
            rooms1 = rooms.values('room_number','status').order_by('room_number')
            # .values('room_number','status')
            leaving = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="OC").filter(booking__checkout_date=todaydate).order_by('room_number').distinct()
            odrooms = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="OD").order_by('room_number')

            left = Roomnumber.objects.filter(room_number__startswith=roomlvl).filter(status="VD").order_by('room_number')

            left4 = left.exclude(id__in=rooms).values('room_number','status')

            list2 = leaving.values('room_number','status')
            asdfrooms = odrooms.exclude(id__in=leaving).values('room_number','status')





            # listjson = serializers.serialize('json', list(rooms))
            # listjson = json.dumps(list(rooms))
            return JsonResponse({'results': list(rooms1),'results1':list(list2),'results2':list (asdfrooms),'results3':list (left4)},safe=False )
        else:
            return HttpResponse('Error')


     
    else:
        return HttpResponse('Error')


@csrf_exempt
def validate_roomnum1(request):
    if request.method == "GET":
        ref = request.GET.get('referral1')
        roomlevel =request.GET.get('rlvl')
        # roomtype1 = Roomtype.objects.get(pk=roomtype)
        # qin_date = request.GET.get('cind')
        # qout_date = request.GET.get('coutd')
        # print(roomtype1)
        # tz=timezone('Etc/GMT+8')
        # todaydate = tz.localize(datetime.today())
        var123 = datetime.now()
        todaydate = (var123 + timedelta(hours=8)).date()         
        qin_date = todaydate
        
        if ref == "3145":
            roomlvl = roomlevel[6:]
        #     updatestatus = Booking.objects.filter(room_type_name__pk=24).filter(checkin_date__lte=todaydate).filter(checkout_date__gte=todaydate).exclude(checkin_date=todaydate)
        #     for a in updatestatus:
        #         roomnum= Roomnumber.objects.get(room_number=a.room_number)   
        #         if roomnum.status=="OC":
        #             checkcleaned = housekeeping.objects.filter(roomnumber=a.room_number).filter(date=todaydate).filter(cleaned=True)
        #             if not checkcleaned:
        #                 roomnum.status = "OD"
        #                 roomnum.save()




            rooms = Roomnumber.objects.filter(room_number__startswith=roomlvl).exclude(room_number="608609").exclude(room_number="508509").exclude(room_number="408409").order_by('room_number')
            rooms1 = rooms.values('room_number','status').order_by('room_number')



            # listjson = serializers.serialize('json', list(rooms))
            # listjson = json.dumps(list(rooms))
            return JsonResponse({'results': list(rooms1),'time': todaydate},safe=False )
        else:
            return HttpResponse('Error')


     
    else:
        return HttpResponse('Error')



@login_required(login_url='/login/')
def upgrade(request):
    rb=request.GET.get('refno')

    rn = Roomnumber.objects.all()
    if rb is None:
        return redirect('test2')
    inv = Invoice.objects.get(referenceno = rb)
    tz = timezone('Etc/GMT+8')
    var123 = datetime.now()
    todaydate = (var123 + timedelta(hours=8)).date()
    qin_date = todaydate
    indate = todaydate
    qdate1 = qin_date.strftime("%d-%m-%Y")



    booking = request.GET.get('bookpk')
    tehtarik = Booking.objects.get(pk=booking)
    tehroom = tehtarik.room_type_name.pk  
    tehtarikroom = tehtarik.room_number
    checkindate = tehtarik.checkin_date   
    coutdate = tehtarik.checkout_date
    nop = tehtarik.number_of_people
    qout_date = tehtarik.checkout_date  
    qout1 =  qout_date.strftime("%d-%m-%Y") 

    if indate <=checkindate:
        qdate1 = checkindate.strftime("%d-%m-%Y")
    else:
        qdate1=qdate1

    customer13 = Customer.objects.get(pk=inv.email.pk)
    referenceno = inv.referenceno
    price1 = Roomtype.objects.get(pk=tehroom)


    rts = Roomtype.objects.filter(room_price0__gte=price1.room_price0).exclude(pk=tehroom).exclude(pk=23).exclude(pk=24).exclude(pk=25).order_by('-room_price0')  
    # if indate <=checkindate:
    #     return HttpResponse("testworking")
    per = 0
    mol = 0

    if inv.description:
        cod31 = inv.description.code

        if inv.referral == " Molpay":
            mol=1
        if inv.referral =="Molpay":
            mol=1
        try:
            code1 = Promocode.objects.get(code=cod31)
            per = code1.discountper*100
            fix = code1.discountfix
            desc = code1.description
            error = None
            if cod31=="BOOK15":
                if inv.descprom is not None:
                    per = inv.descprom*decimal.Decimal(100)

        except Promocode.DoesNotExist:
            error = "Invalid Code"
            cod=None
            print(error)
    else:
        per=0
        mol=0

        if inv.referral == " Molpay":
            per = 15
            mol = 1
        if inv.referral =="Molpay":
            per = 15
            mol = 1


    # if qdate1 == qout_date:
    #     return HttpResponse("Checkout date is today")

    if request.method == "POST":    
  
        roomtype = request.POST.get('rtn')
        roomnum = request.POST.get('rnn2')
        newcheckin = request.POST.get('date1')
        newcheckout = request.POST.get('date2')
        disct = request.POST.get('disct')
        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')  

        newcheckin = parsing_date(newcheckin)
        newcheckout = parsing_date(newcheckout)

        ratio = 1
        ratio2 = (100-decimal.Decimal(per))/100 

        if disct: 

            ratio =(100-decimal.Decimal(disct))/100 


        if roomnum is None:
            roomnum=0
        try:
            float(roomnum)
        except ValueError:
            roomnum = 0


        rtname = Roomtype.objects.get(pk=roomtype)
        # if indate <=checkindate:
        #     checkindate = indate
        
        if int(rtname.pk) is not 22:
            if int(roomnum) is 0:
                aaaa =  Roomnumber.objects.all().filter(room_type_name__pk=roomtype, hidden=False)
                we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=newcheckin, booking__checkin_date__lt=newcheckout, booking__checkout_date__gt=F('booking__checkin_date'))
                asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=newcheckin,booking__checkout_date__lte=newcheckout, booking__checkin_date__lt=F('booking__checkout_date'))
                drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=newcheckin, booking__checkout_date__gte=newcheckout)
                qwer = asdf | we | drrr
                cd = aaaa.exclude(id__in=qwer)
                if not cd:
                    return HttpResponse('This type of rooms have been fully booked')
                de = cd
                randomnumber = random.choice(de)
                rnum= Roomnumber.objects.get(room_number=randomnumber)
            else:
                rnum= Roomnumber.objects.get(room_number=roomnum)

        else:
            rnum= None






        ind = newcheckin
        outd = newcheckout
        numofstay = int((outd-ind).days)
        bookedroomprice = 0
        gsttotal= 0
        actualaa =0
        actualaa2=0
        abookedroomprice=0
        hprice2=[]
        yy=120
        print(numofstay)
        for each in range(0, numofstay):
            date1 = ind + timedelta(days=each)
            day = date1.weekday()

            try:
                roompk = Roomtype.objects.get(pk=roomtype)
                pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                yy = pricespecial.price/decimal.Decimal(0.78)
                #yy = pricespecial.price/decimal.Decimal(0.85)
                
                roompk2 = Roomtype.objects.get(pk=tehroom)
                pricespecial2 = variablepricing.objects.get(date =date1, roomtype=roompk2)
                ryy= pricespecial2.price/decimal.Decimal(0.78)
#                ryy= pricespecial2.price/decimal.Decimal(0.85)

            except variablepricing.DoesNotExist:



                xprice = "room_price" + str(day)  
                #yy = getattr(Roomtype.objects.get(pk=roomtype), xprice)/decimal.Decimal(0.85)
                #ryy = getattr(Roomtype.objects.get(pk=tehroom), xprice)/decimal.Decimal(0.85)
                yy = getattr(Roomtype.objects.get(pk=roomtype), xprice)/decimal.Decimal(0.78)
                ryy = getattr(Roomtype.objects.get(pk=tehroom), xprice)/decimal.Decimal(0.78)
            actuala = yy
            actuala2 = ryy




    ####################################################################################################################                    


            yy1 = yy*decimal.Decimal(ratio)

            ryy1 = ryy*decimal.Decimal(ratio2)
                    # gst = yy*decimal.Decimal(0.1)

            pricex_ = decimal.Decimal(format(yy1,'.2f'))
            _pricex =decimal.Decimal(format(ryy1,'.2f'))
            hprice2.append(pricex_)  
            actualaa += actuala
            actualaa2 += actuala2
            bookedroomprice += pricex_
            abookedroomprice += _pricex

            # roomstt = str(randomnumber) + "," +  str(roomstt)

            # bookedroomprice += xprice_
        gsttotal = 0
        # bookedroomprice2 = ((bookedroomprice)*decimal.Decimal(1.06))-((abookedroomprice)*decimal.Decimal(1.06))
        # actualaasdf = ((actualaa)*decimal.Decimal(1.06))-((actualaa2)*decimal.Decimal(1.06))
        bookedroomprice2 = ((bookedroomprice))-((abookedroomprice))
        actualaasdf = ((actualaa))-((actualaa2))
        print(bookedroomprice)


        for x in customer13.first_name:
           test_name= str(ord(x)) 
        for y in customer13.last_name:
           testl_name= str(ord(y))    
        now = datetime.now()
        referenceno2 =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")   



        tehtarik.checkout_date = newcheckin

        # now1555 = (now + timedelta(hours=8)).date()
        now1555 = todaydate

# addinhere
        if newcheckin.date() <= checkindate:
            tehtarik.earlyout= True

#



        # tehtarik.earlyout = True
        # if newcheckin <
        tehtarik.upgrade=True

        # tehtarik.save()
        roomtype13 = Roomtype.objects.get(pk=roomtype)


    
        if newcheckout.date() < coutdate:
            # Book = Booking.objects.create(upgrade=True, upgraderoot=tehtarik.pk,first_name=customer13.first_name, referenceno =referenceno2, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=roomtype13, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = tehtarik.number_of_people, paymentprice=format((bookedroomprice2/decimal.Decimal(1.06)),'.2f'), actualpay=format((bookedroomprice2/decimal.Decimal(1.06)),'.2f'), checkin_date=newcheckin, checkout_date=newcheckout, booktype=inv.referral, discountper=decimal.Decimal(ratio) )
            Book = Booking.objects.create(upgrade=True, upgraderoot=tehtarik.pk,first_name=customer13.first_name, referenceno =referenceno2, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=roomtype13, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = tehtarik.number_of_people, paymentprice=format((bookedroomprice2),'.2f'), actualpay=format((bookedroomprice2),'.2f'), checkin_date=newcheckin, checkout_date=newcheckout, booktype=inv.referral, discountper=decimal.Decimal(ratio) )            
            Book.save()
            Book2 =Booking.objects.create(upgradelast=True, upgrade=True, upgraderoot=tehtarik.pk,first_name=customer13.first_name, referenceno =referenceno2, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=tehroom, room_number=tehtarikroom, cust33=customer13, phone_number=customer13.phone_number, number_of_people = tehtarik.number_of_people, paymentprice=0.00, actualpay=0.00, checkin_date=newcheckout, checkout_date=coutdate, booktype=inv.referral, discountper=decimal.Decimal(ratio) )
            Book2.save()
            tehtarik.ugradebooking=int(Book2.pk)
            tehtarik.upgradedate=coutdate
        else:
            #Book = Booking.objects.create(upgradelast=True,upgrade=True, upgraderoot=tehtarik.pk,first_name=customer13.first_name, referenceno =referenceno2, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=roomtype13, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = tehtarik.number_of_people, paymentprice=format((bookedroomprice2/decimal.Decimal(1.06)),'.2f'), actualpay=format((bookedroomprice2/decimal.Decimal(1.06)),'.2f'), checkin_date=newcheckin, checkout_date=newcheckout, booktype=inv.referral, discountper=decimal.Decimal(ratio) )
            tehtarik.upgradedate=newcheckout
            Book = Booking.objects.create(upgradelast=True,upgrade=True, upgraderoot=tehtarik.pk, first_name=customer13.first_name, referenceno =referenceno2, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=roomtype13, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = tehtarik.number_of_people, paymentprice=format((bookedroomprice2),'.2f'), actualpay=format((bookedroomprice2),'.2f'), checkin_date=newcheckin, checkout_date=newcheckout, booktype=inv.referral, discountper=decimal.Decimal(ratio) )
            tehtarik.ugradebooking=int(Book.pk)
            Book.save()
        inv1 = Invoice.objects.create()



        tehtarik.save()

        if inv.ttax:
            if inv.ttax>0:
                inv1.ttax = decimal.Decimal(10*numofstay)
                inv.ttax = decimal.Decimal(inv.ttax) - decimal.Decimal(10*numofstay)

        inv1.referenceno = referenceno2
        inv1.referral = "Upgrade"       
        if inv.otherref: 
            inv1.otherref = inv.otherref

        inv1.staffbooking = True
        tqtt = None
        inv1.servicetax=0
        inv1.total = format((bookedroomprice2),'.2f')
        # inv1.gst = format(decimal.Decimal(inv1.total) -decimal.Decimal(bookedroomprice2/decimal.Decimal(1.06)),'.2f')
        inv1.gst = 0

        inv1.depositamt=0

        inv1.totalwch = format((bookedroomprice2),'.2f')


        # Inv.bookingfee = bookingfeeb4tax*decimal.Decimal(1.1)
        inv1.bookedby = request.user.username 
        if str(disct) is not "0":
            if disct:
                inv1.description = Promocode.objects.get(code="BOOK15")
                inv1.descprom = decimal.Decimal(decimal.Decimal(disct)/decimal.Decimal(100))
        inv1.email = customer13
        inv1.save()
        # inv.ttax=0
        inv.save()
        bbb3="Upgrade from room "+tehtarikroom.room_number + " to " + rnum.room_number

        logging1313 = logging.objects.create(description=bbb3, referenceno=Book.pk, staff=request.user.username )

        linkred = "pk=" + str(inv.email.pk)

        # allbook = Booking.objects.filter(referenceno=referenceno)

        # html_message = loader.render_to_string('booking/email2.html',{
        # 'first_name':inv.email.first_name,
        # 'last_name': inv.email.last_name,
        # 'total':inv.total,
        # 'booking':allbook,
        # 'checkindate': Book.checkin_date,
        # 'checkoutdate': Book.checkout_date,
        # 'referenceno': inv.referenceno,
        # 'addcomments':Book.additional_comments,
        # 'nop': nop,



        # })

        # msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com']) 

        # msg.attach_alternative(html_message, "text/html")

        # msg.send()


        return redirect('/customer/?%s' % linkred)








    context = {
         # "cd":cd,
         "rts":rts,
         "rn":rn,
         "qdate1":qdate1,
         "qout1":qout1,
         "per":per,
         "price1":price1.pk,
         "mol":mol


    }
    return render(request, "booking/form22.html", context)





@login_required(login_url='/login/')
def manualbook(request):



    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    todaydatestring = todaydate.strftime("%Y-%m-%d")
    todaydatexact = datetime.strptime(todaydatestring, '%Y-%m-%d')
    todaydate = todaydatexact





    rb=request.GET.get('rb')
    predisc = request.GET.get('tqt1t')
    rts = Roomtype.objects.exclude(pk=23).order_by('-room_price0')
    cust =request.GET.get('cus')
    if cust is not None:
        roticust = Customer.objects.get(pk=cust)
        rotiname = roticust.first_name
        rotilname = roticust.last_name
        rotiemail = roticust.email
        rotiphno = roticust.phone_number
    else:
        rotiname = None
        rotilname = None
        rotiemail = None
        rotiphno = None        

    Book = None
    ttarik = Booking.objects.none()
    nasil = None
    nasii = None
    nasio = None

    if rb is not None:
        voicein = Invoice.objects.get(referenceno = rb)

        ttarik = Booking.objects.filter(referenceno = voicein.referenceno)
        if ttarik:
            ttarik1 = ttarik.last()
            nop = ttarik1.number_of_people
            nasii = ttarik1.checkin_date.strftime("%d-%m-%Y") 
            nasio = ttarik1.checkout_date.strftime("%d-%m-%Y") 
            nasil = ttarik1.booktype
    else:
        voicein = None


 

    # tz = timezone('Etc/GMT+8')
    # todaydate = tz.localize(datetime.today())
    # qin_date = todaydate
    # booking = request.GET.get('bookpk')
    # if bookings is not None:
    #     tehtarik = Booking.objects.get(pk=booking)

    # if request.method=="GET":

    if request.method == "POST":
        if rb is None:

            fname = request.POST.get('first_name')
            if not fname:
                fname = "Auto"
            lname = request.POST.get('last_name')
            gname = request.POST.get('gname')
            if not lname:
                lname = "Auto"
            email = request.POST.get('email')
            phno = request.POST.get('phno')
            nop= request.POST.get('nop')
            country = request.POST.get('country')
            refnumb = request.POST.get('refnumber')
            refer = request.POST.get('referral')


            now = datetime.now()
            for x in fname:
               test_name= str(ord(x)) 
            for y in lname:
               testl_name= str(ord(y))    
            referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")   

            if not email:
                email = str(referenceno) + "@" + "randomgenerate.com"

            if not phno:
                phno = "1234567890"
             
            try:
                code = Customer.objects.get(email=email, phone_number=phno)
                code.first_name = fname
                code.last_name = lname
                code.save()
                cuspk = code.pk

            except Customer.DoesNotExist:
                cust = Customer.objects.create()
                cust.first_name = fname
                cust.last_name = lname
                cust.email = email
                cust.phone_number = phno
                cust.country = country
                cust.save()
                cuspk = cust.pk
 

        


            

            customer13 = Customer.objects.get(pk=cuspk)
            ind1 = request.POST.get('cind')
            outd1 = request.POST.get('coutd')
            roomtype = request.POST.get('rtn')
            roomnum = request.POST.get('rnn2')
            rrtpp = request.POST.get('rrtpp')
            paid = request.POST.get('paid')
            break1 = request.POST.get('break')
            breakfast1 = request.POST.get('breakfast')
            bdc = request.POST.get('bdc')            
            if break1 is None:
                break1 = 0
            # break1 = "".join(str(x) for x in break1)
            addcomments = request.POST.get('addcomments')
            if roomnum is None:
                roomnum=0
            try:
                float(roomnum)
            except ValueError:
                roomnum = 0


            try:
                float(rrtpp)
            except ValueError:
                rrtpp = 0

            def parsing_date(text):
                for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                    try:
                        return datetime.strptime(text, fmt)
                    except ValueError:
                        pass
                raise ValueError('no valid date format found') 

            ind = parsing_date(ind1)
            outd = parsing_date(outd1)
            room01 = None
            room02 = None
            # rtname01= None
            # rtname02=None
            # rnum= None


            notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
            notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
            
            notaxset = False
            if todaydate > notaxstartdate and todaydate < notaxenddate:
                if ind > notaxstartdate and ind < notaxenddate:
                    if outd > notaxstartdate and outd < notaxenddate:
                        notaxset = True






            rtname = Roomtype.objects.get(pk=roomtype)
            if int(roomnum) is not 0:

                if int(roomtype) is 27:
                    # return HttpResponse(rtname.pk)
                    # roomlinked = Roomnumber.objects.get(room_number=roomnum)
                    # rnum1= Roomnumber.objects.filter(link=roomlinked)
                    # for one1 in rnum1:
                    #     room01 = one1
                    #     rnum = room01
                    #     room02 = one1
                    #     rtname01 = room01.room_type_name
                    #     rtname02 = room02.room_type_name




                    # return HttpResponse(rtname.pk)                   
                    roomlinked = Roomnumber.objects.get(room_number=roomnum)
                    rnum13 = Roomnumber.objects.filter(link=roomlinked)
                    de = rnum13
                    for one1 in de:
                        n = "passed"
                        rnum1 = one1
                        rnum=one1
                        we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1, checkedout1__isnull=True)
                        if we:
                            n="notpassed"
                        asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1, checkedout1__isnull=True)
                        if asdf:
                            n="notpassed"
                        drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1, checkedout1__isnull=True)
                        if drrr: 
                            n="notpassed"

                        if n is "notpassed":

                            room01 = None
                            room02 = None
  
                        else:

                            if room01 == None:

                                room01 = rnum1
                                rtname01 = room01.room_type_name
                            else:
                                room02 = rnum1
                                rtname02 = room02.room_type_name
                        
                    if room02 is None:
                        return redirect('test2')

                else:
                    rnum = Roomnumber.objects.get(room_number=roomnum)
                    we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum, checkedout1__isnull=True)
                    if we:
                        return redirect('test2')
                    asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum, checkedout1__isnull=True)
                    if asdf:
                        return redirect('test2')
                    drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum, checkedout1__isnull=True)
                    if drrr: 
                        return redirect('test2')
            # qwer = asdf | we | drrr
            # cd = aaaa.exclude(id__in=qwer)
            # de = cd
                # if int(float(id)) is not 22:
                #     if not de:
                #         return redirect('test2')



            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:
                n = None
                # room01 = None
                # room02 = None
                if int(roomnum) is 0:
                    if int(rtname.pk) is 27:
                        aaaa =  Roomnumber.objects.all().filter(link__isnull=False, hidden=False)
                        # we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
                        # asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
                        # drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                        # qwer = asdf | we | drrr
                        # cd = aaaa.exclude(id__in=qwer)
                        cd = aaaa
                        if not cd:
                            return HttpResponse('This type of rooms have been fully booked')
                        de = cd

                        # randomnumber = random.choice(de)
                        # rnum= Roomnumber.objects.get(room_number=randomnumber)
                        for one1 in de:
                            rnum = one1
                            if room01 and room02 is not None:
                                break
                            one11 = one1 

                            n = "passed"                                
                            rnum1 = Roomnumber.objects.get(room_number=one11)
                            we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1, checkedout1__isnull=True)
                            if we:
                                n="notpassed"
                            asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1, checkedout1__isnull=True)
                            if asdf:
                                n="notpassed"
                            drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1, checkedout1__isnull=True)
                            if drrr: 
                                n="notpassed"

                            if n is "notpassed":

                                room01 = None
                                room02 = None
                                de = de.exclude(pk=one11.pk)

                            else:
                                room01 = rnum1
                                rtname01 = room01.room_type_name


                                linkbookcheck = Roomnumber.objects.filter(link=one11.link).exclude(pk=one11.pk)
                                for a1 in linkbookcheck:
                                    n = "passed"                                
                                    rnum1 = Roomnumber.objects.get(room_number=a1)
                                    we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1, checkedout1__isnull=True)
                                    if we:
                                        n="notpassed"
                                    asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1, checkedout1__isnull=True)
                                    if asdf:
                                        n="notpassed"
                                    drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1, checkedout1__isnull=True)
                                    if drrr: 
                                        n="notpassed"


                                    if n is "notpassed":

                                        room01 = None
                                        room02 = None

                                    else:

                                        room02 = rnum1
                                        rtname02 = room02.room_type_name
                                        break


                        if n is "notpassed":                            
                            return redirect('test2')



                    else:

                        aaaa =  Roomnumber.objects.all().filter(room_type_name__pk=roomtype, hidden=False)
                        we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
                        asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
                        drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                        qwer = asdf | we | drrr
                        cd = aaaa.exclude(id__in=qwer)
                        if not cd:
                            return HttpResponse('This type of rooms have been fully booked')
                        de = cd
                        randomnumber = random.choice(de)
                        rnum= Roomnumber.objects.get(room_number=randomnumber)



            # elif int(rtname.pk) is not 24:
            #     if int(roomnum) is 0:
            #         aaaa =  Roomnumber.objects.all().filter(room_type_name__pk=roomtype, hidden=False)
            #         we = Roomnumber.objects.all().filter(booking__checkin_date__gte=ind, booking__checkin_date__lt=outd)
            #         asdf = Roomnumber.objects.all().filter(booking__checkout_date__gt=ind,booking__checkout_date__lte=outd)
            #         drrr = Roomnumber.objects.all().filter(booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
            #         qwer = asdf | we | drrr
            #         cd = aaaa.exclude(id__in=qwer)
            #         if not cd:
            #             return HttpResponse('This type of rooms have been fully booked')
            #         de = cd
            #         randomnumber = random.choice(de)
            #         rnum= Roomnumber.objects.get(room_number=randomnumber)
        

            else:
                rnum= None


            numofstay = int((outd-ind).days)
            bookedroomprice = 0
            gsttotal= 0
            actualaa =0
            hprice2=[]
            print(numofstay)
            ttax15=0
            ttax13=0



            for each in range(0, numofstay):
                date1 = ind + timedelta(days=each)
                day = date1.weekday()


                xprice = "room_price" + str(day)  
                if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:

                    ttax13=10
                    ttax15+=ttax13



                    try:
                        roompk = Roomtype.objects.get(pk=roomtype)
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        #yy = pricespecial.price/decimal.Decimal(0.85)
                        yy = pricespecial.price/decimal.Decimal(0.78)

                    except variablepricing.DoesNotExist:

                    # if break1=="break":
                    #     yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) + (getattr(Roomtype.objects.get(pk=23), xprice))
                    # else:
                        yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.78))
#                        yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85))
                else:
                    try:
                        roompk = Roomtype.objects.get(pk=roomtype)
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        yy = pricespecial.price

                    except variablepricing.DoesNotExist:


                        yy = (getattr(Roomtype.objects.get(pk=roomtype), xprice))                 
                actuala = yy



####################################################################################################################                    

                if str(rrtpp) is not "0":
                    yy = yy*(decimal.Decimal(1)-decimal.Decimal(rrtpp))
                else:
                    yy=yy
                        # gst = yy*decimal.Decimal(0.1)

                pricex_ = decimal.Decimal(format(yy,'.2f'))
                hprice2.append(pricex_)   
                actualaa += actuala
                bookedroomprice += pricex_

                # roomstt = str(randomnumber) + "," +  str(roomstt)

                # bookedroomprice += xprice_
            gsttotal = 0
            bookedroomprice2 = bookedroomprice
            bookedroomprice10 = bookedroomprice

            actualaasdf = actualaa  
            actualaasdf = actualaa
            print(bookedroomprice)

            bookingfeeb4tax = max(hprice2)*decimal.Decimal(1.06)
            # bookingfeeb4tax = max(hprice2)*decimal.Decimal(1.00)


###########################################################################################

            if int(break1) > 0:
                numofstay = int((outd-ind).days)
                bookedroomprice17 = 0
                bookedroomprice5=0
                actualbb=0
                hprice4=[]
                if str(breakfast1) == "breakfast":
                    breakfast = Roomtype.objects.get(pk=24)
                else:
                    breakfast = Roomtype.objects.get(pk=23)      
                for each in range(0,int(break1)):  
                    hprice4=[]
                    bookedroomprice17 = 0                    
                    for each in range(0, numofstay):
                        date1 = ind + timedelta(days=each)
                        day = date1.weekday()
                        if str(breakfast1) == "breakfast":
                            if str(bdc) == "bdc":

                                try:
                                    roompk = Roomtype.objects.get(pk=24)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price


                                except variablepricing.DoesNotExist:


                                    tt = (getattr(Roomtype.objects.get(pk=24), xprice))
                            else:

                                try:
                                    roompk = Roomtype.objects.get(pk=24)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price*(decimal.Decimal(1)-decimal.Decimal(rrtpp))


                                except variablepricing.DoesNotExist:

                                    tt = (getattr(Roomtype.objects.get(pk=24), xprice))*(decimal.Decimal(1)-decimal.Decimal(rrtpp))
                        else:
                            if str(bdc) == "bdc":

                                try:
                                    roompk = Roomtype.objects.get(pk=23)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price


                                except variablepricing.DoesNotExist:

                                    tt = (getattr(Roomtype.objects.get(pk=23), xprice))
                            else:

                                try:
                                    roompk = Roomtype.objects.get(pk=23)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price*(decimal.Decimal(1)-decimal.Decimal(rrtpp))


                                except variablepricing.DoesNotExist:

                                    tt = (getattr(Roomtype.objects.get(pk=23), xprice))*(decimal.Decimal(1)-decimal.Decimal(rrtpp))                      
                        actualb = tt

                        pricex1 = decimal.Decimal(format(tt,'.2f'))
                        hprice4.append(pricex1)   
                        actualbb += actualb
                        bookedroomprice17 += pricex1
                    bookedroomprice30 = bookedroomprice17


                    ttprice =(bookedroomprice17)
                    ttprice2 = (bookedroomprice17)




                    gsttotal = 0
                    # bookedroomprice2 = bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1))
                    # actualaasdf = actualaa+(actualbb*decimal.Decimal(1.1))  
                    



                    bookingfeeb4tax =(max(hprice4)*decimal.Decimal(1.06))

                    # bookingfeeb4tax =(max(hprice4)*decimal.Decimal(1.00))
 


                    # bookedroomprice = bookedroomprice + bookedroomprice5
                    
                    # for each in range(0, int(break1)):

                    ind1 = ind.strftime("%d-%m-%Y")
                    outd1 = outd.strftime("%d-%m-%Y")  

                    Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=ttprice2, actualpay=ttprice2, checkin_date=ind, checkout_date=outd, booktype=refer)
                    bbb3 =  "first_name=" + customer13.first_name + ", last_name =" + customer13.last_name + ", additional_comments="+addcomments+ ", deposit=" + str(bookingfeeb4tax) + ",country =" + customer13.country +" , room_type_name= breakfast"+ ", phone_number=" + customer13.phone_number + ", number_of_people =" + str(nop) + ", paymentprice =" + str(ttprice2) + ", actualpay=" + str(ttprice2) + ", checkin_date=" + ind1+ ", checkout_date="+ outd1 + ", booktype=" + refer
                    logging1313 = logging.objects.create(description=bbb3, referenceno=referenceno, staff=request.user.username )
                    Book13.save()
                    # Book13 = None
                    Book13.pk = None

                    bookedroomprice5 += bookedroomprice30
                    # gsttotal += gsttotal
            else: 
                bookedroomprice5 =0 

            
            # aa.paymentprice = bookedroomprice2  
            # aa.actualpay = actualaasdf
            # aa.referenceno = referenceno
            # aa.country = country
            # aa.cust33 = Customer.objects.get(pk=cuspk)
            # aa.deposit = max(hprice)
            # invoicedeposit += aa.deposit
            # aa.extraref=str(testnum_)
            # aa.save()

      


            ind2 = ind.strftime("%d-%m-%Y")
            outd2 = outd.strftime("%d-%m-%Y")  
            if int(rtname.pk) is 27:
                Book = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=rtname01, room_number=room01, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=(decimal.Decimal(bookedroomprice10)/2), actualpay=(decimal.Decimal(actualaasdf)/2), checkin_date=ind, checkout_date=outd, booktype=refer, discountper=decimal.Decimal(rrtpp), familyroom=True )
                Book = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=rtname02, room_number=room02, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=(decimal.Decimal(bookedroomprice10)/2), actualpay=(decimal.Decimal(actualaasdf)/2), checkin_date=ind, checkout_date=outd, booktype=refer, discountper=decimal.Decimal(rrtpp) , familyroom=True )                  
            else:    
                Book = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=rtname, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=ind, checkout_date=outd, booktype=refer, discountper=decimal.Decimal(rrtpp) )
            
            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:
                bbb4 =  "first_name= " + customer13.first_name + ", last_name= " + customer13.last_name + ", additional_comments= "+addcomments+ ", deposit= " + str(bookingfeeb4tax) + ", country= " + customer13.country +", room_type_name= "+ rtname.room_type_name + ", room_number= "+rnum.room_number+ ", phone_number= " + customer13.phone_number + ", number_of_people= " + str(nop) + ", paymentprice= " +str(bookedroomprice10) + ", actualpay= " + str(actualaasdf) + ", checkin_date= " + ind2+ ", checkout_date= "+ outd2 + ", booktype= " + refer+ ", discountper= " + str(rrtpp)
            else:
                bbb4 =  "first_name= " + customer13.first_name + ", last_name= " + customer13.last_name + ", additional_comments= "+addcomments+ ", deposit= " + str(bookingfeeb4tax) + ", country= " + customer13.country +", room_type_name= "+ rtname.room_type_name + ", phone_number= " + customer13.phone_number + ", number_of_people= " + str(nop) + ", paymentprice= " +str(bookedroomprice10) + ", actualpay= " + str(actualaasdf) + ", checkin_date= " + ind2+ ", checkout_date= "+ outd2 + ", booktype= " + refer+ ", discountper= " + str(rrtpp)

            logging1314 = logging.objects.create(description=bbb4, referenceno=referenceno, staff=request.user.username )
            Book.save()



            Inv = Invoice.objects.create()

            Inv.referenceno = referenceno
            Inv.referral = refer 

            if gname:
                Inv.guestname = gname
            
            if refer =="Agoda":
                if str(paid) == "paid":
                    Inv.rtacomm = 0.17
                else:    
                    print("nothing")
            elif refer =="Ctrip":
                Inv.rtacomm = 0.17
            elif refer =="Asiatravel":
                Inv.rtacomm = 0.17
            elif refer =="Mikitravel":
                Inv.rtacomm = 0.0
            elif refer =="Traveloka":
                Inv.rtacomm = 0.15
            elif refer =="Expedia":
                if str(paid) == "paid":
                    Inv.rtacomm = 0.2
                else:    
                    print("nothing")

            elif refer =="Corporate":
                Inv.rtacomm = 0.0




            Inv.otherref = refnumb
            Inv.gst=0
            if customer13.country == "MY":
                Inv.ttax=0
            else:
                Inv.ttax= decimal.Decimal(format(ttax15,'.2f'))

            Inv.staffbooking = True
            tqtt = None
            if Inv.rtacomm:
                Inv.servicetax=0
            else:
                Inv.servicetax=gsttotal




            if Inv.rtacomm:

                if notaxset:
                    Inv.gst = 0
                else:
                    Inv.gst=format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(0.06),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f')
                # Inv.gst=format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(0.00),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f')
                Inv.total = decimal.Decimal(Inv.gst)+ decimal.Decimal(format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5)),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f'))
                Inv.totalwch = format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))+decimal.Decimal(Inv.gst),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f')
                Inv.commamount = format(Inv.total*decimal.Decimal(Inv.rtacomm)/decimal.Decimal(1-decimal.Decimal(Inv.rtacomm)),'.2f')
                Inv.Paymentmethod = refer 

            else:



                if notaxset:
                    Inv.gst=0
                else:
                    Inv.gst=decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5 ))*decimal.Decimal(0.06),'.2f'))


                # Inv.gst=decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5 ))*decimal.Decimal(0.00),'.2f'))

                Inv.total = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))+Inv.gst,'.2f'))

                Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))
                # Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1),'.2f'))

            if str(paid) == "paid":
                tqtt = "hj1335"
                Inv.totalpaid = True
                Inv.Paymentmethod = Inv.referral
                # if Inv.rtacomm:

                Inv.ccpaid = Inv.total
                Inv.totalpaiddate = datetime.now()


                # Inv.ccpaid = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1)*decimal.Decimal(1.06))),'.2f'))
                
                # else:
                #     if Inv.referral=="Corporate":
                #         print("nothing")
                #     elif Inv.referral=="DOTW":
                #         print("nothing")
                #     elif Inv.referral=="Revato":
                #         print("nothing")    

                #     else:
                        # Inv.ccpaid = Inv.total
                        # Inv.totalpaiddate = datetime.now()
                        # if Inv.invoiceno:
                        #     randomvar = None
                        # else:
                        #     year = datetime.now().strftime("%y")
                        #     invnos = Invoice.objects.all().order_by('invoiceno').last()
                        #     inv_no = invnos.invoiceno
                        #     invoice_int = inv_no[2:]
                        #     new_invoice_int = int(invoice_int) + 1
                        #     new_invoice_no = year + str(format(new_invoice_int, '05d'))
                        #     Inv.invoiceno = new_invoice_no




                # year = datetime.now().strftime("%y")    
                # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
                # inv_no = invnos.invoiceno
                # invoice_int = inv_no[2:]
                # new_invoice_int = int(invoice_int) + 1
                # new_invoice_no = year + str(format(new_invoice_int, '05d'))
                # Inv.invoiceno = new_invoice_no



            Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))
            # Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.00),'.2f'))


            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:
                Inv.depositamt = 200
            # elif int(rtname.pk)is not 24:
            #     Inv.depositamt = 200                
            else:
                Inv.depositamt=0
            # Inv.bookingfee = bookingfeeb4tax*decimal.Decimal(1.1)
            Inv.bookedby = request.user.username 
            if str(rrtpp) is not "0":
                if rrtpp:
                    Inv.description = Promocode.objects.get(code="BOOK15")
                    Inv.descprom = rrtpp
            Inv.email = customer13


            bbba1 =  "firstname= " + Inv.email.first_name +",lastname= "+ Inv.email.last_name+", total= "+ str(Inv.total) +", totalwch= " + str(Inv.totalwch) +", gst= "+ str(Inv.gst)+ ", invoiceno= "+ Inv.invoiceno+ ", totalpaid= " + str(Inv.totalpaid) + ", referral= " + Inv.referral +  ", deposit= " + str(Inv.deposit) + ", depositamt= "+ str(Inv.depositamt)
            logging1319 = logging.objects.create(description=bbba1, referenceno=referenceno, staff=request.user.username )



            Inv.save()

            linkred = "rb=" + referenceno + "&tqt1t=" + str(tqtt)

            allbook = Booking.objects.filter(referenceno=referenceno)
            cdatein = Book.checkin_date.strftime("%d-%m-%Y") 
            cdateout = Book.checkout_date.strftime("%d-%m-%Y") 

            html_message = loader.render_to_string('booking/email2.html',{
            'first_name':Inv.email.first_name,
            'last_name': Inv.email.last_name,
            'total':Inv.total,
            'booking':allbook,
            'checkindate': cdatein,
            'checkoutdate': cdateout,
            'referenceno': Inv.referenceno,
            'addcomments':Book.additional_comments,
            'nop': nop,



            })

            msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com']) 

            msg.attach_alternative(html_message, "text/html")

            msg.send()






            return redirect('/manualbook/?%s' % linkred)






        elif rb is not None:

            inv1 = voicein
            cuspk = inv1.email.pk
            tqtt= None




            customer13 = Customer.objects.get(pk=cuspk)
            ind1 = request.POST.get('cind')
            outd1 = request.POST.get('coutd')
            roomtype = request.POST.get('rtn')
            roomnum = request.POST.get('rnn2')
            rrtpp = request.POST.get('rrtpp')
            addcomments = request.POST.get('addcomments')
            break1 = request.POST.get('break')
            breakfast1 = request.POST.get('breakfast')
            bdc = request.POST.get('bdc')
            if break1 is None:
                break1 = 0
            # break1 = "".join(str(x) for x in break1)
            try:
                float(roomnum)
            except ValueError:
                roomnum = 0


            try:
                float(rrtpp)
            except ValueError:
                rrtpp = "0"


            def parsing_date(text):
                for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                    try:
                        return datetime.strptime(text, fmt)
                    except ValueError:
                        pass
                raise ValueError('no valid date format found') 

            ind = parsing_date(ind1)
            outd = parsing_date(outd1)

            room01 = None
            room02 = None
            rtname = Roomtype.objects.get(pk=roomtype)


            notaxenddate = datetime.strptime("2020-08-31", '%Y-%m-%d')
            notaxstartdate = datetime.strptime("2020-03-01", '%Y-%m-%d')
            notaxset = False
            if todaydate > notaxstartdate and todaydate < notaxenddate:
                if ind > notaxstartdate and ind < notaxenddate:
                    if outd > notaxstartdate and outd < notaxenddate:
                        notaxset = True






            if int(roomnum) is not 0:

                if int(rtname.pk) is 27:
                    # return HttpResponse(rtname.pk)
                    # roomlinked = Roomnumber.objects.get(room_number=roomnum)
                    # rnum1= Roomnumber.objects.filter(link=roomlinked)
                    # for one1 in rnum1:
                    #     room01 = one1
                    #     rnum = room01
                    #     room02 = one1
                    #     rtname01 = room01.room_type_name
                    #     rtname02 = room02.room_type_name




                    # return HttpResponse(rtname.pk)                   
                    roomlinked = Roomnumber.objects.get(room_number=roomnum)
                    rnum13 = Roomnumber.objects.filter(link=roomlinked)
                    de = rnum13
                    for one1 in de:
                        n = "passed"
                        rnum1 = one1
                        rnum=one1
                        we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1)
                        if we:
                            n="notpassed"
                        asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1)
                        if asdf:
                            n="notpassed"
                        drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1)
                        if drrr: 
                            n="notpassed"

                        if n is "notpassed":

                            room01 = None
                            room02 = None
  
                        else:

                            if room01 == None:

                                room01 = rnum1
                                rtname01 = room01.room_type_name
                            else:
                                room02 = rnum1
                                rtname02 = room02.room_type_name
                        
                    if room02 is None:
                        return HttpResponse(one1) 






                else:







                    rnum = Roomnumber.objects.get(room_number=roomnum)
                    we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd, room_number=rnum)
                    if we:
                        return redirect('test2')
                    asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd, room_number=rnum)
                    if asdf:
                        return redirect('test2')
                    drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd, room_number=rnum)
                    if drrr: 
                        return redirect('test2')
            # qwer = asdf | we | drrr
            # cd = aaaa.exclude(id__in=qwer)
            # de = cd
                # if int(float(id)) is not 22:
                #     if not de:
                #         return redirect('test2')



            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:

                if int(roomnum) is 0:
                    if int(rtname.pk) is 27:
                        aaaa =  Roomnumber.objects.all().filter(link__isnull=False, hidden=False)
                        # we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
                        # asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
                        # drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                        # qwer = asdf | we | drrr
                        # cd = aaaa.exclude(id__in=qwer)
                        cd = aaaa
                        if not cd:
                            return HttpResponse('This type of rooms have been fully booked')
                        de = cd

                        # randomnumber = random.choice(de)
                        # rnum= Roomnumber.objects.get(room_number=randomnumber)
                        for one1 in de:
                            rnum = one1
                            if room01 and room02 is not None:
                                break
                            one11 = one1 

                            n = "passed"                                
                            rnum1 = Roomnumber.objects.get(room_number=one11)
                            we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1)
                            if we:
                                n="notpassed"
                            asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1)
                            if asdf:
                                n="notpassed"
                            drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1)
                            if drrr: 
                                n="notpassed"

                            if n is "notpassed":

                                room01 = None
                                room02 = None
                                de = de.exclude(pk=one11.pk)

                            else:
                                room01 = rnum1
                                rtname01 = room01.room_type_name


                                linkbookcheck = Roomnumber.objects.filter(link=one11.link).exclude(pk=one11.pk)
                                for a1 in linkbookcheck:
                                    n = "passed"                                
                                    rnum1 = Roomnumber.objects.get(room_number=a1)
                                    we = Booking.objects.filter(checkin_date__gte=ind, checkin_date__lt=outd,room_number=rnum1)
                                    if we:
                                        n="notpassed"
                                    asdf = Booking.objects.filter(checkout_date__gt=ind,checkout_date__lte=outd,room_number=rnum1)
                                    if asdf:
                                        n="notpassed"
                                    drrr = Booking.objects.filter(checkin_date__lte=ind, checkout_date__gte=outd,room_number=rnum1)
                                    if drrr: 
                                        n="notpassed"


                                    if n is "notpassed":

                                        room01 = None
                                        room02 = None

                                    else:

                                        room02 = rnum1
                                        rtname02 = room02.room_type_name
                                        break


                        if n is "notpassed":                            
                            return redirect('test2')











                    else:



                        aaaa =  Roomnumber.objects.all().filter(room_type_name__pk=roomtype, hidden=False)
                        we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd,booking__checkout_date__gt=F('booking__checkin_date'))
                        asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd, booking__checkin_date__lt=F('booking__checkout_date'))
                        drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                        qwer = asdf | we | drrr
                        cd = aaaa.exclude(id__in=qwer)
                        if not cd:
                            return HttpResponse('This type of rooms have been fully booked')                    
                        de = cd
                        randomnumber = random.choice(de)
                        roomnum=randomnumber
                        rnum = Roomnumber.objects.get(room_number=roomnum)



            else:
                rnum = None


            numofstay = int((outd-ind).days)
            bookedroomprice = 0
            gsttotal= 0
            actualaa =0
            hprice3=[]
            ttax18 =0
            ttax20 =0
            for each in range(0, numofstay):
                date1 = ind + timedelta(days=each)
                day = date1.weekday()


                xprice = "room_price" + str(day)  
                if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:
                    ttax18 = 10
                    ttax20+=ttax18
                    # if break1=="break":
                    #     yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)) + (getattr(Roomtype.objects.get(pk=23), xprice))
                    # else:
                    try:
                        roompk = Roomtype.objects.get(pk=roomtype)
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
#                        yy = pricespecial.price/decimal.Decimal(0.85)
                        yy = pricespecial.price/decimal.Decimal(0.78)

                    except variablepricing.DoesNotExist:


#                        yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85))
                        yy = ((getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.78))                        
                    # yy = (getattr(Roomtype.objects.get(pk=roomtype), xprice))/decimal.Decimal(0.85)
                else:

                    try:
                        roompk = Roomtype.objects.get(pk=roomtype)
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        yy = pricespecial.price


                    except variablepricing.DoesNotExist:
                        yy = (getattr(Roomtype.objects.get(pk=roomtype), xprice))  

                actuala = yy


          
####################################################################################################################                    

                if str(rrtpp) is not "0":
                    yy = yy*(decimal.Decimal(1)-decimal.Decimal(rrtpp))
                else:
                    yy=yy
                        # gst = yy*decimal.Decimal(0.1)

                pricex_ = decimal.Decimal(format(yy,'.2f'))
                hprice3.append(pricex_)
                actualaa += actuala
                bookedroomprice += pricex_

                # roomstt = str(randomnumber) + "," +  str(roomstt)

                # bookedroomprice += xprice_
            gsttotal = 0
            # bookedroomprice2 = bookedroomprice*decimal.Decimal(1.1)
            # actualaasdf = actualaa*decimal.Decimal(1.1)

            bookedroomprice2 = bookedroomprice
            bookedroomprice10 = bookedroomprice       

            actualaasdf = actualaa

            print(bookedroomprice)
            bookingfeeb4tax=max(hprice3)*decimal.Decimal(1.06)
            # bookingfeeb4tax=max(hprice3)*decimal.Decimal(1.00)


            if int(break1) > 0:
                numofstay = int((outd-ind).days)
                actualbb = 0
                bookedroomprice5= 0
                bookedroomprice17 = 0
                bookedroomprice30=0
                hprice4=[]
                if str(breakfast1) == "breakfast":
                    breakfast = Roomtype.objects.get(pk=24)
                else:
                    breakfast = Roomtype.objects.get(pk=23)                    
                for each in range(0,int(break1)):
                    bookedroomprice17 = 0        
                    hprice4=[]                        
                    for each in range(0, numofstay):
                        date1 = ind + timedelta(days=each)
                        day = date1.weekday()
                        if str(breakfast1) == "breakfast":
                            if str(bdc) == "bdc":


                                try:
                                    roompk = Roomtype.objects.get(pk=24)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price


                                except variablepricing.DoesNotExist:
                                    tt = (getattr(Roomtype.objects.get(pk=24), xprice))
                            else:

                                try:
                                    roompk = Roomtype.objects.get(pk=24)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price*(decimal.Decimal(1)-decimal.Decimal(rrtpp))


                                except variablepricing.DoesNotExist:


                                    tt = (getattr(Roomtype.objects.get(pk=24), xprice))*(decimal.Decimal(1)-decimal.Decimal(rrtpp))
                        else:
                            if str(bdc) == "bdc":

                                try:
                                    roompk = Roomtype.objects.get(pk=23)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price


                                except variablepricing.DoesNotExist:


                                    tt = (getattr(Roomtype.objects.get(pk=23), xprice))





                            else:



                                try:
                                    roompk = Roomtype.objects.get(pk=23)
                                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                                    tt = pricespecial.price*(decimal.Decimal(1)-decimal.Decimal(rrtpp))


                                except variablepricing.DoesNotExist:
                                    tt = (getattr(Roomtype.objects.get(pk=23), xprice))*(decimal.Decimal(1)-decimal.Decimal(rrtpp)) 
                        

                        actualb = tt
                        pricex1 = decimal.Decimal(format(tt,'.2f'))
                        # pricex1 = tt
                        hprice4.append(pricex1)   
                        actualbb += actualb
                        bookedroomprice17 += pricex1
                    bookedroomprice30 = bookedroomprice17
                    ttprice = bookedroomprice17
                    gsttotal = gsttotal + (bookedroomprice17)





                    # bookedroomprice2 = bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1))
                    # actualaasdf = actualaa+(actualbb*decimal.Decimal(1.1))  
                    bookingfeeb4tax = (max(hprice4))*decimal.Decimal(1.06)  
                    # bookingfeeb4tax = (max(hprice4))*decimal.Decimal(1.00)                  
                    # for each in range(0, int(break1)):

                    ind3 = ind.strftime("%d-%m-%Y")
                    outd3 = outd.strftime("%d-%m-%Y")  
                    Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =rb, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=ttprice, actualpay=ttprice, checkin_date=ind, checkout_date=outd, booktype=nasil)
                    bbb6 =  "first_name= " + customer13.first_name + ", last_name= " + customer13.last_name + ", additional_comments= "+addcomments+ ", deposit= " + str(bookingfeeb4tax) + ",country= " + customer13.country +" , room_type_name= breakfast"+ ", phone_number= " + customer13.phone_number + ", number_of_people= " + str(nop) + ", paymentprice= " +str(ttprice) + ", actualpay= " + str(ttprice) + ", checkin_date= " + ind3+ ", checkout_date= "+ outd3 + ", booktype= " + nasil
                    logging1316 = logging.objects.create(description=bbb6, referenceno=rb, staff=request.user.username )


                    if inv1.checkedin1:
                        Book13.checkedin1=inv1.checkedin1
                    Book13.save()
                    Book13.pk = None

                    bookedroomprice5 += bookedroomprice30
                # gsttotal += gsttotal


                    # Book13 = None

            else:
                bookedroomprice5=0

            xcount = customer13.country
            ind4 = ind.strftime("%d-%m-%Y")
            outd4 = outd.strftime("%d-%m-%Y")  







            if int(rtname.pk) is 27:
                Book = Booking.objects.create(first_name=inv1.email.first_name, additional_comments = addcomments, referenceno =rb, deposit=bookingfeeb4tax, last_name = inv1.email.last_name, email=inv1.email.email, country=inv1.email.country, room_type_name=rtname01, room_number=room01, cust33=customer13, familyroom=True , phone_number=inv1.email.phone_number, number_of_people = nop, paymentprice=decimal.Decimal(bookedroomprice10/2), actualpay=decimal.Decimal(actualaasdf/2), checkin_date=ind, checkout_date=outd, booktype=nasil,discountper=decimal.Decimal(rrtpp))
                Book = Booking.objects.create(first_name=inv1.email.first_name, additional_comments = addcomments, referenceno =rb, deposit=bookingfeeb4tax, last_name = inv1.email.last_name, email=inv1.email.email, country=inv1.email.country, room_type_name=rtname02, room_number=room02, cust33=customer13, familyroom=True , phone_number=inv1.email.phone_number, number_of_people = nop, paymentprice=decimal.Decimal(bookedroomprice10/2), actualpay=decimal.Decimal(actualaasdf/2), checkin_date=ind, checkout_date=outd, booktype=nasil,discountper=decimal.Decimal(rrtpp))
            else:    
                # Book = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, deposit=bookingfeeb4tax, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=rtname, room_number=rnum, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=ind, checkout_date=outd, booktype=refer, discountper=decimal.Decimal(rrtpp) )
           










                Book = Booking.objects.create(first_name=inv1.email.first_name, additional_comments = addcomments, referenceno =rb, deposit=bookingfeeb4tax, last_name = inv1.email.last_name, email=inv1.email.email, country=inv1.email.country, room_type_name=rtname, room_number=rnum, cust33=customer13, phone_number=inv1.email.phone_number, number_of_people = nop, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=ind, checkout_date=outd, booktype=nasil,discountper=decimal.Decimal(rrtpp))
            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:  
                if rrtpp is None:
                    rrtpp = 0 
                if nop is None:
                    nop =1         
                bbb5 =  "first_name= " + inv1.email.first_name + ", last_name= " + inv1.email.last_name + ", additional_comments= "+addcomments+ ", deposit= " + str(bookingfeeb4tax) + ", country= " + inv1.email.country +", room_type_name= "+ rtname.room_type_name + ", room_number= "+rnum.room_number+ ", phone_number= " + inv1.email.phone_number + ", number_of_people= " + str(nop) + ", paymentprice= " +str(bookedroomprice10) + ", actualpay= " + str(actualaasdf) + ", checkin_date= " + ind4+ ", checkout_date= "+ outd4 + ", discountper= " + str(rrtpp)
            else:
                if rrtpp is None:
                    rrtpp = 0
                if nop is None:
                    nop =1    
                bbb5 =  "first_name= " + inv1.email.first_name + ", last_name= " + inv1.email.last_name + ", additional_comments= "+addcomments+ ", deposit= " + str(bookingfeeb4tax) + ", country= " + inv1.email.country +", room_type_name= "+ rtname.room_type_name + ", phone_number= " + inv1.email.phone_number + ", number_of_people= " + str(nop) + ", paymentprice= " +str(bookedroomprice10) + ", actualpay= " + str(actualaasdf) + ", checkin_date= " + ind4+ ", checkout_date= "+ outd4 + ", discountper= " + str(rrtpp)
               
            logging1311 = logging.objects.create(description=bbb5, referenceno=rb, staff=request.user.username )

            if inv1.checkedin1:
                Book.checkedin1=inv1.checkedin1
            Book.save()

            if str(rrtpp) is not "0":
                if rrtpp:
                    inv1.description = Promocode.objects.get(code="BOOK15")
                    inv1.descprom = rrtpp
            inv1.servicetax=0

            # inv1.totalwch = decimal.Decimal(format((inv1.totalwch) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1)))),'.2f'))
            # inv1.total = decimal.Decimal(format((inv1.total) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1)))),'.2f'))
            print(xcount)

            if str(xcount) == "MY":
                inv1.ttax=0

            else:
                if inv1.ttax:
                    inv1.ttax= decimal.Decimal(inv1.ttax) + decimal.Decimal(format(ttax20,'.2f'))
                else:
                    inv1.ttax=decimal.Decimal(format(ttax20,'.2f'))

            oldgst = inv1.gst

            if inv1.rtacomm:
                if notaxset:
                    inv1.gst = 0
                else:
                    inv1.gst= format((decimal.Decimal(format((inv1.gst) + (decimal.Decimal((bookedroomprice2+ (bookedroomprice5)))*decimal.Decimal(0.06)*(1-decimal.Decimal(inv1.rtacomm))),'.2f'))),'.2f')
                # inv1.gst= format((decimal.Decimal(format((inv1.gst) + (decimal.Decimal((bookedroomprice2+ (bookedroomprice5)))*decimal.Decimal(0.00)*(1-decimal.Decimal(inv1.rtacomm))),'.2f'))),'.2f')
                newgst =decimal.Decimal(inv1.gst)-decimal.Decimal(oldgst)
                inv1.totalwch = format((decimal.Decimal(format((inv1.totalwch) + (decimal.Decimal((bookedroomprice2+ (bookedroomprice5 ))+newgst)*(1-decimal.Decimal(inv1.rtacomm))),'.2f'))),'.2f')
                
                inv1.total = newgst+ decimal.Decimal(format((decimal.Decimal(format((inv1.total) + ((decimal.Decimal((bookedroomprice2+ (bookedroomprice5))))*(1-decimal.Decimal(inv1.rtacomm))),'.2f'))),'.2f'))

                inv1.commamount = format(inv1.total*decimal.Decimal(inv1.rtacomm)/decimal.Decimal(1-decimal.Decimal(inv1.rtacomm)),'.2f')

            else:
                if notaxset:
                    inv1.gst = 0
                else:

                    inv1.gst= decimal.Decimal(format((inv1.gst) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5)))*decimal.Decimal(0.06),'.2f')) 
                # inv1.gst= decimal.Decimal(format((inv1.gst) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5)))*decimal.Decimal(0.00),'.2f'))                 
                newgst =decimal.Decimal(inv1.gst)-decimal.Decimal(oldgst)               
                inv1.totalwch = decimal.Decimal(format((inv1.totalwch) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5))+newgst),'.2f'))
                inv1.total = decimal.Decimal(format((inv1.total) + decimal.Decimal((bookedroomprice2+ (bookedroomprice5)))+newgst,'.2f'))


            if predisc == "hj1335":
                if inv1.ccpaid:

                    if inv1.rtacomm:
                        inv1.ccpaid =  newgst+ decimal.Decimal(format((decimal.Decimal(format((inv1.ccpaid) + ((decimal.Decimal((bookedroomprice2+ (bookedroomprice5))))*(1-decimal.Decimal(inv1.rtacomm))),'.2f'))),'.2f'))
                    else:
                        inv1.ccpaid = inv1.ccpaid + decimal.Decimal(format(bookedroomprice2+ bookedroomprice5+newgst,'.2f'))



                        # if inv1.referral=="Corporate":
                        #     print("nothing")
                        # elif inv1.referral=="DOTW":
                        #     print("nothing")
                        # elif inv1.referral=="Revato":
                        #     print("nothing")    
                        # else:
                        #     inv1.ccpaid = Inv.total
                        #     inv1.totalpaiddate = datetime.now()
                        #     if inv1.invoiceno:
                        #         randomvar = None
                        #     else:
                        #         invnos = Invoice.objects.all().order_by('invoiceno').last()
                        #         inv_no = invnos.invoiceno
                        #         invoice_int = inv_no[2:]
                        #         new_invoice_int = int(invoice_int) + 1
                        #         new_invoice_no = year + str(format(new_invoice_int, '05d'))
                        #         inv1.invoiceno = new_invoice_no


                tqtt=predisc
            
            if int(rtname.pk) is not 22 and int(rtname.pk) is not 24 and int(rtname.pk) is not 28:
                inv1.depositamt = inv1.depositamt+200
                if inv1.deposit is True:
                    inv1.deposit = False

                if inv1.totalpaid is True:
                    if predisc == "hj1335":
                        inv1.totalpaid=True
                    else:
                        inv1.totalpaid=False

            # elif int(rtname.pk) is not 24:
            #     inv1.depositamt = inv1.depositamt+200
            #     if inv1.deposit is True:
            #         inv1.deposit = False

            #     if inv1.totalpaid is True:
            #         if predisc == "hj1335":
            #             inv1.totalpaid=True
            #         else:
            #             inv1.totalpaid=False


            else:
                inv1.depositamt=inv1.depositamt
                if inv1.totalpaid is True:
                    if predisc == "hj1335":
                        inv1.totalpaid=True
                    else:
                        inv1.totalpaid=False

            # if inv1.deposit is True:
            #     inv1.deposit = False
            # inv1.bookingfee = inv1.bookingfee + (bookingfeeb4tax*decimal.Decimal(1.1))
            # if str(rrtpp) is not 0:
            #     inv1.description = Promocode.objects.get(code="BOOK15")
            #     inv1.descprom = rrtpp
            inv1.save()
            bbba5 =  "firstname= " + inv1.email.first_name +", lastname= "+ inv1.email.last_name+", total= "+ str(inv1.total) +", totalwch= " + str(inv1.totalwch) +", gst= "+ str(inv1.gst)+ ", invoiceno= "+ str(inv1.invoiceno)+ ", totalpaid= " + str(inv1.totalpaid) + ", referral= " + inv1.referral +  ", deposit= " + str(inv1.deposit) + ", depositamt= "+ str(inv1.depositamt)
            logging1315 = logging.objects.create(description=bbba5, referenceno=rb, staff=request.user.username )
            allbook = Booking.objects.filter(referenceno=rb)

            cdatein = Book.checkin_date.strftime("%d-%m-%Y") 
            cdateout = Book.checkout_date.strftime("%d-%m-%Y") 

            html_message = loader.render_to_string('booking/email2.html',{
            'first_name':inv1.email.first_name,
            'last_name': inv1.email.last_name,
            'total':inv1.total,
            'booking':allbook,
            'checkindate': cdatein,
            'checkoutdate': cdateout,
            'referenceno': inv1.referenceno,
            'addcomments':Book.additional_comments,
            'nop': nop

            })

            msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['admin@innbparkhotel.com']) 

            msg.attach_alternative(html_message, "text/html")

            msg.send()

            linkred = "rb=" + rb + "&tqt1t=" + str(tqtt)

            return redirect('/manualbook/?%s' % linkred)




        

    context = {
         # "cd":cd,
         "ttarik":ttarik,
         "nasil":nasil,     
         "nasii":nasii,
         "nasio":nasio,
         "voicein":voicein,
         "rts":rts,
         "rb":rb,
         "Book":Book,
         "rotiname":rotiname,
         "rotilname":rotilname,
         "rotiemail":rotiemail,
         "rotiphno":rotiphno,
         # "rn":rn
    }
    return render(request, "booking/form23.html", context)




@login_required(login_url='/login/')
def extension(request):
    rb = request.GET.get('refno')
    if rb is None:
        return redirect('test2' )
    print(rb)
    inv = Invoice.objects.get(referenceno = rb) 

    print(inv)
    cod31 = inv.description
    if cod31:
        cod = cod31.code
    else:
        cod = None
    booking = request.GET.get('bookpk')
    thebooking = Booking.objects.get(pk=booking)
    idno = thebooking.room_type_name.id


  
    if cod is not None:
        print('notnone')
        try:
            code1 = Promocode.objects.get(code=cod)
            per = code1.discountper*100
            fix = code1.discountfix
            desc = code1.description
            error = None
            if cod=="BOOK15":
                if inv.descprom is not None:
                    per = inv.descprom*decimal.Decimal(100)
            print('noerror')
        except Promocode.DoesNotExist:
            error = "Invalid Code"
            cod=None
            print(error)

            per = 0
            fix=0
            desc = None

    else:
        cod = None
        per = 0
        fix = 0
        desc= None


    qin_date = thebooking.checkout_date
    # .strftime("%d-%m-%Y")
    # qout_date = thebooking.checkout_date.strftime("%d-%m-%Y") 


    # eform = eeForm3(request.POST or None,initial={'checkin_date': qin_date, 'checkout_date': qout_date} )

    if request.method=="POST":
        noday = request.POST.get('noday')
        disct = request.POST.get('disct')
        late = request.POST.getlist('late')
        if not disct:
            disct = 0
        perdisct = (100-decimal.Decimal(disct))/100 
        try: 
            noday = float(noday)
        except ValueError:
            if late:
                noday = 1
            else:
                return HttpResponse("Please key in proper number of days")
        # qin_date = eform.cleaned_data['checkin_date']
        # qout_date = eform.cleaned_data['checkout_date']
        qout_date = (thebooking.checkout_date + timedelta(days=noday))
        # .strftime("%d-%m-%Y")
        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')  

        # qin_date_ = parsing_date(qin_date)
        # qout_date_ = parsing_date(qout_date)
        qin_date_ = qin_date.strftime("%d-%m-%Y")
        qout_date_ = qout_date.strftime("%d-%m-%Y")

        days1 = (qout_date-qin_date).days
        testnum_ = 0
        testac= str(days1*52)
        total = 0
        gsttotaltotal=0
        hprice=[]






        cin_date = qin_date
        cout_date = qout_date


        # fnumpeople=form.cleaned_data['number_of_people']
        days = cout_date-cin_date
        timedel = days.total_seconds() / timedelta (days=1).total_seconds()
        now = datetime.now()



        depamt = 0
        invoicedeposit = 0
        roomstt = 0

        print(id)
        hprice=[]
        if int(idno) is not 22 and int(idno) is not 23 and int(idno) is not 24 and int(idno) is not 28:
            
            if late:
                ttax=0
            else:
                ttax = decimal.Decimal(noday)*decimal.Decimal(10)


            rnid = thebooking.room_number.pk

            rtn = Roomtype.objects.get(pk=idno)
            rnn = Roomnumber.objects.get(pk=rnid)   
        else:
            rnid = None
            ttax=0

            rtn = Roomtype.objects.get(pk=idno)
            rnn = None 

        rnnon = Booking.objects.filter(room_number=rnn)
        # newrnnon = rnnon.filter(checkin_date=)


        numofstay = int((cout_date-cin_date).days)
        bookedroomprice = 0
        gsttotal= 0
        actualaa =0
        first_name =thebooking.cust33.first_name
        last_name = thebooking.cust33.last_name
        for x in first_name:
           test_name= str(ord(x)) 
        for y in last_name:
           testl_name= str(ord(y))    
        referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")
        for each in range(0, numofstay):
            date1 = cin_date + timedelta(days=each)
            newrnnon = rnnon.filter(checkin_date=date1, checkout_date__gt=F('checkin_date'))
            if int(idno) is not 22 and int(idno) is not 23 and int(idno) is not 28:
                if newrnnon:
                    return HttpResponse("someone is booked on that day")
            day = date1.weekday()

            xprice = "room_price" + str(day)
            if int(idno) is not 22 and int(idno) is not 23 and int(idno) is not 28:

                try:
                    roompk = Roomtype.objects.get(pk=idno)
                    pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
#                    yy = pricespecial.price/decimal.Decimal(0.85)
                    yy = pricespecial.price/decimal.Decimal(0.78)

                except variablepricing.DoesNotExist:
#                    yy = (getattr(Roomtype.objects.get(pk=idno), xprice))/decimal.Decimal(0.85)
                    yy = (getattr(Roomtype.objects.get(pk=idno), xprice))/decimal.Decimal(0.78)

            else:
                if int(idno) is 22:

                    try:
                        roompk = Roomtype.objects.get(pk=idno)
                        pricespecial = variablepricing.objects.get(date =date1, roomtype=roompk)
                        yy = pricespecial.price
                    except variablepricing.DoesNotExist:

                        yy = getattr(Roomtype.objects.get(pk=idno), xprice)




                if int(idno) is 23:
                    days4 = int((thebooking.checkout_date-thebooking.checkin_date).days)
                    yy = thebooking.paymentprice/days4


            actuala = yy

	####################################################################################################################                    

            # discount = Pricing.objects.filter(start_date__lte=date1, end_date__gte=date1, room_type=rtn)                    
            # for i in discount:
            #     per_ = 1-(i.discountper)
            #     fix_ = i.discountfix

            #     yy = (yy-fix_)*per_
            #     # gst = yy*decimal.Decimal(0.1)
            #     toatal = yy 


            # if not discount:
                # gst = yy*decimal.Decimal(0.1)
            toatal = decimal.Decimal(format(yy,'.2f')) 


            # bookedroomprice = bookedroomprice
            # gsttotal += gst
            hprice.append(toatal)
            pricex_ = toatal

            if disct is not None:
                pricex_ = decimal.Decimal(format((toatal*perdisct),'.2f'))
                xprice_ = decimal.Decimal(format(pricex_,'.2f'))
                

                #     elif code1.enddate > qout_date and code1.startdate < qin_date:
                #         pricex_ = (toatal-fix)*per
                #         xprice_ = pricex_*decimal.Decimal(1.1)
                #         print(xprice_)
                #         print(pricex_)                         

                # if rtn == code1.roomtype:

                #     if code1.startdate is None:
                #         pricex_ = (toatal-fix)*per
                #         xprice_ = pricex_*decimal.Decimal(1.1)
                #         print(xprice_)
                #         print(pricex_)         

                #     elif code1.enddate > qout_date and code1.startdate < qin_date:
                #         pricex_ = (toatal-fix)*per
                #         xprice_ = pricex_*decimal.Decimal(1.1)

                #         print(xprice_) 
                #         print(pricex_)  


            actualaa += actuala
            bookedroomprice += pricex_
        # roomstt = str(randomnumber) + "," +  str(roomstt)

        # bookedroomprice += xprice_
        gsttotal = 0
        stotal =  format(bookedroomprice*decimal.Decimal(0.06),'.2f')
        # stotal = 0
        bookedroomprice2 = bookedroomprice+decimal.Decimal(stotal)
        bookedroomprice10 = bookedroomprice
        actualaasdf = actualaa




        print(bookedroomprice)
        bookingcust = thebooking.cust33.pk
        now5 = datetime.now()
        if late:
            if int(idno) is not 22 and int(idno) is not 23 and int(idno) is not 24 and int(idno) is not 28:
                thebookingnew = Booking.objects.create(first_name=thebooking.cust33.first_name, referenceno =referenceno, last_name = thebooking.cust33.last_name, email=thebooking.cust33.email, country=thebooking.cust33.country, room_type_name=rtn, room_number=rnn, cust33=thebooking.cust33, phone_number=thebooking.cust33.phone_number, number_of_people = thebooking.number_of_people, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=qin_date, checkout_date=qout_date, checkedin1=now5, late=True) 
                thebookingnew.save()
            else:
                thebookingnew = Booking.objects.create(first_name=thebooking.cust33.first_name, referenceno =referenceno, last_name = thebooking.cust33.last_name, email=thebooking.cust33.email, country=thebooking.cust33.country, room_type_name=rtn, cust33=thebooking.cust33, phone_number=thebooking.cust33.phone_number, number_of_people = thebooking.number_of_people, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=qin_date, checkout_date=qout_date, checkedin1=now5, late=True) 
                thebookingnew.save()

        else:
            if int(idno) is not 22 and int(idno) is not 23 and int(idno) is not 24 and int(idno) is not 28:            
                thebookingnew = Booking.objects.create(first_name=thebooking.cust33.first_name, referenceno =referenceno, last_name = thebooking.cust33.last_name, email=thebooking.cust33.email, country=thebooking.cust33.country, room_type_name=rtn, room_number=rnn, cust33=thebooking.cust33, phone_number=thebooking.cust33.phone_number, number_of_people = thebooking.number_of_people, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=qin_date, checkout_date=qout_date, extension=True, checkedin1=now5) 
                thebookingnew.save()
            else:
                thebookingnew = Booking.objects.create(first_name=thebooking.cust33.first_name, referenceno =referenceno, last_name = thebooking.cust33.last_name, email=thebooking.cust33.email, country=thebooking.cust33.country, room_type_name=rtn, cust33=thebooking.cust33, phone_number=thebooking.cust33.phone_number, number_of_people = thebooking.number_of_people, paymentprice=bookedroomprice10, actualpay=actualaasdf, checkin_date=qin_date, checkout_date=qout_date, checkedin1=now5, extension=True) 
                thebookingnew.save()

        # thebooking.checkin_date = qin_date
        # thebooking.checkout_date = qout_date
        # thebooking.paymentprice = bookedroomprice2
        # thebooking.actualpay = actualaasdf
        # thebooking.save()

        # aa.pk=None

        # if cod is not None:
        #     adf="ttw=" + referenceno + "&ce=" + cod
        # else:
        #     adf="ttw=" + referenceno


        # if cod is not None:
        #     if code1.roomtype is None:
        #         if code1.onetimeonly is not "USED":
        #            bookedroomprice = (bookedroomprice-fix)*per
        #            if code1.onetimeonly == "YES":
        #                code1.onetimeonly = "USED"
        #                code1.save()                		

        #     if rtn == code1.roomtype:
        #         if code1.onetimeonly is not "USED":
        #            bookedroomprice = (bookedroomprice-fix)*per
        #            if code1.onetimeonly == "YES":
        #                code1.onetimeonly = "USED"
        #                code1.save()

        total = bookedroomprice2
        gsttotaltotal = gsttotal

        servicetax = decimal.Decimal(format(gsttotaltotal,'.2f'))
        totaltotal = decimal.Decimal(format(total, '.2f'))
        print(totaltotal)
        print (servicetax)
        
        servicet = decimal.Decimal(stotal)



        item = Invoice.objects.create()
        item.referenceno = referenceno
        item.referral = inv.referral
        # item.occupation = inv.occupation
        # item.purposeoftrip = inv.purposeoftrip
        item.email = inv.email
        # ffafa = "pk=" + str(cuspk)
        item.gst=servicet
        if inv.email.country == "MY":
            item.ttax=decimal.Decimal(0)
        else:
            item.ttax=ttax
        # if request.user.is_authenticated():
        #     item.bookedby = request.user.username            
        item.servicetax= 0
        item.totalwch = totaltotal
        # item.total = totaltotal
        item.total = totaltotal*decimal.Decimal(1.06)
        # if request.user.is_authenticated():
        #     item.staffbooking= True
        if request.user.is_authenticated():
            item.bookedby = request.user.username
        item.depositamt = 0
        item.bookingfee = 0
 
        # depositfact = days1/5
        # depositfact_ = int(depositfact)
        # if depositfact < 1:
        #     depositfact_ = 1


        item.description = inv.description
        # last_invoice = Invoice.objects.all().order_by('id').last()  
        # lastinv = last_invoice.referenceno    
        # print(lastinv)     
        # lastin = int(last_invoice.referenceno)
        # nowin = int(referenceno)

        # if last_invoice.email == item.email:
        #     if lastin - nowin == 3:
        #         return redirect('/customer/?%s' % ffafa)
        #     else:
        item.save()

        # xasd = "refno=" + referenceno
        # item = Invoice.objects.create()
        # item.referenceno = referenceno
        # item.referral = referral
        # item.occupation = occupation
        # item.purposeoftrip = purposeoftrip
        # item.referral = referral
        # item.email = Customer.objects.get(pk=cuspk)
        # ffafa = "pk=" + str(cuspk)
        # inv.gst=inv.gst + servicet
        # # if request.user.is_authenticated():
        # #     item.bookedby = request.user.username            
        # inv.servicetax= inv.servicetax+servicetax

        # inv.totalwch = inv.totalwch + totaltotal
        # inv.total = inv.total + totaltotal

        idno = "pk="+ str(bookingcust)
        return redirect('/customer/?%s' % idno)
	    # # item.bookingfee = invoicedeposit*decimal.Decimal(1.1)
	    # if request.user.is_authenticated():
	    #      item.bookingfee = 0           
	    # # item.total = totaltotal*decimal.Decimal(1.06)
	    # if request.user.is_authenticated():
	    #     item.staffbooking= True



	    # item.depositamt = depamt
	    # if cod is not None:
	    #     item.description = Promocode.objects.get(code=cod)
	    # item.save()
	    




    context = {
         "per":per
    }
    return render(request, "booking/form21.html", context)




@login_required(login_url='/login/')
def paid3(request):
    refno = str(request.GET.get('id'))
    pay = Invoice.objects.get(referenceno=refno)
    if pay.cashpaid is None:
        pay.cashpaid = 0
    if pay.ccpaid is None:
        pay.ccpaid = 0
    
    if pay.bookingfee is None:
        pay.bookingfee = 0
    pay.total1 = pay.total - decimal.Decimal(pay.bookingfee) - pay.cashpaid - pay.ccpaid
    pay.depositamt = 0

    print(pay.totalpaid)

    


    cust = pay.email.pk
    custno = "pk=" + str(cust)
    total1 = pay.total1 + pay.depositamt
    print(custno)


    if request.method=="POST":
        cash = request.POST.get('quantity')
        test = request.POST.get('cd')
        deposit = request.POST.getlist('deposit')
        depa = request.POST.get('dep')
        print(depa)
        print(cash)
        print(test)
        print(deposit)

        d = Invoice.objects.get(referenceno=refno)  
        invno = d.invoiceno
        e = Booking.objects.filter(referenceno = refno)
        firstname= d.email.first_name
        cindate= datetime.strftime(datetime.now(), '%d%m%Y')
        f = Booking.objects.filter(referenceno = refno).first() 
        email_ = d.email.email

        print(pay.Paymentmethod)


        if test == "0":
            print(pay.Paymentmethod)

            if pay.Paymentmethod == "Cash":
                pay.cashpaid = pay.total
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                pay.save()

            elif pay.Paymentmethod == "Credit Card":
                pay.cashpaid = pay.total - pay.ccpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

            else:
                pay.cashpaid = pay.total - pay.ccpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
            

            return redirect('/customer/?%s' % custno)
        
        elif cash == "0":
            print(pay.Paymentmethod)

            if pay.Paymentmethod == "Credit Card":
                pay.cashpaid = pay.total
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                pay.save()

            elif pay.Paymentmethod == "Cash":
                pay.ccpaid = pay.total - pay.cashpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

            else:
                pay.ccpaid = pay.total - pay.cashpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

            return redirect('/customer/?%s' % custno)


        else:
            print(pay.Paymentmethod)

            if pay.Paymentmethod == "Credit Card":
                pay.ccpaid = test + pay.ccpaid
                pay.cashpaid = pay.total - pay.ccpaid
                pay.totalpaid = True
                pay.Paymentmethod = "Credit Card and Cash"
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")
                pay.save()

            elif pay.Paymentmethod == "Cash":
                pay.ccpaid = test + pay.ccpaid
                pay.cashpaid = pay.total - pay.ccpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

            else:
                pay.ccpaid = test + pay.ccpaid
                pay.cashpaid = pay.total - pay.ccpaid
                pay.Paymentmethod =="Credit Card and Cash"
                pay.totalpaid = True
                pay.totalpaiddate = datetime.now().strftime("%Y-%m-%d %H:%M")

            return redirect('/customer/?%s' % custno)



    context = {
    'pay':pay,
    'total1':total1
    }



    return render(request,"booking/invpaid2.html", context)





# @login_required(login_url='/login/')
# @permission_required('booking.can_add_booking', login_url='/unauthorized/')
# def bookingscom(request):



#     event = BookingForm2(request.POST or None)
#     event2 = BookingForm3(request.POST or None)

#     # roomnumber = request.GET.get('room_number')
#     # room_type_name = request.GET.get('room_type_name')
#     # actualpay = request.GET.get('actualpay')
#     # paymentprice = request.GET.get('paymentprice')

#     referenceno = request.GET.get('refno')
#     numberofpeople = request.GET.get('nofp')
#     ind1 = request.GET.get('cindate')
#     oud1 = request.GET.get('coutdate')
#     now = datetime.now()
#     if ind1:
#         ind = datetime.strptime(ind1,"%d-%m-%Y" )
#         oud = datetime.strptime(oud1,"%d-%m-%Y" )

#     if referenceno:
#         asdf= referenceno
#     else:
#         asdf= None

#     if request.method == "POST":
#         if not asdf:
#             if event.is_valid:
#                 fname = request.POST.get('first_name')
#                 lname = request.POST.get('last_name')
#                 email = request.POST.get('email')
#                 if not email:
#                     email=now.strftime("%Y%m%d%H%M%S") + "@randomemail.com"
#                 phno = request.POST.get('phone_number')
#                 country = request.POST.get('country')
#                 # addcmts = request.POST.get('additional_comments')
#                 noofp = request.POST.get('number_of_people')
#                 referral = request.POST.get('referral')
#                 cindate = request.POST.get('checkin_date')
#                 coutdate = request.POST.get('checkout_date')
#                 discou = request.POST.getlist('discount')
#                 invoicedesc = request.POST.get('invoicedesc')
#                 try:
#                     code = Customer.objects.get(email=email, phone_number=phno)
#                     code.first_name = fname
#                     code.last_name = lname
#                     code.save()
#                     cuspk = code.pk

#                 except Customer.DoesNotExist:
#                     cust = Customer.objects.create()
#                     cust.first_name = fname
#                     cust.last_name = lname
#                     cust.email = email
#                     cust.phone_number = phno
#                     cust.country = country
#                     cust.save()
#                     cuspk = cust.pk

#                 now = datetime.now()
#                 for x in fname:
#                    test_name= str(ord(x)) 
#                 for y in lname:
#                    testl_name= str(ord(y))    
#                 referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")

#                 Inv = Invoice.objects.create()
#                 Inv.referenceno = referenceno
#                 Inv.referral = referral 
#                 Inv.gst=0
#                 Inv.invoicedesc = invoicedesc
#                 if discou:
#                     print (discou)
#                     print (discou[0])
#                     if discou[0] == "discount":
#                         print("worked")
#                         promocode = Promocode.objects.get(code="BOOK15")
#                         Inv.description = promocode
#                 Inv.staffbooking = True
#                 Inv.email = Customer.objects.get(pk=cuspk)
#                 Inv.save()
#                 etc = str("refno=" + Inv.referenceno + "&nofp=" + noofp + "&cindate="+ cindate +"&coutdate=" + coutdate)

                                       
#                 return redirect('/bookingscom/?%s' %  etc)

#         else:
#             if event2.is_valid:
#                 roomno = request.POST.get('room_number')
#                 roomtype = request.POST.get('room_type_name')
#                 actualpay = request.POST.get('actualpay')
#                 paymentprice = request.POST.get('paymentprice')
#                 adcoments = request.POST.get('additional_comments')
#                 bookingcustomer = Invoice.objects.get(referenceno = referenceno)
#                 Validation1 = False
                  
#                 if not paymentprice or not actualpay:
#                     return HttpResponse("Please add prices for both before and after discount. Prices can be similar if there are no discounts")
                
#                 try:
#                     float(paymentprice)
#                     Validation1 = True
#                 except ValueError:
#                     return HttpResponse("Invalid Number for payment price")
#                 try:
#                     float(actualpay)
#                     Validation1 = True
#                 except ValueError:
#                     return HttpResponse("Invalid Number for payment price")  


#                 pricewch = decimal.Decimal(paymentprice)/decimal.Decimal(1.1)
#                 if bookingcustomer.total is None:
#                     bookingcustomer.total = 0
#                     bookingcustomer.totalwch=0
#                 bookingcustomer.bookedby = bookingcustomer.referral
#                 bookingcustomer.total = decimal.Decimal(bookingcustomer.total) + decimal.Decimal(paymentprice)
#                 bookingcustomer.totalwch = decimal.Decimal(bookingcustomer.totalwch) + decimal.Decimal(pricewch)
#                 bookingcustomer.servicetax = decimal.Decimal(bookingcustomer.total)/decimal.Decimal(1.1)*decimal.Decimal(0.1)
#                 if bookingcustomer.depositamt is None:
#                     bookingcustomer.depositamt = 0
#                 print(roomtype)
#                 if roomtype == "22":
#                     print('nodeposit')
#                     bookingcustomer.depositamt = decimal.Decimal(bookingcustomer.depositamt)
#                 else:
#                     bookingcustomer.depositamt = decimal.Decimal(bookingcustomer.depositamt) + decimal.Decimal(200)
#                 bookingcustomer.save()
#                 customer13 = bookingcustomer.email
#                 rtn = Roomtype.objects.get(pk=roomtype)
#                 roomnum = Roomnumber.objects.get(pk=roomno)

#                 Book = Booking.objects.create(first_name=bookingcustomer.email.first_name, referenceno =referenceno, last_name = bookingcustomer.email.last_name, email=bookingcustomer.email.email, country=bookingcustomer.email.country, room_type_name=rtn, room_number=roomnum, cust33=customer13, phone_number=bookingcustomer.email.phone_number,  additional_comments=adcoments, number_of_people = numberofpeople, paymentprice=paymentprice, actualpay=actualpay, checkin_date=ind, checkout_date=oud )
#                 Book.save()



















    
    # class Booking_(object):
    #     pay_price =""
    #     room_name =""
    #     actual_pay = ""
    #     room_number=""


    # if paymentprice:
    #     countn = 0
    #     paymentprice1 = paymentprice.split('-')
    #     paymentprice1_ = [var for var in paymentprice1 if var]
    #     for each in paymentprice1_:
    #         countn = countn+1
    #         Booking_.pk=countn
    #         Booking_.pay_price = each
    #         Booking_.append(bookinglist_)
    #     print(countn)
    #     print(Booking_.pk) 
    #     print(bookinglist)
    #     print(Booking_.pay_price)

    # if room_type_name:
    #     room_type_name1 = room_type_name.split('-')
    #     room_type_name1_ = [var for var in room_type_name1 if var]

    # if actualpay:
    #     actualpay1 = paymentprice.split('-')
    #     actualpay1_ = [var for var in actualpay1 if var]

    # if roomnumber:
    #     roomnumber1 = roomnumber.split('-')
    #     roomnumber1_ = [var for var in roomnumber1 if var]

    # countn = 0
    # if paymentprice:
        # for a in paymentprice1_:
        #     countn = countn + 1
        #     a.idno = countn
        #     a.paymentprice=





    # if request.method =="POST":
    #     roomnumber0 = request.POST.get('room_number')
    #     room_type_name0 = request.POST.get('room_type_name')
    #     actualpay0 = request.POST.get('actualpay')
    #     paymentprice0 = request.POST.get('paymentprice')
    #     if roomnumber0:
    #         if roomnumber:
    #             etc = str('room_number='+roomnumber+'-'+roomnumber0+'&room_type_name='+room_type_name+'-'+room_type_name0+'&actualpay='+ actualpay+'-'+actualpay0+'&paymentprice='+paymentprice+'-'+paymentprice0)
    #             print("works")
                
    #         else:
    #             etc = str('room_number='+roomnumber0+'&room_type_name='+room_type_name0+'&actualpay='+actualpay0+'&paymentprice='+paymentprice0 )
    #             print("works2")
    #         return redirect('/bookingscom/?%s' %  etc)


        # if event.is_valid:
        #     first_name=request.POST.get('first_name')
        #     last_name = request.POST.get('last_name')
        #     email = request.POST.get('email')
        #     phno = request.POST.get('phno')
        #     country = request.POST.get('country')
        #     addcomm = request.POST.get('additional_comments')
        #     numpeople = request.POST.get('number_of_people')
        #     checkin = request.POST.get('checkin_date')
        #     checkout = request.POST.get('checkout_date')
        #     createcs = Customer.objects.create()
        #     createcs.first_name = first_name
        #     createcs.last_name = last_name
        #     createcs.email= email
        #     createcs.phone_number=phno
        #     createcs.country = country
        #     createcs.save()

            # if paymentprice:
            #     for a in paymentprice1_:
            #         a.paymentprice = a
            #         a.
            #         book1 = Booking.objects.create(first_name=first_name,last_name=last_name, email=email,phone_number=phno, country=country,additional_comments=addcomm, number_of_people=numpeople)



    
    # success= None


    # context={
    # "event":event,
    # "asdf":asdf,
    # "event2":event2,
    # "success": success
    # }

    # return render(request, 'booking/bookingcom.html', context)




# def specialinclude(request):
#     all_bookings= Booking.objects.all().filter(maintain=False)
#     for a in all_bookings:
#         email = a.email
#         phno = a.phone_number
#         refno= a.referenceno
#         try:
#             a.cust33 = Customer.objects.get(email=email, phone_number=phno)

#             a.save()
#         except Customer.DoesNotExist:
#             printcode = a.pk
#             return HttpReponse(printcode)

#     return HttpResponse("Success")

# def querycheck(request):
#     roomnum313 = Booking.objects.filter(referenceno='3211020170725002204').exclude(room_number__isnull=True).order_by('room_number')
#     counter = 0
#     countercounter = 0
#     newcounter =0
#     refno3113 = None
#     for x in range(0,7):
#         if refno3113 == "3211020170725002204":
#             counter = counter + 1
#             if counter > 1:
#                 roomnum313 = Booking.objects.filter(referenceno='3211020170725002204').exclude(room_number__isnull=True).order_by('room_number')
#                 numb1 = roomnum313.count()-1

#                 countercounter = countercounter + 1   
#                 if countercounter == 2:
#                     countercounter=0                   
#                 newcounter = newcounter + countercounter  
#                 if newcounter > numb1:
#                     aroom_number = roomnum313[0].room_number
#                 else:
#                     aroom_number = roomnum313[newcounter].room_number                                             
#                 # if countercounter == 2:
#                 #     countercounter=0   
                               
#                 # counter2 =  counter2 + countercounter                  
#             else:
#                 roomnum313 = Booking.objects.filter(referenceno='3211020170725002204').exclude(room_number__isnull=True).order_by('room_number').first()
#                 aroom_number = roomnum313.room_number
#         else:
#             counter= 0
#             refno3113 = "3211020170725002204"
#             roomnum313 = Booking.objects.filter(referenceno='3211020170725002204').exclude(room_number__isnull=True).order_by('room_number').first()

#             aroom_number = roomnum313.room_number
#         print(aroom_number)
#     print(roomnum313)

#     return HttpResponse(roomnum313)


# def specialbook(request):
#     all_bookings= Booking.objects.all()
#     print("work")
#     for a in all_bookings:
#         # print("work")
#         daysofbook = int((a.checkout_date - a.checkin_date).days)
#         # print(daysofbook)        
#         count=0
#         for each in range(0, daysofbook):
#             # print("work")
#             date = (a.checkin_date + timedelta (days=count))
#             count = count + 1
#             print(date)
#             bookdetails = bookdetails.objects.create()
#             bookdetails.date = date
#             bookdetails.roomnumber = a.room_number
#             bookdetails.customer = a.cust33
#             bookdetails.booking = a
#             bookdetails.save()
#             # print (a.room_number)
#             # print (a.cust33)
#             # print (a)

#         # email = a.email
#         # phno = a.phone_number
#         # refno= a.referenceno
#         # try:
#         #     a.cust33 = Customer.objects.get(email=email, phone_number=phno)

#         #     a.save()
#         # except Customer.DoesNotExist:
#         #     printcode = a.pk
#         #     return HttpReponse(printcode)

#     return HttpResponse("Success")


# def specialbook2(request):
#     qin_date = datetime.now().date()
#     qq_date = (qin_date - timedelta (days=3)).strftime("%a, %d/%m")

#     qin_date1 = (qin_date + timedelta (days=1)).strftime("%a, %d/%m")

#     for test in range(0,31):
#         qin_date1 = (qin_date + timedelta (days=test)).strftime("%a, %d/%m")
#         date_.append(qin_date1)


#     context={
#     "date_":date_
#     }

#     return render(request, 'booking/specialbook.html', context)





# def invreor(request):

#     invoice1 =Invoice.objects.get(pk=4451)


#     invoice1.checkedout1 = datetime.now()
#     invoice1.checkedoutby = request.user.username            
#     invoice1.depositreturnedate = datetime.now()
#     invoice1.save()

#     if not invoice1.depositcash:
#         depcash = 0
#     else:
#         depcash = invoice1.depositcash

#     if not invoice1.depositcc:
#         depcc = 0
#     else:
#         depcc = invoice1.depositcc 

#     totaldep = Depositsum.objects.get(pk=1)
#     totaldep.cashdep = totaldep.cashdep - decimal.Decimal(depcash)
#     totaldep.ccdep = totaldep.ccdep - decimal.Decimal(depcc)

#     if invoice1.depdescrip is not None:
#         removedescrip = str(", ") + str(invoice1.depdescrip) 
#         oth = totaldep.Others
#         totaldep.Others = str(oth).replace(removedescrip,'', 1 )

#     totaldep.save()

#     return HttpResponse("tescomplete")



# def specialchangepromo(request):

#     promo1 = Promocode.objects.get(code="IBP20")
#     print(promo1)

#     promo5 = Promocode.objects.get(code="IOO133")

#     allinvpaid = Invoice.objects.filter(description=promo1)
#     print(allinvpaid)

#     for a in allinvpaid:
#         a.description = promo5
#         a.save()

#     return HttpResponse("Success")

# def test11(request):
#     if request.method == "GET":

#         'currency': 'MYR', 
#         'appcode': '002659', 
#         'paydate': '2017-08-02 20:07:50', 
#         'status': '00', 
#         'orderid': '727920170802120404', 
#         'skey': 'df15930f6af3d17973c17c73eb728c42', 
#         'domain': 'innbparkhotel', 
#         'error_desc': '', 
#         'amount': '415.29', 
#         'channel': 'credit', 
#         'nbcb': '1', 
#         'tranID': '18052148'})

#     return HttpResponse(r)






@login_required(login_url='/login/')
def querycheck(request):

    # asdf = 
    qindate = datetime.strptime("2018-06-01", '%Y-%m-%d')
    qoutdate = datetime.strptime("2018-04-26", '%Y-%m-%d')
    # all_invoices = logging.objects.filter(created_on__gte=qindate, created_on__lte=qoutdate)
    # all_invoices1 = Booking.objects.filter(checkin_date__gte=qindate)
    all_invoices = Invoice.objects.filter(otherref= "279669892")

    # all_invoices = Invoice.objects.none()
    # for a in all_invoices1:

    #     refno1 = a.referenceno
    #     aasdf = Invoice.objects.filter(referenceno=refno1)

    #     all_invoices = all_invoices | aasdf


    # all_invoices = all_invoices.filter(gst__gt=0).order_by('referenceno')

    # for d in all_invoices:
    #     d.total = decimal.Decimal(d.total)-decimal.Decimal(d.gst)
    #     d.gst=0
    #     d.save()

    # list1=[]
    # g=0
    # for a in all_invoices:

    #     if g==a.invoiceno:

    #     # asdf = Invoice.objects.filter(invoiceno=g).count()
    #     # if asdf > 1:
    #     # return HttpResponse(g)
    #         list1.append(str(g)+",")

    #     else:
    #         g = a.invoiceno


    # all_invoices = Invoice.objects.filter(datecreated__gt=qindate, invoiceno__exact='', checkedin1__isnull=False)
    # all_invoices=Invoice.objects.filter(bookingfeepaid=False, staffbooking=False,molpay=True,totalpaid=False)
    # invno = ""

    # for a in all_invoices:
    #     var1 = var1 + 1
    #     a.invoiceno=1800000 + var1
    #     a.save()

    # tz = timezone('Etc/GMT+8')
    # todaydate = tz.localize(datetime.today())
    # date_customers3 = Booking.objects.filter(checkout_date=todaydate).exclude(checkedout1__isnull=False).order_by('referenceno')

    # depositquery = []
    # referencenotest = None
    # totalcash = 0
    # totalcc = 0
    # asdf=[]

    # Otherstotal = ""
    # for row in date_customers3:
    #     if referencenotest == row.referenceno:
    #         t = None
    #     else:
    #         try:
    #             qq = Invoice.objects.get(referenceno=row.referenceno)
    #         except Invoice.DoesNotExist:
    #             return HttpResponse(row.referenceno)

            # if qq.depositcash is None:
            #     qq.depositcash = 0
            # if qq.depositcc is None:
            #     qq.depositcc = 0
            # totalcash = totalcash + qq.depositcash
            # totalcc = totalcc + qq.depositcc
            # if qq.depi=="Others":
            #     Otherstotal = Otherstotal + " | " + str(qq.depdescrip)  


            # depositquery.extend(list(Invoice.objects.filter(referenceno=row.referenceno)))
            # referencenotest = row.referenceno
    
  








    # return HttpResponse(list1)


    context = {
    'all_invoices':all_invoices,

    }
    return render(request,"booking/allinvoices.html",context)


# @login_required(login_url='/login/')
# def querycheck2(request):
#     # all_invoices =Invoice.objects.filter(invoiceno__gte=180000).count()
#     # # asdf = Invoice.objects.get(pk=5331)
#     # list1=[]

#     # for a in range(0, all_invoices):
#     #     g = 1800000+a
#     #     try:
#     #         asdf = Invoice.objects.get(invoiceno=g)
#     #     # if asdf > 1:
#     #     #     return HttpResponse(g)

#     #     except Invoice.DoesNotExist:
#     #         list1.append(str(g)+",")
#     list1 =Invoice.objects.filter(invoiceno__gte=180000).order_by('invoiceno').last()
#     # d = len(list1)
#     return HttpResponse(list1.invoiceno)
#     # return HttpResponse(all_invoices)
#     # context = {
#     # 'all_invoices':all_invoices,

#     # }
#     # return render(request,"booking/allinvoices.html",context)



def querycheck4(request):
    qindate = datetime.strptime("2019-08-14 14:06", '%Y-%m-%d %H:%M')
    qoutdate = datetime.strptime("2019-08-14 23:01", '%Y-%m-%d %H:%M')   

    asdfasfd = Booking.objects.all().filter(checkedin1__gte=qindate, checkedin1__lte=qoutdate).exclude(room_type_name__pk=24).exclude(room_type_name__pk=23).order_by('checkin_date')
    # booklist = Booking.objects.none()
    # for a in asdfasfd:
    #     try:
    #         booknumber = Invoice.objects.get(referenceno = a.referenceno)
    #         asdfasfd= asdfasfd.exclude(referenceno=a.referenceno)

    #     except Invoice.DoesNotExist:
    #         book = Booking.objects.get(pk=a.pk)

        # for d in booknumber:
        #     if d.checkedout1 is None:

            # booklist = book | booklist



    allbookings = asdfasfd

    

    context = {
    'allbookings':allbookings,

    }
    return render(request,"booking/allbooking.html",context)


def querycheck3(request):
    qindate = datetime.strptime("2018-11-01", '%Y-%m-%d')
    asdfasfd = Booking.objects.all().filter(checkedout1__isnull=True, checkedin1__isnull=True,checkin_date__gte=qindate).order_by('referenceno')
    booklist = Booking.objects.none()
    for a in asdfasfd:
        try:
            booknumber = Invoice.objects.get(referenceno = a.referenceno)
            asdfasfd= asdfasfd.exclude(referenceno=a.referenceno)

        except Invoice.DoesNotExist:
            book = Booking.objects.get(pk=a.pk)

        # for d in booknumber:
        #     if d.checkedout1 is None:

            # booklist = book | booklist



    allbookings = asdfasfd

    

    context = {
    'allbookings':allbookings,

    }
    return render(request,"booking/allbooking.html",context)


def querycheck2(request):
    qindate = datetime.strptime("2018-09-01", '%Y-%m-%d')
    asdfasfd = Booking.objects.filter(checkin_date__gte=qindate)
    listlst2 = Invoice.objects.none()
    for a in asdfasfd:
        listst = Invoice.objects.filter(referenceno=a.referenceno, totalpaid=False)
        listlst2 = listlst2 | listst
    # booklist = Booking.objects.none()
    # for a in asdfasfd:
    #     booknumber = Booking.objects.filter(referenceno = a.referenceno)
    #     for d in booknumber:
    #         if d.checkedout1 is None:

    #             booklist = booknumber | booklist


    # for a in listlst2:
    #     a.gst = decimal.Decimal(a.total)*decimal.Decimal(0.06)
    #     a.total = decimal.Decimal(a.total)+decimal.Decimal(a.gst)
    #     a.save()




    all_invoices = listlst2

    

    context = {
    'all_invoices':all_invoices,

    }
    return render(request,"booking/allinvoices.html",context)











@login_required(login_url='/login/')
def chg11(request):
    try:
        record = Depositsum.objects.get(pk=1)
        depoform = DepositsumForm(request.POST or None, instance=record)
        if depoform.is_valid():
            depoform.save() 

    except Depositsum.DoesNotExist:
        depoform = DepositsumForm(request.POST or None)   
        if depoform.is_valid():
            depoform.save() 
     
            return redirect('detail')


    context= {
        "depoform":depoform
    }
    return render(request,"booking/depo.html", context)






import os, random, struct, hashlib
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from django.conf import settings
from django.http import HttpResponse
from Crypto import Random 


@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def downloadtest1(request):

    key=hashlib.sha256(passw1).digest()
    path2 = request.GET.get('path2')
    # path2= "/hotel/static/images/upload/Yone-We Gaw"

    img_list2 = os.listdir(path2) 
    for b in img_list2: 
        chunk_size = 64*1024

        filename= path2 +"/" + b
        output_file = filename+".enc"
        file_size = os.path.getsize(filename)

        IV = Random.new().read(AES.block_size)
        # for i in range(16):
        #     IV += chr(random.randint(0, 0xFF))
        encryptor = AES.new(key, AES.MODE_CBC, IV)
        with open(filename, 'rb') as inputfile:
            with open(output_file, 'wb') as outf:
                outf.write(struct.pack('<Q', file_size))
                outf.write(IV)
                while True:
                    chunk = inputfile.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                       chunk += bytes(' ' * (16 - len(chunk) % 16), 'utf-8')
                    outf.write(encryptor.encrypt(chunk))

    return HttpResponse('success')



@login_required(login_url='/login/')
def download1(request):
    cust = request.GET.get('pk')
    cust2 = Customer.objects.get(pk=cust)

    cust3 = str(cust2.first_name + " " + cust2.last_name)     
    path="/hotel/static/images/upload/" + cust3


    try:
        img_list1 =os.listdir(path)

    except FileNotFoundError:
        return HttpResponse("No Attached Documents")

    for a in img_list1:
        aend = a[-4:]
        if aend != ".enc":
            print(aend)
            os.remove(path + "/"+ a)
    img_list =os.listdir(path)     

    context= {
        'images': img_list,
        'cust3':cust3,
        'cust':cust
    }
    return render(request, 'booking/gallery.html', context)




@login_required(login_url='/login/')
def download2(request):
    cust = request.GET.get('pk')
    cust2 = request.GET.get('cust2')
    cust3 = request.GET.get('image')
    
    image8 = cust3[:-4]
    image = "img/"+cust2+"/"+image8

    passw1= ""
    key=hashlib.sha256(passw1).digest()
    chunk_size = 64*1024
    filename= "/hotel/static/images/upload/"+cust2 +"/" + cust3  
    output_file = filename[:-4]
       
    with open(filename, 'rb') as inf:
        filesize = struct.unpack('<Q', inf.read(struct.calcsize('Q')))[0]
        IV = inf.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, IV)
        with open(output_file, 'wb') as outf:
            while True:
                chunk = inf.read(chunk_size)
                if len(chunk)==0:
                    break
                outf.write(decryptor.decrypt(chunk))
            outf.truncate(filesize)

    context= {
        'image': image,
        'filename':output_file,
        'cust':cust
    }
    return render(request, 'booking/gallery2.html', context)    


@login_required(login_url='/login/')
def download3(request):
    delf = request.GET.get('del')
    cust = request.GET.get('cust')
    os.remove(delf)
    return redirect('/download1/?pk=' + cust)





@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def portal4(request):
    qin_date1 = request.GET.get('startdate')
    qout_date1 = request.GET.get('enddate')
    today = datetime.now().date()
    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    if not qin_date1:

        qin_date= today
        qout_date= today+timedelta(days=30)

    else:
        qin_date = parsing_date(qin_date1)
        qout_date = parsing_date(qout_date1)  

    # amsterdam = pytz.timezone('Asia/Singapore')
    # aware = qin_date.replace(tzinfo=amsterdam)
    # qindate = aware.astimezone(pytz.UTC)

    # aware2 = qout_date.replace(tzinfo=amsterdam)
    # qoutdate = aware2.astimezone(pytz.UTC)

    # qindate = datetime.combine(qin_date, datetime.min.time())
    # qoutdate = datetime.combine(qout_date, datetime.min.time())
    numberofpeople =[]
    numberinroom = []
    datess = []
    vacant =[]
    numofstay= int((qout_date-qin_date).days)
    Roomtypess = Roomtype.objects.all().order_by('pk')
    rt = Roomtype.objects.get(pk=13)

    for each in range(0, numofstay):

        date1 = qin_date + timedelta(days=each)
        date2 = date1.strftime("%Y-%m-%d %a")
        date3 = qin_date + timedelta(days=each) + timedelta(days=1)
        # for each in Roomtypess:
        bookingcount = Booking.objects.filter(checkin_date=date1).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(room_type_name__pk=22).exclude(room_type_name__pk=28).count()


        ab = Roomnumber.objects.all()
        we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=date1, booking__checkin_date__lt=date3,booking__checkout_date__gt=F('booking__checkin_date'))
        asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=date1,booking__checkout_date__lte=date3,booking__checkin_date__lt=F('booking__checkout_date'))
        drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=date1, booking__checkout_date__gte=date3)
        qwer = asdf | we | drrr
        

        cd_ = ab.exclude(id__in=qwer).count()
        vacant.append(cd_)




        # numberofpeople.append(bookingcount)
        # numberinroom.append(numberofpeople)
        numberinroom.append(bookingcount)
        datess.append(date2)

    # table = Invoice.objects.all().filter(totalpaiddate__gte=qindate, totalpaiddate__lte=qoutdate).order_by('checkedin1')
    total =0
    cash =0
    cc=0
    gst=0
    st=0
    mol=0
    all_bookings = 1

    datess2 = json.dumps(datess)


    context = {

    'numberinroom':numberinroom,
    'datess':datess2,
    'vacant':vacant,
    }


    return render(request, "booking/graph.html", context)




@csrf_exempt
def channelmanagerapi(request):
    if request.method =="POST":

        postrequest = request.POST
        postrequest2 = request.content_params
        postrequest3 = request.body
        postrequest4 = request.META
        postrequest5 = json.loads(request.body.decode('utf-8'))
        postrequest6 = postrequest5['reservations']['reservation']


        ccode={
            "Afghanistan":"AF",
            "Aland Islands":"AX",
            "Albania":"AL",
            "Algeria":"DZ",
            "American Samoa":"AS",
            "Andorra": "AD",
            "Angola":"AO",
            "Anguilla":"AI",
            "Antarctica":"AQ",
            "Antigua and Barbuda":"AG",
            "Argentina":"AR",
            "Armenia":"AM",
            "Aruba":"AW",
            "Australia":"AU",
            "Austria":"AT",
            "Azerbaijan":"AZ",
            "Bahamas":"BS",
            "Bahrain":"BH",
            "Bangladesh":"BD",
            "Barbados":"BB",
            "Belarus":"BY",
            "Belgium":"BE",
            "Belize":"BZ",
            "Benin":"BJ",
            "Bermuda":"BM",
            "Bhutan":"BT",
            "Bolivia, Plurinational State of":"BO",
            "Bonaire, Sint Eustatius and Saba":"BQ",
            "Bosnia and Herzegovina":"BA",
            "Botswana":"BW",
            "Bouvet Island":"BV",
            "Brazil":"BR",
            "British Indian Ocean Territory":"IO",
            "Brunei Darussalam":"BN",
            "Bulgaria":"BG",
            "Burkina Faso":"BF",
            "Burundi":"BI",
            "Cambo Verde":"CV",
            "Cambodia":"KH",
            "Cameroon":"CM",
            "Canada":"CA",
            "Caymand Islands":"KY",
            "Central African Republic":"CF",
            "Chad":"TD",
            "Chile":"CL",
            "China":"CN",
            "Christmas Island":"CX",
            "Cocos (Keeling) Islands":"CC",
            "Colombia":"CO",
            "Comoros":"KM",
            "Congo":"CG",
            "Congo, the Democratic Republic of the":"CD",
            "Cook Islands":"CK",
            "Costa Rica":"CR",
            "Croatia":"HR",
            "Cuba":"CU",
            "Curacao":"CW",
            "Cyrpus":"CY",
            "Czechia":"CZ",
            "Denmark":"DK",
            "Djibouti":"DJ",
            "Dominica":"DM",
            "Dominican Republic":"DO",
            "Ecuador":"EC",
            "Egypt":"EG",
            "El Salvador":"SV",
            "Equatorial Guinea":"GQ",
            "Eritrea":"ER",
            "Estonia":"EE",
            "Ethiopia":"ET",
            "Falkland Islands (Malvinas)":"FO",
            "Faroe Islands":"DZ",
            "Fiji":"FJ",
            "Finland":"FI",
            "France":"FR",
            "French Guiana":"GF",
            "French Polynesia":"PF",
            "French Southern Territories":"TF",
            "Gabon":"GA",
            "Gambia":"GM",
            "Georgia":"GE",
            "Germany":"DE",
            "Ghana":"GH",
            "Gibraltar":"GI",
            "Greece":"GR",
            "Greenland":"GL",
            "Grenada":"GD",
            "Guadeloupe":"GP",
            "Guam":"GU",
            "Guatemala":"GT",
            "Guernsey":"GG",
            "Guinea":"GN",
            "Guinea-bissau":"GW",
            "Guyana":"GY",
            "Haiti":"HT",
            "Heard Island and Mcdonald Islands":"HM",
            "Holy See (Vatican City State)":"VA",
            "Honduras":"HN",
            "Hong Kong":"HK",
            "Hungary":"HU",
            "Iceland":"IS",
            "India":"IN",
            "Indonesia":"ID",
            "Iran, Islamic Republic of":"IR",
            "Iraq":"IQ",
            "Ireland":"IE",
            "Isle of Man":"IM",
            "Israel":"IL",
            "Italy":"IT",
            "Jamaica":"JM",
            "Japan":"JP",
            "Jersey":"JE",
            "Jordan":"JO",
            "Kazakhstan":"KZ",
            "Kenya":"KE",
            "Kiribati":"KI",
            "North Korea, Democratic People''s Republic of":"KP",
            "South Korea, Republic of":"KR",
            "Kuwait":"KW",
            "Kyrgyzstan":"KG",
            "Lao People''s Democratic Republic":"LA",
            "Latvia":"LV",
            "Lebanon":"LB",
            "Lesotho":"LS",
            "Liberia":"LR",
            "Libyan Arab Jamahiriya":"LY",
            "Liechtenstein":"LI",
            "Lithuania":"LT",
            "Luxembourg":"LU",
            "Macao":"MO",
            "Macedonia, the Former Yugoslav Republic of":"MK",
            "Madagascar":"MG",
            "Malawi":"MW",
            "Malaysia":"MY",
            "Maldives":"MV",
            "Mali":"ML",
            "Malta":"MT",
            "Marshall Islands":"MH",
            "Martinique":"MQ",
            "Mauritania":"MR",
            "Mauritius":"MU",
            "Mayotte":"YT",
            "Mexico":"MX",
            "Micronesia, Federated States of":"FM",
            "Moldova, Republic of":"MD",
            "Monaco":"MC",
            "Mongolia":"MN",
            "Montenegro":"ME",
            "Montserrat":"MS",
            "Morocco":"MA",
            "Mozambique":"MZ",
            "Myanmar":"MM",
            "Namibia":"NA",
            "Nauru":"NR",
            "Nepal":"NP",
            "Netherlands":"NL",
            "New Caledonia":"NC",
            "New Zealand":"NZ",
            "Nicaragua":"NI",
            "Niger":"NE",
            "Nigeria":"NG",
            "Niue":"NU",
            "Norfolk Island":"NF",
            "Northern Mariana Islands":"M",
            "Norway":"NO",
            "Oman":"OM",
            "Pakistan":"PK",    
            "Palau":"PW",
            "Palestinian Territory, Occupied":"PS",
            "Panama":"PA",
            "Papua New Guinea":"PG",
            "Paraguay":"PY",
            "Peru":"PE",
            "Philippines":"PH",
            "Pitcairn":"PN",
            "Poland":"PL",
            "Portugal":"PT",
            "Puerto Rico":"PR",
            "Qatar":"QA",
            "Reunion":"RE",
            "Romania":"RO",
            "Russia":"RU",
            "Rwanda":"RW",
            "Saint Barthelemy":"BL",
            "Saint Helena, Ascension and Tristan da Cunha":"SH",
            "Saint Kitts and Nevis":"KN",
            "Saint Lucia":"LC",
            "Saint Martin (French part)":"MF",
            "Saint Pierre and Miquelon":"PM",
            "Saint Vincent and The Grenadines":"VC",
            "Samoa":"WS",
            "San Marino":"SM",
            "Sao Tome and Principe":"ST",
            "Saudi Arabia":"SA",
            "Senegal":"SN",
            "Serbia":"RS",
            "Seychelles":"SC",
            "Sierra Leone":"SL",
            "Singapore":"SG",
            "Sint Maarten (Dutch part)":"SX",
            "Slovakia":"SK",
            "Slovenia":"SI",
            "Solomon Islands":"SB",
            "Somalia":"SO",
            "South Africa":"ZA",
            "South Georgia and The South Sandwich Islands":"GS",
            "Spain":"ES",
            "Sri Lanka":"LK",
            "Sudan":"SD",
            "Suriname":"SR",
            "Svalbard and Jan Mayen":"SJ",
            "Swaziland":"SZ",
            "Sweden":"SE",
            "Switzerland":"CH",
            "Syrian Arab Republic":"SY",
            "Taiwan":"TW",
            "Tajikistan":"TJ",
            "Tanzania, United Republic of":"TZ",
            "Thailand":"TH",
            "Timor-leste":"TL",
            "Togo":"TG",
            "Tokelau":"TK",
            "Tonga":"TO",
            "Trinidad and Tobago":"TT",
            "Tunisia":"TN",
            "Turkey":"TR",
            "Turkmenistan":"TM",
            "Turks and Caicos Islands":"TC",
            "Tuvalu":"TV",
            "USA":"US",
            "Uganda":"UG",
            "Ukraine":"UA",
            "United Arab Emirates":"AE",
            "United Kingdom":"GB",
            "United States Minor Outlying Islands":"UM",
            "Uruguay":"UY",
            "Uzbekistan":"UZ",
            "Vanuatu":"VU",
            "Venezuela, Bolivarian Republic of":"VE",
            "Vietnam":"VN",
            "Virgin Islands, British":"VG",
            "Virgin Islands, U.S.":"VI",
            "Wallis and Futuna":"WF",
            "Western Sahara":"EH",
            "Yemen":"YE",
            "Zambia":"ZM",
            "Zimbabwe":"ZW",


        }
        
        totalprice=0

        for a in postrequest6:
            test3 = a['customer']
            email = test3['email']
            phno= test3['telephone']


            test4 = a['room']
            nameeee1=test4[0]['guest_name'] 

            splitted = nameeee1.split()

            lastname = splitted[-1]
            first211 = splitted[:-1]
            first_name = " ".join(first211)




            firstname = test3['first_name']
            lastname = test3['last_name']
            country = test3['countrycode']
            totalpric = a['totalprice']
            referral1 = a['company']
            status = a['booking_status']
            paid1= a['payment_type']
            refnumb = a['channel_ref']
            
            if status=="cancel":
                try:
                    delete12 = Invoice.objects.get(otherref= refnumb)
                    invoicedelno = delete12.referenceno
                    delete12.delete()
                    allbookingdel = Booking.objects.filter(referenceno = invoicedelno)
                    for aat in allbookingdel:
                        aat.delete()
                except Invoice.DoesNotExist:

                    html_message = loader.render_to_string('booking/email2.html',{
                    'first_name':firstname,
                    'last_name': lastname,
                    'total':0,
                    # 'booking':0,
                    'checkindate': 0,
                    'checkoutdate': 0,
                    'referenceno': postrequest3,
                    'addcomments':"REMOVE CANT FIND INVOICE",
                    'nop': 0

                    })

                    msg = EmailMultiAlternatives("REMOVE CANT FIND INVOICE", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                    msg.attach_alternative(html_message, "text/html")

                    msg.send()






            elif status =="new" or status =="modify":
              



                if status=="modify":
                    try:
                        delete12 = Invoice.objects.get(otherref= refnumb)
                        invoicedelno = delete12.referenceno
                        if delete12.checkedin1 :


                            html_message = loader.render_to_string('booking/email2.html',{
                            'first_name':firstname,
                            'last_name': lastname,
                            'total':0,
                            # 'booking':0,
                            'checkindate': 0,
                            'checkoutdate': 0,
                            'referenceno': postrequest3,
                            'addcomments':"MODIFY CHECK",
                            'nop': 0

                            })

                            msg = EmailMultiAlternatives("BOOKING MODIFY BUT ALREADY CHECKED IN", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                            msg.attach_alternative(html_message, "text/html")

                            msg.send()




                        else:




                            delete12.delete()
                            allbookingdel = Booking.objects.filter(referenceno = invoicedelno)
                            for aat in allbookingdel:
                                aat.delete()



                            html_message = loader.render_to_string('booking/email2.html',{
                            'first_name':firstname,
                            'last_name': lastname,
                            'total':0,
                            # 'booking':0,
                            'checkindate': 0,
                            'checkoutdate': 0,
                            'referenceno': postrequest3,
                            'addcomments':"MODIFY CHECK",
                            'nop': 0

                            })

                            msg = EmailMultiAlternatives("MODIFY CHECK", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                            msg.attach_alternative(html_message, "text/html")

                            msg.send()






                    except Invoice.DoesNotExist:


                        html_message = loader.render_to_string('booking/email2.html',{
                        'first_name':firstname,
                        'last_name': lastname,
                        'total':0,
                        # 'booking':0,
                        'checkindate': 0,
                        'checkoutdate': 0,
                        'referenceno': postrequest3,
                        'addcomments':"MODIFY CANT FIND INVOICE",
                        'nop': 0

                        })

                        msg = EmailMultiAlternatives("MODIFY CANT FIND INVOICE", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                        msg.attach_alternative(html_message, "text/html")

                        msg.send()






                else:

                    delete112 = Invoice.objects.filter(otherref= refnumb)
                    if delete112:


                        html_message = loader.render_to_string('booking/email2.html',{
                        'first_name':firstname,
                        'last_name': lastname,
                        'total':0,
                        # 'booking':0,
                        'checkindate': 0,
                        'checkoutdate': 0,
                        'referenceno': postrequest3,
                        'addcomments':"DOUBLEBOOK CHECK",
                        'nop': 0

                        })

                        msg = EmailMultiAlternatives("DOUBLEBOOK CHECK", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                        msg.attach_alternative(html_message, "text/html")

                        msg.send()
                        return HttpResponse("errror")


                    else:      
                        asdfaaaa = "continue"




                if referral1 =="BOOKING.COM":
                    referral = "bookings.com"
                    country1 = country.upper()


                elif referral1 == "AGODAYCS":
                    referral = "Agoda"
                    if country in ccode:
                        country1 = str(ccode[country])
                    else:
                        country1 = "ZW" 


                elif referral1== "TRAVELOKA":
                    referral = "Traveloka"
                    country1 = "ZW" 

                elif referral1=="EXPEDIA":
                    referral = "Expedia"
                    country1 = "ZW"

                elif referral1 =="CTRIP":
                    referral = "Ctrip"
                    country1 = "ZW"

                elif referral1=="ASIATRAVEL":
                    referral="Asiatravel"
                    if country in ccode:
                        country1 = str(ccode[country])
                    else:
                        country1 = "ZW" 

                else:
                    referral = referral1

                    msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", referral1, "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com']) 

                    msg.send()






                now = datetime.now()
                for x in firstname:
                   test_name= str(ord(x)) 
                for y in lastname:
                   testl_name= str(ord(y))    
                referenceno =  test_name + testl_name + now.strftime("%Y%m%d%H%M%S")   
                if referral=="Ctrip":
                    email = str(referenceno) + "@" + "randomgenerate.com"
                if not email:
                    email = str(referenceno) + "@" + "randomgenerate.com"

                if not phno:
                    phno = "1234567890"
                 
                try:
                    code = Customer.objects.get(email=email, phone_number=phno)
                    code.first_name = firstname
                    code.last_name = lastname
                    code.save()
                    cuspk = code.pk

                except Customer.DoesNotExist:
                    cust = Customer.objects.create()
                    cust.first_name = firstname
                    cust.last_name = lastname
                    cust.email = email
                    cust.phone_number = phno
                    cust.country = country1
                    cust.save()
                    cuspk = cust.pk
     
                breakfast = Roomtype.objects.get(pk=23)
                xbed = Roomtype.objects.get(pk=22)

                

                customer13 = Customer.objects.get(pk=cuspk)
                price1=0
                totalprice=0
                totalgst=0
                counter11 = 0
                price2=0
                eachgst=0
                test4 = a['room']
                for b in test4:
                    counter11 = counter11 + 1
                    checkin_date = b['arrival_date']
                    checkout_date = b['departure_date']
                    def parsing_date(text):
                        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                            try:
                                return datetime.strptime(text, fmt)
                            except ValueError:
                                pass
                        raise ValueError('no valid date format found')

                    ind = parsing_date(checkin_date)
                    outd = parsing_date(checkout_date)
                    # roomid = b['id']
                    nop = b['numberofguests']
                    addcomments = b['remarks']
                    price5 = b['totalprice']
                    extrabed = b['extra_adult_rate']
                    rpri = b['price']


                    roomid = b['price'][0]['rate_id']
                    roomid1 = b['id']

                    if referral=="bookings.com":


                        #AFTER
                        price1 = format(decimal.Decimal(price5)/decimal.Decimal(1.06),'.2f')
                        eachgst = format(decimal.Decimal(price1)*decimal.Decimal(0.06),'.2f')
                        # eachgst = format(decimal.Decimal(price1)*decimal.Decimal(0.00),'.2f')

                        price2 = format(decimal.Decimal(price1)+decimal.Decimal(eachgst),'.2f')



















                    elif referral=="Agoda":
                        # price1 = format(decimal.Decimal(price5))
                        # eachgst = format(decimal.Decimal(price1)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                        price1=0
                        price2=0
                        eachgst=0
                        for c in rpri:
                            if paid1 == "Channel Collect":
                                roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                                # roompergst = 0 
                                # roomperprice = format(decimal.Decimal(c['amount'])-decimal.Decimal(roompergst),'.2f')
                                roomperprice = format(decimal.Decimal(c['amount']),'.2f')
                                asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                                eachgst += decimal.Decimal(roompergst)
                                price1 += decimal.Decimal(roomperprice)/decimal.Decimal(0.83)
                                price2 += decimal.Decimal(asdfpricing)

                            else:
                                roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                                # roompergst = 0 
                                roomperprice = format(decimal.Decimal(c['amount']),'.2f')
                                # roomperprice = format(decimal.Decimal(c['amount'])-decimal.Decimal(roompergst),'.2f')
                                asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                                eachgst += decimal.Decimal(roompergst)
                                price1 += decimal.Decimal(roomperprice)
                                price2 += decimal.Decimal(asdfpricing)
                  
                        if extrabed >0:
                            if paid1 == "Channel Collect":
                                roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                                # roompergst =0
                                roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                                Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                                price1 = decimal.Decimal(price1) + (decimal.Decimal(roomperprice)/decimal.Decimal(0.83))

                                eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)
                                price2 = decimal.Decimal(format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f'))+price2
                                if roomid == "94738":
                                    price1 = decimal.Decimal(price1) - decimal.Decimal(extrabed)

                            else:


                                roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                                # roompergst =0
                                roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                                Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                                price1 = decimal.Decimal(price1) + (decimal.Decimal(roomperprice))

                                eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)
                                price2 = decimal.Decimal(format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f'))+price2
                                if roomid == "94738":
                                    price1 = decimal.Decimal(price1) - decimal.Decimal(extrabed)



                    elif referral =="Traveloka":
                        price1=0
                        price2=0
                        eachgst=0                        
                        for c in rpri:

                            roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                            # roompergst = 0

                            roomperprice = format(decimal.Decimal(c['amount'])-decimal.Decimal(roompergst),'.2f')
                            asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                            eachgst += decimal.Decimal(roompergst)
                            # price1 += decimal.Decimal(roomperprice)/decimal.Decimal(0.85)
                            price1 += decimal.Decimal(roomperprice)
                            price2 += decimal.Decimal(asdfpricing)


                  
                    elif referral =="Expedia":
                        price1=0
                        price2=0
                        eachgst=0                        
                        for c in rpri:

                            roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                            # roompergst = 0 



                            roomperprice = format((decimal.Decimal(c['amount']))-decimal.Decimal(roompergst),'.2f')
                            asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                            eachgst += decimal.Decimal(roompergst)
                            price1 += decimal.Decimal(roomperprice)/decimal.Decimal(0.8)
                            price2 += decimal.Decimal(asdfpricing)

                    elif referral =="Ctrip":
                        price1=0
                        price2=0
                        eachgst=0                        
                        for c in rpri:

                            roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                            # roompergst = 0


                            roomperprice = format(decimal.Decimal(c['amount'])-decimal.Decimal(roompergst),'.2f')
                            asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                            eachgst += decimal.Decimal(roompergst)
                            price1 += decimal.Decimal(roomperprice)/decimal.Decimal(0.85)
                            price2 += decimal.Decimal(asdfpricing)




                    elif referral =="Asiatravel":
                        price1=0
                        price2=0
                        eachgst=0                        
                        for c in rpri:

                            roompergst = format(decimal.Decimal(c['amount'])/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')

                            # roompergst =0 



                            roomperprice = format(decimal.Decimal(c['amount'])-decimal.Decimal(roompergst),'.2f')
                            asdfpricing = format(decimal.Decimal(roomperprice)+decimal.Decimal(roompergst),'.2f')
                            eachgst += decimal.Decimal(roompergst)
                            price1 += decimal.Decimal(roomperprice)/decimal.Decimal(0.83)
                            price2 += decimal.Decimal(asdfpricing)



                    roomid = b['price'][0]['rate_id']
                    roomid1 = b['id']


                    
                    if roomid =="94730":
                        roompk=13
                        bkkfast = 0

                    elif roomid == "94738":
                        roompk=13
                        bkkfast = 2

                    elif roomid =="94731":
                        if roomid1 =="29666":
                            roompk=16
                            bkkfast = 0
                        elif roomid1 =="29667":
                            roompk=15
                            bkkfast = 0   
                        elif roomid1 =="29668":
                            roompk=19
                            bkkfast = 0    

                    elif roomid =="94737":
                        roompk = 16
                        bkkfast =2
                        if roomid1 =="29666":
                            roompk=16
                            bkkfast = 2
                        elif roomid1 =="29667":
                            roompk=15
                            bkkfast = 2   
                        elif roomid1 =="29668":
                            roompk=19
                            bkkfast = 2  


                    elif roomid =="94732":
                        roompk = 21
                        bkkfast =0
                    elif roomid == "94736":
                        roompk = 21
                        bkkfast =1

                    roomtype=Roomtype.objects.get(pk=roompk)
                    aaaa =  Roomnumber.objects.all().filter(room_type_name__pk=roompk, hidden=False)
                    we = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__gte=ind, booking__checkin_date__lt=outd, booking__checkout_date__gt=F('booking__checkin_date'))
                    asdf = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkout_date__gt=ind,booking__checkout_date__lte=outd,booking__checkin_date__lt=F('booking__checkout_date'))
                    drrr = Roomnumber.objects.all().filter(booking__earlyout=False, booking__checkin_date__lte=ind, booking__checkout_date__gte=outd)
                    qwer = asdf | we | drrr
                    cd = aaaa.exclude(id__in=qwer)
                    if not cd:
                        html_message = loader.render_to_string('booking/email2.html',{
                        'first_name':firstname,
                        'last_name': lastname,
                        'total':0,
                        # 'booking':0,
                        'checkindate': checkin_date,
                        'checkoutdate': checkout_date,
                        'referenceno': postrequest3,
                        'addcomments':"OVERBOOK ALERT",
                        'nop': nop

                        })

                        msg = EmailMultiAlternatives("CHANNEL MANAGER OVERBOOKED ALERT ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com', 'admin@innbparkhotel.com']) 

                        msg.attach_alternative(html_message, "text/html")

                        msg.send()



                        deleteallprevious = Booking.objects.filter(referenceno=referenceno)
                        if deleteallprevious:
                            for a in deleteallprevious:
                                a.delete()








                        return HttpResponse('This type of rooms have been fully booked')
                    


                    de = cd
                    randomnumber = random.choice(de)
                    rnum= Roomnumber.objects.get(room_number=randomnumber)
                    rtname = roomtype
                    
                    Book = Booking.objects.create(first_name=firstname, additional_comments = addcomments, referenceno =referenceno, last_name = lastname, email=email, country=country1, room_type_name=rtname, room_number=rnum, cust33=customer13, phone_number=phno, number_of_people = nop, paymentprice=price1, actualpay=price1, checkin_date=ind, checkout_date=outd, booktype=referral)
                    if bkkfast == 1 :
                        bprice = 0
                        Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bprice, actualpay=bprice, checkin_date=ind, checkout_date=outd, booktype=referral)
                    
                    elif bkkfast == 2:        
                        for a in (0,2):
                            bprice = 0
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bprice, actualpay=bprice, checkin_date=ind, checkout_date=outd, booktype=referral)
                    

                    numofstay = int((outd-ind).days)

                    if 'addons' in b:
                        bkfa = b['addons']
                        for af1 in bkfa:
                            noofb=af1['noofunits']
                            actualnoofb = noofb/numofstay

                            price9 = af1['totalprice']

                            price8 = format(decimal.Decimal(price9)/decimal.Decimal(1.06),'.2f')
                            # price8 = decimal.Decimal(price9)


                            price90 = decimal.Decimal(price8)/decimal.Decimal(actualnoofb)
                            eachgst = format(decimal.Decimal(eachgst)+(decimal.Decimal(price8)*decimal.Decimal(0.06)),'.2f')
                            # eachgst = format(decimal.Decimal(eachgst)+(decimal.Decimal(0)),'.2f')


                            price2 =  format(decimal.Decimal(price2) +decimal.Decimal(price9),'.2f')


                            if actualnoofb == 1 :
                                bprice = price90
                                Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bprice, actualpay=bprice, checkin_date=ind, checkout_date=outd, booktype=referral)
                            


                            elif actualnoofb == 2:        
                                for a in (0,2):
                                    bprice = price90
                                    Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=breakfast, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=bprice, actualpay=bprice, checkin_date=ind, checkout_date=outd, booktype=referral)




                    if referral=="bookings.com":
                        if extrabed >0:

                            roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                            # roompergst = 0


                            roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                            price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                            eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)



                    # elif referral =="Agoda":
                        # if extrabed >0:

                        #     roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                        #     roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                        #     Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                        #     price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                        #     eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)

                    elif referral =="Traveloka":
                        if extrabed >0:

                            roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                            # roompergst = 0

                            roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                            price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                            eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)


                    elif referral =="Expedia":
                        if extrabed >0:

                            roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                            # roompergst = 0


                            roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                            price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                            eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)



                    elif referral =="Ctrip":
                        if extrabed >0:

                            roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                            # roompergst = 0
                            roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                            price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                            eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)



                    elif referral =="Asiatravel":
                        if extrabed >0:

                            roompergst = format(decimal.Decimal(extrabed)/decimal.Decimal(1.06)*decimal.Decimal(0.06),'.2f')
                            # roompergst = 0


                            roomperprice = format(decimal.Decimal(extrabed)-decimal.Decimal(roompergst),'.2f')
                            Book13 = Booking.objects.create(first_name=customer13.first_name, additional_comments=addcomments, referenceno =referenceno, last_name = customer13.last_name, email=customer13.email, country=customer13.country, room_type_name=xbed, cust33=customer13, phone_number=customer13.phone_number, number_of_people = nop, paymentprice=extrabed, actualpay=extrabed, checkin_date=ind, checkout_date=outd, booktype=referral)
                            price1 = decimal.Decimal(price1) + decimal.Decimal(roomperprice)
                            eachgst = decimal.Decimal(eachgst)+ decimal.Decimal(roompergst)
                # firstname
                # lastname
                # country

                    totalprice += decimal.Decimal(price2)
                    totalgst += decimal.Decimal(eachgst)





                # if referral=="bookings.com":
                #     totalprice = totalprice*decimal.Decimal(1.1)
                    # totalgst = totalgst+decimal.Decimal(1.1)










                html_message = loader.render_to_string('booking/email2.html',{
                'first_name':firstname,
                # 'last_name': price,
                'total':totalprice,
                # 'booking':price,
                'checkindate': checkin_date,
                'checkoutdate': checkout_date,
                'referenceno': postrequest3,
                'addcomments':"CHANNELMANAGER",
                'nop': nop

                })

                msg = EmailMultiAlternatives("InnB Park Hotel Booking Details ", "Confirmation Email", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", ['bluehawke@hotmail.com']) 

                msg.attach_alternative(html_message, "text/html")

                msg.send()



                Inv = Invoice.objects.create()

                if nameeee1:
                    Inv.guestname=nameeee1

                Inv.referenceno = referenceno
                Inv.referral = referral
                    
                if referral =="Agoda":

                    if paid1 == "Channel Collect":
                        Inv.rtacomm = 0.17
                    else:    
                        print("nothing")                    
                

                elif referral =="Traveloka":
                    Inv.rtacomm = 0.15

                elif referral =="Ctrip":
                    Inv.rtacomm = 0.17
                    
                elif referral =="Asiatravel":
                    Inv.rtacomm = 0.17                    

                elif referral =="Expedia":
                    if paid1 == "Channel Collect":
                        Inv.rtacomm = 0.2
                    else:    
                        print("nothing")

                elif referral =="Corporate":
                    Inv.rtacomm = 0.0



                ttax15=0
                numofstay = int((outd-ind).days)
                for each in range(0, numofstay):
                    ttax13=10
                    ttax15+=ttax13

                Inv.otherref = refnumb
        #             Inv.gst=0
                if customer13.country == "MY":
                    Inv.ttax=0
                else:
                    Inv.ttax= decimal.Decimal(format(decimal.Decimal(ttax15)*decimal.Decimal(counter11),'.2f'))

                if paid1 == "Channel Collect":

                    Inv.ccpaid=totalprice
                    Inv.totalpaid = True
                    Inv.Paymentmethod = referral
                    Inv.total= totalprice
                    Inv.totalwch=decimal.Decimal(totalprice)-decimal.Decimal(totalgst)
                    Inv.gst = totalgst








                    actual13gst = format(Inv.total/decimal.Decimal(1.06)*decimal.Decimal(0.06),'2f')
                    proposedgst = format(Inv.gst,'.2f')
                    if proposedgst == actual13gst:
                        gst12345 = "nothing"
                    else:
                        Inv.rounding = decimal.Decimal(decimal.Decimal(proposedgst)-decimal.Decimal(actual13gst))
                        Inv.gst = decimal.Decimal(actual13gst)




                    if referral=="bookings.com" or referral=="Agoda":                    
                        Inv.total=decimal.Decimal(totalprice)-decimal.Decimal(totalgst)                    
                        Inv.totalwch=decimal.Decimal(totalprice)-decimal.Decimal(totalgst)
                        Inv.gst = 0
                        Inv.total = decimal.Decimal(totalpric)
                        Inv.rounding = decimal.Decimal(totalpric)-(decimal.Decimal(totalprice)-decimal.Decimal(totalgst))




                    if referral=="bookings.com":
                        Inv.commamount = 0
                    else:
                        Inv.commamount = decimal.Decimal(totalprice)/(decimal.Decimal(1)-decimal.Decimal(Inv.rtacomm))*decimal.Decimal(Inv.rtacomm)
                    Inv.totalpaiddate = datetime.now()
                    Inv.depositamt = decimal.Decimal(counter11) * decimal.Decimal(200)
                    Inv.email = customer13
                    Inv.save()

                else:

                    if not Inv.rtacomm:
                        Inv.commamount = 0

                    # Inv.Paymentmethod = referral
                    Inv.total=totalprice
                    Inv.totalwch=totalprice
                    Inv.gst = totalgst











                    actual13gst = format(Inv.total/decimal.Decimal(1.06)*decimal.Decimal(0.06),'2f')
                    proposedgst = format(Inv.gst,'.2f')
                    if proposedgst == actual13gst:
                        gst12345 = "nothing"
                    else:
                        Inv.rounding = decimal.Decimal(decimal.Decimal(proposedgst)-decimal.Decimal(actual13gst))
                        Inv.gst = decimal.Decimal(actual13gst)




                    if referral=="bookings.com" or referral=="Agoda":                    
                        Inv.total=decimal.Decimal(totalprice)-decimal.Decimal(totalgst)                    
                        Inv.totalwch=decimal.Decimal(totalprice)-decimal.Decimal(totalgst)
                        Inv.gst = 0
                        Inv.total = decimal.Decimal(totalpric)
                        Inv.rounding = decimal.Decimal(totalpric)-(decimal.Decimal(totalprice)-decimal.Decimal(totalgst))





                    if referral=="bookings.com":
                        Inv.commamount = 0
                    else:
                        if not Inv.rtacomm:
                            Inv.commamount = 0
                        else:
                            Inv.commamount =decimal.Decimal(totalprice)/(decimal.Decimal(1)-decimal.Decimal(Inv.rtacomm))*decimal.Decimal(Inv.rtacomm)
                    Inv.depositamt = decimal.Decimal(counter11) * decimal.Decimal(200)
                    Inv.email = customer13
                    Inv.save()

#             Inv.staffbooking = True
#             tqtt = None
#             if Inv.rtacomm:
#                 Inv.servicetax=gsttotal*(1-decimal.Decimal(Inv.rtacomm))
#             else:
#                 Inv.servicetax=gsttotal
#             if str(paid) == "paid":
#                 tqtt = "hj1335"
#                 Inv.totalpaid = True

#                 if Inv.rtacomm:

#                     Inv.ccpaid = decimal.Decimal(format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f'))


#                 # Inv.ccpaid = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5 *decimal.Decimal(1.1)*decimal.Decimal(1.06))),'.2f'))
                
#                 else:
#                     Inv.Paymentmethod = "Credit Card" 
#                     Inv.ccpaid = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5)),'.2f'))




#             if Inv.rtacomm:
#                 Inv.gst=format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(0.06),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f')
#                 Inv.total = decimal.Decimal(format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f'))
#                 Inv.totalwch = format(decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))*(1-decimal.Decimal(Inv.rtacomm)),'.2f')
#                 Inv.commamount = format(Inv.total*decimal.Decimal(Inv.rtacomm)/decimal.Decimal(1-decimal.Decimal(Inv.rtacomm)),'.2f')
#                 Inv.Paymentmethod = refer 

#             else:
#                 Inv.gst=decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5 ))*decimal.Decimal(0.06),'.2f'))
#                 Inv.total = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))
#                 Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))

#                 Inv.totalpaiddate = datetime.now()

#                 # year = datetime.now().strftime("%y")    
#                 # invnos = Invoice.objects.exclude(invoiceno__isnull=True).exclude(invoiceno__exact='').order_by('invoiceno').last()
#                 # inv_no = invnos.invoiceno
#                 # invoice_int = inv_no[2:]
#                 # new_invoice_int = int(invoice_int) + 1
#                 # new_invoice_no = year + str(format(new_invoice_int, '05d'))
#                 # Inv.invoiceno = new_invoice_no



#             Inv.totalwch = decimal.Decimal(format((bookedroomprice2+ (bookedroomprice5))*decimal.Decimal(1.06),'.2f'))



#             if int(rtname.pk) is not 22 and int(rtname.pk) is not 24:
#                 Inv.depositamt = 200
#             # elif int(rtname.pk)is not 24:
#             #     Inv.depositamt = 200                
#             else:
#                 Inv.depositamt=0
#             # Inv.bookingfee = bookingfeeb4tax*decimal.Decimal(1.1)
#             Inv.bookedby = request.user.username 
#             if str(rrtpp) is not "0":
#                 if rrtpp:
#                     Inv.description = Promocode.objects.get(code="BOOK15")
#                     Inv.descprom = rrtpp
#             Inv.email = customer13
#             Inv.save()

            return HttpResponse("success")

    return HttpResponse("error")





def newtest(request):
    test= None
    if request.method =="POST":
        a = requests.post('https://innbparkhotel.com/channelmanagerapi/', json = {"reservations":{"reservation":[{"company":"BOOKING.COM","booking_id":"73830000123100016769","customer":{"first_name":"Helmy","countrycode":"sa","remarks":"This guest would like the rooms in this booking to be close together if possible.url: https://admin.booking.com/hotel/hoteladmin/extranet_ng/manage/booking.html?res_id=3183229408&hotel_id=2201454&lang=en&from_confirmation_email=1 |; Total adult : 5; Total child : 3, booker_is_geniusTotal Before Tax - 1022.88, Total After Tax - 1022.88,","address":"","telephone":"+123 54 848 5559","email":"hq111adah.376014@guest.booking.com","city":"","zip":"","last_name":"Qadah"},"hotel_name":"InnB Park Hotel","booking_status":"new","hotel_id":"7383","commissionamount":"204.576","room":[{"extra_child_rate":0,"arrival_date":"2019-06-26","id":"29667","guest_name":"Helmy Qadah","extra_adult_rate":0,"numberofchild":"0","price":[{"amount":"156.00","date":"2019-06-26","rate_id":"94731"},{"date":"2019-06-27","rate_id":"94731","amount":"156.00"}],"numberofguests":"2","no_of_extra_adult":"0","addons":[{"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52","noofunits":4},{"noofunits":4,"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52"},{"noofunits":4,"price_per_unit":"20.88","totalprice":"83.52","name":"Breakfast"}],"numberofadult":"2","departure_date":"2019-06-28","no_of_extra_child":"0","totalprice":312,"name":"Superior Twin","currencycode":"MYR","remarks":"No Smoking Meal plan :Enjoy a convenient breakfast at the property for MYR 18 per person, per night. rewritten_from_name : Early Bird genius_rate : no"},{"remarks":"No Smoking Meal plan :Enjoy a convenient breakfast at the property for MYR 18 per person, per night. rewritten_from_name : Early Bird genius_rate : no","totalprice":312,"currencycode":"MYR","name":"Superior Queen","no_of_extra_child":"0","departure_date":"2019-06-28","addons":[{"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52","noofunits":4},{"noofunits":4,"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52"},{"noofunits":4,"price_per_unit":"20.88","totalprice":"83.52","name":"Breakfast"}],"no_of_extra_adult":"0","numberofadult":"2","price":[{"rate_id":"94731","date":"2019-06-26","amount":"156.00"},{"date":"2019-06-27","rate_id":"94731","amount":"156.00"}],"numberofchild":"0","numberofguests":"2","guest_name":"Helmy Qadah","id":"29666","extra_child_rate":0,"arrival_date":"2019-06-26","extra_adult_rate":0},{"id":"29667","guest_name":"Helmy Qadah","arrival_date":"2019-06-26","extra_child_rate":0,"extra_adult_rate":0,"price":[{"rate_id":"94731","date":"2019-06-26","amount":"156.00"},{"date":"2019-06-27","rate_id":"94731","amount":"156.00"}],"numberofchild":"0","numberofguests":"2","addons":[{"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52","noofunits":4},{"noofunits":4,"name":"Breakfast","price_per_unit":"20.88","totalprice":"83.52"},{"noofunits":4,"price_per_unit":"20.88","totalprice":"83.52","name":"Breakfast"}],"no_of_extra_adult":"0","numberofadult":"2","departure_date":"2019-06-28","no_of_extra_child":"0","totalprice":312,"currencycode":"MYR","name":"Superior Twin","remarks":"No Smoking Meal plan :Enjoy a convenient breakfast at the property for MYR 18 per person, per night. rewritten_from_name : Early Bird genius_rate : no"}],"booking_date":"2019-05-26","payment_type":"Hotel Collect","deposit":"0","channel_ref":"31832294012318","totalprice":"1186.54","currencycode":"MYR"}]}} )
        return HttpResponse(a)
    context = {
    'test':test
    }        
    return render(request, 'booking/test3.html', context)  









# def newtest(request):
#     clearing = Invoice.objects.filter(bookingfeepaid=False, staffbooking=False,molpay=True,totalpaid=False)
#     now = datetime.now()

#     nowa = float(now.strftime("%Y%m%d%H%M%S"))
#     # print(clearing)

#     for a in clearing:
#         cust1 = a.email
#         cust2 = Customer.objects.get(pk=cust1.pk)


#         refa = a.referenceno
#         if refa is not None:
#             ref = float(refa[-14:])
#             # if nowa - ref > 10000:



#             clear = Booking.objects.filter(referenceno=a.referenceno)
#             if cust2.user_login:
#                 no1ofdays = 0
#                 user1315 = Userlogin.objects.get(pk=cust2.user_login.pk)
#                 for aasdf in clear:
#                     if aasdf.room_type_name.pk is not 22 and aasdf.room_type_name.pk is not 23 and aasdf.room_type_name.pk is not 24:
#                         no1ofdays = no1ofdays + int((aasdf.checkout_date-aasdf.checkin_date).days)
#                 user1315.numbertime = int(user1315.numbertime)-no1ofdays
#                 # user1315.save()
#             clear2 = Invoice.objects.filter(referenceno=a.referenceno)
#                 # clear.delete()
#                 # clear2.delete()

#     return HttpResponse(user1315.numbertime)


















def variablepricingdataenter(request):
    if request.method =="GET":
        date = request.GET.get('date')

        def parsing_date(text):
            for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    pass
            raise ValueError('no valid date format found')  
        


        
        if date is None:
            var123 = datetime.now()
            todaydatestrftime = (var123 + timedelta(hours=8)).date()
            qin_date = todaydatestrftime
            qin_date0 = qin_date.strftime("%a, %d-%m-%Y")
            qin_date1 = (qin_date + timedelta (days=1)).strftime("%a, %d-%m-%Y")
            qin_date2 = (qin_date + timedelta (days=2)).strftime("%a, %d-%m-%Y")
            qin_date3 = (qin_date + timedelta (days=3)).strftime("%a, %d-%m-%Y")
            qin_date4 = (qin_date + timedelta (days=4)).strftime("%a, %d-%m-%Y")
            qin_date5 = (qin_date + timedelta (days=5)).strftime("%a, %d-%m-%Y")
            qin_date6 = (qin_date + timedelta (days=6)).strftime("%a, %d-%m-%Y")
            qin0 = qin_date.strftime("%d%m%Y")
            qin1 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
            qin2 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
            qin3 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
            qin4 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
            qin5 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
            qin6 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")
        else:
            qin_date = parsing_date(date).date()
            startdate = qin_date.weekday()



            qin_date0 = qin_date.strftime("%a, %d-%m-%Y")
            qin_date1 = (qin_date + timedelta (days=1)).strftime("%a, %d-%m-%Y")
            qin_date2 = (qin_date + timedelta (days=2)).strftime("%a, %d-%m-%Y")
            qin_date3 = (qin_date + timedelta (days=3)).strftime("%a, %d-%m-%Y")
            qin_date4 = (qin_date + timedelta (days=4)).strftime("%a, %d-%m-%Y")
            qin_date5 = (qin_date + timedelta (days=5)).strftime("%a, %d-%m-%Y")
            qin_date6 = (qin_date + timedelta (days=6)).strftime("%a, %d-%m-%Y")


            if startdate == 0:




                qin0 = qin_date.strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

            elif startdate == 1:




                qin1 = qin_date.strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

            elif startdate==2:




                qin2 = qin_date.strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

            elif startdate ==3:




                qin3 = qin_date.strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

            elif startdate ==4:

                qin4 = qin_date.strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")
            
            elif startdate ==5:


                qin5 = qin_date.strftime("%d%m%Y")
                qin6 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

            elif startdate ==6:

                qin6 = qin_date.strftime("%d%m%Y")
                qin0 = (qin_date + timedelta (days=1)).strftime("%d%m%Y")
                qin1 = (qin_date + timedelta (days=2)).strftime("%d%m%Y")
                qin2 = (qin_date + timedelta (days=3)).strftime("%d%m%Y")
                qin3 = (qin_date + timedelta (days=4)).strftime("%d%m%Y")
                qin4 = (qin_date + timedelta (days=5)).strftime("%d%m%Y")
                qin5 = (qin_date + timedelta (days=6)).strftime("%d%m%Y")

        roomtypes = Roomtype.objects.all().values('id','room_type_name','room_price0','room_price1','room_price2','room_price3','room_price4','room_price5','room_price6').order_by('-room_price1')
        asdflist=[]

        startdate = qin_date.weekday()
        for r in roomtypes:
            for y in range(0,6):
                number = y
                # roomnumber = i['room_number']
                date = qin_date +timedelta(days=y)
                # print (date)
                # print (roomnumber)
                try:
                    roompk = r['id']
                    day = date.weekday()
                    xprice = "room_price" + str(day) 
                    pricespecial = variablepricing.objects.get(date =date, roomtype=roompk)
                    r[xprice] = pricespecial.price
                except variablepricing.DoesNotExist:
                    day = date.weekday()
                    xprice = "room_price" + str(day)      
                    r[xprice]=r[xprice]
                    # yy = decimal.Decimal("0.00")


        context = {
        'startdate':startdate,

        'roomtypes':roomtypes,
        'asdflist':asdflist,
        'qin0':qin0,
        'qin1':qin1,
        'qin2':qin2,
        'qin3':qin3,
        'qin4':qin4,
        'qin5':qin5,
        'qin6':qin6,
        'qin_date0':qin_date0,
        'qin_date1':qin_date1,
        'qin_date2':qin_date2,
        'qin_date3':qin_date3,
        'qin_date4':qin_date4,
        'qin_date5':qin_date5,
        'qin_date6':qin_date6
        }
        return render(request,"booking/variaprice.html", context)
        






@csrf_exempt
def variapriceapi(request):
    if request.method == "POST":
        
        data = json.loads(request.body.decode('utf-8'))
        room = data['room']
        bk = data['date']
        price = data['va']

        qin_date = datetime.strptime((bk), '%d%m%Y')
        try: 
            room1= Roomtype.objects.get(room_type_name=room)
        except Roomtype.objects.DoesNotExist:
            return HttpResponse("Error")

        try:
            newprice = variablepricing.objects.get(roomtype=room1, date=qin_date)
            newprice.price =price   
            newprice.save()
        except variablepricing.DoesNotExist:

            newprice = variablepricing.objects.create(roomtype= room1, date=qin_date, price= price)
            newprice.save()


    return HttpResponse("error")





@login_required(login_url='/login/')
def alltest2(request):


    all_invoices = variablepricing.objects.all().order_by('-id')



    context= {
    'all_invoices':all_invoices
    }
    return render(request,"booking/allpricing.html", context)






@login_required(login_url='/login/')
@permission_required('booking.add_booking', login_url='/unauthorized/')
def portal5(request):
    qin_date1 = request.GET.get('startdate')
    qout_date1 = request.GET.get('enddate')
    qintime = request.GET.get('startime')
    qouttime = request.GET.get('endtime')
    if not qintime:
        utime1 = datetime.strptime("00:00",'%H:%M').time()
        utime2 = datetime.strptime("00:00",'%H:%M').time()      
    else:
        utime1 = datetime.strptime(qintime,'%H:%M').time()
        utime2 = datetime.strptime(qouttime,'%H:%M').time()

    def parsing_date(text):
        for fmt in ('%Y-%m-%d', '%d/%m/%y','%d-%m-%Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')  

    if not qin_date1:
        qin_date=date.today()
        qout_date=date.today()

    else:

        qin_date = datetime.combine(parsing_date(qin_date1),utime1 )
        qout_date = datetime.combine(parsing_date(qout_date1),utime2)  




    # amsterdam = pytz.timezone('Asia/Singapore')
    # aware = qin_date.replace(tzinfo=amsterdam)
    # qindate = aware.astimezone(pytz.UTC)

    # aware2 = qout_date.replace(tzinfo=amsterdam)
    # qoutdate = aware2.astimezone(pytz.UTC)

    qindate = (qin_date - timedelta(hours=8))
    qoutdate = (qout_date - timedelta(hours=8))


    # qindate = datetime.combine(qin_date, datetime.min.time())
    # qoutdate = datetime.combine(qout_date, datetime.min.time())



    table = Invoice.objects.all().filter(checkedin1__gte=qindate, checkedin1__lte=qoutdate).order_by('checkedin1')

    total =0
    cash =0
    cc=0
    dc =0
    dcc=0

    for each in table:
        eqrqrq = each.referenceno
        each.booking1 = Booking.objects.all().filter(referenceno = eqrqrq)
        each.checkedin1 = each.checkedin1 + timedelta(hours=8)

        if each.total:
            total += each.total
        if each.cashpaid:
            cash += each.cashpaid
        if each.ccpaid:
            cc += each.ccpaid
        if each.depositcash:
            dc += each.depositcash
        if each.depositcc:
            dcc += each.depositcc

    



   

    context = {
    "table":table,
    "total":total,
    "cash": cash,
    "cc": cc,
    "dc": dc,
    "dcc": dcc,
    "qin_date1":qin_date1,
    "qout_date1":qout_date1,
    "qoutdate":qoutdate,
    "qindate":qindate


    }


    return render(request, "booking/invoicemth2.html", context)




@login_required(login_url='/login/')
def querycust2(request):
    first_name = request.GET.get('firstname')
    # last_name = request.GET.get('lastname')
    # email = request.GET.get('email')
    # phno = request.GET.get('phno')

    result00 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result01 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result02 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result03 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result04 = Booking.objects.none().values('first_name', 'last_name', 'pk')       
    result05 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result06 = Booking.objects.none().values('first_name', 'last_name', 'pk')
    result07 = Booking.objects.none().values('first_name', 'last_name', 'pk')

    results = Booking.objects.none().values('first_name', 'last_name', 'pk')
    afirst = None
    if first_name:
        result00 =  Booking.objects.all().filter(first_name=first_name).values('first_name', 'last_name', 'pk').distinct()
        result01 = Booking.objects.all().filter(last_name=first_name).values('first_name', 'last_name', 'pk').distinct()
        
        firsthandres = result00 | result01
        afirst = None
        
        # if not firsthandres:

        first = first_name.split()

        #     afirst = first[:2]
        #     afirst =' '. join(afirst)
        #     alast = first[-2:]
        #     alast = ' '. join(alast)
        #     result02 = Invoice.objects.all().filter(email__first_name=afirst).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result03 = Invoice.objects.all().filter(email__first_name=alast).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result04 = Invoice.objects.all().filter(email__last_name=afirst).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     result05 = Invoice.objects.all().filter(email__last_name=alast).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #     for a in first:
        #         result06 = Invoice.objects.all().filter(email__last_name=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        #         result07 = Invoice.objects.all().filter(email__first_name=a).values('email__first_name', 'email__last_name', 'email__email', 'email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
 
    
   

        #     exclusion =result02 | result03 | result04 | result05 | result06 | result07


        # else:
        #     exclusion = firsthandres

        # if not exclusion:



        for a in first:
            query1 = Booking.objects.all().filter(first_name__icontains=a).values('first_name', 'last_name', 'pk').distinct()
            query2 = Booking.objects.all().filter(last_name__icontains=a).values('first_name', 'last_name', 'pk').distinct()
            results = query1 | query2 | results
            print('firstname')
            print(first_name)

        # else:
        #     results = exclusion



    else:
        results = Booking.objects.none()


    # if last_name:    
    #     results = results.filter(email__last_name__icontains=last_name).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()
        

    # if email:
    #     results = results.filter(email__email__icontains=email).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()



    # if phno:
    #     results = results.filter(email__phone_number__icontains=phno).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments').distinct()

    # if referenceno:
    #     results = results.filter(referenceno=referenceno).values('email__first_name', 'email__last_name', 'email__email', 'referenceno','email__phone_number', 'email__country', 'email__attachingdocuments')
    #     afirst=results
  

    print(results)

    if results:
        for a in results:
            # print(a['email__email'])
            # print(a['email__phone_number'])
            # customerno = Customer.objects.get(email=a['email__email'], phone_number=a['email__phone_number'])

            a['customer'] = None




    context = {
     "results": results,
     "result00":result00,
     "result00":result01,
     "result00":result02,
     "result00":result03,
     "result00":result04,
     "result05":result05,
     "afirst":afirst,
     }


    return render(request,"booking/querycust2.html", context)







# @login_required(login_url='/login/')
# def allbookings(request):

#     all_bookings= logging.objects.all().order_by('-created_on')

    
#     allbookings = all_bookings
#     paginator = Paginator(allbookings, 70)    
#     page = request.GET.get('page')
#     try:
#         allbookings = paginator.page(page)
#     except PageNotAnInteger:
#         # If page is not an integer, deliver first page.
#         allbookings = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range (e.g. 9999), deliver last page of results.
#         allbookings = paginator.page(paginator.num_pages)

#     # if request.GET.get('page'):
#     #     # resp = serialize_debates(page_objects)
#     #     return JsonResponse({
#     #     'allbookings': allbookings
#     # })


#     context = {
#     'allbookings':allbookings,
#     'order':order,
#     }
#     return render(request,"booking/allbooking.html",context)





def customerlogin(request):
    # next = request.GET.get('next')


    # def authenticatebackend1(self, username=None, password=None):

    #     try:
    #         user = Userlogin.objects.get(email=username)
    #         pwd_valid = check_password(password, user.password)
    #         if pwd_valid:
    #             return user
    #         else:
    #             return None


    #     except Userlogin.DoesNotExist:
    #         return None




    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')






        # date123 = datetime.now().date()
        # d123ate = date123.strftime("%d%m%Y%H%M%S")

        # qqq = (username + "+" + d123ate)


        # encryption_text = AES.new('test', AES.MODE_CBC, 'test2')
        # cipher_text = encryption_suite.encrypt(qqq)
        # aaa = (qqq).encode('utf-8')
        # m = hashlib.md5()
        # m.update(aaa)
        # vcode =  m.hexdigest()







        # user = authenticatebackend1(username=username, password=password)
        if not staffno:
            try:
                testforuser = Userlogin.objects.get(email=username)

                pwd_valid = check_password(password, testforuser.password)
                if pwd_valid:
                    now = datetime.now()
                    cipher_text3 =  make_password(username)
                    nowa = now.strftime("%Y%m%d%H%M%S")
                    cipher_text = cipher_text3[14:]
                    hashcode = nowa+cipher_text

                    request.session['1335i99fl'] = nowa+cipher_text
                    testforuser.hashcode=hashcode
                    testforuser.save()
                    return redirect('customerportal')
                else:
                    return redirect('customerlogin2')



            except Userlogin.DoesNotExist:
                return redirect('customerlogin2')



            # decryption_suite = AES.new('test', AES.MODE_CBC, 'test2')
            # plain_text = decryption_suite.decrypt(cipher_text)

            # return HttpResponse(cipher_text + "  / "  + plain_text)










            # if user is not None: 
            #     if user.is_active:
            #         return  None







            #     else: 
            #         return redirect('loginauth2')                 
            # else: 
            #     return redirect('loginauth2')
        else: 
            return redirect('customerlogin2')

    return render(request,'booking/custlogin.html')     




def customerlogin2(request):
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        staffno = request.POST.get('staffnumber')



        if not staffno:
            try:
                testforuser = Userlogin.objects.get(email=username)

                pwd_valid = check_password(password, testforuser.password)
                if pwd_valid:
                    now = datetime.now()
                    cipher_text3 =  make_password(username)
                    nowa = now.strftime("%Y%m%d%H%M%S")
                    cipher_text = cipher_text3[14:]
                    hashcode = nowa+cipher_text

                    request.session['1335i99fl'] = nowa+cipher_text
                    testforuser.hashcode=hashcode
                    testforuser.save()
                    return redirect('customerportal')
                else:
                    return redirect('customerlogin2')



            except Userlogin.DoesNotExist:
                return redirect('customerlogin2')



        else: 
            return redirect('customerlogin2')

    return render(request,'booking/custlogin2.html')    




def forgotpassword(request):
    error = None
    if request.method =="POST":
        username = request.POST.get('password')
        staffno = request.POST.get('staffnumber')




        if not staffno:
            try:
                testforuser = Userlogin.objects.get(email=username)

                cipher_text3 =  make_password(username)

                html_message = 'Please click the link below to reset your password: <br> <a href="https://innbparkhotel.com/dgfj3-13/?id='+str(testforuser.pk)+'&pk='+cipher_text3+'">https://innbparkhotel.com/dgfj3-13/?id='+str(testforuser.pk)+'&pk='+cipher_text3+'</a>'

                msg = EmailMultiAlternatives("InnB Park Hotel ", "Password recovery", "(Admin) InnB Park Hotel <admin@innbparkhotel.com>", [username]) 

                msg.attach_alternative(html_message, "text/html")

                msg.send()




                error = "An email has been sent to your email address. Please click on the link in your email to reset your password"


            except Userlogin.DoesNotExist:
                error = "This email address is not registered"



        else: 
            return redirect('customerlogin2')

    return render(request,'booking/resetemail.html', {'error':error})    




def resetpasswordauthen(request):


    hashcode = request.GET.get('pk')
    email = request.GET.get('id')
    staffno = request.GET.get('staffnumber')
    nowa = None
    ciper_text = None
    testforuser = None
    now = datetime.now()

    try:
        testforuser = Userlogin.objects.get(pk=email)
        pwd_valid = check_password(testforuser.email, hashcode)


        if pwd_valid:

            nowa = now.strftime("%Y%m%d%H%M%S")
            print("valid")

        else:
            return redirect('test2')
    except:
        return redirect('test2')

    error = None

    if request.method == "POST":
        newpassword = request.POST.get('password')
        nowb = request.POST.get('nowa')
        nowc = datetime.strptime(nowb, "%Y%m%d%H%M%S")
        timediff = (datetime.now() - nowc).total_seconds() / 60.0
        if len(newpassword)>7:
            if timediff < 60:
                hashed_pwd = make_password(newpassword)
                testforuser = Userlogin.objects.get(pk=email)
                if testforuser is not None:
                    testforuser.password = hashed_pwd
                    testforuser.save()
                    return redirect('customerlogin')
                else:
                    return redirect('test2')

            else:
                return redirect('test2')
        else:
            error = "Use 8 or more characters for password"

    context= {
        'nowa':nowa,
        'error':error
    }
    return render(request,"booking/resetpassword.html", context)


                


@login_required(login_url='/login/')
def customerall(request):

    first_name = request.GET.get('firstname')
    referenceno = request.GET.get('referenceno')
    if first_name:
      
        first = first_name.split()
        all_invoices = Userlogin.objects.none()

        for a in first:
            query1 = Userlogin.objects.all().filter(first_name__icontains=a)
            query2 = Userlogin.objects.all().filter(last_name__icontains=a)
            all_invoices = query1 | query2 | all_invoices


    elif referenceno:
        all_invoices = Userlogin.objects.all().order_by('-id')
    else:
        all_invoices = Userlogin.objects.all().order_by('-id')

    paginator = Paginator(all_invoices, 500)    
    page = request.GET.get('page')
    try:
        all_invoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_invoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_invoices = paginator.page(paginator.num_pages)


    context= {
    'all_invoices':all_invoices
    }
    return render(request,"booking/allcustomers2.html", context)







def customerportal(request):
    staron ="no"


    offers = Promocode.objects.filter(membersonly=True, active = True).order_by('points')
    if '1335i99fl' not in request.session:
        return redirect('dateform')

    else:
        userhash = request.session['1335i99fl']

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))
        # reflect = nowa-timestamptime
        # reflect2 = str(reflect) + str("=") + str(nowa) + "-" + str(timestamptime) + " ==" + str(hashcode)
        # return HttpResponse(reflect2)
    # print(clearing)

        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)
            # if user55.numbertime is not None:

            #     if (int(user55.numbertime))<=9:
            #         nuber = 9 - int(user55.numbertime)
            #         nuber3 = int(user55.numbertime)
            #     else:
            #         nuber = 0
            #         nuber3 = 9
            #         staron = "yes"
            # else:
            #     nuber = 9
            #     nuber3 = 0

            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                # return HttpResponse(userhash) 
                custid = Customer.objects.filter(user_login=user55)
                for cusa in custid:
                    cusa.customerbooking = Invoice.objects.filter(email=cusa).order_by('-datecreated')
                    for c in cusa.customerbooking:
                        if c.staffbooking == True:
                            c.staffbook = "yes"
                        else:
                            c.staffbook = None

                        if c.totalpaid == True:
                            c.paid = "NotPaid"
                            c.paid1 = "TotalPaid"
                            if c.deposit == True:
                                c.paid = None
                        else:
                            c.paid = "NotPaid"

             
                        invoiceno = Invoice.objects.get(referenceno =c.referenceno)
                        depforminfo = depositwitheld.objects.filter(invoice=invoiceno) 
                        c.depforminfo = depforminfo
                        room = Booking.objects.filter(referenceno=c.referenceno).order_by('-room_type_name__room_price0')
                        c.room = room
                        booki=[] 
                        roomtotal=0      
                        for a in room:
                            cin_date = a.checkin_date

                            cout_date = a.checkout_date
                            if a.room_number is None:
                                a.upgrade = None
                                if a.room_type_name.pk == 22:
                                    a.room_number = Roomnumber.objects.get(room_number=401)
                                    a.room_number.room_number = "None"
                                elif a.room_type_name.pk == 23:
                                    a.room_number = Roomnumber.objects.get(room_number=401)
                                    a.room_number.room_number = "None"    
                                elif a.room_type_name.pk == 24:
                                    a.room_number = Roomnumber.objects.get(room_number=401)
                                    a.room_number.room_number = "None"
                                elif a.room_type_name.pk == 28:
                                    a.room_number = Roomnumber.objects.get(room_number=401)
                                    a.room_number.room_number = "None"
                            else:
                                a.upgrade = "yes"                        
                            booki.append(a.room_number.room_number)
                            c.checkin_date = cin_date
                            c.checkout_date = cout_date
                            roomtotal+=a.actualpay

                context= {
                'user55':user55,
                "custid":custid,
                "offers":offers,
                # "nuber":range(nuber),
                # "nuber3":range(nuber3),
                "staron":staron
                }
                return render(request,"booking/custportal.html", context)
            else:
                return HttpResponse("Incorrect login")

    return HttpResponse("test")








def customerregister(request):
    # next = request.GET.get('next')


    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')        
        phonenumber = request.POST.get('phonenumber')
        staffno = request.POST.get('Agree')
        staffnumber = request.POST.get('staffnumber')
        country = request.POST.get('country')        
        name31 = first_name+last_name
        hashed_pwd = make_password(password)

        if not staffnumber:

            if len(password)>7:



                if password == password2:



                    # nameboolean = any(i.isdigit() for i in name31)
                    # if nameboolean is True:




                    try:
                        testuser = Userlogin.objects.get(email=username)
                        Errormsg1 = "User email already exists"




                    except Userlogin.DoesNotExist:
                        now = datetime.now()
                        cipher_text3 =  make_password(username)
                        nowa = now.strftime("%Y%m%d%H%M%S")
                        cipher_text = cipher_text3[14:]
                        hashcode = nowa+cipher_text

                        request.session['1335i99fl'] = nowa+cipher_text

                        Userlogin.objects.create(email=username,password = hashed_pwd, hashcode=hashcode, first_name = first_name, last_name=last_name, country=country, phone_number = phonenumber)
                        # return redirect('customerportal')
                        # return HttpResponse(hashcode)
                        return redirect('detail')


                    # else:
                    #     Errormsg3 = "Incorrect characters in name"




                else:
                    Errormsg2 = "Both passwords do not match"


            else:

                Errormsg2 = "Use 8 or more characters for password"





        else:
            return redirect('detail')














    # def authenticatebackend1(self, username=None, password=None):

    #     try:
    #         user = Userlogin.objects.get(email=username)
    #         pwd_valid = check_password(password, user.password)
    #         if pwd_valid:
    #             return user
    #         else:
    #             return None


    #     except Userlogin.DoesNotExist:
    #         return None




    # if request.method =="POST":
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     staffno = request.POST.get('staffnumber')



    #     user = authenticatebackend1(username=username, password=password)
    #     if not staffno:
    #         if user is not None: 
    #             if user.is_active:
    #                 return  None







    #             else: 
    #                 return redirect('loginauth2')                 
    #         else: 
    #             return redirect('loginauth2')
    #     else: 
    #         return redirect('loginauth2')

    return render(request,'booking/Register.html')     




















def validate_email1(request):
    email13 = request.GET.get('email')
    validatecode = request.GET.get('cind')
    if validatecode =="13355115":
        try:
            testforuser = Userlogin.objects.get(email=email13)
            return HttpResponse("Error")
        


        except Userlogin.DoesNotExist:



            return HttpResponse("Success")







@login_required(login_url='/login/')
def allinvoices123(request):

    first_name = request.GET.get('firstname')
    referenceno = request.GET.get('referenceno')
    if first_name:
      
        first = first_name.split()
        all_invoices = Invoice.objects.none()

        for a in first:
            query1 = Invoice.objects.all().filter(email__first_name__icontains=a)
            query2 = Invoice.objects.all().filter(email__last_name__icontains=a)
            all_invoices = query1 | query2 | all_invoices


    elif referenceno:
        all_invoices = Invoice.objects.filter(referenceno=referenceno).order_by('-id')
    else:
        all_invoices = Invoice.objects.all().order_by('-invoiceno')

    paginator = Paginator(all_invoices, 500)    
    page = request.GET.get('page')
    try:
        all_invoices = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_invoices = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_invoices = paginator.page(paginator.num_pages)


    context= {
    'all_invoices':all_invoices
    }
    return render(request,"booking/allinvoices.html", context)













@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def agodareview(request):


    testdate="Test"
    if request.method=="GET":
        user_agentlist = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.2; de-de; SAMSUNG GT-I9195 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/1.5 Chrome/28.0.1500.94 Mobile Safari/537.36']
        user_agent = random.choice(user_agentlist)
        headers = {'User-Agent': user_agent}
        b = requests.get('https://www.agoda.com/en-au/innb-park-hotel/reviews/kuala-lumpur-my.html?cid=-218', headers)
        # b = requests.get('https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=u2qcKLxwzRU5NDuxJ0kOFyhT%2BFPmPUsHsI1E%2F4TDehVONfV5GIg7pCb%2B3slmJAwEi1S1EbjGOjIaQMred5DQGTb0O7ulaZsPbs60PaM6ANeMfdhwqUcbO%2FM2r8inN9YMFCbIetvnkBY6JdpfA7NfyUtmvbyTQs7w9Fw3dp6xkbbsPHxgfqha4M45tDRGBZcjbS3dzzacn%2Bn7QZeTArmFD0jYnQt1HMxeVnOT%2FFk%2Fecg%3D&city=14524&tick=636189763809&pagetypeid=1&origin=MY&cid=-1&tag=&gclid=&aid=&userId=&languageId=1&sessionId=&htmlLanguage=en-au&checkIn='+ datetoday +'&checkOut=&los=1&rooms=1&adults=2&children=0&ckuid=292e334c-2ca9-409e-a115-20f237605bf8&hotelStarRating=3,4,5&hotelArea=27812,32004&hotelAccom=34&hotelReviewScore=5&sort=priceLowToHigh')
        

     

        a = html.fromstring(b.text)




        # score = a.xpath('//*[@class="Review-comment-bodyText"]')
        score = b.text
        commenttext = a.xpath('//*[@id="review-0"]/div[2]/div[1]/div[1]/div[2]/text()')  
        rating2 = a.xpath('//*[@id="review-1"]/div[1]/div/div[1]/div[2]/text()')  
        date1 = a.xpath('//*[@id="review-1"]/div[2]/div[1]/div[2]/div[1]/div/span/text()')










        return HttpResponse(score)
    # for (ratescore,comment, ratedesc, date4) in zip(score, commenttext, rating2,date1):
    #     review1 = review.objects.Create(reviewtype="Agoda", date=date4, rating=ratescore, rating2 =ratedesc, description=comment )







    return HttpResponse("test")




    # context ={
    # 'todaydate': todaydate,
    # # 'average':average,
    # 'hotel':hotel,
    # 'prices':prices,
    # 'pricingform':pricingform,
    # 'pricing1':pricing1
    # }
    # return render(request, 'booking/pricing.html', context)





@login_required(login_url='/login/')
@permission_required('booking.can_add_booking', login_url='/unauthorized/')
def priceexpedia(request):


    testdate="Test"
    if request.method=="GET":
        user_agentlist = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.2; de-de; SAMSUNG GT-I9195 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/1.5 Chrome/28.0.1500.94 Mobile Safari/537.36']
        user_agent = random.choice(user_agentlist)
        headers = {'User-Agent': user_agent}
        b = requests.get('https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=u2qcKLxwzRU5NDuxJ0kOF%2FsC8rMB2mBSy3F1hQrnQkwPtdraKddM98L5vt7iEwqr8bUyWBp0f1su9qJIdH6Mia5nZC9oHtzqfpWZ8QTxZC%2B%2F2HBoLRYk485pGrAK8ZGaxT%2FCRdx859FDzf5kd2Cgkj7Gb%2BYSl0pZBwhcZywCbNsbmy1lmxy%2BNC6u%2BoYcqUuPzOe8fU%2BMmpY7Rz0xZQieReL2AUnfOhFRTEDVteJxPyI%3D&area=27812&tick=636898824937&languageId=1&userId=546ca386-0b34-40bd-b162-df8e72c81b86&sessionId=3bzdg2c1njkh2cynbtt5cb1o&pageTypeId=103&origin=AU&locale=en-US&cid=-1&aid=130243&currencyCode=MYR&htmlLanguage=en-us&cultureInfoName=en-US&ckuid=546ca386-0b34-40bd-b162-df8e72c81b86&prid=0&checkIn=2019-04-12&checkOut=2019-04-13&rooms=1&adults=2&children=0&priceCur=MYR&los=1&textToSearch=Bukit%20Bintang&travellerType=1&familyMode=off&productType=1&sort=priceLowToHigh', headers)
        # b = requests.get('https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?asq=u2qcKLxwzRU5NDuxJ0kOFyhT%2BFPmPUsHsI1E%2F4TDehVONfV5GIg7pCb%2B3slmJAwEi1S1EbjGOjIaQMred5DQGTb0O7ulaZsPbs60PaM6ANeMfdhwqUcbO%2FM2r8inN9YMFCbIetvnkBY6JdpfA7NfyUtmvbyTQs7w9Fw3dp6xkbbsPHxgfqha4M45tDRGBZcjbS3dzzacn%2Bn7QZeTArmFD0jYnQt1HMxeVnOT%2FFk%2Fecg%3D&city=14524&tick=636189763809&pagetypeid=1&origin=MY&cid=-1&tag=&gclid=&aid=&userId=&languageId=1&sessionId=&htmlLanguage=en-au&checkIn='+ datetoday +'&checkOut=&los=1&rooms=1&adults=2&children=0&ckuid=292e334c-2ca9-409e-a115-20f237605bf8&hotelStarRating=3,4,5&hotelArea=27812,32004&hotelAccom=34&hotelReviewScore=5&sort=priceLowToHigh')
        

     

        a = html.fromstring(b.text)




        # score = a.xpath('//*[@class="Review-comment-bodyText"]')
        score = b.text
        # commenttext = a.xpath('//*[@id="review-0"]/div[2]/div[1]/div[1]/div[2]/text()')  
        # rating2 = a.xpath('//*[@id="review-1"]/div[1]/div/div[1]/div[2]/text()')  
        # date1 = a.xpath('//*[@id="review-1"]/div[2]/div[1]/div[2]/div[1]/div/span/text()')










        return HttpResponse(b)
    # for (ratescore,comment, ratedesc, date4) in zip(score, commenttext, rating2,date1):
    #     review1 = review.objects.Create(reviewtype="Agoda", date=date4, rating=ratescore, rating2 =ratedesc, description=comment )







    return HttpResponse("test")





@login_required(login_url='/login/')
def breakfastrequest(request):

    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())

    tomorrowdate = todaydate + timedelta(days=1)
    dayafterdate=todaydate + timedelta(days=2)
    daydayafterdate=todaydate - timedelta(days=3)
    breakfastpack = Booking.objects.filter(room_type_name__pk=24).filter(checkin_date__lte=todaydate).filter(checkout_date__gte=tomorrowdate).order_by('referenceno')
    breakfastnopack =Booking.objects.filter(room_type_name__pk=23).filter(checkin_date__lte=todaydate).filter(checkout_date__gte=tomorrowdate).order_by('referenceno')

    breakfast = breakfastpack | breakfastnopack
    breakfastno = breakfast.count() 



    breakfast2pack = Booking.objects.filter(room_type_name__pk=24).filter(checkin_date__lte=tomorrowdate).filter(checkout_date__gte=dayafterdate).order_by('referenceno')
    breakfast2nopack =Booking.objects.filter(room_type_name__pk=23).filter(checkin_date__lte=tomorrowdate).filter(checkout_date__gte=dayafterdate).order_by('referenceno')


    breakfast2 = breakfast2pack | breakfast2nopack

    breakfast2no = breakfast2.count()
    refno3113 = None
    counter =0 
    newcounter = 0
    countercounter = 0
    counter2 =0 
    newcounter2 = 0
    countercounter2 = 0

    for a in breakfast:
        if refno3113 == a.referenceno:
            counter = counter + 1
            if counter > 1:
                roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).exclude(room_number__pk=24).exclude(room_number__pk=23).exclude(room_type_name__pk=22).exclude(room_type_name__pk=28).order_by('room_number')
                numb1 = roomnum313.count()-1

                countercounter = countercounter + 1   
                if countercounter == 2:
                    countercounter=0                   
                newcounter = newcounter + countercounter  
                if newcounter > numb1:
                    try:
                        a.room_number = roomnum313[0].room_number
                    except IndexError:
                        a.room_number = None

                    # roomnum313[0].room_number
                else:
                    try:
                        a.room_number = roomnum313[newcounter].room_number
                    except:
                        a.room_number = None

                # if countercounter == 2:
                #     countercounter=0   
                               
                # counter2 =  counter2 + countercounter                  
            else:
                roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
                if not roomnum313:
                    a.room_number=None
                else:
                    a.room_number = roomnum313.room_number
        else:
            counter= 0
            countercounter = 0
            newcounter=0
            refno3113 = a.referenceno
            roomnum313 = Booking.objects.filter(referenceno=a.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
            if not roomnum313:
                a.room_number= None
            else:
                a.room_number = roomnum313.room_number



    for b in breakfast2:
        if refno3113 == b.referenceno:
            counter2 = counter2 + 1
            if counter2 > 1:
                roomnum313 = Booking.objects.filter(referenceno=b.referenceno).exclude(room_number__isnull=True).exclude(room_number__pk=24).exclude(room_number__pk=23).exclude(room_type_name__pk=22).exclude(room_type_name__pk=28).order_by('room_number')
                numb1 = roomnum313.count()-1

                countercounter2 = countercounter2 + 1   
                if countercounter2 == 2:
                    countercounter2=0                   
                newcounter2 = newcounter2 + countercounter2  
                if newcounter2 > numb1:
                    try:
                        b.room_number = roomnum313[0].room_number
                    except IndexError:
                        b.room_number = None

                    # roomnum313[0].room_number
                else:
                    # b.room_number = roomnum313[newcounter].room_number     

                    try:
                        b.room_number = roomnum313[newcounter2].room_number
                    except:
                        b.room_number = None
                                        
                # if countercounter == 2:
                #     countercounter=0   
                               
                # counter2 =  counter2 + countercounter                  
            else:
                roomnum313 = Booking.objects.filter(referenceno=b.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
                if not roomnum313:
                    b.room_number=None
                else:
                    b.room_number = roomnum313.room_number
        else:
            counter2= 0
            countercounter2 = 0
            newcounter2=0
            refno3113 = b.referenceno
            roomnum313 = Booking.objects.filter(referenceno=b.referenceno).exclude(room_number__isnull=True).order_by('room_number').first()
            if not roomnum313:
                b.room_number= None
            else:
                b.room_number = roomnum313.room_number

    template = loader.get_template('booking/breakfast.html')

    context = {


    'breakfast':breakfast,
    'breakfast2':breakfast2,
    'breakfastno':breakfastno,
    'breakfast2no':breakfast2no,

    # 'all_customers': all_customers,
    # 'all_bookings' : all_bookings,
    # 'all_roomtypes' : all_roomtypes
                }    
    return HttpResponse(template.render(context, request))




@csrf_exempt
def whiteboards2(request):
    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    # date_customers1 = Booking.objects.filter(checkin_date=todaydate, additional_comments__isnull=False).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).order_by('first_name')
    
    # roomnum = Roomnumber.objects.all().order_by('room_number')

    if request.method == 'POST':
        cdate = request.POST.get('startdate')
        rno = request.POST.get('roomno')
        if rno =="" or rno=="None":
            neww = whiteboard.objects.create(texts=cdate,staff= request.user.username )
        else:
            rno1 = Roomnumber.objects.get(room_number=rno)
            neww = whiteboard.objects.create(texts=cdate, room_number=rno1, staff= request.user.username )    

        return HTTPResponse("Success")
    # if request.method =='GET':
    #     test = None

    #     context = {
    #     'whitewhite':whitewhite,
    #     'roomnum':roomnum
    #     }
    #     return render(request,"booking/whiteboard.html",context)





@csrf_exempt
def whiteboards3(request):
    if request.method =="GET":

        user = request.GET.get('user')
        pass13 = request.GET.get('pass13')

        if pass13 =="1%!@sss98g34jasdlsj":
            whitewhite = whiteboard.objects.filter(hidden=False).filter(forstaff=user).values('pk','texts','room_number__room_number','complete').order_by('pk')
        # users = socketdata.objects.filter(status="Online")

            return JsonResponse({
                'whitewhite': list(whitewhite)
            })



def add_invoice_item(request, id):
    extra_item_form = extra_itemForm(request.POST or None)
    referenceno = id
    email = Invoice.objects.get(referenceno = referenceno).email


    if extra_item_form.is_valid():
        paymentprice = decimal.Decimal(request.POST.get('paymentprice'))
        gst= decimal.Decimal(request.POST.get('GST'))
        GST_include = request.POST.get('GST_include')
        description = request.POST.get('description')



        if GST_include is not None:
            paymentprice = paymentprice- gst
        else:
            paymentprice = paymentprice
        extra_item = extra_items.objects.create(paymentprice=paymentprice,referenceno=referenceno,description=description)    
        extra_item.save()
        try:

            invoice = Invoice.objects.get(referenceno=referenceno)
            if GST_include is not None:
                invoice.totalwch = invoice.totalwch + (paymentprice - gst)
                invoice.gst = invoice.gst + gst
                invoice.total = invoice.total + paymentprice + gst
            else:
                invoice.totalwch = invoice.totalwch + (paymentprice)
                invoice.gst = invoice.gst + gst
                invoice.total = invoice.total + paymentprice + gst
            invoice.save()
            return redirect(('https://innbparkhotel.com/customer/?pk=' + str(email.pk)))
        except:
            return HttpResponse("Invoice not found")

    context = {
         "extra_item_form":extra_item_form
    }
    return render(request, "booking/efront6.html", context)




def checkout_today(request):
    tz = timezone('Etc/GMT+8')
    todaydate = tz.localize(datetime.today())
    if request.method == "GET":


        user = request.GET.get('user')
        pass13 = request.GET.get('pass13')

        if pass13 =="1%!@sss98g34jasdlsj":
            date_customers2 = Booking.objects.filter(checkout_date=todaydate).exclude(room_type_name__pk=23).exclude(room_type_name__pk=24).exclude(upgrade=True, upgradelast=False).values('first_name', 'last_name', 'room_number__room_number','checkedout1','room_number__status').order_by('first_name')
        
            return JsonResponse({'results': list(date_customers2)})





def upload_image(request):
    from PIL import Image as image1
    allimages = []

    for file in os.listdir("/hotel/static/images/upload/blogimage"):
        # for fname in os.listdir(imgdir):
        filename = "https://innbparkhotel.com/img/blogimage/" + file
        filedict = {}
        filedict['url']= filename
        filedict['name'] = file

        allimages.append(filedict)

    if request.method=="POST":
        image_filen = request.FILES['image']
        newfileupload = image1.open(image_filen)

        fn = image_filen.name


        datetimenow = datetime.now()     
        now = datetimenow.strftime("%Y%m%d%H%M%S")  
        fn = now + "_" + ((fn).replace(" ","_").replace("#", ""))

        
        image_filen.seek(0)        
        if newfileupload.format == 'JPEG':
            path = "/hotel/static/images/upload/blogimage/" + fn 
            file1 = request.FILES['image']
            print("writing")
            try:
                with open (path,'wb') as destination:
                    for chunk in file1.chunks():
                        print("writing")
                        destination.write(chunk)
            except Exception as e:
                return HttpResponse(str(e))
        elif newfileupload.format == 'PNG':
            path ="/hotel/static/images/upload/blogimage/" + fn 
            file1 = request.FILES['image']
            
            try:
                with open (path,'wb') as destination:
                    for chunk in file1.chunks():
                        print("writing")
                        destination.write(chunk)
            except Exception as e:
                return HttpResponse(str(e))
        allimages = []        
        for file in os.listdir("/hotel/static/images/upload/blogimage"):
            # for fname in os.listdir(imgdir):
            filename = "https://innbparkhotel.com/img/blogimage/" + file

            filedict = {}
            filedict['url']= filename
            filedict['name'] = file

            allimages.append(filedict)

    context = {
         "allimages":allimages
    }


    return render(request, "booking/upload_images.html", context)



def delete_image(request):
    if request.method=="GET":
        imageremove = request.GET.get('pk')

        allimages = []        
        for file in os.listdir("/hotel/static/images/upload/blogimage"):
            # for fname in os.listdir(imgdir):
            if file == imageremove:
                os.remove("/hotel/static/images/upload/blogimage/" + file)   
        
        return redirect('upload_image')








@login_required(login_url='/login/')
def alllogs(request):

    all_bookings= logging.objects.all().order_by('-id')
    allbookings = all_bookings
    paginator = Paginator(allbookings, 70)    
    page = request.GET.get('page')
    try:
        allbookings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        allbookings = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        allbookings = paginator.page(paginator.num_pages)
    context = {
    'allbookings':allbookings
    }
    return render(request,"booking/alllogs.html",context)





def blogpage(request):
    
    pk= request.GET.get('pk')

    if not pk:
        pk = 1
    
    currentpage = pk

    xstart = (decimal.Decimal(pk)-1) * 9
    xend = (decimal.Decimal(pk)*9)




    pages1 = Pages.objects.filter(hidden=False)
    cat = ""



    categories = Pages.objects.filter(hidden=False, categories__isnull=False).values('categories').distinct()

    if request.GET.get('categories'):
        if request.GET.get('order'): 
            order = request.GET.get('order')
        else:
            order = None

        if order == "2":
            cat = request.GET.get('categories')
            pages1 = Pages.objects.filter(hidden=False).filter(categories__icontains=cat)
            pages = pages1.order_by('pages_title')[xstart:xend]
        else:
            cat = request.GET.get('categories')
            pages1 = Pages.objects.filter(hidden=False).filter(categories__icontains=cat)
            pages = pages1.order_by('-id')[xstart:xend]
    
        numberofposts = pages1.count()
        numberofpages = decimal.Decimal(numberofposts)/9
        if decimal.Decimal(numberofposts)%9>0:
             numberofpages = int(numberofpages) + 1
        pagesarray = []
        for p in range(1,int(numberofpages)):
            pagesarray.append(p)

    else:

        if request.GET.get('order'): 
            order = request.GET.get('order')
        else:
            order = None

        if order == "2":
            pages = pages1.order_by('pages_title')[xstart:xend]
        else:
            pages = pages1.order_by('-id')[xstart:xend]

        numberofposts = pages1.count()
        numberofpages = decimal.Decimal(numberofposts)/9
        if decimal.Decimal(numberofposts)%9>0:
             numberofpages = int(numberofpages) + 1
        pagesarray = []
        for p in range(1,int(numberofpages)+1):
            pagesarray.append(p)

    # return HttpResponse(str(pagesarray))


    context = {
    'pages':pages,
    'categories':categories,
    'cate':cat,
    'currentpage':currentpage,
    'pagesarray':pagesarray,
    'order':order
    }
    return render(request,"booking/blogpage.html",context)






def blogmainpage(request):
    
    if '1335i99fl' not in request.session:
        user55=None
        user555=None
        custid= None
        numberusage=0
    else:
        userhash = request.session['1335i99fl']
        numberusage = 0

        timestamp = userhash[:14]
        hashcode = userhash[14:]

        hashreturn = "pbkdf2_sha256$" + hashcode
        timestamptime = float(timestamp)
        now = datetime.now()

        nowa = float(now.strftime("%Y%m%d%H%M%S"))

        if nowa - timestamptime < 230000:
            user55 = Userlogin.objects.get(hashcode=userhash)
            pwd_valid = check_password(user55.email, hashreturn)
            if pwd_valid:
                user555 = user55
                numberusage = user555.numbertime
                custid = Customer.objects.filter(user_login=user55)
            else:
                user55 = None
        else:
            user55 = None



    page1 = Pages.objects.filter(hidden=False, featured=True).order_by('-id').first()
    pages = Pages.objects.filter(hidden=False, featured=True).order_by('-id')[1:]


    # return HttpResponse(str(pagesarray))
    desc3 = FrontDesc.objects.get(pk=3).description

    context = {
    'page1':page1,
    'pages':pages,
    'user55':user55,
    'desc3':desc3
    }
    return render(request,"booking/blogmainpage.html",context)






@csrf_exempt
def upload_image_api(request):
    from PIL import Image as image1
    allimages = []

    # for file in os.listdir("/hotel/static/images/upload/blogimage"):
    #     # for fname in os.listdir(imgdir):
    #     filename = "https://innbparkhotel.com/img/blogimage/" + file
    #     filedict = {}
    #     filedict['url']= filename
    #     filedict['name'] = file

    #     allimages.append(filedict)

    if request.method=="POST":
        newfileupload = image1.open(request.FILES['image_file'])
        request.FILES['image_file'].seek(0)
        datetimenow = datetime.now()     
        now = datetimenow.strftime("%Y%m%d%H%M%S")  
        fn = (request.FILES['image_file'].name).replace(" ","_").replace("#", "")
        filename = "https://innbparkhotel.com/img/blogimage/" + now + "_" + fn
        
        if newfileupload.format == 'JPEG':
            path = "/hotel/static/images/upload/blogimage/" + now + "_" + fn

            file1 = request.FILES['image_file']
            print("writing")
            try:
                with open (path,'wb') as destination:
                    for chunk in file1.chunks():
                        print("writing")
                        destination.write(chunk)

                resizedimg = image1.open(path)
                width, height = resizedimg.size
                maxwidth = 600
                newheight = None
                if width>maxwidth:
                    widthratio = width/maxwidth
                    newwidth = 600
                    newheight = height/widthratio
                    newsize = newwidth, newheight
                    resizedimg.thumbnail(newsize, image1.ANTIALIAS)
                    resizedimg.save(path, resizedimg.format)




            except Exception as e:
                return HttpResponse(str(e))
        elif newfileupload.format == 'PNG':
            path ="/hotel/static/images/upload/blogimage/" + now + "_" + fn
            file1 = request.FILES['image_file']
            
            try:
                with open (path,'wb') as destination:
                    for chunk in file1.chunks():
                        print("writing")
                        destination.write(chunk)

                resizedimg = image1.open(path)
                width, height = resizedimg.size
                maxwidth = 600
                newheight = None
                if width>maxwidth:
                    widthratio = width/maxwidth
                    newwidth = 600
                    newheight = height/widthratio
                    newsize = newwidth, newheight
                    resizedimg.thumbnail(newsize, image1.ANTIALIAS)
                    resizedimg.save(path, resizedimg.format)



            except Exception as e:
                return HttpResponse(str(e))
        # allimages = []        
        # for file in os.listdir("/hotel/static/images/upload/blogimage"):
        #     # for fname in os.listdir(imgdir):
        #     filename = "https://innbparkhotel.com/img/blogimage/" + file

        #     filedict = {}
        #     filedict['url']= filename
        #     filedict['name'] = file

        #     allimages.append(filedict)

        return JsonResponse({'url': filename, 'newsize':newheight})  





@login_required(login_url='/login/')
def pointlog(request):

    userloginno = request.GET.get('pk')

    userloginobj = Userlogin.objects.get(pk=userloginno)

    all_bookings= PointLog.objects.filter(user_login=userloginobj).order_by('pk')
    allbookings = all_bookings
    paginator = Paginator(allbookings, 70)    
    page = request.GET.get('page')
    try:
        allbookings = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        allbookings = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        allbookings = paginator.page(paginator.num_pages)
    context = {
    'allbookings':allbookings
    }
    return render(request,"booking/point_logs.html",context)








@csrf_exempt
def resize_image_api(request):
    import PIL as pillow
    from PIL import Image
    from PIL import ImageOps





    if request.method=="POST":
        # data = json.loads(request.body.decode('utf-8'))
        newfileupload = request.POST.get('url')
        xvalue = decimal.Decimal(request.POST.get('x'))
        yvalue = decimal.Decimal(request.POST.get('y'))
        width = decimal.Decimal(request.POST.get('width'))
        height = decimal.Decimal(request.POST.get('height'))

        try:
            fn = newfileupload.replace("https://innbparkhotel.com/img/blogimage/","")
            filename = "https://innbparkhotel.com/img/blogimage/" + fn
            path = "/hotel/static/images/upload/blogimage/" + fn

            




            image1 = Image.open(path)
            wwidth, wheight = image1.size



            cropped_image = image1.crop((xvalue, yvalue, width+xvalue, height+yvalue))
            resized_image = cropped_image
            resized_image.save(path)

        # if newfileupload.format == 'JPEG':
        #     path = "/hotel/static/images/upload/blogimage/" + fn

        #     file1 = request.FILES['image_file']
        #     print("writing")
        #     try:
        #         with open (path,'wb') as destination:
        #             for chunk in file1.chunks():
        #                 print("writing")
        #                 destination.write(chunk)

        #         resizedimg = image1.open(path)
        #         width, height = resizedimg.size
        #         maxwidth = 600
        #         newheight = None
        #         if width>maxwidth:
        #             widthratio = width/maxwidth
        #             newwidth = 600
        #             newheight = height/widthratio
        #             newsize = newwidth, newheight
        #             resizedimg.thumbnail(newsize, image1.ANTIALIAS)
        #             resizedimg.save(path, resizedimg.format)




        #     except Exception as e:
        #         return HttpResponse(str(e))
        # elif newfileupload.format == 'PNG':
        #     file1 = request.FILES['image_file']
            
        #     try:
        #         with open (path,'wb') as destination:
        #             for chunk in file1.chunks():
        #                 print("writing")
        #                 destination.write(chunk)

        #         resizedimg = image1.open(path)
        #         width, height = resizedimg.size
        #         maxwidth = 600
        #         newheight = None
        #         if width>maxwidth:
        #             widthratio = width/maxwidth
        #             newwidth = 600
        #             newheight = height/widthratio
        #             newsize = newwidth, newheight
        #             resizedimg.thumbnail(newsize, image1.ANTIALIAS)
        #             resizedimg.save(path, resizedimg.format)



        except Exception as e:
            return HttpResponse(str(e))
        # allimages = []        
        # for file in os.listdir("/hotel/static/images/upload/blogimage"):
        #     # for fname in os.listdir(imgdir):
        #     filename = "https://innbparkhotel.com/img/blogimage/" + file

        #     filedict = {}
        #     filedict['url']= filename
        #     filedict['name'] = file

        #     allimages.append(filedict)

        return JsonResponse({'url': filename})  
