from django.shortcuts import render

def map(request):
    return render(request, 'canteen_browser/map.html')
