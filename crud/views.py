from django.shortcuts import render, redirect
from .models import Member, Document, Ajax, CsvUpload
import datetime
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from crud.forms import *
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# Create your views here.

def index(request):
    return render(request, 'index.html')

def myview(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    else:
        return redirect('index')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def lista(request):
    members_list = Member.objects.all()
    paginator = Paginator(members_list, 5)
    page = request.GET.get('page')
    try:
        members = paginator.page(page)
    except PageNotAnInteger:
        members = paginator.page(1)
    except EmptyPage:
        members = paginator.page(paginator.num_pages)
    return render(request, 'list.html', {'members': members})

@login_required
def create(request):
    if request.method == 'POST':
        member = Member(
            firstname=request.POST['firstname'],
            lastname=request.POST['lastname'],
            mobile_number=request.POST['mobile_number'],
            description=request.POST['description'],
            location=request.POST['location'],
            date=request.POST['date'],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(), )
        try:
            member.full_clean()
        except ValidationError as e:
            pass
        member.save()
        messages.success(request, 'Member was created successfully!')
        return redirect('/list')
    else:
        return render(request, 'add.html')

@login_required
def edit(request, id):
    members = Member.objects.get(id=id)
    context = {'members': members}
    return render(request, 'edit.html', context)


@login_required
def update(request, id):
    member = Member.objects.get(id=id)
    member.firstname = request.POST['firstname']
    member.lastname = request.POST['lastname']
    member.mobile_number = request.POST['mobile_number']
    member.description = request.POST['description']
    member.location = request.POST['location']
    member.date = request.POST['date']
    member.save()
    messages.success(request, 'Member was updated successfully!')
    return redirect('/list')

@login_required
def delete(request, id):
    member = Member.objects.get(id=id)
    member.delete()
    messages.warning(request, 'Member was deleted successfully!')
    return redirect('/list')


@staff_member_required
def fileupload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        document = Document(
            description=request.POST['description'],
            document=myfile.name,
            uploaded_at=datetime.datetime.now(), )
        document.save()
        messages.success(request, 'File uploaded successfully!')
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return redirect('fileupload')
    else:
        documents = Document.objects.order_by('-uploaded_at')[:3]
        context = {'documents': documents}
    return render(request, 'fileupload.html', context)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def ajax(request):
    if request.method == 'POST':
        if is_ajax(request):
            data = Ajax(
                text=request.POST['text'],
                search=request.POST['search'],
                email=request.POST['email'],
                telephone=request.POST['telephone'],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
            data.save()
            astr = "<html><b> you sent an ajax post request </b> <br> returned data: %s</html>" % data
            return JsonResponse({'data': 'success'})
    else:
        ajax_list = Ajax.objects.order_by('-created_at')
        context = {'ajax_list': ajax_list}
    return render(request, 'ajax.html', {'ajax_list': ajax_list})


@csrf_protect
def getajax(request):
    if request.method == 'GET':
        if is_ajax(request):
            data = Ajax.objects.order_by('-created_at').first()
            created = data.created_at.strftime('%m-%d-%Y %H:%M:%S')
            datas = {"id": data.id, "text": data.text, "search": data.search, "email": data.email,
                     "telephone": data.telephone, "created_at": created}
            return JsonResponse(datas)
    else:
        return JsonResponse({'data': 'failure'})


@csrf_protect
def ajax_delete(request):
    if request.method == 'GET':
        if is_ajax(request):
            id = request.GET['id']
            ajax = Ajax.objects.get(id=id)
            ajax.delete()
            return JsonResponse({'data': 'success'})
    else:
        return JsonResponse({'data': 'failure'})


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
 #       import pdb;pdb.set_trace()
        if form.is_valid():
            users = User(
                username=form.cleaned_data['username'],
                password=make_password(form.cleaned_data['password1']),
                is_staff=False,
                is_active=True,
                is_superuser=False,
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            try:
                users.full_clean()
            except ValidationError as e:
                pass

            try:
                validate_password(form.cleaned_data['password1'], user=None, password_validators=None)
            except ValidationError as e:
                form.add_error('password1', e)  # to be displayed with the field's errors
                return render(request, 'register.html', {'form': form})


            users.save()
            messages.success(request, 'Member was created successfully!')
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def register_success(request):
    return render(request, 'success.html')

@login_required
def users(request):    
    return render(request, 'users.html', {'users': users})

@csrf_protect
def ausers(request):
    result_list = list(User.objects.all()\
                .values('id',
                        'username',
                        'first_name',
                        'last_name',
                        'email',
                        'is_staff',
                       ))
#    alist = [dict(q) for q in result_list]
  
    return JsonResponse(result_list, safe=False)

#   paginator = Paginator(users_list, 5)
#    page = request.GET.get('page')
#    try:
#        users = paginator.page(page)
#    except PageNotAnInteger:
#        users = paginator.page(1)
#    except EmptyPage:
#        users = paginator.page(paginator.num_pages)
#    return render(request, 'users.html', {'users': users})

@login_required
def user_delete(request, id):
    user = User.objects.get(id=id)
    user.delete()
    messages.warning(request, 'User was deleted successfully!')
    return redirect('/users')

@login_required
def upload_csv(request):
    if 'GET' == request.method:
        # csv_list = CsvUpload.objects.all()
        # paginator = Paginator(csv_list, 7)
        # page = request.GET.get('page')
        # try:
        #     csvdata = paginator.page(page)
        # except PageNotAnInteger:
        #     csvdata = paginator.page(1)
        # except EmptyPage:
        #     csvdata = paginator.page(paginator.num_pages)
        # return render(request, 'upload_csv.html', {'csvdata': csvdata})
        csvdata = CsvUpload.objects.all()
        context = {'csvdata': csvdata}
        return render(request, 'upload_csv.html', context)
    try:
        csv_file = request.FILES["csv_file"]

        if len(csv_file) == 0:
            messages.warning(request, 'Empty File')
            return render(request, 'upload_csv.html')

        if not csv_file.name.endswith('.csv'):
            messages.warning(request, 'File is not CSV type')
            return render(request, 'upload_csv.html')

        if csv_file.multiple_chunks():
            messages.warning(request, 'Uploaded file is too big (%.2f MB).' % (csv_file.size / (1000 * 1000),))
            return render(request, 'upload_csv.html')

        file_data = csv_file.read().decode("utf-8")

        lines = file_data.split("\n")
        for index, line in enumerate(lines):
            fields = line.split(",")
            if index == 0:
                if (fields[0] == 'name') and (fields[1] == 'description') and (fields[2] == 'end_date') and (
                        fields[3] == 'notes'):
                    pass
                else:
                    messages.warning(request, 'File is not Correct Headers')
                    return render(request, 'upload_csv.html')
                    break
            else:
                print(index)
                if (len(fields[0]) != 0) and (len(fields[1]) != 0) and (len(fields[2]) != 0) and (len(fields[3]) != 0):
                    data = CsvUpload(
                        name=fields[0],
                        description=fields[1],
                        end_date=datetime.datetime.now(),
                        notes=fields[3]
                    )
                    data.save()
        messages.success(request, "Successfully Uploaded CSV File")
        return redirect('/upload/csv/')

    except Exception as e:
        messages.warning(request, "Unable to upload file. " + e)
        return redirect('/upload/csv/')


@login_required
def changePassword(request):
    print('changepasword')
    return render(request, 'change_password.html')


@login_required
def deleteFiles(request, id):
    file = Document.objects.get(id=id)
    file.delete()
    messages.warning(request, 'File was deleted successfully!')
    return redirect('/fileupload')

@csrf_protect
def storeuser(request):
    myid = request.POST['id']
    if myid:
        data = User.objects.get(id=myid)
        data.username = request.POST['username']
        data.first_name = request.POST['first_name']
        data.last_name = request.POST['last_name']
        data.email = request.POST['email']
        data.is_staff = request.POST['is_staff']
        if request.POST['password']:
            data.password = password=make_password(request.POST['password'])
        data.save()
    else:
        data = User(
                username=request.POST['username'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                is_staff=request.POST['is_staff'],
                password=make_password(request.POST['password']),
            )
        data.save()
    return JsonResponse({'data': 'success'})


@csrf_protect
def edituser(request, id):
    member = User.objects.get(id=id)
    member_dict = {
        "id": member.id,
        "username": member.username,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "email": member.email,
        "is_staff": member.is_staff,
    }
    return JsonResponse(member_dict, safe=False)

@login_required
def deleteuser(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return JsonResponse({'user': 'success'})

@login_required
def profile(request):
    return render(request, 'profile.html')

@csrf_protect
def saveprofile(request, id):
    data = User.objects.get(id=id)
    data.first_name = request.POST['first_name']
    data.last_name = request.POST['last_name']
    data.email = request.POST['email']
    if request.POST['password']:
        data.password = password=make_password(request.POST['password'])
    data.save()
    messages.success(request, "Dati salvati con successo.")
    return redirect('/profile')
    
