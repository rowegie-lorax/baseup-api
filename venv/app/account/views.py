from .models import User

from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext

from oauth2_provider.views.application import ApplicationList, ApplicationUpdate,\
											  ApplicationDetail, ApplicationDelete,\
											  ApplicationRegistration

def index(request):
	error = None
	message = ''
	if request.method == 'POST':
		try:
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
			else:
				error = True
				message = 'Invalid Credentials'
		except Exception as e:
			error = True
			message = 'Invalid Credentials'
		
	return render(request, 'index.html', {'error': error, 'message': message})

def signup(request):
	error = None
	message = ''
	if request.method == 'POST':
		try:
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			email = request.POST.get('email')
			password = request.POST.get('password')
			user = User.objects.create_user(first_name, last_name, email, password)

			error = False
			message = 'Sign up success! Login your account'
		except Exception as e:
			error = True
			message = str(e)

	return render(request, 'sign_up.html', {'error': error, 'message': message})

def home(request):
	return render(request, 'home/home.html')

def edit_profile(request):
	return render(request, 'home/edit_profile.html')

def user_login(request):
	if request.method == 'POST':
		try:
			email = request.POST.get('email').strip()
			password = request.POST.get('password')
			
			user = authenticate(email=email, password=password)
			
			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				return HttpResponse('Invalid Credentials', status=400)
		except Exception as e:
			return HttpResponse('Error:' + str(e), status=400)
	return HttpResponse('Error:', status=400)


class ApplicationCustomView(ApplicationList):
	template_name = "oauth_views/app_list.html"


class ApplicationCustomRegister(ApplicationRegistration):
    template_name = "oauth_views/app_register.html"


class ApplicationCustomUpdate(ApplicationUpdate):
	template_name = "oauth_views/app_upd.html"


class ApplicationCustomDetails(ApplicationDetail):
	template_name = "oauth_views/app_details.html"


class ApplicationCustomDelete(ApplicationDelete):
	template_name = "oauth_views/app_delete_confirm.html"
