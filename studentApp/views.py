import datetime
from django.urls import reverse

from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.urls.base import reverse
from django.utils.translation import gettext as _

from studentApp.EmailBackEnd import EmailBackEnd


def showDemoPage(request):
    return render(request, 'demo.html')

def ShowLoginPage(request):
    return render(request,'login_page.html')

def dologin(request):
    if request.method!='POST':
        return HttpResponse('<h1>Mathod Not Allowed</h1>')
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'),password=request.POST.get('password'))
        if user!= None:
            login(request,user)
            if user.user_type=='1':
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=='2':
                return HttpResponseRedirect(reverse('staff_home'))
            else:
                return HttpResponseRedirect(reverse('student_home'))
        else:
            messages.error(request,'Invalid Login Details')
            return HttpResponseRedirect('/')


def GetUserDetails(request):
    if request.user!= None:
        return HttpResponse('User :'+request.user.email+' usertype : '+str(request.user.user_type))
    else:
        return HttpResponse('Please Login Frist')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
    
