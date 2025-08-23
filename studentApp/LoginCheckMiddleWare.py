from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _

class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename = view_func.__module__
        user = request.user
        if user.is_authenticated:
            if user.user_type == '1':
                if modulename == 'studentApp.HodViews':
                    pass
                elif modulename == 'studentApp.views' or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('admin_home'))
            elif user.user_type == '2':
                if modulename == 'studentApp.StaffViews' or modulename == "studentApp.EditResultViewClass":
                    pass
                elif modulename == 'studentApp.views' or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('staff_home'))
            elif user.user_type == '3':
                if modulename == 'studentApp.StudentViews':
                    pass
                elif modulename == 'studentApp.views':
                    pass
                else:
                    return HttpResponseRedirect(reverse('stusent_home'))
            else:
                return HttpResponseRedirect(reverse('show_login'))
                 
        else:
            if request.path == reverse('show_login') or request.path == reverse('do_login') or modulename == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse('show_login'))