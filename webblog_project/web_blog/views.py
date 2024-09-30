from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login
from allauth.account.forms import SignupForm

from django.http import HttpResponse
# Create your views here.


def login(request):
   return render(request, 'login.html')


def register(request):
   if request.method == 'POST':
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      password2 = request.POST['password2']

      if password != password2:
         return HttpResponse("Passwords do not match.")

      if User.objects.filter(username=username).exists():
         return HttpResponse("Username already exists.")

      if User.objects.filter(email=email).exists():
         return HttpResponse("Email already exists.")

      user = User.objects.create_user(username=username, email=email, password=password)
      user.save()
      login(request, user)
      return redirect('home')  # Chuyển hướng đến trang chủ sau khi đăng ký thành công
   return render(request, 'register.html')