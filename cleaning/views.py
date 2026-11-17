from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def services(request):
    return render(request, 'services.html')

def calculator(request):
    return render(request, 'calculator.html')

def contacts(request):
    return render(request, 'contacts.html')
