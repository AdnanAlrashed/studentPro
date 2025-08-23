from typing import Any, Mapping, Optional, Type, Union
from django.forms.utils import ErrorList
from studentApp.models import *
from django import forms
from django.forms import ChoiceField
from django.http import request


class ChoiceNoValidation(ChoiceField):
    def validate(self, value):
        pass

class DateInput(forms.DateInput):
    input_type = 'date'

class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={'class':'form-control','autocomplete':'off'}))
    password = forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label="first Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(label="UserName",max_length=50,widget=forms.TextInput(attrs={'class':'form-control','autocomplete':'off'}))
    address = forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    course_list = []
    try:

        courses = Courses.objects.all()
        
        for course in courses:
            small_course = (course.id,course.course_name)
            course_list.append(small_course)
    except:
        course_list = []
    
    session_list = []
    try:

        sessions = SessionYearModle.object.all()
        
        for ses in sessions:
            small_ses = (ses.id,"Start"+" " + str(ses.sesstion_start_year) + " "+"End"+" "+ str(ses.sesstion_end_year))
            session_list.append(small_ses)
    except:
        session_list = []

    gender_choice = (
        ("Male","Male"),
        ("Female","Female")
    )

    course = forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={'class':'form-control'}))
    sex = forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={'class':'form-control'}))
    session_year_id= forms.ChoiceField(label="Session Year",widget=forms.Select(attrs={'class':'form-control'}),choices=session_list)
    profile_pic = forms.FileField(label="Profile Pic",max_length=50)

# Form For Eait Student
class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label="first Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(label="UserName",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    address = forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))


    
    course_list = []
    try:
        courses = Courses.objects.all()
        for course in courses:
            small_course = (course.id,course.course_name)
            course_list.append(small_course)
    except:
        course_list = []

    session_list = []
    try:

        sessions = SessionYearModle.object.all()
        
        for ses in sessions:
            small_ses = (ses.id,"Start"+" " + str(ses.sesstion_start_year) + " "+"End"+" "+ str(ses.sesstion_end_year))
            session_list.append(small_ses)
    except:
        session_list = []
    
    gender_choice = (
        ("Male","Male"),
        ("Female","Female")
    )

    course = forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={'class':'form-control'}))
    sex = forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={'class':'form-control'}))
    session_year_id= forms.ChoiceField(label="Session Year",widget=forms.Select(attrs={'class':'form-control'}),choices=session_list)
    profile_pic = forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={'class':'form-control'}),required=False)

class AddStaffForm(forms.Form):
    email = forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label="first Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(label="UserName",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))
    address = forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={'class':'form-control'}))


class EditResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.staff_id = kwargs.pop("staff_id")
        super().__init__()

        subject_list = []
        try:
            subjects = Subjects.objects.filter(staff_id=self.staff_id)
            for subject in subjects:
                subject_single = (subject.id,subject.subject_name)
                subject_list.append(subject_single)

        except:
            subject_list = []

        session_list = []
        try:
            sessions = SessionYearModle.object.all()
            for session in sessions:
                session_single = (session.id,session.sesstion_start_year+" TO "+session.sesstion_end_year)
                session_list.append(session_single)
        except:
            session_list = []
        self.subject_id = forms.ChoiceField(label="Subject",choices=subject_list,widget=forms.Select(attrs={"class":"form-control"}))
        self.session_ids = forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
        self.student_ids = forms.ChoiceField(label="Student",widget=forms.Select(attrs={"class":"form-control"}))
        self.assignment_marks = forms.CharField(label="Assignment Marks",widget=forms.TextInput(attrs={"class":"form-control"}))
        self.exam_marks = forms.CharField(label="Exam Marks",widget=forms.TextInput(attrs={"class":"form-control"}))


class EditResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.staff_id=kwargs.pop("staff_id")
        super(EditResultForm,self).__init__(*args,**kwargs)
        subject_list = []
        try:
            subjects=Subjects.objects.filter(staff_id=self.staff_id)
            for subject in subjects:
                subject_single = (subject.id,subject.subject_name)
                subject_list.append(subject_single)
        except:
            subject_list = []
        self.fields['subject_id'].choices=subject_list

    session_list = []
    try:
        sessions=SessionYearModle.object.all()
        for session in sessions:
            session_single=(session.id,str(session.sesstion_start_year)+" TO "+str(session.sesstion_end_year))
            session_list.append(session_single)
    except:
        session_list = []


        
    subject_id=forms.ChoiceField(label="Subject",widget=forms.Select(attrs={"class":"form-control"}))
    session_ids=forms.ChoiceField(label="Sesssion Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    student_ids=ChoiceNoValidation(label="Student",widget=forms.Select(attrs={"class":"form-control"}))
    assignment_marks=forms.CharField(label="Assingment Marks",widget=forms.TextInput(attrs={"class":"form-control"}))
    exam_marks=forms.CharField(label="Exam Marks",widget=forms.TextInput(attrs={"class":"form-control"}))