from django.db import models
from django.core.validators import RegexValidator
from datetime import date, datetime
import os, random, struct, hashlib
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random 
from django.contrib.auth.models import User

def upload_location(instance, filename):
  return "%s/%s" %(instance, filename)

class Roomtype(models.Model):
    room_type_name = models.CharField(max_length=50)
    room_type_description = models.TextField()
    room_max_people = models.IntegerField()
    room_kids = models.IntegerField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    bedsize = models.CharField(max_length=50, blank=True, null=True)
    addbed = models.BooleanField(default=False)
    area = models.CharField(max_length=50, blank=True, null=True)
    room_price0 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    room_price1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)
    room_price2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)
    room_price3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)
    room_price4 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)
    room_price5 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)
    room_price6 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,default=0)                        
    room_image = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    room_image2 = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    room_image3 = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    room_image4 = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    def __str__ (self):
        return self.room_type_name     







class Userlogin(models.Model):
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)    
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=50, null=True, blank=True) 
    hashcode = models.CharField(max_length=100, null=True, blank=True) 
    numbertime = models.CharField(max_length=10, default="0", null=True, blank=True) 
    lastpromo = models.IntegerField(default=0)





class Roomnumber(models.Model):
    room_number = models.CharField(max_length=50, unique=True)  
    room_type_name = models.ForeignKey(Roomtype, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default="Ready")
    hidden = models.BooleanField(default=False)
    link = models.ForeignKey('self', blank=True,null=True)

    def __str__ (self):
        return self.room_number 


def upload_location2(instance, filename):
  return "%s/%s" %(instance, filename)     

class Customer(models.Model):
    passno = models.CharField(max_length=50, null=True, blank=True)      
    suffix = models.CharField(max_length=10, blank=True, null=True)    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)    
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=50, null=True, blank=True)  
    occupation = models.CharField(max_length=50, null=True, blank =True)
    plus = models.CharField(max_length=500, null=True, blank=True)
    neg = models.CharField(max_length=500, null=True, blank=True)      
    attachingdocuments = models.FileField(upload_to=upload_location2, null=True, blank=True)
    attachingdocuments2 = models.FileField(upload_to=upload_location2, null=True, blank=True)
    attachingdocuments3 = models.FileField(upload_to=upload_location2, null=True, blank=True)
    attachingdocuments4 = models.FileField(upload_to=upload_location2, null=True, blank=True)         
    user_login = models.ForeignKey(Userlogin, on_delete=models.PROTECT, blank=True, null=True)


    def __str__ (self):
        return self.first_name + " " + self.last_name  



    def save(self,*args, **kwargs): 
        super(Customer, self).save(*args, **kwargs)        
        if self.attachingdocuments:         
            chunk_size = 64*1024
            output_file = filename+".enc"
            file_size = os.path.getsize(filename)

            IV = Random.new().read(AES.block_size)

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
            os.remove(filename)
            self.attachingdocuments= None 
            self.save()












class Booking(models.Model):
    suffix = models.CharField(max_length=10, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=50)
    referenceno = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    country = models.CharField(max_length=50, blank=True)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number format: +60312345678.")
    room_type_name = models.ForeignKey(Roomtype, null=True, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20 )
    room_number = models.ForeignKey(Roomnumber, on_delete=models.PROTECT, blank = True, null=True)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    checkout_date2 = models.DateField(blank=True, null=True)
    earlyout = models.BooleanField(default=False)
    additional_comments = models.CharField(max_length=550, blank=True)
    # booking_success = models.BooleanField(default=False)
    number_of_people = models.IntegerField(blank=True, null=True)
    referral = models.CharField(max_length=50, blank=True, null=True)    
    # ipaddress = models.CharField(max_length=20, null=True, blank=True)
    paymentprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    actualpay = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    extraref = models.CharField(max_length=10, null=True, blank=True)
    checkedin1 = models.DateTimeField(blank=True, null=True)
    checkedout1 = models.DateTimeField(blank=True, null=True)
    purposeoftrip = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    maintain = models.BooleanField(default=False)
    cust33 = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    extension = models.BooleanField(default=False)
    late = models.BooleanField(default=False)
    booktype = models.CharField(max_length=50, blank=True, null=True)
    discountper = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    relatedroom = models.CharField(max_length=50, blank=True, null=True)
    familyroom = models.BooleanField(default=False)
    # predisc = models.BooleanField(default=False)
    upgrade = models.BooleanField(default=False)
    upgradedate = models.DateField(blank=True, null=True)
    ugradebooking = models.IntegerField(blank=True, null=True)
    upgraderoot = models.IntegerField(blank=True, null=True)
    upgradelast = models.BooleanField(default=False)
    def __str__ (self):
        return self.first_name




