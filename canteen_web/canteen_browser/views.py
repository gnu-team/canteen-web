from django.shortcuts import render

def index(request):
    return render(request, 'canteen_browser/index.html')
