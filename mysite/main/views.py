from django.shortcuts import render, redirect
from django.contrib.auth import logout

def profile(request):
  return render(request, "profile.html")

def login_view(request):
  return render(request, "login.html")

def logout_view(request):
  logout(request)
  return redirect("/")