class Pages(models.Model):
    pages_name = models.CharField(max_length=100)
    pages_title = models.CharField(max_length=100)
    page_short_description = models.CharField(max_length=100)
    pages_content = models.TextField(blank=True, null=True)
    pages_image = models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    pages_large_image = models.ImageField(upload_to=upload_location, blank=True, null=True)
    hidden = models.BooleanField(default=False)
    categories = models.CharField(max_length=100, blank=True, null=True)
    featured = models.BooleanField(default=False)

    def __str__ (self):
        return self.pages_name    

def upload_location(instance, filename):
  return "%s/%s" %(instance, filename)



class FrontPage(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    image= models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    link= models.CharField(max_length=100, blank=True, null=True)

    def __str__ (self):
        return self.title

def upload_location(instance, filename):
  return "%s/%s" %(instance, filename)

  
class FrontImage(models.Model):
    image= models.ImageField(upload_to=upload_location, blank=True, null=True, width_field="", height_field="",)
    description = models.CharField(max_length=100, blank=True, null=True)
    descriptiontitle = models.CharField(max_length=100, blank=True, null=True)

class FrontDesc(models.Model):
    description = models.CharField(max_length=2000)
# class Bookinggroup(models.Model):


class Feedback(models.Model):
    contactname= models.CharField(max_length=70, null=True)
    contactno=models.CharField(max_length=10, null=True)
    contactemail=models.EmailField(null=True)
    description=models.TextField(max_length=750, blank=True, null=True)
    date2 = models.DateTimeField(auto_now_add=True, blank=True, null=True)   


    



class Promocode(models.Model):
    code = models.CharField(max_length=6)
    discountper = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    discountfix = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    onetimeonly = models.CharField(max_length=100, blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    validfrom = models.DateField(blank=True, null=True)
    validto = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    daysbefore = models.IntegerField(blank=True, null=True)
    dayseffective = models.IntegerField(blank=True, null=True)    
    roomeffectiveno = models.IntegerField(blank=True, null=True)
    specialprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    specialbreakfastprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    roomtype = models.ForeignKey(Roomtype, blank=True, null=True)
    membersonly = models.BooleanField(default=False)
    sendemail = models.BooleanField(default=False)
    points = models.IntegerField(blank=True, null=True)
    def __str__ (self):
        return self.description   
        

def increment_invoice_number():
    invoiceslot = Invoice.objects.filter(slot=True)
    last_invoice = Invoice.objects.all().order_by('id').last()
    if invoiceslot:
        last_invoice = invoiceslot.order_by('id').first()
        last_invoice.slot = False
        last_invoice.save()

    year = datetime.now().strftime("%y")
    if not last_invoice:
        return year + '00001'
    if not last_invoice.invoiceno:
        return year + '00001'
    invoice_no = last_invoice.invoiceno
    # invoice_int = int(invoice_no.split(year)[-1])
    # new_invoice_int = invoice_int + 1
    # new_invoice_no = year + str(format(new_invoice_int, '05d'))
    invoice_int = invoice_no[2:]
    new_invoice_int = int(invoice_int) + 1
    new_invoice_no = year + str(format(new_invoice_int, '05d'))
    
    return new_invoice_no

class Invoice(models.Model):
    passno = models.CharField(max_length=50, null=True, blank=True)   
    rtacomm= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    commamount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    invoiceno = models.CharField(max_length=150, default="", blank=True, null=True)
    referenceno = models.CharField(max_length=150, blank=True, null=True)
    email = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    totalwch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    depositamt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.ForeignKey(Promocode,on_delete=models.PROTECT, blank=True, null=True)
    totalpaid = models.BooleanField(default=False)
    bookingfee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bookingfeepaid = models.BooleanField(default=False)
    totalpaiddate = models.DateTimeField(blank=True, null=True)
    depositpaiddate = models.DateTimeField(blank=True, null=True)
    depositreturnedate = models.DateTimeField(blank=True, null=True)
    depositreturned = models.BooleanField(default=False)
    depositcash = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    depositcc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    otherdeposit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    depositpaidby = models.CharField(blank=True, null=True, max_length=100)
    depi = models.CharField(blank=True, null=True, max_length=100)
    deposit = models.BooleanField(default=False)
    bookedby = models.CharField(blank=True, null=True, max_length=100)
    # depositpaymentmethod = models.CharField(max_length=50, blank=True, null=True)
    referral = models.CharField(max_length=50, blank=True, null=True)
    staffbooking = models.BooleanField(default=False) 
    molpay = models.BooleanField(default=False)     
    Paymentmethod = models.CharField(max_length=50, blank=True, null=True)
    # paymentdescription = models.CharField(max_length=100, blank=True, null=True)
    cashpaid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ccpaid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paymentchange = models.CharField(max_length=100, blank=True, null=True)
    datecreated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    checkedin1 = models.DateTimeField(blank=True, null=True)
    checkedinby = models.CharField(blank=True, null=True, max_length=100)
    checkedoutby = models.CharField(blank=True, null=True, max_length=100)    
    checkedout1 = models.DateTimeField(blank=True, null=True)
    depdescrip = models.CharField(blank=True, null=True, max_length=100)
    purposeoftrip = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    gst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rounding = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    servicetax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ttax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    slot = models.BooleanField(default=False)
    invoicedesc = models.CharField(max_length=300, blank=True, null=True)
    additionalcharges= models.CharField(max_length=100, blank=True, null=True)
    additionalcharge= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    otherref = models.CharField(max_length=50, blank=True, null=True)
    descprom = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    addressline1= models.CharField(max_length=70, blank=True, null=True)
    addressline2= models.CharField(max_length=70, blank=True, null=True)
    addressline3= models.CharField(max_length=70, blank=True, null=True)   
    guestname = models.CharField(max_length=150,  blank=True, null=True) 


class Pricing(models.Model):
    pricingname = models.CharField(max_length=10)
    discountper = models.DecimalField(max_digits=10, decimal_places=2)
    discountfix = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(max_length=100, blank=True, null=True)
    room_type = models.ForeignKey(Roomtype, on_delete=models.CASCADE)   



class Employeeclass(models.Model):
    name = models.CharField(max_length=50)
    wages = models.DecimalField(max_digits=10, decimal_places=2, blank=True)


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number format: +60312345678.")
    phone_number = models.CharField( max_length=16 )
    employeclass= models.ForeignKey(Employeeclass, blank=True, null=True)


class Events(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=16 )
    number_of_attendees = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.CharField(max_length=10, blank= True, null=True)
    event_type = models.CharField(max_length=500)
    services = models.CharField(max_length=500, blank=True, null=True)
    daterequested = models.DateTimeField(auto_now_add=True, blank=True, null=True)    


class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Specialrequests(models.Model):
    description = models.CharField(max_length=1000)
    date = models.DateField(blank=True, null=True)
    room_number = models.CharField(max_length=5, null=True, blank=True)
    name = models.CharField(max_length=100)


class Fedback2(models.Model):
    purpose = models.CharField(max_length=20, blank=True, null=True)
    hospitality = models.IntegerField(blank=True, null=True)
    service = models.IntegerField(blank=True, null=True)
    efficiency = models.IntegerField(blank=True, null=True)
    knowledgeable = models.IntegerField(blank=True, null=True)
    comfort = models.IntegerField(blank=True, null=True)
    cleanliness = models.IntegerField(blank=True, null=True)
    atmosphere = models.IntegerField(blank=True, null=True)
    bathroom = models.IntegerField(blank=True, null=True)
    quality = models.IntegerField(blank=True, null=True)
    diversity = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    service2 = models.IntegerField(blank=True, null=True)
    breakfastservice = models.IntegerField(blank=True, null=True)
    pricerat = models.IntegerField(blank=True, null=True)
    locat = models.IntegerField(blank=True, null=True)
    comments= models.CharField(blank=True, null=True, max_length=500)


class nearbyprices(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    hotel = models.CharField(max_length=1000, blank=True, null=True)
    prices = models.CharField(max_length=1000,blank=True, null=True)
    average = models.CharField(max_length=20, blank=True, null=True)


class depositwitheld(models.Model):
    invoice = models.ForeignKey(Invoice, blank=True, null=True )
    itemname = models.CharField(max_length=300, blank=True, null=True)
    itemprice = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, default=0)


class bookdetails(models.Model):
    date = models.DateField()
    room_number = models.ForeignKey(Roomnumber, on_delete=models.PROTECT, blank = True, null=True) 
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, blank=True, null=True)
    # checkedin = models.BooleanField(default=False)
    # pricing = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class housekeeping(models.Model):
    date = models.DateField()
    room_number = models.ForeignKey(Roomnumber, on_delete=models.PROTECT, blank=True, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, blank=True, null=True)
    staff = models.CharField(max_length=300, blank=True, null=True)
    cleaned = models.BooleanField(default=False)
    water = models.IntegerField(blank=True, null=True)
    coffeebag = models.IntegerField(blank=True, null=True)
    teabag = models.IntegerField(blank=True, null=True)
    dentalkit = models.IntegerField(blank=True, null=True)
    shaverkit = models.IntegerField(blank=True, null=True)
    bodylotion = models.IntegerField(blank=True, null=True)
    shampoo=models.IntegerField(blank=True, null=True)
    soap = models.IntegerField(blank=True, null=True)
    comb = models.IntegerField(blank=True, null=True)
    showercap = models.IntegerField(blank=True, null=True)
    sanitarybag =models.IntegerField(blank=True, null=True)
    toiletpaper = models.IntegerField(blank=True, null=True)
    slipper = models.IntegerField(blank=True, null=True)
    repairsneeded = models.CharField(max_length=300, blank=True, null=True)


class Depositsum(models.Model):
    ccdep = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cashdep= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Others = models.TextField(blank=True, null=True)
    cash= models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

class variablepricing(models.Model):
    roomtype = models.ForeignKey(Roomtype, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)



class logging(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    referenceno = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=5000, blank=True, null=True)
    staff = models.CharField(max_length=300, blank=True, null=True)





class reportdate(models.Model): 
	staff = models.CharField(max_length=300, blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	




class whiteboard(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    room_number = models.ForeignKey(Roomnumber, blank=True, null=True)
    texts = models.CharField(max_length=5000, blank=True, null=True)
    staff = models.CharField(max_length=300,blank=True, null=True)
    hidden = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    roomservice = models.BooleanField(default=False)
    forstaff = models.CharField(max_length=300,blank=True, null=True)
    read =  models.BooleanField(default=False)




class Timerole(models.Model):
    user = models.OneToOneField(User)
    inTime = models.TimeField(blank=True, null=True)
    outTime = models.TimeField(blank=True, null=True)




class reviews(models.Model):
    reviewtype = models.CharField(max_length=100,blank=True, null=True)
    date = models.CharField(max_length=50,blank=True, null=True)    
    rating = models.CharField(max_length=10,blank=True, null=True)
    rating2 = models.CharField(max_length=20,blank=True, null=True)
    description = models.CharField(max_length=300,blank=True, null=True)
    name = models.CharField(max_length=100,blank=True, null=True)



class socketdata(models.Model):
    username =  models.CharField(max_length=100,blank=True, null=True)
    sockid = models.CharField(max_length=100,blank=True, null=True)
    logintime = models.DateTimeField(blank=True, null=True)
    logofftime = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=100,blank=True, null=True)






class housekeepingroom(models.Model):
    date = models.DateField()
    room_number = models.ForeignKey(Roomnumber, on_delete=models.PROTECT, blank=True, null=True)
    staff = models.CharField(max_length=300, blank=True, null=True)
    cleaned = models.BooleanField(default=False)
    water = models.IntegerField(blank=True, null=True)
    coffeebag = models.IntegerField(blank=True, null=True)
    teabag = models.IntegerField(blank=True, null=True)
    dentalkit = models.IntegerField(blank=True, null=True)
    shaverkit = models.IntegerField(blank=True, null=True)
    bodylotion = models.IntegerField(blank=True, null=True)
    shampoo=models.IntegerField(blank=True, null=True)
    soap = models.IntegerField(blank=True, null=True)
    comb = models.IntegerField(blank=True, null=True)
    showercap = models.IntegerField(blank=True, null=True)
    sanitarybag =models.IntegerField(blank=True, null=True)
    toiletpaper = models.IntegerField(blank=True, null=True)
    slipper = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True, null=True)
    status = models.CharField(max_length=300, blank=True, null=True)
    checked = models.BooleanField(default=False)


class trolley(models.Model):
    trolleyno = models.CharField(max_length=50, blank=True, null=True)
    date2 = models.DateTimeField(auto_now_add=True, blank=True, null=True)   
    water = models.IntegerField(blank=True, null=True)
    coffeebag = models.IntegerField(blank=True, null=True)
    teabag = models.IntegerField(blank=True, null=True)
    dentalkit = models.IntegerField(blank=True, null=True)
    shaverkit = models.IntegerField(blank=True, null=True)
    bodylotion = models.IntegerField(blank=True, null=True)
    shampoo=models.IntegerField(blank=True, null=True)
    soap = models.IntegerField(blank=True, null=True)
    comb = models.IntegerField(blank=True, null=True)
    showercap = models.IntegerField(blank=True, null=True)
    sanitarybag =models.IntegerField(blank=True, null=True)
    toiletpaper = models.IntegerField(blank=True, null=True)
    slipper = models.IntegerField(blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True,null=True)




class extra_items(models.Model):
    description = models.CharField(max_length=1000, blank=True, null=True)
    paymentprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    referenceno = models.CharField(max_length=150, blank=True)


class PointLog(models.Model):
    user_login = models.ForeignKey(Userlogin, on_delete=models.PROTECT, blank=True, null=True)
    pointused = models.CharField(max_length=100, blank=True, null=True)
    pointdescription = models.CharField(max_length=1000, blank=True, null=True)



class promocoderooms(models.Model):
    promocode = models.ForeignKey(Promocode)
    roomtype = models.ForeignKey(Roomtype, blank=True, null=True)
