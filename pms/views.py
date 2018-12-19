import os, shutil, base64, json, hashlib
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Q
from django.db import transaction, IntegrityError
from time import strftime
from .models import User, Publication, Transaction_publication
from .tools import readConfiguration, kwGenerator

def register(request):
    message = None
    status = "success"
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password")
        
        existUser = User.objects.filter(email=email)
        if existUser.exists():
            print existUser
            message = "This email already exists. Please change it."
            status = "error"
        else:
            newUser = User(username=username, email=email, password=password)
            newUser.save()
            message = "You successfully registered! Now login!"
            
    return render(request, "pms/register.html", {"message" : message, "status": status})

def login(request):
    message = None
    status = None
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        try:
            user = User.objects.get(email=email.lower())
            password_instore = user.password
            encryption = hashlib.md5()
            encryption.update(password_instore)
            password_md5 = encryption.hexdigest()
            if password == password_md5:
                request.session["userId"] = user.id
                request.session["username"] = user.username
                request.session["balance"] = user.credit_point
                return redirect(reverse("upload_publication"))
            else:
                message = "Wrong email or password."
                status = "error"
        except User.DoesNotExist:
            message = "Wrong email or password."
            status = "error"
    return render(request, "pms/login.html", {"message":message, "status": status})

def retrieve(request):
    message = None
    email = request.POST.get("email", "")
    if request.method == "POST":
        try:
            user = User.objects.get(email=email.lower())
            password = user.password
            send_mail(
                'Get back your password.',
                'Your password: ' + password,
                'apache@outlook.com',
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass
        message = "Your password was sent to your email."
    return render(request, "pms/retrieve.html", {"message":message, "status":"success"})    

def logout(request):
    request.session.flush()  #remove all the data stored in session
    return redirect(reverse("login"))

def upload_publication(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    message = None
    if request.method == "POST":
        #Write the uploaded file to the Uploads folder on Terra
        fileData = request.FILES.get("file_data")
        file_name = fileData.name
        file_path = os.path.join(readConfiguration("l_uploadRootDir_publication"), file_name.split(".")[0])
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name_new = ".".join([strftime("%H_%M_%S_%m_%d_%Y"), file_name.split(".")[1]])
        file_location = os.path.join(file_path, file_name_new)
        
        with open(file_location, 'wb+') as destination:
            for chunk in fileData.chunks():
                destination.write(chunk)
                
        #Store the info of the uploaded info into database on the local server
        title = request.POST.get("title")
        category = request.POST.get("category")
        authors = request.POST.get("authors")
        institution = request.POST.get("institution")
        publication_date = request.POST.get("publication_date")
        keywords = request.POST.get("keywords")
        
        price = request.POST.get("price")
        if not price:
            price = 0
        price = float(price)
        
        public_or_not = int(request.POST.get("public_or_not", 0))
        abstract = request.POST.get("abstract", "")
        upload_date = strftime("%m/%d/%Y")
        
        publication = Publication(title=title, category=category, authors=authors, 
                                  institution=institution, publication_date=publication_date, price=price,
                                  keywords=keywords, public_or_not=public_or_not, abstract=abstract, 
                                  file_name=file_name, file_location=file_location, 
                                  uploader_id=user_id, upload_date=upload_date)
        publication.save()
        
    return render(request, "pms/upload_publication.html",{"message": message, "username": request.session.get("username"), "balance": request.session.get("balance")})

def search_publication(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    publicationSet = Publication.objects.filter(Q(public_or_not=1) | Q(uploader_id=user_id))  #complex lookups with Q objects
    purchaseList = Transaction_publication.objects.filter(user_id = user_id)
    publicationList = []
    processList = []
    uploaderList = []
    #Remove the files that are not accessible (deleted or not mounted)
    for publication in publicationSet:
        if os.path.exists(publication.file_location):
            publicationList.append(publication)
            #test if publication.id in purchaseList
            uploaderList.append(User.objects.get(pk=publication.uploader_id).username)
            if user_id==publication.uploader_id or purchaseList.filter(publication_id=publication.id).exists():
                processList.append(1)
            else:
                processList.append(0)
    dataList = zip(publicationList, uploaderList, processList)
    return render(request, "pms/search_publication.html", {"dataList": dataList, "username": request.session.get("username"), "balance": request.session.get("balance")})

def detail_publication(request, publication_id):
    user_id = request.session.get("userId")
    if not user_id:
        return render(request, "pms/login.html")
    publication = Publication.objects.get(pk=publication_id)
    purchased = False
    if user_id != publication.uploader_id:
        if Transaction_publication.objects.filter(user_id=user_id, publication_id=publication.id).exists():
            purchased = True
    
    return render(request, "pms/detail_publication.html", {"publication":publication, "userId": user_id, "uploaderId": publication.uploader_id, "purchased": purchased, "username":request.session.get("username"), "balance": request.session.get("balance")})
    
def save_publication(request):
    user_id = request.session.get("userId")
    if not user_id:
        return redirect(reverse("login"))
    if request.method=="POST":
        publication_id = request.POST.get("publication_id")
        title = request.POST.get("title")
        authors = request.POST.get("authors")
        keywords = request.POST.get("keywords")
        institution = request.POST.get("institution")
        category = request.POST.get("category")
        public_or_not = request.POST.get("public_or_not")
        price = request.POST.get("price")
        publication_date = request.POST.get("publication_date")
        abstract = request.POST.get("publication_abstract")
        
        publication = Publication.objects.get(id = publication_id)
        publication.title = title
        publication.authors = authors
        publication.keywords = keywords
        publication.institution = institution
        publication.category = category
        publication.public_or_not = public_or_not
        publication.price = price
        publication.publication_date = publication_date
        publication.abstract = abstract
        
        publication.save()
        
    return HttpResponse("success")

def order_publication(request):
    if not request.session.get("userId"):
        return redirect(reverse("login"))
    publication_id = request.POST.get("publication_id")
    publication = Publication.objects.get(id=publication_id)
    return render(request, "pub/order_publication.html", {"publication": publication, "username":request.session.get("username"), "balance": request.session.get("balance")})
    
@transaction.atomic    
def payment_publication(request):
    if not request.session.get("userId"):
        return redirect(reverse("login"))
    
    message = None
    paymentMethod = request.POST.get("paymentMethod")
    publication_id = request.POST.get("publication_id")
    
    publication = Publication.objects.get(id=publication_id)
    price = publication.price
    user_id = request.session.get("userId")
    
    if paymentMethod == "creditPoint":
        origin = User.objects.get(pk=publication.uploader_id)
        user = User.objects.get(pk=user_id)
        if user.credit_point >= price:
            try:
                with transaction.atomic():
                    user.credit_point -= price
                    origin.credit_point += price
                    user.save()
                    origin.save()
                    oneTransaction = Transaction_publication(user_id = user_id, publication_id = publication_id, amount=price)
                    oneTransaction.save()
                    request.session["balance"] = user.credit_point
                message = "Success@Go to the search page to find your purchased data!"
            except IntegrityError:
                message = "Error@Transaction failed due to internal error."
        else:
            message = "Warning@Your credit point balance is not enough to buy this publication! Try other payment options."
    elif paymentMethod == "creditCard":
        print "come here for testing."
        oneTransaction = Transaction(user_id = user_id, publication_id = publication_id, amount=price)
        oneTransaction.save()
        message = "success@Go to the search page to find your purchased data!"
    else:  #paypal
        pass
    return HttpResponse(message)

def process_publication(request, publication_id):
    if not request.session.get("userId"):
        return redirect(reverse("login"))
    publication = Publication.objects.get(pk=publication_id)
    publication_location = publication.file_location
    #call Xing's keywords generator
    keyword_weightList = kwGenerator(publication_location)
    print keyword_weightList
    keywordTuple, weightTuple = zip(*keyword_weightList)
    label = "Extracted keywords for publication: " + publication.title
    keywordTuple = [x.encode('utf-8') for x in keywordTuple]
    keywordList = map(str, keywordTuple)
    weightList = list(weightTuple)
    return render(request, "pms/action_publication.html", {"label": label, "keyword_weightList": keyword_weightList, "keywordList":keywordList, "weightList": weightList, "username": request.session.get("username"), "balance": request.session.get("balance")})
